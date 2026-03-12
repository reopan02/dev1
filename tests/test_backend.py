#!/usr/bin/env python3
"""
快速测试脚本 - 验证后端API功能
"""

import os
import sys
import base64
import json
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_imports():
    """测试依赖导入"""
    print("🔍 测试依赖导入...")
    try:
        import fastapi
        import httpx
        from dotenv import load_dotenv
        print("✅ 所有依赖导入成功")
        return True
    except ImportError as e:
        print(f"❌ 依赖导入失败: {e}")
        return False

def test_env_config():
    """测试环境配置"""
    print("\n🔍 测试环境配置...")
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")

    api_key = os.getenv("YUNWU_API_KEY")
    if not api_key:
        print("❌ YUNWU_API_KEY 未配置")
        return False

    print(f"✅ API密钥已配置 (长度: {len(api_key)})")
    return True

def test_prompt_template():
    """测试提示词模板加载"""
    print("\n🔍 测试提示词模板...")
    try:
        from services.prompt_loader import load_reverse_prompt_template
        template = load_reverse_prompt_template()
        print(f"✅ 模板加载成功 (长度: {len(template)} 字符)")
        print(f"   预览: {template[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 模板加载失败: {e}")
        return False

def test_gemini_client():
    """测试Gemini客户端初始化"""
    print("\n🔍 测试Gemini客户端...")
    try:
        from dotenv import load_dotenv
        load_dotenv(backend_dir / ".env")

        from services.gemini_client import GeminiClient
        client = GeminiClient()
        print("✅ Gemini客户端初始化成功")
        print(f"   分析模型: {client.analyze_model}")
        print(f"   生成模型: {client.image_model}")
        return True
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return False

def test_image_validation():
    """测试图片验证"""
    print("\n🔍 测试图片验证...")
    try:
        from dotenv import load_dotenv
        load_dotenv(backend_dir / ".env")

        from services.gemini_client import GeminiClient
        client = GeminiClient()

        # 测试有效的Base64
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        result = client.validate_image_base64(test_image)

        if result:
            print("✅ 图片验证功能正常")
            return True
        else:
            print("❌ 图片验证失败")
            return False
    except Exception as e:
        print(f"❌ 图片验证测试失败: {e}")
        return False

def test_api_schemas():
    """测试API数据模型"""
    print("\n🔍 测试API数据模型...")
    try:
        from models.schemas import AnalyzeRequest, GenerateRequest

        # 测试AnalyzeRequest
        analyze_req = AnalyzeRequest(image="test_base64")
        print(f"✅ AnalyzeRequest: {analyze_req.model_dump()}")

        # 测试GenerateRequest
        generate_req = GenerateRequest(
            target_image="test_base64",
            prompt="测试提示词",
            aspect_ratio="1:1",
            image_size="1K"
        )
        print(f"✅ GenerateRequest: {generate_req.model_dump()}")

        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("动漫卡片生成器 - 后端测试")
    print("=" * 60)

    tests = [
        ("依赖导入", test_imports),
        ("环境配置", test_env_config),
        ("提示词模板", test_prompt_template),
        ("Gemini客户端", test_gemini_client),
        ("图片验证", test_image_validation),
        ("API数据模型", test_api_schemas),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 测试异常: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！可以启动应用了。")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
