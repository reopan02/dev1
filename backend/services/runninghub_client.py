import asyncio
import importlib
from dataclasses import dataclass
from typing import cast

import httpx

_config_module = importlib.import_module("config")
Settings = _config_module.Settings


@dataclass(frozen=True)
class ModelConfig:
    display_name: str
    api_path: str
    api_path_official: str
    image_to_image_modes: tuple[str, ...]


# 所有模型统一参数格式：resolution（必填）+ aspectRatio（可选）+ imageUrls（图生图）
MODELS: dict[str, ModelConfig] = {
    "nano-banana-v2": ModelConfig(
        display_name="Nano Banana V2",
        api_path="rhart-image-n-g31-flash",
        api_path_official="rhart-image-n-g31-flash",
        image_to_image_modes=("image-to-image",),
    ),
    "nano-banana-pro": ModelConfig(
        display_name="Nano Banana Pro",
        api_path="rhart-image-n-pro",
        api_path_official="rhart-image-n-pro",
        image_to_image_modes=("edit",),
    ),
    "seedream-v4": ModelConfig(
        display_name="Seedream v4",
        api_path="seedream-v4",
        api_path_official="seedream-v4",
        image_to_image_modes=("image-to-image",),
    ),
    "seedream-v4.5": ModelConfig(
        display_name="Seedream v4.5",
        api_path="seedream-v4.5",
        api_path_official="seedream-v4.5",
        image_to_image_modes=("image-to-image",),
    ),
    "seedream-v5-lite": ModelConfig(
        display_name="Seedream v5 Lite",
        api_path="seedream-v5-lite",
        api_path_official="seedream-v5-lite",
        image_to_image_modes=("image-to-image",),
    ),
}

# 旧 model ID → 新 model ID 兼容映射
MODEL_ALIASES: dict[str, str] = {
    "gemini-3-pro-image-preview": "nano-banana-pro",
    "gemini-3.1-flash-image-preview": "nano-banana-v2",
}

IMAGE_SIZE_TO_RESOLUTION: dict[str, str] = {
    "1K": "1k",
    "2K": "2k",
    "3K": "3k",
    "4K": "4k",
}


def _as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("RunningHub 返回了非对象格式响应")
    return cast(dict[str, object], value)


def _as_list(value: object) -> list[object]:
    if not isinstance(value, list):
        return []
    return value


def _as_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _build_payload(
    prompt: str,
    aspect_ratio: str,
    image_size: str,
    is_img2img: bool,
    image_data_uris: list[str] | None,
) -> dict[str, object]:
    """统一构建请求 payload — 所有模型共用 resolution + aspectRatio 格式。"""
    resolution = IMAGE_SIZE_TO_RESOLUTION.get(image_size.upper(), "2k")

    payload: dict[str, object] = {
        "prompt": prompt,
        "resolution": resolution,
    }

    # aspectRatio 可选，仅在非 auto 时传递
    if aspect_ratio and aspect_ratio != "auto":
        payload["aspectRatio"] = aspect_ratio

    if is_img2img and image_data_uris:
        payload["imageUrls"] = image_data_uris

    return payload


def _base64_to_data_uri(image_base64: str) -> str:
    """将裸 base64 字符串转为 data URI（imageUrls 支持此格式，免上传）。"""
    if image_base64.startswith("data:"):
        return image_base64
    return f"data:image/png;base64,{image_base64}"


