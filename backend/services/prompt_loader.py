import os
from pathlib import Path


def load_reverse_prompt_template() -> str:
    """加载反向提示词模板"""
    template_path = Path(__file__).parent.parent.parent / "Guidance" / "reverse_prompt.md"

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
