#!/usr/bin/env python3
"""
真实故事计划 —— 微信公众号HTML生成器

将Markdown格式的非虚构公众号文章转换为可直接复制粘贴到公众号编辑器的HTML格式。
内联所有样式，确保排版效果不丢失。

风格：纪实人文，克制沉稳，大行间距，留白充足，无鲜艳配色。
"""

import os
import sys
import base64
import re
import markdown
from bs4 import BeautifulSoup


def image_to_base64(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif'
        }.get(ext, 'image/png')
        return f'data:{mime_type};base64,{base64_data}'
    except Exception as e:
        print(f"警告：无法读取图片 {image_path}: {e}")
        return None


def generate_wechat_html(markdown_content, output_path="article.html", images_dir=None):
    """
    将Markdown转换为真实故事计划风格的微信公众号HTML

    Args:
        markdown_content (str): Markdown格式的文章内容
        output_path (str): 输出HTML文件路径
        images_dir (str): 图片目录路径，用于嵌入图片

    Returns:
        str: 生成的HTML内容
    """
    html = markdown.markdown(
        markdown_content,
        extensions=[
            'extra',
            'nl2br',
        ]
    )

    soup = BeautifulSoup(html, 'html.parser')

    # 真实故事计划专属样式 —— 纪实人文风格
    # 主色调：深灰/黑色，无鲜艳强调色，大行间距，留白充足
    styles = {
        'h1': {
            'font-size': '22px',
            'font-weight': 'bold',
            'color': '#1a1a1a',
            'margin-top': '32px',
            'margin-bottom': '20px',
            'text-align': 'left',
            'letter-spacing': '1px',
            'line-height': '1.6',
        },
        'h2': {
            'font-size': '18px',
            'font-weight': 'bold',
            'color': '#1a1a1a',
            'margin-top': '32px',
            'margin-bottom': '16px',
            'line-height': '1.6',
        },
        'h3': {
            'font-size': '16px',
            'font-weight': 'bold',
            'color': '#333333',
            'margin-top': '24px',
            'margin-bottom': '12px',
            'line-height': '1.6',
        },
        'p': {
            'font-size': '17px',
            'line-height': '2.0',
            'color': '#2d2d2d',
            'margin-bottom': '20px',
            'text-align': 'justify',
            'letter-spacing': '0.3px',
        },
        'strong': {
            'color': '#1a1a1a',
            'font-weight': 'bold',
        },
        'blockquote': {
            'background-color': '#f8f7f5',
            'padding': '18px 24px',
            'margin': '24px 0',
            'border-left': '3px solid #999999',
            'font-style': 'normal',
            'color': '#555555',
            'font-size': '16px',
            'line-height': '1.9',
        },
        'ul': {
            'font-size': '17px',
            'line-height': '2.0',
            'margin-bottom': '20px',
            'padding-left': '28px',
            'color': '#2d2d2d',
        },
        'ol': {
            'font-size': '17px',
            'line-height': '2.0',
            'margin-bottom': '20px',
            'padding-left': '28px',
            'color': '#2d2d2d',
        },
        'li': {
            'margin-bottom': '10px',
        },
        'code': {
            'background-color': '#f5f5f4',
            'padding': '2px 6px',
            'border-radius': '3px',
            'font-family': 'Consolas, Monaco, monospace',
            'font-size': '14px',
            'color': '#444444',
        },
        'pre': {
            'background-color': '#f5f5f4',
            'padding': '16px',
            'border-radius': '4px',
            'overflow-x': 'auto',
            'margin': '20px 0',
        },
        'hr': {
            'border': 'none',
            'border-top': '1px solid #e8e6e3',
            'margin': '36px 0',
        },
        'table': {
            'width': '100%',
            'border-collapse': 'collapse',
            'margin': '20px 0',
        },
        'th': {
            'background-color': '#f5f5f4',
            'padding': '10px 14px',
            'text-align': 'left',
            'border-bottom': '2px solid #dddddd',
            'font-weight': 'bold',
            'font-size': '15px',
            'color': '#333333',
        },
        'td': {
            'padding': '10px 14px',
            'border-bottom': '1px solid #ebebeb',
            'font-size': '15px',
            'color': '#2d2d2d',
        },
        'img': {
            'max-width': '100%',
            'height': 'auto',
            'display': 'block',
            'margin': '28px auto',
            'border-radius': '2px',
        },
    }

    def apply_style(tag, tag_styles):
        style_str = '; '.join([f'{k}: {v}' for k, v in tag_styles.items()])
        tag['style'] = style_str

    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if tag.name in styles:
            apply_style(tag, styles[tag.name])

    for tag in soup.find_all('p'):
        apply_style(tag, styles['p'])

    for tag in soup.find_all('strong'):
        apply_style(tag, styles['strong'])

    for tag in soup.find_all('blockquote'):
        apply_style(tag, styles['blockquote'])

    for tag in soup.find_all(['ul', 'ol']):
        apply_style(tag, styles['ul'] if tag.name == 'ul' else styles['ol'])

    for tag in soup.find_all('li'):
        apply_style(tag, styles['li'])

    for tag in soup.find_all('code'):
        if tag.parent.name != 'pre':
            apply_style(tag, styles['code'])

    for tag in soup.find_all('pre'):
        apply_style(tag, styles['pre'])

    for tag in soup.find_all('hr'):
        apply_style(tag, styles['hr'])

    for table in soup.find_all('table'):
        apply_style(table, styles['table'])
        for th in table.find_all('th'):
            apply_style(th, styles['th'])
        for td in table.find_all('td'):
            apply_style(td, styles['td'])

    for img in soup.find_all('img'):
        apply_style(img, styles['img'])

    # 处理图片（第一遍：外部URL）
    for img in soup.find_all('img'):
        original_src = img.get('src', '')
        if original_src.startswith(('http://', 'https://')):
            print(f"✓ 使用外部图片URL: {original_src}")
            img['src'] = original_src
            img['_processed'] = True
        else:
            img['_processed'] = False

    # 处理图片（第二遍：本地图片或占位符）
    if images_dir:
        image_files = []
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_files.append(filename)

        if image_files:
            print(f"\n找到 {len(image_files)} 张图片文件：{image_files}")

        for img in soup.find_all('img'):
            if img.get('_processed'):
                continue

            original_src = img.get('src', '')
            alt_text = img.get('alt', '')
            image_path = None

            if image_files:
                if alt_text:
                    for filename in image_files:
                        if alt_text in filename or filename.startswith(alt_text):
                            image_path = os.path.join(images_dir, filename)
                            break

                if not image_path and original_src:
                    src_filename = os.path.basename(original_src)
                    for filename in image_files:
                        if src_filename in filename or filename.startswith(src_filename):
                            image_path = os.path.join(images_dir, filename)
                            break

                if not image_path and ('封面' in alt_text or '封面' in original_src):
                    for filename in image_files:
                        if '封面' in filename:
                            image_path = os.path.join(images_dir, filename)
                            break

                if not image_path:
                    for filename in image_files:
                        if '配图' in filename:
                            image_path = os.path.join(images_dir, filename)
                            if filename in image_files:
                                image_files.remove(filename)
                            break

            if image_path:
                base64_data = image_to_base64(image_path)
                if base64_data:
                    img['src'] = base64_data
                    print(f"✓ 已嵌入图片: {os.path.basename(image_path)}")
                    continue

            # 未找到图片，使用克制风格的占位符
            placeholder = soup.new_tag('div')
            placeholder['style'] = (
                'background-color: #f8f7f5; '
                'padding: 28px 20px; '
                'text-align: center; '
                'border: 1px dashed #cccccc; '
                'margin: 28px 0; '
                'color: #888888; '
                'font-size: 14px;'
            )
            display_text = alt_text if alt_text else (original_src if original_src else "图片")
            if '封面' in display_text:
                size_info = "建议尺寸：900×383像素（2.35:1比例）"
            else:
                size_info = "建议尺寸：900×500像素（16:9比例）"
            placeholder.string = f'[ {display_text} | {size_info} ]'
            img.replace_with(placeholder)
            print(f"✗ 未找到图片，使用占位符: {display_text}")
    else:
        for img in soup.find_all('img'):
            if img.get('_processed'):
                continue
            placeholder = soup.new_tag('div')
            placeholder['style'] = (
                'background-color: #f8f7f5; '
                'padding: 28px 20px; '
                'text-align: center; '
                'border: 1px dashed #cccccc; '
                'margin: 28px 0; '
                'color: #888888; '
                'font-size: 14px;'
            )
            original_src = img.get('src', '')
            alt_text = img.get('alt', '')
            display_text = alt_text if alt_text else (original_src if original_src else "图片")
            if '封面' in display_text:
                size_info = "建议尺寸：900×383像素（2.35:1比例）"
            else:
                size_info = "建议尺寸：900×500像素（16:9比例）"
            placeholder.string = f'[ {display_text} | {size_info} ]'
            img.replace_with(placeholder)
            print(f"[!] 未找到图片，使用占位符: {display_text}")

    # 清理 _processed 属性
    for tag in soup.find_all(True):
        if tag.has_attr('_processed'):
            del tag['_processed']

    # 生成完整HTML文档 —— 真实故事计划阅读风格
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>真实故事计划</title>
    <style>
        body {{
            font-family: "Georgia", "Noto Serif SC", "宋体", serif;
            max-width: 677px;
            margin: 0 auto;
            padding: 24px 20px 48px;
            background-color: #ffffff;
            color: #2d2d2d;
        }}
        .article {{
            margin-top: 16px;
        }}
        /* 段落首行不缩进（公众号风格） */
        p {{
            text-indent: 0;
        }}
    </style>
