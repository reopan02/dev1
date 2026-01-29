#!/usr/bin/env python3
"""
测试Gemini图片生成API调用
"""

import os
import sys
import asyncio
import base64
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

async def test_generate_image():
    """测试图片生成"""
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")

    from services.gemini_client import GeminiClient

    print("🔍 测试Gemini图片生成API...")
    print()

    # 创建一个简单的测试图片（1x1像素PNG）
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    test_prompt = """
产品居中放置，俯视角度拍摄。
纯白背景，简洁专业。
柔和自然光从左上方45度照射，右侧形成淡淡阴影，增强立体感。
产品占画面中心约60%，四周适当留白，黄金分割比例。
色彩鲜明，与白色背景形成对比，整体明亮清新。
    """.strip()

    try:
        client = GeminiClient()
        print(f"✅ 客户端初始化成功")
        print(f"   API Base URL: {client.base_url}")
        print(f"   图片生成模型: {client.image_model}")
        print()

        print("📤 发送图片生成请求...")
        print(f"   提示词: {test_prompt[:50]}...")
        print(f"   宽高比: 1:1")
        print(f"   分辨率: 1K")
        print()

        result = await client.generate_image(
            prompt=test_prompt,
            reference_image_base64=test_image_base64,
            aspect_ratio="1:1",
            image_size="1K"
        )

        print(f"✅ 图片生成成功!")
        print(f"   返回数据长度: {len(result)} 字符")
        print(f"   数据预览: {result[:100]}...")

        # 保存测试图片
        output_file = Path(__file__).parent / "test_generated_image.png"
        with open(output_file, "wb") as f:
            f.write(base64.b64decode(result))
        print(f"   已保存到: {output_file}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_generate_image())
    sys.exit(0 if result else 1)
