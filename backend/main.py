import json
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
import os
import traceback
from pathlib import Path
from typing import AsyncGenerator

from models.schemas import (
    AnalyzeRequest,
    GenerateRequest,
    GenerateResponse,
    ErrorResponse,
    FusePromptRequest,
    RecognizeProductRequest,
)
from services.gemini_client import GeminiClient
from services.llm_manager import LLMManager
from services.prompt_loader import load_reverse_prompt_template, load_fuse_prompt_template, load_recognize_product_template
from config import get_settings

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

# 初始化客户端
settings = get_settings()
gemini_client = GeminiClient(settings)
llm_manager = LLMManager(settings)

# 加载提示词模板（全部在启动时加载）
try:
    reverse_prompt_template = load_reverse_prompt_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    reverse_prompt_template = "请分析这张图片的构图、光影、背景、风格等元素，生成一段可用于图片生成的提示词。"

try:
    fuse_prompt_template = load_fuse_prompt_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    fuse_prompt_template = "请将目标产品信息融入到竞品分析模板中，生成新的图片生成提示词。"

try:
    recognize_template = load_recognize_product_template()
except FileNotFoundError as e:
    print(f"警告: {e}")
    recognize_template = "请识别图片中的产品信息，包括产品名称、类别、颜色、材质等特征。"


def _sse_chunk(content: str, done: bool = False) -> str:
    """Format a single SSE data line."""
    return f"data: {json.dumps({'content': content, 'done': done}, ensure_ascii=False)}\n\n"


def _sse_error(message: str) -> str:
    """Format an SSE error line."""
    return f"data: {json.dumps({'error': message, 'done': True}, ensure_ascii=False)}\n\n"


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "E-Commerce Image Generator API"}


@app.post("/api/analyze")
async def analyze_competitor_image(request: AnalyzeRequest):
    """
    分析竞品图片并生成构图提示词（SSE流式响应）

    - **image**: Base64编码的竞品图片
    """
    # 预流验证：返回400 JSON（非SSE）
    is_valid, error_msg = gemini_client.validate_image_base64(request.image)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    async def generate() -> AsyncGenerator[str, None]:
        try:
            messages = [
                {"role": "system", "content": reverse_prompt_template},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张电商图片并生成构图提示词"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{request.image}"}
                        }
                    ]
                }
            ]
            async for chunk in llm_manager.stream_chat(messages):
                yield _sse_chunk(chunk)
            yield _sse_chunk("", done=True)
        except Exception as e:
            traceback.print_exc()
            yield _sse_error(f"图片分析失败: {str(e)}")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_product_image(request: GenerateRequest):
    """
    生成新的产品图片

    - **target_image**: Base64编码的目标产品图片（可选，为空时使用文生图模式）
    - **prompt**: 编辑后的构图提示词
    - **aspect_ratio**: 图片宽高比（可选，默认1:1）
    - **image_size**: 图片分辨率（可选，默认1K）
    """
    try:
        # 判断生成模式
        is_text_to_image = not request.target_image or request.target_image.strip() == ""

        # 图生图模式时验证图片
        if not is_text_to_image:
            is_valid, error_msg = gemini_client.validate_image_base64(request.target_image)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )

        # 验证提示词
        if not request.prompt or len(request.prompt.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提示词不能为空"
            )

        # 调用Gemini生成图片
        generated_image = await gemini_client.generate_image(
            prompt=request.prompt,
            reference_image_base64=request.target_image if not is_text_to_image else None,
            aspect_ratio=request.aspect_ratio,
            image_size=request.image_size,
            model=request.model
        )

        return GenerateResponse(generated_image=generated_image)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片生成失败: {str(e)}"
        )


@app.post("/api/fuse-prompt")
async def fuse_prompt(request: FusePromptRequest):
    """
    融合产品信息与竞品分析结果（SSE流式响应）

    - **analysis_result**: 竞品分析得到的原始提示词
    - **product_info**: 用户输入的目标产品信息
    """
    # 预流验证：返回400 JSON（非SSE）
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

    async def generate() -> AsyncGenerator[str, None]:
        try:
            messages = [
                {"role": "system", "content": fuse_prompt_template},
                {
                    "role": "user",
                    "content": f"## 竞品分析模板\n\n{request.analysis_result}\n\n## 目标产品信息\n\n{request.product_info}"
                }
            ]
            async for chunk in llm_manager.stream_chat(messages):
                yield _sse_chunk(chunk)
            yield _sse_chunk("", done=True)
        except Exception as e:
            traceback.print_exc()
            yield _sse_error(f"提示词融合失败: {str(e)}")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/recognize-product")
async def recognize_product(request: RecognizeProductRequest):
    """
    识别产品图片中的产品信息（SSE流式响应）

    - **image**: Base64编码的产品图片
    """
    # 预流验证：返回400 JSON（非SSE）
    is_valid, error_msg = gemini_client.validate_image_base64(request.image)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    async def generate() -> AsyncGenerator[str, None]:
        try:
            messages = [
                {"role": "system", "content": recognize_template},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别这张图片中的产品信息"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{request.image}"}
                        }
                    ]
                }
            ]
            # recognize uses temperature=0.3 (lower for more factual output)
            async for chunk in llm_manager.stream_chat(messages, temperature=settings.llm_recognize_temperature):
                yield _sse_chunk(chunk)
            yield _sse_chunk("", done=True)
        except Exception as e:
            traceback.print_exc()
            yield _sse_error(f"产品识别失败: {str(e)}")

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
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
