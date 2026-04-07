"""
自然壁纸生成脚本
生成符合苹果手机屏幕尺寸的自然治愈风格壁纸
"""
import os
import random
import argparse
from datetime import datetime

# 苹果手机壁纸尺寸标准
IPHONE_SIZES = {
    "iphone16_pro_max": {"width": 2868, "height": 1320, "name": "iPhone 16 Pro Max"},
    "iphone16_pro": {"width": 2622, "height": 1206, "name": "iPhone 16 Pro"},
    "iphone16": {"width": 2556, "height": 1179, "name": "iPhone 16"},
    "iphone16_plus": {"width": 2796, "height": 1290, "name": "iPhone 16 Plus"},
}

# 自然治愈风格元素库
NATURE_ELEMENTS = {
    "landscapes": [
        "连绵起伏的山脉", "雪峰日出", "高山草甸", "峡谷晨雾",
        "沙漠绿洲", "热带雨林", "北欧峡湾", "瑞士湖泊"
    ],
    "oceans": [
        "蓝色渐变海面", "粉色沙滩海岸", "星空倒映海面", "珊瑚礁潜水视角",
        "悬崖海浪", "海蚀洞穴", "热带海岛日落", "冰岛黑沙滩海浪"
    ],
    "forests": [
        "晨雾森林", "苔藓秘境", "秋色林间", "樱花隧道",
        "竹林深处", "红杉巨木", "极光森林", "萤火虫之夜"
    ],
    "celestial": [
        "银河星空", "流星划过", "极光爆发", "超级月亮",
        "星云特写", "日全食", "流星雨", "晨曦云海"
    ],
    "flowers": [
        "薰衣草花田", "郁金香海洋", "向日葵花海", "樱花盛开",
        "玫瑰花园", "罂粟花田", "莲花池", "蒲公英绒球"
    ],
    "sunrise_sunset": [
        "海边日落", "沙漠日落", "湖边日出", "草原晨曦",
        "富士山晨曦", "热气球日出", "灯塔日落", "威尼斯黄昏"
    ]
}

# 视觉风格关键词
STYLE_KEYWORDS = [
    "电影级构图", "8K超高清", "辛烷渲染", "戏剧性光线",
    "柔和散射光", "黄金时刻", "蓝调时刻", "景深虚化",
    "超宽画幅", "电影感色调"
]

# 色彩风格
COLOR_STYLES = [
    "低饱和度莫兰迪色系", "高饱和度鲜明对比", "暖色调金色系",
    "冷色调蓝色系", "马卡龙糖果色", "高级感灰调"
]


def generate_prompt(category: str = None, custom_theme: str = None) -> str:
    """
    生成壁纸提示词

    Args:
        category: 自然元素类别 (landscapes/oceans/forests/celestial/flowers/sunrise_sunset)
        custom_theme: 自定义主题描述

    Returns:
        完整的AI绘图提示词
    """
    # 如果指定了类别，从该类别中随机选择
    if category and category in NATURE_ELEMENTS:
        main_element = random.choice(NATURE_ELEMENTS[category])
    elif custom_theme:
        main_element = custom_theme
    else:
        # 随机选择所有类别中的元素
        all_elements = []
        for elements in NATURE_ELEMENTS.values():
            all_elements.extend(elements)
        main_element = random.choice(all_elements)

    # 随机组合风格
    style = random.choice(STYLE_KEYWORDS)
    color = random.choice(COLOR_STYLES)

    # 构建完整提示词
    prompt = f"""
{major_element}为主题的自然治愈风格壁纸设计。

画面要求：
- 主视觉：{main_element}
- 构图：中央重点构图，留白充足，简约大气
- 光影：自然光线，{style}
- 色彩：{color}，对比度适中，视觉舒适
- 氛围：宁静治愈，给人以心灵慰藉

技术规格：
- 画面纯净无杂物，无人物元素
- 无文字、水印、签名
- 画面整洁，边缘处理自然

请生成一张充满诗意和治愈感的自然风景壁纸。
"""

    return prompt


def get_iphone_size(size_name: str = None) -> dict:
    """
    获取iPhone壁纸尺寸

    Args:
        size_name: 尺寸名称，如 "iphone16_pro" 或 "auto"

    Returns:
        包含width, height, name的字典
    """
    if size_name == "auto":
        # 随机选择
        return random.choice(list(IPHONE_SIZES.values()))
    elif size_name in IPHONE_SIZES:
        return IPHONE_SIZES[size_name]
    else:
        # 默认使用iPhone 16 Pro Max
        return IPHONE_SIZES["iphone16_pro_max"]


def generate_output_filename(size_info: dict) -> str:
    """生成带时间戳的输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"wallpaper_{size_info['name'].replace(' ', '_')}_{timestamp}.png"


def main():
    parser = argparse.ArgumentParser(description="自然治愈风格壁纸生成器")
    parser.add_argument("--category", "-c", choices=list(NATURE_ELEMENTS.keys()),
                        help="自然元素类别")
    parser.add_argument("--theme", "-t", type=str,
                        help="自定义主题描述")
    parser.add_argument("--size", "-s", default="auto",
                        choices=list(IPHONE_SIZES.keys()) + ["auto"],
                        help="iPhone尺寸")
    parser.add_argument("--output", "-o", type=str,
                        help="输出文件路径")

    args = parser.parse_args()

    # 生成提示词
    prompt = generate_prompt(args.category, args.theme)
    size_info = get_iphone_size(args.size)

    # 输出结果
    print("=" * 60)
    print("🌿 自然治愈壁纸生成器")
    print("=" * 60)
    print(f"\n📐 目标尺寸: {size_info['name']}")
    print(f"   分辨率: {size_info['width']} x {size_info['height']}")
    print(f"\n🎨 生成提示词:\n{prompt}")

    if args.output:
        output_file = args.output
    else:
        output_file = generate_output_filename(size_info)

    print(f"\n📁 输出文件: {output_file}")
    print("=" * 60)

    # 返回生成参数，供后续流程使用
    return {
        "prompt": prompt,
        "size": size_info,
        "output": output_file
    }


if __name__ == "__main__":
    main()
