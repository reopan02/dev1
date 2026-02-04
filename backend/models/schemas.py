from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """竞品图片分析请求"""
    image: str = Field(..., description="Base64编码的图片数据")


class AnalyzeResponse(BaseModel):
    """竞品图片分析响应"""
    prompt: str = Field(..., description="生成的构图提示词")
    status: str = Field(default="success", description="处理状态")


class GenerateRequest(BaseModel):
    """图片生成请求"""
    target_image: Optional[str] = Field(
        default=None,
        description="Base64编码的目标产品图片，为空时使用文生图模式，否则使用图生图模式"
    )
    prompt: str = Field(..., description="编辑后的构图提示词")
    aspect_ratio: Optional[str] = Field(default="1:1", description="图片宽高比")
    image_size: Optional[str] = Field(default="1K", description="图片分辨率: 1K, 2K, 4K")


class GenerateResponse(BaseModel):
    """图片生成响应"""
    generated_image: str = Field(..., description="Base64编码的生成图片")
    status: str = Field(default="success", description="处理状态")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    status: str = Field(default="error", description="处理状态")


class FusePromptRequest(BaseModel):
    """提示词融合请求"""
    analysis_result: str = Field(..., description="竞品分析得到的原始提示词")
    product_info: str = Field(..., description="用户输入的目标产品信息")


class FusePromptResponse(BaseModel):
    """提示词融合响应"""
    fused_prompt: str = Field(..., description="融合后的提示词")
    status: str = Field(default="success", description="处理状态")


class RecognizeProductRequest(BaseModel):
    """产品信息识别请求"""
    image: str = Field(..., description="Base64编码的产品图片")
    mode: str = Field(
        default="simple",
        description="识别模式: simple(简洁) 或 detailed(详细)"
    )


class RecognizeProductResponse(BaseModel):
    """产品信息识别响应"""
    product_info: str = Field(..., description="识别出的产品信息")
    status: str = Field(default="success", description="处理状态")
