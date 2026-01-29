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
        reference_image_base64: str,
        aspect_ratio: str = "1:1",
        image_size: str = "1K"
    ) -> str:
        """
        使用Gemini图片生成API

        Args:
            prompt: 构图提示词
            reference_image_base64: Base64编码的参考图片（目标产品）
            aspect_ratio: 宽高比，如 "1:1", "16:9", "9:16"
            image_size: 分辨率，如 "1K", "2K", "4K"

        Returns:
            Base64编码的生成图片
        """
        # 根据云雾API文档，使用Gemini原生格式
        # 参考: https://yunwu.apifox.cn/api-379838953.md
        url = f"{self.base_url}/v1beta/models/{self.image_model}:generateContent"

        # 构建请求体
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": reference_image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_modalities": ["IMAGE"]
            }
        }

        # 添加图片配置
        if aspect_ratio or image_size:
            image_config = {}
            if aspect_ratio:
                image_config["aspect_ratio"] = aspect_ratio
            if image_size:
                image_config["image_size"] = image_size
            payload["generationConfig"]["image_config"] = image_config

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

    def validate_image_base64(self, image_base64: str) -> bool:
        """验证Base64图片是否有效"""
        try:
            # 移除可能的data URL前缀
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]

            # 解码并验证
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))

            # 检查图片大小（限制5MB）
            if len(image_data) > 5 * 1024 * 1024:
                return False

            return True
        except Exception:
            return False
