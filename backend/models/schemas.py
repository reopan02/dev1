from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """参考卡片分析请求"""
    image: str = Field(..., description="Base64编码的图片数据")


class AnalyzeResponse(BaseModel):
    """参考卡片分析响应"""
    prompt: str = Field(..., description="生成的卡面风格提示词")
    status: str = Field(default="success", description="处理状态")


class GenerateRequest(BaseModel):
    """卡片图片生成请求"""
    target_images: Optional[list[str]] = Field(
        default=None,
        description="Base64编码的目标角色图片列表（最多10张），为空时使用文生图模式，否则使用图生图模式"
    )
    prompt: str = Field(..., description="编辑后的卡面风格提示词")
    aspect_ratio: Optional[str] = Field(default="1:1", description="图片宽高比")
    image_size: Optional[str] = Field(default="2K", description="图片分辨率: 1K, 2K, 3K, 4K")
    model: Optional[str] = Field(
        default="nano-banana-v2",
        description="图片生成模型: nano-banana-v2, nano-banana-pro, seedream-v4, seedream-v4.5, seedream-v5-lite"
    )


class GenerateResponse(BaseModel):
    """卡片图片生成响应"""
    image_url: str = Field(..., description="生成图片的URL")
    status: str = Field(default="success", description="处理状态")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    status: str = Field(default="error", description="处理状态")


class FusePromptRequest(BaseModel):
    """提示词融合请求"""
    analysis_result: str = Field(..., description="参考卡片分析得到的风格提示词")
    product_info: str = Field(..., description="用户输入的目标角色信息")


class FusePromptResponse(BaseModel):
    """提示词融合响应"""
    fused_prompt: str = Field(..., description="融合后的提示词")
    status: str = Field(default="success", description="处理状态")


class RecognizeProductRequest(BaseModel):
    """角色信息识别请求"""
    image: str = Field(..., description="Base64编码的动漫角色图片")


class RecognizeProductResponse(BaseModel):
    """角色信息识别响应"""
    product_info: str = Field(..., description="识别出的角色信息")
    status: str = Field(default="success", description="处理状态")
