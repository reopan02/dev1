import base64
from io import BytesIO

from PIL import Image


def validate_image_base64(image_base64: str) -> tuple[bool, str]:
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


def is_valid_image(image_base64: str) -> bool:
    """向后兼容的简单验证方法"""
    is_valid, _ = validate_image_base64(image_base64)
    return is_valid
