import asyncio
import base64
import httpx
from typing import Optional, cast

from config import Settings

# Model ID → RunningHub API path segment mapping
RUNNINGHUB_MODELS = {
    "seedream-v4": "seedream-v4",
    "seedream-v4.5": "seedream-v4.5",
    "seedream-v5-lite": "seedream-v5-lite",
}

# Aspect ratio → (width, height) mapping for Seedream models
ASPECT_RATIO_MAP = {
    "1:1": (2048, 2048),
    "16:9": (2048, 1152),
    "9:16": (1152, 2048),
    "4:3": (2048, 1536),
    "3:4": (1536, 2048),
}

# image_size → resolution param mapping
IMAGE_SIZE_TO_RESOLUTION = {
    "1K": "1k",
    "2K": "2k",
    "4K": "4k",
}


def is_runninghub_model(model: str) -> bool:
    """Check if a model ID should be routed to RunningHub."""
    return model in RUNNINGHUB_MODELS


class RunningHubClient:
    """RunningHub 标准模型 API 客户端 — 用于 Seedream 系列图像生成"""

    def __init__(self, settings: Settings):
        self.base_url = settings.runninghub_base_url.rstrip("/")
        self.api_key = settings.runninghub_api_key.get_secret_value()
        self.poll_interval = 3  # seconds between status polls
        self.max_poll_time = 300  # max wait time in seconds

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _upload_image_base64(self, client: httpx.AsyncClient, image_base64: str) -> str:
        """Upload a base64 image to RunningHub and return the file URL.

        RunningHub standard model API requires imageUrls (URLs), not raw base64.
        We upload via /task/openapi/upload to get a hosted URL.
        """
        image_bytes = base64.b64decode(image_base64)

        url = f"{self.base_url}/task/openapi/upload"
        files = {"file": ("input.jpg", image_bytes, "image/jpeg")}
        data = {"apiKey": self.api_key, "fileType": "input"}

        response = await client.post(url, files=files, data=data, timeout=60.0)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            raise ValueError(f"RunningHub 图片上传失败: {result.get('msg', '未知错误')}")

        file_name = result["data"]["fileName"]
        # Construct the viewable URL
        return f"{self.base_url}/view?filename={file_name}&type=input&subfolder="

    async def _submit_task(
        self,
        client: httpx.AsyncClient,
        model_path: str,
        mode: str,
        payload: dict,
    ) -> dict:
        """Submit a generation task and return the initial response."""
        url = f"{self.base_url}/openapi/v2/{model_path}/{mode}"
        response = await client.post(url, headers=self._get_headers(), json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()

    async def _poll_task(self, client: httpx.AsyncClient, task_id: str) -> dict:
        """Poll task status until SUCCESS or FAILED."""
        url = f"{self.base_url}/openapi/v2/query"
        elapsed = 0.0

        while elapsed < self.max_poll_time:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json={"taskId": task_id},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            status = result.get("status", "")

            if status == "SUCCESS":
                return result
            if status == "FAILED":
                error_msg = result.get("errorMessage") or "任务失败"
                failed_reason = result.get("failedReason")
                if failed_reason:
                    error_msg += f" — {failed_reason}"
                raise ValueError(f"RunningHub 任务失败: {error_msg}")

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(f"RunningHub 任务超时（等待 {self.max_poll_time}s）")

    async def generate_image(
        self,
        prompt: str,
        model: str,
        reference_image_base64: Optional[str] = None,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
    ) -> str:
        """Generate an image using RunningHub standard model API.

        Args:
            prompt: Generation prompt text.
            model: Model identifier (e.g. "seedream-v4.5").
            reference_image_base64: Optional base64 reference image for image-to-image.
            aspect_ratio: Aspect ratio string like "1:1", "16:9".
            image_size: Resolution tier like "1K", "2K", "4K".

        Returns:
            Base64-encoded generated image.
        """
        model_path = RUNNINGHUB_MODELS.get(model)
        if not model_path:
            raise ValueError(f"不支持的 RunningHub 模型: {model}")

        is_img2img = bool(reference_image_base64 and reference_image_base64.strip())

        # Build request payload
        dims = ASPECT_RATIO_MAP.get(aspect_ratio, (2048, 2048))
        resolution = IMAGE_SIZE_TO_RESOLUTION.get(image_size)

        payload: dict = {"prompt": prompt}

        # Use resolution param if available (takes priority over width/height)
        if resolution:
            payload["resolution"] = resolution
        else:
            payload["width"] = dims[0]
            payload["height"] = dims[1]

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Image-to-image: upload reference and add imageUrls
            if is_img2img:
                assert reference_image_base64 is not None
                image_url = await self._upload_image_base64(client, reference_image_base64)
                payload["imageUrls"] = [image_url]
                mode = "image-to-image"
            else:
                mode = "text-to-image"

            # Submit task
            submit_result = await self._submit_task(client, model_path, mode, payload)

            task_id = submit_result.get("taskId")
            if not task_id:
                raise ValueError(f"RunningHub 未返回 taskId: {submit_result}")

            status = submit_result.get("status", "")

            # If already succeeded (unlikely but possible)
            if status == "SUCCESS" and submit_result.get("results"):
                result_data = submit_result
            elif status == "FAILED":
                raise ValueError(f"RunningHub 任务提交即失败: {submit_result.get('errorMessage', '')}")
            else:
                # Poll until done
                result_data = await self._poll_task(client, task_id)

            # Extract image URL from results
            results = result_data.get("results") or []
            if not results:
                raise ValueError("RunningHub 任务完成但未返回结果")

            image_url = results[0].get("url")
            if not image_url:
                raise ValueError("RunningHub 结果中未找到图片 URL")

            # Download the image and convert to base64
            img_response = await client.get(image_url, timeout=60.0)
            img_response.raise_for_status()
            return base64.b64encode(img_response.content).decode("utf-8")