class RunningHubClient:
    """RunningHub 标准模型 API 客户端（统一处理全部图像生成模型）"""

    def __init__(self, settings: Settings):
        self.base_url: str = settings.runninghub_base_url.rstrip("/")
        self.api_key: str = settings.runninghub_api_key.get_secret_value()
        self.poll_interval: int = 3
        self.max_poll_time: int = 300

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _submit_task(
        self,
        client: httpx.AsyncClient,
        model_path: str,
        mode: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        url = f"{self.base_url}/openapi/v2/{model_path}/{mode}"
        response = await client.post(url, headers=self._get_headers(), json=payload, timeout=60.0)
        response.raise_for_status()
        return _as_dict(cast(object, response.json()))

    async def _poll_task(self, client: httpx.AsyncClient, task_id: str) -> dict[str, object]:
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
            result = _as_dict(cast(object, response.json()))
            task_status = _as_str(result.get("status"))

            if task_status == "SUCCESS":
                return result

            if task_status == "FAILED":
                error_msg = _as_str(result.get("errorMessage"), "任务失败")
                failed_reason = result.get("failedReason")
                if failed_reason is not None:
                    error_msg += f" — {failed_reason}"
                raise ValueError(f"RunningHub 任务失败: {error_msg}")

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(f"RunningHub 任务超时（等待 {self.max_poll_time}s）")

    async def _submit_and_wait(
        self,
        client: httpx.AsyncClient,
        model_path: str,
        mode: str,
        payload: dict[str, object],
    ) -> dict[str, object]:
        submit_result = await self._submit_task(client, model_path, mode, payload)

        task_id = _as_str(submit_result.get("taskId"))
        if not task_id:
            raise ValueError(f"RunningHub 未返回 taskId: {submit_result}")

        task_status = _as_str(submit_result.get("status"))
        if task_status == "SUCCESS":
            return submit_result
        if task_status == "FAILED":
            error_msg = _as_str(submit_result.get("errorMessage"), "任务失败")
            failed_reason = submit_result.get("failedReason")
            if failed_reason is not None:
                error_msg += f" — {failed_reason}"
            raise ValueError(f"RunningHub 任务提交即失败: {error_msg}")

        return await self._poll_task(client, task_id)

    async def _run_with_fallback(
        self,
        client: httpx.AsyncClient,
        model_config: ModelConfig,
        mode_candidates: tuple[str, ...],
        payload: dict[str, object],
    ) -> dict[str, object]:
        """先尝试低价渠道版，失败则 fallback 到官方稳定版。"""
        path_candidates = [model_config.api_path]
        if model_config.api_path_official != model_config.api_path:
            path_candidates.append(model_config.api_path_official)

        last_error: Exception | None = None

        for model_path in path_candidates:
            for mode in mode_candidates:
                try:
                    return await self._submit_and_wait(client, model_path, mode, payload)
                except Exception as exc:
                    last_error = exc

        raise ValueError(
            f"RunningHub 调用失败（路径: {path_candidates}, 模式: {list(mode_candidates)}）: {last_error}"
        )

    def _extract_first_image_url(self, result_data: dict[str, object]) -> str:
        results = _as_list(result_data.get("results"))
        if not results:
            raise ValueError("RunningHub 任务完成但未返回结果")

        first_result = _as_dict(results[0])
        image_url = _as_str(first_result.get("url"))
        if not image_url:
            raise ValueError("RunningHub 结果中未找到图片 URL")
        return image_url

    async def generate_image(
        self,
        prompt: str,
        model: str,
        reference_images: list[str] | None = None,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
    ) -> str:
        """生成图片并返回结果图片 URL。"""
        # 兼容旧 model ID
        resolved_model = MODEL_ALIASES.get(model, model)
        model_config = MODELS.get(resolved_model)
        if not model_config:
            raise ValueError(f"不支持的 RunningHub 模型: {model}")

        is_img2img = bool(reference_images and len(reference_images) > 0)

        # imageUrls 支持 base64 data URI，无需先上传
        image_data_uris: list[str] | None = None
        if is_img2img and reference_images:
            image_data_uris = [_base64_to_data_uri(img) for img in reference_images]

        payload = _build_payload(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            is_img2img=is_img2img,
            image_data_uris=image_data_uris,
        )

        mode_candidates = model_config.image_to_image_modes if is_img2img else ("text-to-image",)

        async with httpx.AsyncClient(timeout=60.0) as client:
            result_data = await self._run_with_fallback(client, model_config, mode_candidates, payload)

        return self._extract_first_image_url(result_data)
