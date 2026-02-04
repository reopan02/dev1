import os
import base64
import httpx
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image


class GeminiClient:
    """云雾API中转站的Gemini客户端"""

    def __init__(self):
        self.api_key = os.getenv("YUNWU_API_KEY")
        self.base_url = os.getenv("YUNWU_BASE_URL", "https://yunwu.zeabur.app/v1")
        self.analyze_model = os.getenv("GEMINI_ANALYZE_MODEL", "gemini-2.5-pro")
        self.image_model = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")

        if not self.api_key:
            raise ValueError("YUNWU_API_KEY环境变量未设置")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def analyze_image(self, image_base64: str, system_instruction: str) -> str:
        """
        使用Gemini 2.5 Pro分析图片并生成提示词

        Args:
            image_base64: Base64编码的图片
            system_instruction: 系统指令（reverse_prompt模板）

        Returns:
            生成的提示词文本
        """
        # 根据云雾API文档，使用chat兼容格式
        url = f"{self.base_url}/v1/chat/completions"

        # 构建消息
        payload = {
            "model": self.analyze_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请分析这张电商图片并生成构图提示词"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.7
            #"max_tokens": 1024
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def generate_image(
        self,
        prompt: str,
        reference_image_base64: Optional[str] = None,
        aspect_ratio: str = "1:1",
        image_size: str = "1K"
    ) -> str:
        """
        使用Gemini图片生成API

        Args:
            prompt: 构图提示词
            reference_image_base64: Base64编码的参考图片（目标产品），
                                    为空时使用文生图模式，否则使用图生图模式
            aspect_ratio: 宽高比，如 "1:1", "16:9", "9:16"
            image_size: 分辨率，如 "1K", "2K", "4K"

        Returns:
            Base64编码的生成图片
        """
        # 根据云雾API文档，使用Gemini原生格式
        # 参考: https://yunwu.apifox.cn/api-379838953.md
        url = f"{self.base_url}/v1beta/models/{self.image_model}:generateContent"

        # 判断生成模式：inlineData为空（None或空字符串）时使用文生图，否则使用图生图
        is_text_to_image = not reference_image_base64 or reference_image_base64.strip() == ""

        # 构建请求体（使用正确的camelCase格式）
        if is_text_to_image:
            # 文生图模式：仅包含文本提示词
            parts = [{"text": prompt}]
        else:
            # 图生图模式：包含参考图片和文本提示词
            parts = [
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": reference_image_base64
                    }
                },
                {"text": prompt}
            ]

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        # 添加图片配置（使用camelCase格式）
        if aspect_ratio or image_size:
            image_config = {}
            if aspect_ratio:
                image_config["aspectRatio"] = aspect_ratio
            if image_size:
                image_config["imageSize"] = image_size
            payload["generationConfig"]["imageConfig"] = image_config

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            result = response.json()

            # 解析Gemini原生格式响应
            # Gemini 3 Pro Image Preview 是思考模型，响应可能包含:
            # - thoughtSignature: 加密的思考过程签名（应跳过）
            # - text: 文本响应
            # - inline_data/inlineData: 生成的图片数据
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    for part in parts:
                        # 跳过 thoughtSignature，只查找图片数据
                        # 支持 snake_case 和 camelCase 两种格式
                        if "inline_data" in part:
                            data = part["inline_data"].get("data", "")
                            if data:
                                return data
                        elif "inlineData" in part:
                            data = part["inlineData"].get("data", "")
                            if data:
                                return data

            # 检查是否只有 thoughtSignature（模型仍在思考，未生成图片）
            if "candidates" in result and len(result["candidates"]) > 0:
                parts = result["candidates"][0].get("content", {}).get("parts", [])
                has_only_thought = all("thoughtSignature" in p for p in parts)
                if has_only_thought:
                    raise ValueError("模型返回了思考签名但未生成图片，请重试或简化提示词")

            raise ValueError(f"API响应中未找到生成的图片。响应结构: {result}")

    async def fuse_prompt(self, analysis_result: str, product_info: str, system_instruction: str) -> str:
        """
        使用Gemini将产品信息与分析结果融合

        Args:
            analysis_result: 竞品分析得到的原始提示词
            product_info: 用户输入的目标产品信息
            system_instruction: 系统指令（fuse_prompt模板）

        Returns:
            融合后的提示词文本
        """
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.analyze_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": f"## 竞品分析模板\n\n{analysis_result}\n\n## 目标产品信息\n\n{product_info}"
                }
            ],
            "temperature": 0.7
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

    def validate_image_base64(self, image_base64: str) -> tuple[bool, str]:
        """
        验证Base64图片是否有效

        Returns:
            (is_valid, error_message) - 验证结果和错误信息
        """
        if not image_base64:
            return False, "图片数据为空"

        try:
            # 移除可能的data URL前缀
            clean_base64 = image_base64
            if "," in image_base64:
                clean_base64 = image_base64.split(",")[1]

            # 检查base64字符串是否为空
            if not clean_base64 or clean_base64.strip() == "":
                return False, "图片数据为空"

            # 解码base64
            try:
                image_data = base64.b64decode(clean_base64)
            except Exception:
                return False, "无效的Base64编码"

            # 检查图片大小（限制5MB）
            if len(image_data) > 5 * 1024 * 1024:
                return False, f"图片过大（{len(image_data) / 1024 / 1024:.1f}MB），最大支持5MB"

            # 验证图片格式
            try:
                image = Image.open(BytesIO(image_data))
                image.verify()  # 验证图片完整性
            except Exception:
                return False, "无效的图片格式，请上传 JPEG、PNG、GIF 或 WebP 格式"

            return True, ""
        except Exception as e:
            return False, f"图片验证失败: {str(e)}"

    def is_valid_image(self, image_base64: str) -> bool:
        """向后兼容的简单验证方法"""
        is_valid, _ = self.validate_image_base64(image_base64)
        return is_valid

    async def recognize_product(self, image_base64: str, system_instruction: str) -> str:
        """
        使用Gemini识别产品信息

        Args:
            image_base64: Base64编码的产品图片
            system_instruction: 系统指令（识别模式提示词模板）

        Returns:
            识别出的产品信息文本
        """
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": self.analyze_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请识别这张图片中的产品信息"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.3
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]
