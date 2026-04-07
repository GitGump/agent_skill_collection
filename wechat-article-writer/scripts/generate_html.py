#!/usr/bin/env python3
"""
微信公众号HTML生成器

将Markdown格式的公众号文章转换为可直接复制粘贴到公众号编辑器的HTML格式，
内联所有样式，确保排版效果不丢失。

支持图片base64嵌入，可直接在HTML中显示图片。
新增功能：自动检测并提示图片引用问题。
"""

import os
import sys
import base64
import re
import markdown
from bs4 import BeautifulSoup


def image_to_base64(image_path):
    """
    将图片转换为base64编码

    Args:
        image_path (str): 图片文件路径

    Returns:
        str: base64编码的图片数据URL
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        # 根据文件扩展名确定MIME类型
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
    将Markdown转换为微信公众号友好的HTML

    Args:
        markdown_content (str): Markdown格式的文章内容
        output_path (str): 输出HTML文件路径
        images_dir (str): 图片目录路径，用于嵌入图片

    Returns:
        str: 生成的HTML内容
    """
    # 将Markdown转换为HTML
    html = markdown.markdown(
        markdown_content,
        extensions=[
            'extra',  # 支持表格、定义列表等
            'codehilite',  # 代码高亮
            'nl2br',  # 换行转<br>
        ]
    )

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 定义公众号友好的样式
    styles = {
        'h1': {
            'font-size': '24px',
            'font-weight': 'bold',
            'color': '#000000',
            'margin-top': '30px',
            'margin-bottom': '20px',
            'text-align': 'center',
        },
        'h2': {
            'font-size': '20px',
            'font-weight': 'bold',
            'color': '#000000',
            'margin-top': '25px',
            'margin-bottom': '15px',
            'border-left': '4px solid #ff6b6b',
            'padding-left': '10px',
        },
        'h3': {
            'font-size': '18px',
            'font-weight': 'bold',
            'color': '#000000',
            'margin-top': '20px',
            'margin-bottom': '10px',
        },
        'p': {
            'font-size': '16px',
            'line-height': '1.75',
            'color': '#333333',
            'margin-bottom': '15px',
            'text-align': 'justify',
        },
        'strong': {
            'color': '#ff6b6b',
            'font-weight': 'bold',
        },
        'blockquote': {
            'background-color': '#f5f5f5',
            'padding': '15px 20px',
            'margin': '20px 0',
            'border-left': '4px solid #ff6b6b',
            'font-style': 'italic',
            'color': '#666666',
        },
        'ul': {
            'font-size': '16px',
            'line-height': '1.75',
            'margin-bottom': '15px',
            'padding-left': '30px',
        },
        'ol': {
            'font-size': '16px',
            'line-height': '1.75',
            'margin-bottom': '15px',
            'padding-left': '30px',
        },
        'li': {
            'margin-bottom': '8px',
        },
        'code': {
            'background-color': '#f5f5f5',
            'padding': '2px 6px',
            'border-radius': '3px',
            'font-family': 'Consolas, Monaco, monospace',
            'font-size': '14px',
        },
        'pre': {
            'background-color': '#f5f5f5',
            'padding': '15px',
            'border-radius': '5px',
            'overflow-x': 'auto',
            'margin': '20px 0',
        },
        'hr': {
            'border': 'none',
            'border-top': '2px dashed #e0e0e0',
            'margin': '30px 0',
        },
        'table': {
            'width': '100%',
            'border-collapse': 'collapse',
            'margin': '20px 0',
        },
        'th': {
            'background-color': '#f5f5f5',
            'padding': '12px',
            'text-align': 'left',
            'border-bottom': '2px solid #e0e0e0',
            'font-weight': 'bold',
        },
        'td': {
            'padding': '12px',
            'border-bottom': '1px solid #e0e0e0',
        },
        'img': {
            'max-width': '100%',
            'height': 'auto',
            'display': 'block',
            'margin': '20px auto',
        },
    }

    # 应用内联样式
    def apply_style(tag, tag_styles):
        """将样式字典应用到标签"""
        style_str = '; '.join([f'{k}: {v}' for k, v in tag_styles.items()])
        tag['style'] = style_str

    # 为不同标签应用样式
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag_name = tag.name
        if tag_name in styles:
            apply_style(tag, styles[tag_name])

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
        # 检查是否在pre标签内（代码块）
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

    # 处理图片嵌入（第一遍：处理外部URL）
    for img in soup.find_all('img'):
        original_src = img.get('src', '')

        # 检查是否是外部URL，如果是，保留URL并跳过后续处理
        if original_src.startswith(('http://', 'https://')):
            print(f"✓ 使用外部图片URL: {original_src}")
            # 确保使用URL
            img['src'] = original_src
            # 标记为已处理
            img['_processed'] = True
            continue
        else:
            # 标记为未处理
            img['_processed'] = False

    # 处理图片嵌入（第二遍：处理本地图片或占位符）
    if images_dir:
        # 获取images_dir下所有图片文件
        image_files = []
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_files.append(filename)

        if image_files:
            print(f"\n找到 {len(image_files)} 张图片文件：{image_files}")

        for img in soup.find_all('img'):
            # 跳过已处理的图片（外部URL）
            if img.get('_processed'):
                continue

            # 获取图片的原始路径（可能是相对路径）
            original_src = img.get('src', '')
            alt_text = img.get('alt', '')

            # 查找对应的本地图片文件
            image_path = None

            if image_files:
                # 方法1：通过alt属性匹配
                if alt_text:
                    for filename in image_files:
                        if alt_text in filename or filename.startswith(alt_text):
                            image_path = os.path.join(images_dir, filename)
                            print(f"  通过alt属性匹配: {alt_text} -> {filename}")
                            break

                # 方法2：通过src属性匹配
                if not image_path and original_src:
                    src_filename = os.path.basename(original_src)
                    for filename in image_files:
                        if src_filename in filename or filename.startswith(src_filename):
                            image_path = os.path.join(images_dir, filename)
                            print(f"  通过src属性匹配: {src_filename} -> {filename}")
                            break

                # 方法3：直接匹配封面图
                if not image_path and ('封面' in alt_text or '封面' in original_src):
                    for filename in image_files:
                        if '封面' in filename:
                            image_path = os.path.join(images_dir, filename)
                            print(f"  通过关键词匹配: 封面 -> {filename}")
                            break

                # 方法4：直接匹配配图（按顺序）
                if not image_path:
                    for filename in image_files:
                        if '配图' in filename:
                            image_path = os.path.join(images_dir, filename)
                            print(f"  通过关键词匹配: 配图 -> {filename}")
                            # 从列表中移除，避免重复
                            if filename in image_files:
                                image_files.remove(filename)
                            break

            # 如果找到图片文件，转换为base64嵌入
            if image_path:
                base64_data = image_to_base64(image_path)
                if base64_data:
                    img['src'] = base64_data
                    print(f"✓ 已嵌入图片: {os.path.basename(image_path)}")
                    continue

            # 如果没有找到图片，使用占位符
            placeholder = soup.new_tag('div')
            placeholder['style'] = (
                'background-color: #f0f0f0; '
                'padding: 30px 20px; '
                'text-align: center; '
                'border: 3px dashed #ff6b6b; '
                'margin: 20px 0; '
                'color: #666; '
                'font-size: 16px;'
            )
            display_text = alt_text if alt_text else (original_src if original_src else "图片")

            # 根据图片类型提供不同的占位符
            if '封面' in display_text:
                size_info = "建议尺寸：900×383像素（2.35:1比例）"
            else:
                size_info = "建议尺寸：900×500像素（16:9比例）"

            placeholder.string = f'📌 {display_text}\n\n{size_info}\n[请在此处上传配图，或提供图片URL]'
            img.replace_with(placeholder)
            print(f"✗ 未找到图片，使用占位符: {display_text}")
    else:
        # 没有提供images_dir，为所有未处理的图片使用占位符
        for img in soup.find_all('img'):
            # 跳过已处理的图片（外部URL）
            if img.get('_processed'):
                continue

            placeholder = soup.new_tag('div')
            placeholder['style'] = (
                'background-color: #f0f0f0; '
                'padding: 30px 20px; '
                'text-align: center; '
                'border: 3px dashed #ff6b6b; '
                'margin: 20px 0; '
                'color: #666; '
                'font-size: 16px;'
            )
            original_src = img.get('src', '')
            alt_text = img.get('alt', '')
            display_text = alt_text if alt_text else (original_src if original_src else "图片")

            # 根据图片类型提供不同的占位符
            if '封面' in display_text:
                size_info = "建议尺寸：900×383像素（2.35:1比例）"
            else:
                size_info = "建议尺寸：900×500像素（16:9比例）"

            placeholder.string = f'📌 {display_text}\n\n{size_info}\n[请在此处上传配图，或提供图片URL]'
            img.replace_with(placeholder)
            print(f"✗ 未找到图片，使用占位符: {display_text}")

    # 移除所有_processed属性
    for img in soup.find_all('img'):
        if img.has_attr('_processed'):
            del img['_processed']
    for img in soup.find_all(True):
        if img.has_attr('_processed'):
            del img['_processed']

    # 添加分隔线样式
    for hr in soup.find_all('hr'):
        hr.string = '——————————————'

    # 生成完整的HTML文档
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 677px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        .article {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="article">
        {str(soup.prettify())}
    </div>
</body>
</html>"""

    # 写入文件
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

    # 读取Markdown文件
    if not os.path.exists(markdown_path):
        print(f"错误：文件不存在 - {markdown_path}")
        sys.exit(1)

    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # 生成HTML
    generate_wechat_html(markdown_content, output_path, images_dir)

    print(f"\n✅ HTML文件已生成：{output_path}")
    print(f"\n使用步骤：")
    print(f"1. 在浏览器中打开 {output_path}")
    print(f"2. 全选内容（Ctrl+A / Cmd+A）")
    print(f"3. 复制（Ctrl+C / Cmd+C）")
    print(f"4. 粘贴到微信公众号编辑器（Ctrl+V / Cmd+V）")
    if images_dir:
        print(f"5. 图片已嵌入，无需单独上传！")
    else:
        print(f"5. 上传配图替换占位符")
    
    # 检查HTML文件大小
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    if file_size > 5:
        print(f"\n⚠️  警告：HTML文件大小为 {file_size:.2f}MB，可能影响公众号编辑器加载速度")
        print(f"建议：使用外部URL图片而非本地图片转base64")


if __name__ == '__main__':
    main()