</head>
<body>
    <div class="article">
        {str(soup.prettify())}
    </div>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    return full_html


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python generate_html.py <markdown文件路径> [输出HTML路径] [图片目录路径]")
        print("\n示例：")
        print("  python generate_html.py article.md")
        print("  python generate_html.py article.md output.html")
        print("  python generate_html.py article.md output.html ./images")
        sys.exit(1)

    markdown_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else markdown_path.replace('.md', '.html')
    images_dir = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(markdown_path):
        print(f"错误：文件不存在 - {markdown_path}")
        sys.exit(1)

    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    generate_wechat_html(markdown_content, output_path, images_dir)

    print(f"\n[OK] HTML文件已生成：{output_path}")
    print(f"\n发布步骤：")
    print(f"1. 在浏览器中打开 {output_path}")
    print(f"2. 全选内容（Ctrl+A）")
    print(f"3. 复制（Ctrl+C）")
    print(f"4. 粘贴到微信公众号编辑器（Ctrl+V）")
    if images_dir:
        print(f"5. 图片已嵌入，无需单独上传")
    else:
        print(f"5. 替换图片占位符或上传配图")

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    if file_size > 5:
        print(f"\n⚠️  HTML文件 {file_size:.2f}MB，建议使用外部图片URL而非本地base64")


if __name__ == '__main__':
    main()
