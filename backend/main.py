from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from pathlib import Path

from models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    GenerateRequest,
    GenerateResponse,
    ErrorResponse,
    FusePromptRequest,
    FusePromptResponse
)
from services.gemini_client import GeminiClient
from services.prompt_loader import load_reverse_prompt_template, load_fuse_prompt_template

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="E-Commerce Image Generator API",
    description="电商图片生成器 - 使用Gemini AI分析竞品并生成新图片",
    version="1.0.0"
)

# CORS配置（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Gemini客户端
gemini_client = GeminiClient()

# 加载提示词模板
try:
    reverse_prompt_template = load_reverse_prompt_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    reverse_prompt_template = "请分析这张图片的构图、光影、背景、风格等元素，生成一段可用于图片生成的提示词。"

# 加载融合提示词模板
try:
    fuse_prompt_template = load_fuse_prompt_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    fuse_prompt_template = "请将目标产品信息融入到竞品分析模板中，生成新的图片生成提示词。"


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "E-Commerce Image Generator API"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_competitor_image(request: AnalyzeRequest):
    """
    分析竞品图片并生成构图提示词

    - **image**: Base64编码的竞品图片
    """
    try:
        # 验证图片
        if not gemini_client.validate_image_base64(request.image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的图片格式或图片过大（最大5MB）"
            )

        # 调用Gemini分析
        prompt = await gemini_client.analyze_image(
            image_base64=request.image,
            system_instruction=reverse_prompt_template
        )

        return AnalyzeResponse(prompt=prompt.strip())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片分析失败: {str(e)}"
        )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_product_image(request: GenerateRequest):
    """
    生成新的产品图片

    - **target_image**: Base64编码的目标产品图片
    - **prompt**: 编辑后的构图提示词
    - **aspect_ratio**: 图片宽高比（可选，默认1:1）
    - **image_size**: 图片分辨率（可选，默认1K）
    """
    try:
        # 验证图片
        if not gemini_client.validate_image_base64(request.target_image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的图片格式或图片过大（最大5MB）"
            )

        # 验证提示词
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提示词过短，请提供详细的构图描述"
            )

        # 调用Gemini生成图片
        generated_image = await gemini_client.generate_image(
            prompt=request.prompt,
            reference_image_base64=request.target_image,
            aspect_ratio=request.aspect_ratio,
            image_size=request.image_size
        )

        return GenerateResponse(generated_image=generated_image)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片生成失败: {str(e)}"
        )


@app.post("/api/fuse-prompt", response_model=FusePromptResponse)
async def fuse_prompt(request: FusePromptRequest):
    """
    融合产品信息与竞品分析结果

    - **analysis_result**: 竞品分析得到的原始提示词
    - **product_info**: 用户输入的目标产品信息
    """
    try:
        # 验证输入
        if not request.analysis_result or len(request.analysis_result.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="竞品分析结果过短"
            )

        if not request.product_info or len(request.product_info.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入产品信息"
            )

        # 调用Gemini融合
        fused = await gemini_client.fuse_prompt(
            analysis_result=request.analysis_result,
            product_info=request.product_info,
            system_instruction=fuse_prompt_template
        )

        return FusePromptResponse(fused_prompt=fused.strip())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提示词融合失败: {str(e)}"
        )


# 生产环境：挂载静态文件
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """服务前端应用"""
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
