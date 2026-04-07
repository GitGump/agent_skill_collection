"""
水印添加工具
为壁纸图片添加半透明水印，保护原创内容
"""
import os
from PIL import Image, ImageDraw, ImageFont
import argparse


def create_watermark_image(
    text: str,
    image_size: tuple,
    position: str = "bottom_right",
    opacity: int = 80,
    font_size: int = 24,
    color: tuple = (255, 255, 255)
) -> Image.Image:
    """
    创建水印图片

    Args:
        text: 水印文字
        image_size: 原图尺寸 (width, height)
        position: 水印位置 (top_left, top_right, bottom_left, bottom_right, center)
        opacity: 透明度 (0-255)
        font_size: 字体大小
        color: RGB颜色

    Returns:
        带水印的PIL Image对象
    """
    width, height = image_size

    # 创建透明背景
    watermark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    # 尝试使用系统字体，否则使用默认字体
    try:
        # Windows系统字体路径
        font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 计算文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 边距
    padding = 30

    # 根据位置计算坐标
    positions = {
        "top_left": (padding, padding),
        "top_right": (width - text_width - padding, padding),
        "bottom_left": (padding, height - text_height - padding),
        "bottom_right": (width - text_width - padding, height - text_height - padding),
        "center": ((width - text_width) // 2, (height - text_height) // 2)
    }

    pos = positions.get(position, positions["bottom_right"])

    # 绘制文字（带透明度）
    alpha = opacity
    draw.text(pos, text, font=font, fill=(*color, alpha))

    return watermark


def add_text_watermark(
    input_path: str,
    output_path: str,
    watermark_text: str = "山野收容所",
    position: str = "bottom_right",
    opacity: int = 60,
    font_size: int = 28
) -> bool:
    """
    为图片添加文字水印

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        watermark_text: 水印文字
        position: 水印位置
        opacity: 透明度 (0-100)
        font_size: 字体大小

    Returns:
        是否成功
    """
    try:
        # 打开原图
        img = Image.open(input_path)

        # 如果是RGB模式，转换为RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 创建水印
        watermark = create_watermark_image(
            text=watermark_text,
            image_size=img.size,
            position=position,
            opacity=int(opacity * 2.55),  # 转换为0-255范围
            font_size=font_size,
            color=(255, 255, 255)  # 白色水印
        )

        # 将水印应用到原图
        watermarked = Image.alpha_composite(img, watermark)

        # 转换回RGB（如果是PNG保存）
        if output_path.lower().endswith('.png'):
            watermarked.convert('RGBA').save(output_path)
        else:
            watermarked.convert('RGB').save(output_path)

        print(f"✅ 水印添加成功: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 水印添加失败: {str(e)}")
        return False


def add_image_watermark(
    input_path: str,
    output_path: str,
    watermark_path: str,
    position: str = "bottom_right",
    opacity: int = 60,
    margin: int = 30
) -> bool:
    """
    为图片添加图片水印

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        watermark_path: 水印图片路径
        position: 水印位置
        opacity: 透明度 (0-100)
        margin: 边距

    Returns:
        是否成功
    """
    try:
        # 打开原图
        img = Image.open(input_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 打开水印图片
        wm = Image.open(watermark_path)
        if wm.mode != 'RGBA':
            wm = wm.convert('RGBA')

        # 调整水印大小（相对于原图的10%）
        wm_width = int(img.width * 0.1)
        wm_height = int(wm_width * wm.height / wm.width)
        wm = wm.resize((wm_width, wm_height), Image.Resampling.LANCZOS)

        # 调整透明度
        alpha = wm.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity / 100))
        wm.putalpha(alpha)

        # 计算位置
        positions = {
            "top_left": (margin, margin),
            "top_right": (img.width - wm.width - margin, margin),
            "bottom_left": (margin, img.height - wm.height - margin),
            "bottom_right": (img.width - wm.width - margin, img.height - wm.height - margin),
            "center": ((img.width - wm.width) // 2, (img.height - wm.height) // 2)
        }

        pos = positions.get(position, positions["bottom_right"])

        # 创建输出图片
        output = Image.new('RGBA', img.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.paste(wm, pos, wm)

        # 保存
        if output_path.lower().endswith('.png'):
            output.save(output_path)
        else:
            output.convert('RGB').save(output_path)

        print(f"✅ 图片水印添加成功: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 图片水印添加失败: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="壁纸水印添加工具")
    parser.add_argument("--input", "-i", required=True, help="输入图片路径")
    parser.add_argument("--output", "-o", required=True, help="输出图片路径")
    parser.add_argument("--text", "-t", default="山野收容所", help="水印文字")
    parser.add_argument("--watermark-image", "-w", help="水印图片路径（优先于文字水印）")
    parser.add_argument("--position", "-p", default="bottom_right",
                       choices=["top_left", "top_right", "bottom_left", "bottom_right", "center"],
                       help="水印位置")
    parser.add_argument("--opacity", "-op", type=int, default=60, help="透明度 (0-100)")
    parser.add_argument("--font-size", "-fs", type=int, default=28, help="字体大小")
    parser.add_argument("--margin", "-m", type=int, default=30, help="边距（图片水印）")

    args = parser.parse_args()

    if args.watermark_image and os.path.exists(args.watermark_image):
        # 使用图片水印
        return add_image_watermark(
            args.input, args.output, args.watermark_image,
            args.position, args.opacity, args.margin
        )
    else:
        # 使用文字水印
        return add_text_watermark(
            args.input, args.output, args.text,
            args.position, args.opacity, args.font_size
        )


if __name__ == "__main__":
    main()
