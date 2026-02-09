import os
from pathlib import Path


def load_reverse_prompt_template() -> str:
    """加载反向提示词模板"""
    template_path = Path(__file__).parent.parent.parent / "Guidance" / "reverse_prompt.md"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def load_fuse_prompt_template() -> str:
    """加载融合提示词模板"""
    template_path = Path(__file__).parent.parent.parent / "Guidance" / "fuse_prompt.md"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def load_recognize_product_template() -> str:
    """
    加载产品识别提示词模板

    Returns:
        提示词模板内容
    """
    template_path = Path(__file__).parent.parent.parent / "Guidance" / "recognize_product.md"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
