#!/usr/bin/env python3
"""
Markdown to HTML Converter for 我就爱看

Usage:
    python generate_html.py input.md output.html
    python generate_html.py input.md output.html ./images
"""

import sys
import re
import os
from pathlib import Path


def read_markdown(md_path):
    """Read markdown file content."""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()


def markdown_to_html(md_content, images_dir=None):
    """Convert markdown to HTML with custom styling."""

    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
            font-size: 17px;
            line-height: 1.9;
            color: #333;
            background-color: #fafafa;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 720px;
            margin: 0 auto;
            background: #fff;
            padding: 48px;
            border-radius: 4px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }}

        h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
            line-height: 1.4;
        }}

        h2 {{
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 40px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #f0f0f0;
        }}

        p {{
            margin-bottom: 20px;
            text-align: justify;
        }}

        blockquote {{
            margin: 28px 0;
            padding: 20px 24px;
            border-left: 4px solid #333;
            background: #f9f9f9;
            color: #555;
            font-style: normal;
            border-radius: 0 4px 4px 0;
        }}

        blockquote p {{
            margin-bottom: 8px;
        }}

        blockquote p:last-child {{
            margin-bottom: 0;
        }}

        strong {{
            font-weight: 600;
            color: #1a1a1a;
        }}

        em {{
            font-style: italic;
            color: #555;
        }}

        ul, ol {{
            margin: 16px 0;
            padding-left: 24px;
        }}

        li {{
            margin-bottom: 8px;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 24px auto;
            border-radius: 4px;
        }}

        .cover-image {{
            margin-bottom: 32px;
        }}

        hr {{
            border: none;
            height: 1px;
            background: #e0e0e0;
            margin: 32px 0;
        }}

        .footer {{
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #eee;
            font-size: 14px;
            color: #888;
            text-align: center;
        }}

        a {{
            color: #333;
            text-decoration: none;
            border-bottom: 1px solid #ddd;
        }}

        a:hover {{
            color: #000;
            border-bottom-color: #333;
        }}

        @media (max-width: 600px) {{
            .container {{
                padding: 24px;
            }}

            h1 {{
                font-size: 24px;
            }}

            body {{
                padding: 20px 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>'''

    # Extract title from first h1
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else '电影深度解析'

    # Process markdown content
    html = md_content

    # Remove title markdown (will be rendered as h1)
    html = re.sub(r'^#\s+.+$', '', html, count=1, flags=re.MULTILINE)

    # Handle headings
    html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Handle bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Handle blockquotes (for quotes and citations)
    html = re.sub(r'^>\s*(.+)$', r'<blockquote><p>\1</p></blockquote>', html, flags=re.MULTILINE)

    # Merge consecutive blockquotes
    html = re.sub(r'</blockquote>\n<blockquote>', '', html)

    # Handle horizontal rules (remove them)
    html = re.sub(r'^---+$', '', html, flags=re.MULTILINE)
    html = re.sub(r'^§+$', '', html, flags=re.MULTILINE)

    # Handle unordered lists
    lines = html.split('\n')
    in_list = False
    processed_lines = []

    for line in lines:
        if re.match(r'^[*-]\s+', line):
            if not in_list:
                processed_lines.append('<ul>')
                in_list = True
            processed_lines.append('<li>' + re.sub(r'^[*-]\s+', '', line) + '</li>')
        else:
            if in_list:
                processed_lines.append('</ul>')
                in_list = False
            processed_lines.append(line)

    if in_list:
        processed_lines.append('</ul>')

    html = '\n'.join(processed_lines)

    # Handle images
    def replace_image(match):
        alt_text = match.group(1)
        src = match.group(2)
        # If src is not absolute URL, prepend images directory
        if images_dir and not src.startswith(('http://', 'https://')):
            src = os.path.join(images_dir, os.path.basename(src))
        return f'<img src="{src}" alt="{alt_text}">'

    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

    # Handle paragraphs (split by double newlines)
    paragraphs = re.split(r'\n\n+', html)
    processed_paragraphs = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Don't wrap if it's already a block element
        if re.match(r'^(<h[1-6]|<ul|<ol|<blockquote|<img|<div)', p):
            processed_paragraphs.append(p)
        else:
            # Wrap in paragraph tags, but handle line breaks within
            p = p.replace('\n', '<br>')
            processed_paragraphs.append(f'<p>{p}</p>')

    content = '\n'.join(processed_paragraphs)

    return html_template.format(title=title, content=content)


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_html.py input.md output.html [images_dir]")
        sys.exit(1)

    md_path = sys.argv[1]
    html_path = sys.argv[2]
    images_dir = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(md_path):
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    md_content = read_markdown(md_path)
    html_content = markdown_to_html(md_content, images_dir)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML generated: {html_path}")


if __name__ == '__main__':
    main()
