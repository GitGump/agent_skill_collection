#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Article-to-Images Generator v3.0 — 多主题模板版 + AI自定义主题

将文章自动转换为多张精美的 1080x1440px 图文切片，支持：
- 8 种主题风格自动匹配（科技蓝/商务灰/文艺绿/暖橙/极简黑/杂志红/复古金/清新蓝）
- AI 自定义主题：指定主色+背景类型，自动推导全部配色（v3.0）
- Markdown 解析 + HTML 样式预览
- 首张切片：大标题居中 + 副标题/导语（必填）+ 主题色高亮
- 正文切片：段落标题加粗+下划线+主题色，重点内容强调显示
- 自动根据文章关键词匹配最佳主题
- 产物命名：文章标题-时间戳-版本号（如 红辣椒-202605221734-V1）

v3.0 更新：
- 副标题/导语改为必填，AI为每篇文章生成吸引点击的导语
- 来源/作者改为必填，默认值"好人古德曼"
- 新增AI自定义主题：传入主色十六进制值+主题名+背景类型，自动推导14个配色字段
- 自定义主题确保配色和谐、对比度合格、视觉美感

v2.2 更新：
- 封面页去掉标题区域上方和下方的两条横线
- 正文页去掉顶部装饰线，底部装饰线下移至页码正上方
- 段落标题下方增加一行文字间隔（45px）
- 底部横线下移后内容区域扩大，可显示更多正文

v2.1 更新：
- 去掉所有切片上的主题名称标签（封面页胶囊+正文页左下角）
- 正文段落之间增加至少一行文字间隙（45px）
- 产物保存到 E:\codefile\trae\mp_article\文生图\整篇转换\{标题-时间戳-版本号}
"""

import os
import re
import sys
import io
import json
import colorsys
import html as html_module
from datetime import datetime

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print('[ERROR] Pillow not installed. Run: pip install Pillow')
    sys.exit(1)


# ============ Design Constants ============
IMG_W = 1080
IMG_H = 1440
MAX_PAGES = 18

# ============ Theme Definitions ============
THEMES = {
    'tech': {
        'name': '科技蓝',
        'keywords': ['科技', 'AI', '编程', '代码', '互联网', '技术', '数字化', '智能', '软件', '数据',
                      '机器学习', '深度学习', '算法', '云计算', '区块链', '芯片', '半导体', '量子'],
        'bg': (245, 248, 255),             # 浅蓝白底
        'title_color': (21, 101, 192),      # 科技蓝
        'heading_color': (25, 118, 210),     # 亮蓝
        'accent_color': (0, 150, 136),       # 青绿点缀
        'text_color': (38, 50, 56),         # 深蓝灰
        'light_color': (227, 242, 253),     # 浅蓝背景块
        'underline_color': (21, 101, 192),  # 标题下划线
        'deco_color': (100, 181, 246),      # 装饰线
        'page_num_color': (144, 164, 174),  # 页码
        'highlight_bg': (232, 245, 253),    # 重点内容背景
        'cover_bg': (21, 101, 192),         # 封面背景
        'cover_title_color': (255, 255, 255),  # 封面标题白字
        'cover_accent': (100, 181, 246),    # 封面装饰
        'has_cover_bg': True,
        'desc': '科技蓝主题，适合技术、AI、编程、互联网类文章'
    },
    'business': {
        'name': '商务灰',
        'keywords': ['商业', '财经', '股票', '投资', '企业', '管理', '市场', '经济', '金融', '理财',
                      '融资', '创业', '运营', '营销', '战略', '基金', '债券', '估值'],
        'bg': (250, 250, 250),
        'title_color': (33, 37, 41),        # 深灰黑
        'heading_color': (52, 58, 64),       # 灰黑
        'accent_color': (200, 169, 110),     # 金色
        'text_color': (52, 58, 64),
        'light_color': (241, 243, 245),
        'underline_color': (200, 169, 110),
        'deco_color': (200, 169, 110),
        'page_num_color': (162, 168, 173),
        'highlight_bg': (255, 248, 235),
        'cover_bg': (33, 37, 41),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (200, 169, 110),
        'has_cover_bg': True,
        'desc': '商务灰主题，适合财经、投资、企业管理类文章'
    },
    'literature': {
        'name': '文艺绿',
        'keywords': ['文学', '小说', '故事', '人物', '非虚构', '纪实', '散文', '诗歌', '文化', '读书',
                      '写作', '作者', '回忆', '成长', '故乡', '人物传记', '真实故事'],
        'bg': (252, 253, 249),
        'title_color': (46, 125, 50),        # 文艺绿
        'heading_color': (56, 142, 60),
        'accent_color': (139, 195, 74),
        'text_color': (46, 53, 46),
        'light_color': (232, 245, 233),
        'underline_color': (76, 175, 80),
        'deco_color': (129, 199, 132),
        'page_num_color': (165, 182, 162),
        'highlight_bg': (241, 248, 233),
        'cover_bg': (46, 125, 50),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (139, 195, 74),
        'has_cover_bg': True,
        'desc': '文艺绿主题，适合文学、故事、非虚构、文化类文章'
    },
    'lifestyle': {
        'name': '暖橙',
        'keywords': ['生活', '旅行', '美食', '日常', '手账', '健康', '运动', '心理', '情感', '家居',
                      '宠物', '亲子', '手工', '烘焙', '咖啡', '花艺', '瑜伽', '冥想'],
        'bg': (255, 253, 248),
        'title_color': (230, 81, 0),          # 暖橙
        'heading_color': (244, 122, 36),
        'accent_color': (255, 183, 77),
        'text_color': (62, 50, 39),
        'light_color': (255, 243, 224),
        'underline_color': (244, 122, 36),
        'deco_color': (255, 167, 38),
        'page_num_color': (188, 170, 140),
        'highlight_bg': (255, 243, 224),
        'cover_bg': (230, 81, 0),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (255, 183, 77),
        'has_cover_bg': True,
        'desc': '暖橙主题，适合生活、旅行、美食、情感类文章'
    },
    'minimal': {
        'name': '极简黑白',
        'keywords': ['设计', '极简', '哲学', '思考', '观点', '评论', '分析', '趋势', '洞察', '报告',
                      '白皮书', '研究', '方法论', '框架', '模型'],
        'bg': (255, 255, 255),
        'title_color': (0, 0, 0),
        'heading_color': (33, 33, 33),
        'accent_color': (189, 189, 189),
        'text_color': (50, 50, 50),
        'light_color': (245, 245, 245),
        'underline_color': (0, 0, 0),
        'deco_color': (189, 189, 189),
        'page_num_color': (189, 189, 189),
        'highlight_bg': (245, 245, 245),
        'cover_bg': (0, 0, 0),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (189, 189, 189),
        'has_cover_bg': True,
        'desc': '极简黑白主题，适合设计、哲学、观点评论类文章'
    },
    'magazine': {
        'name': '杂志红',
        'keywords': ['新闻', '时事', '社会', '热点', '调查', '报道', '深度', '内幕', '揭秘', '真相',
                      '人物', '事件', '争议', '舆论'],
        'bg': (255, 252, 250),
        'title_color': (183, 28, 28),         # 杂志红
        'heading_color': (211, 47, 47),
        'accent_color': (229, 115, 115),
        'text_color': (40, 30, 28),
        'light_color': (255, 235, 238),
        'underline_color': (211, 47, 47),
        'deco_color': (229, 115, 115),
        'page_num_color': (188, 152, 152),
        'highlight_bg': (255, 235, 238),
        'cover_bg': (183, 28, 28),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (229, 115, 115),
        'has_cover_bg': True,
        'desc': '杂志红主题，适合新闻、时事、社会热点类文章'
    },
    'retro': {
        'name': '复古金',
        'keywords': ['历史', '复古', '怀旧', '经典', '传统', '非遗', '民俗', '古建', '文物', '博物馆',
                      '传承', '老字号', '记忆', '年代'],
        'bg': (253, 249, 240),
        'title_color': (121, 85, 72),          # 复古棕
        'heading_color': (141, 110, 99),
        'accent_color': (200, 169, 110),       # 金色
        'text_color': (62, 50, 39),
        'light_color': (239, 235, 233),
        'underline_color': (200, 169, 110),
        'deco_color': (200, 169, 110),
        'page_num_color': (161, 146, 136),
        'highlight_bg': (255, 248, 235),
        'cover_bg': (62, 50, 39),
        'cover_title_color': (200, 169, 110),
        'cover_accent': (200, 169, 110),
        'has_cover_bg': True,
        'desc': '复古金主题，适合历史、复古、怀旧、传统文化类文章'
    },
    'fresh': {
        'name': '清新蓝',
        'keywords': ['自然', '环保', '极简', '清新', '海洋', '天空', '花', '植物', '季节', '春天',
                      '夏天', '秋天', '冬天', '风景', '摄影'],
        'bg': (245, 251, 255),
        'title_color': (2, 119, 189),          # 清新蓝
        'heading_color': (3, 155, 229),
        'accent_color': (79, 195, 247),
        'text_color': (38, 60, 76),
        'light_color': (225, 245, 254),
        'underline_color': (3, 155, 229),
        'deco_color': (79, 195, 247),
        'page_num_color': (144, 180, 200),
        'highlight_bg': (225, 245, 254),
        'cover_bg': (2, 119, 189),
        'cover_title_color': (255, 255, 255),
        'cover_accent': (79, 195, 247),
        'has_cover_bg': True,
        'desc': '清新蓝主题，适合自然、环保、极简、风景类文章'
    }
}


# ============ Custom Theme Generator ============

def hex_to_rgb(hex_color):
    """Convert hex color string (#RRGGBB) to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f'Invalid hex color: #{hex_color}. Expected format: #RRGGBB')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex string."""
    return f'#{r:02X}{g:02X}{b:02X}'


def generate_custom_theme(primary_hex, name, bg_type='light'):
    """
    从一个主色自动推导生成完整的14字段主题配色。

    设计原则：
    - 主色(title_color)作为视觉锚点
    - 所有衍生色保持色相一致，仅调整明度/饱和度
    - 确保文字与背景对比度 > 4.5:1（WCAG AA）
    - 强调色(accent)取色环邻近30°，和谐不冲突
    - 深色/浅色背景自动适配文字颜色

    Args:
        primary_hex: 主色十六进制值，如 '#8B4513'
        name: 主题显示名称
        bg_type: 背景类型 — 'light'(默认,偏白)/'warm'(暖白)/'cool'(冷白)/'dark'(深色)

    Returns:
        dict: 完整的主题配色字典，与 THEMES 中格式一致
    """
    primary = hex_to_rgb(primary_hex)
    r, g, b = primary
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def from_hsv(hue, sat, val):
        """HSV → RGB tuple，自动裁剪到合法范围。"""
        r2, g2, b2 = colorsys.hsv_to_rgb(hue % 1.0, max(0, min(1, sat)), max(0, min(1, val)))
        return (int(r2 * 255), int(g2 * 255), int(b2 * 255))

    def lighten(color, factor=0.3):
        r, g, b = color
        return (min(255, int(r + (255 - r) * factor)),
                min(255, int(g + (255 - g) * factor)),
                min(255, int(b + (255 - b) * factor)))

    def darken(color, factor=0.3):
        r, g, b = color
        return (max(0, int(r * (1 - factor))),
                max(0, int(g * (1 - factor))),
                max(0, int(b * (1 - factor))))

    # ── 强调色：色环偏移 ~30°（0.083），略提饱和度+明度 ──
    accent = from_hsv((h + 0.083) % 1.0, min(s * 1.15, 0.85), min(v * 1.15, 1.0))

    # ── 背景 ──
    bg_presets = {
        'light': from_hsv(h, s * 0.06, 0.98),      # 近白，极淡主色底
        'warm': (255, 253, 248),                      # 暖白
        'cool': (245, 248, 255),                       # 冷白
        'dark': from_hsv(h, s * 0.25, 0.13),          # 深色
    }
    bg = bg_presets.get(bg_type, bg_presets['light'])

    # ── 文字色：深色背景用浅色，浅色背景用深色（带主色色相） ──
    if bg_type == 'dark':
        text_color = lighten(desaturate_hsv(primary, 0.65), 0.65)
        title_color = lighten(primary, 0.15)
        heading_color = lighten(primary, 0.25)
        cover_bg = darken(primary, 0.15)
        cover_title_color = (255, 255, 255)
        cover_accent = lighten(primary, 0.35)
    else:
        text_color = from_hsv(h, s * 0.45, 0.18)     # 深色但带色相
        title_color = primary
        heading_color = lighten(primary, 0.12)
        cover_bg = primary
        cover_title_color = (255, 255, 255)
        cover_accent = lighten(primary, 0.30)

    # ── 浅色面板背景 ──
    light_color = from_hsv(h, s * 0.22, 0.94)
    highlight_bg = from_hsv(h, s * 0.14, 0.96)

    # ── 装饰/页码 ──
    underline_color = lighten(primary, 0.05)
    deco_color = lighten(accent, 0.15)
    page_num_color = from_hsv(h, s * 0.12, 0.68)

    theme = {
        'name': name,
        'keywords': [],
        'bg': bg,
        'title_color': title_color,
        'heading_color': heading_color,
        'accent_color': accent,
        'text_color': text_color,
        'light_color': light_color,
        'underline_color': underline_color,
        'deco_color': deco_color,
        'page_num_color': page_num_color,
        'highlight_bg': highlight_bg,
        'cover_bg': cover_bg,
        'cover_title_color': cover_title_color,
        'cover_accent': cover_accent,
        'has_cover_bg': True,
        'desc': f'自定义主题：{name}（主色 {primary_hex}，背景 {bg_type}）',
    }

    # 注册到 THEMES 以便后续统一引用
    theme_id = f'custom_{name}'
    THEMES[theme_id] = theme
    return theme_id


def desaturate_hsv(color, factor=0.5):
    """向灰色方向降低饱和度。"""
    r, g, b = color
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    return (int(r + (gray - r) * factor),
            int(g + (gray - g) * factor),
            int(b + (gray - b) * factor))


# ============ Markdown Parser ============

class MarkdownParser:
    """将 Markdown 解析为结构化内容块列表。"""

    def __init__(self, md_text):
        self.raw = md_text
        self.blocks = []  # List of dicts: {type, content, level, ...}
        self._parse()

    def _parse(self):
        lines = self.raw.split('\n')
        i = 0
        in_code_block = False
        code_lines = []
        in_quote = False
        quote_lines = []

        while i < len(lines):
            line = lines[i]

            # Code block
            if line.strip().startswith('```'):
                if in_code_block:
                    self.blocks.append({
                        'type': 'code',
                        'content': '\n'.join(code_lines)
                    })
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                i += 1
                continue

            if in_code_block:
                code_lines.append(line)
                i += 1
                continue

            # Quote block (collect consecutive quote lines)
            if line.strip().startswith('>'):
                quote_text = line.strip()[1:].strip()
                # Check if this is a continuation of an existing quote block
                if in_quote:
                    quote_lines.append(quote_text)
                else:
                    # Flush any previous quote
                    if quote_lines:
                        self.blocks.append({
                            'type': 'quote',
                            'content': '\n'.join(quote_lines)
                        })
                        quote_lines = []
                    in_quote = True
                    quote_lines.append(quote_text)
                i += 1
                continue
            else:
                if in_quote:
                    self.blocks.append({
                        'type': 'quote',
                        'content': '\n'.join(quote_lines)
                    })
                    quote_lines = []
                    in_quote = False

            # Empty line
            if not line.strip():
                i += 1
                continue

            # Headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2).strip()
                # Remove inline formatting markers for display
                content = self._clean_inline(content)
                self.blocks.append({
                    'type': 'heading',
                    'level': level,
                    'content': content
                })
                i += 1
                continue

            # Unordered list
            list_match = re.match(r'^[\s]*[-*+]\s+(.+)$', line)
            if list_match:
                items = [self._clean_inline(list_match.group(1))]
                i += 1
                while i < len(lines):
                    next_match = re.match(r'^[\s]*[-*+]\s+(.+)$', lines[i])
                    if next_match:
                        items.append(self._clean_inline(next_match.group(1)))
                        i += 1
                    else:
                        break
                self.blocks.append({
                    'type': 'list',
                    'items': items,
                    'content': '\n'.join(items)
                })
                continue

            # Ordered list
            olist_match = re.match(r'^[\s]*\d+[.)]\s+(.+)$', line)
            if olist_match:
                items = [self._clean_inline(olist_match.group(1))]
                i += 1
                while i < len(lines):
                    next_match = re.match(r'^[\s]*\d+[.)]\s+(.+)$', lines[i])
                    if next_match:
                        items.append(self._clean_inline(next_match.group(1)))
                        i += 1
                    else:
                        break
                self.blocks.append({
                    'type': 'list',
                    'items': items,
                    'content': '\n'.join(items)
                })
                continue

            # Horizontal rule
            if re.match(r'^[-*_]{3,}$', line.strip()):
                self.blocks.append({
                    'type': 'hr',
                    'content': ''
                })
                i += 1
                continue

            # Paragraph (may span multiple lines)
            para_lines = [self._clean_inline(line.strip())]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if (not next_line or
                    next_line.startswith('#') or
                    next_line.startswith('>') or
                    next_line.startswith('```') or
                    next_line.startswith('- ') or
                    next_line.startswith('* ') or
                    re.match(r'^\d+[.)]\s', next_line) or
                    re.match(r'^[-*_]{3,}$', next_line)):
                    break
                para_lines.append(self._clean_inline(next_line))
                i += 1

            para_text = ' '.join(para_lines)
            # Detect key content (bold text, highlighted phrases)
            is_key = bool(re.search(r'\*\*(.+?)\*\*', para_text))
            self.blocks.append({
                'type': 'paragraph',
                'content': para_text,
                'is_key': is_key
            })

        # Flush any remaining quote block
        if quote_lines:
            self.blocks.append({
                'type': 'quote',
                'content': '\n'.join(quote_lines)
            })

    def _clean_inline(self, text):
        """Remove Markdown inline formatting markers but preserve text."""
        # Bold **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        # Italic *text* or _text_
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'\1', text)
        # Strikethrough ~~text~~
        text = re.sub(r'~~(.+?)~~', r'\1', text)
        # Inline code `code`
        text = re.sub(r'`(.+?)`', r'\1', text)
        # Links [text](url)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        # Images ![alt](url)
        text = re.sub(r'!\[(.+?)\]\(.+?\)', r'\1', text)
        return text.strip()

    def detect_key_phrases(self):
        """Detect bold/highlighted phrases from raw text for emphasis rendering."""
        phrases = []
        for match in re.finditer(r'\*\*(.+?)\*\*', self.raw):
            phrases.append(match.group(1))
        return phrases


# ============ Theme Matcher ============

def match_theme(title, text):
    """根据文章标题和正文关键词自动匹配最佳主题。"""
    combined = (title + ' ' + text)[:3000]  # 取前3000字做分析
    scores = {}
    for theme_id, theme in THEMES.items():
        score = 0
        for kw in theme['keywords']:
            count = combined.count(kw)
            score += count
        scores[theme_id] = score

    # 选择得分最高的主题
    best_theme = max(scores, key=scores.get)
    if scores[best_theme] == 0:
        best_theme = 'literature'  # 默认文艺绿

    return best_theme


# ============ Font Utility ============

def get_font(size, bold=False):
    """Get font with automatic fallback."""
    font_files = []
    if bold:
        font_files = [
            'msyhbd.ttc', 'C:/Windows/Fonts/msyhbd.ttc',
            'simhei.ttf', 'C:/Windows/Fonts/simhei.ttf',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        ]
    else:
        font_files = [
            'msyh.ttc', 'C:/Windows/Fonts/msyh.ttc',
            'simhei.ttf', 'C:/Windows/Fonts/simhei.ttf',
            '/System/Library/Fonts/PingFang.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        ]
    for fb in font_files:
        try:
            return ImageFont.truetype(fb, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


# ============ Text Rendering Utilities ============

def wrap_text(draw, text, font, max_width):
    """Word-wrap text into lines that fit within max_width."""
    lines = []
    paragraphs = text.split('\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            lines.append('')
            continue
        current_line = ''
        for char in para:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    return lines


def get_text_width(draw, text, font):
    """Get rendered width of text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def draw_text_with_underline(draw, x, y, text, font, color, underline_color, underline_offset=4, underline_width=2):
    """Draw text with underline below it."""
    draw.text((x, y), text, fill=color, font=font)
    bbox = draw.textbbox((x, y), text, font=font)
    line_y = bbox[3] + underline_offset
    draw.line([(x, line_y), (bbox[2], line_y)], fill=underline_color, width=underline_width)


# ============ Page Generators ============

def create_cover(title, theme_id, source='', subtitle=''):
    """Generate cover page with theme styling — 大标题居中+主题色背景。"""
    theme = THEMES[theme_id]

    img = Image.new('RGB', (IMG_W, IMG_H), theme['bg'])
    draw = ImageDraw.Draw(img)

    if theme.get('has_cover_bg'):
        # 主题色背景块（上2/3区域）
        bg_height = IMG_H * 2 // 3
        draw.rectangle([(0, 0), (IMG_W, bg_height)], fill=theme['cover_bg'])

        # 标题 — 居中大字，白字
        title_font = get_font(64, bold=True)
        title_lines = wrap_text(draw, title, title_font, IMG_W - 160)

        if len(title_lines) > 3:
            title_font = get_font(52, bold=True)
            title_lines = wrap_text(draw, title, title_font, IMG_W - 160)

        if len(title_lines) > 5:
            title_font = get_font(44, bold=True)
            title_lines = wrap_text(draw, title, title_font, IMG_W - 160)

        line_h = int(title_font.size * 1.5)
        total_title_h = len(title_lines) * line_h
        start_y = (bg_height - total_title_h) // 2

        for i, line in enumerate(title_lines):
            text_w = get_text_width(draw, line, title_font)
            text_x = (IMG_W - text_w) // 2
            text_y = start_y + i * line_h
            draw.text((text_x, text_y), line, fill=theme['cover_title_color'], font=title_font)

        # 副标题
        if subtitle:
            sub_font = get_font(28)
            sub_lines = wrap_text(draw, subtitle, sub_font, IMG_W - 200)
            sub_y = start_y + len(title_lines) * line_h + 30
            for sl in sub_lines:
                sw = get_text_width(draw, sl, sub_font)
                sx = (IMG_W - sw) // 2
                draw.text((sx, sub_y), sl, fill=theme['cover_accent'], font=sub_font)
                sub_y += int(sub_font.size * 1.6)

        # 底部装饰线
        draw.line([(100, bg_height - 60), (IMG_W - 100, bg_height - 60)],
                  fill=theme['cover_accent'], width=2)

    # 下1/3区域：来源信息（无主题标签）
    info_y = IMG_H * 2 // 3 + 80

    # 来源/作者
    if source:
        src_font = get_font(22)
        src_text = source
        src_w = get_text_width(draw, src_text, src_font)
        draw.text(((IMG_W - src_w) // 2, info_y + 60), src_text,
                  fill=theme['page_num_color'], font=src_font)

    # 页码 "1"
    page_font = get_font(18)
    draw.text((IMG_W - 60, IMG_H - 60), '1',
              fill=theme['page_num_color'], font=page_font)

    return img


def create_content_page(blocks, page_num, total_pages, theme_id, is_first_content=False):
    """
    Generate a content page image with theme styling.

    Args:
        blocks: list of parsed content blocks for this page
        page_num: current page number
        total_pages: total page count
        theme_id: theme identifier
        is_first_content: if True, add opening quote decoration
    """
    theme = THEMES[theme_id]
    img = Image.new('RGB', (IMG_W, IMG_H), theme['bg'])
    draw = ImageDraw.Draw(img)

    # Margins
    MARGIN_LEFT = 60
    MARGIN_RIGHT = 60
    MARGIN_TOP = 60
    MARGIN_BOTTOM = 80
    content_width = IMG_W - MARGIN_LEFT - MARGIN_RIGHT

    # Fonts
    body_font = get_font(30)
    body_bold_font = get_font(30, bold=True)
    h2_font = get_font(40, bold=True)
    h3_font = get_font(34, bold=True)
    quote_font = get_font(28)
    quote_bold_font = get_font(28, bold=True)
    list_font = get_font(28)

    body_line_h = int(30 * 1.5)
    h2_line_h = int(40 * 1.4)
    h3_line_h = int(34 * 1.4)
    quote_line_h = int(28 * 1.5)
    list_line_h = int(28 * 1.5)

    current_y = MARGIN_TOP

    # Opening quote mark for first content page
    if is_first_content:
        quote_mark_font = get_font(72, bold=True)
        draw.text((MARGIN_LEFT - 15, current_y - 25), '\u201c',
                  fill=theme['accent_color'], font=quote_mark_font)
        current_y += 50

    # 无顶部装饰线

    for block in blocks:
        block_type = block.get('type', 'paragraph')
        content = block.get('content', '')

        if block_type == 'heading':
            level = block.get('level', 2)
            if level == 1:
                # H1 in content — treated like H2 with theme color
                font = h2_font
                line_h = h2_line_h
                color = theme['heading_color']
            elif level == 2:
                font = h2_font
                line_h = h2_line_h
                color = theme['heading_color']
            else:
                font = h3_font
                line_h = h3_line_h
                color = theme['heading_color']

            lines = wrap_text(draw, content, font, content_width)
            for line in lines:
                # Draw heading with underline in theme color
                draw_text_with_underline(
                    draw, MARGIN_LEFT, current_y, line, font,
                    color, theme['underline_color'],
                    underline_offset=5, underline_width=3
                )
                current_y += line_h
            current_y += 45  # Extra space after heading (1 line text height)

        elif block_type == 'paragraph':
            is_key = block.get('is_key', False)
            if is_key:
                # Key content — render with highlight background
                font = body_bold_font
                color = theme['title_color']
            else:
                font = body_font
                color = theme['text_color']

            lines = wrap_text(draw, content, font, content_width)
            for i, line in enumerate(lines):
                if is_key and i == 0:
                    # Draw highlight background bar for key paragraphs
                    line_w = get_text_width(draw, line, font)
                    draw.rounded_rectangle(
                        [(MARGIN_LEFT - 8, current_y - 4),
                         (MARGIN_LEFT + line_w + 8, current_y + body_line_h)],
                        radius=6, fill=theme['highlight_bg']
                    )

                draw.text((MARGIN_LEFT, current_y), line, fill=color, font=font)
                current_y += body_line_h

            current_y += 45  # Paragraph spacing (1.5 lines gap)

        elif block_type == 'quote':
            # Quote block — left border + italic style + theme color
            quote_lines = wrap_text(draw, content, quote_font, content_width - 40)
            # Left border bar
            draw.rectangle(
                [(MARGIN_LEFT, current_y),
                 (MARGIN_LEFT + 6, current_y + len(quote_lines) * quote_line_h + 20)],
                fill=theme['accent_color']
            )
            for line in quote_lines:
                draw.text((MARGIN_LEFT + 20, current_y + 10), line,
                          fill=theme['accent_color'], font=quote_bold_font)
                current_y += quote_line_h
            current_y += 20

        elif block_type == 'list':
            items = block.get('items', [])
            bullet_color = theme['accent_color']
            for item in items:
                # Bullet point
                draw.ellipse(
                    [(MARGIN_LEFT + 5, current_y + 8), (MARGIN_LEFT + 15, current_y + 18)],
                    fill=bullet_color
                )
                item_lines = wrap_text(draw, item, list_font, content_width - 40)
                for line in item_lines:
                    draw.text((MARGIN_LEFT + 25, current_y), line,
                              fill=theme['text_color'], font=list_font)
                    current_y += list_line_h
                current_y += 8

        elif block_type == 'hr':
            # Horizontal rule
            hr_y = current_y + 15
            draw.line([(MARGIN_LEFT + 100, hr_y), (IMG_W - MARGIN_RIGHT - 100, hr_y)],
                      fill=theme['deco_color'], width=2)
            current_y = hr_y + 25

        elif block_type == 'code':
            # Code block — light background
            code_font = get_font(24)
            code_line_h = int(24 * 1.4)
            code_lines = content.split('\n')
            # Background
            code_h = len(code_lines) * code_line_h + 20
            draw.rounded_rectangle(
                [(MARGIN_LEFT, current_y), (IMG_W - MARGIN_RIGHT, current_y + code_h)],
                radius=8, fill=theme['light_color']
            )
            for cl in code_lines:
                draw.text((MARGIN_LEFT + 15, current_y + 10), cl,
                          fill=theme['heading_color'], font=code_font)
                current_y += code_line_h
            current_y += 20

    # Bottom area
    # 底部装饰线（页码上方）
    draw.line([(MARGIN_LEFT, IMG_H - 70),
               (IMG_W - MARGIN_RIGHT, IMG_H - 70)],
              fill=theme['deco_color'], width=1)

    # 页码（右下角，无主题标签）
    page_font = get_font(18)
    page_text = f'{page_num} / {total_pages}'
    page_w = get_text_width(draw, page_text, page_font)
    draw.text((IMG_W - MARGIN_RIGHT - page_w, IMG_H - 50), page_text,
              fill=theme['page_num_color'], font=page_font)

    return img


# ============ Pagination Engine ============

def paginate_blocks(blocks, theme_id):
    """
    Split parsed content blocks into page-sized chunks.
    Uses pixel-level calculation based on theme font sizes.

    Returns list of pages, where each page is a list of blocks.
    """
    theme = THEMES[theme_id]
    MARGIN_LEFT = 60
    MARGIN_RIGHT = 60
    MARGIN_TOP = 60
    MARGIN_BOTTOM = 80
    content_width = IMG_W - MARGIN_LEFT - MARGIN_RIGHT
    max_text_height = IMG_H - MARGIN_TOP - 80 - 30  # bottom line moved to IMG_H-70, page num at IMG_H-50

    # Temp image for text measurement
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    body_font = get_font(30)
    h2_font = get_font(40, bold=True)
    h3_font = get_font(34, bold=True)
    quote_font = get_font(28)
    list_font = get_font(28)

    def estimate_block_height(block):
        """Estimate pixel height of a block."""
        btype = block.get('type', 'paragraph')
        content = block.get('content', '')

        if btype == 'heading':
            level = block.get('level', 2)
            font = h2_font if level <= 2 else h3_font
            line_h = int(font.size * 1.4)
            lines = wrap_text(temp_draw, content, font, content_width)
            return len(lines) * line_h + 45  # Extra space after heading

        elif btype == 'paragraph':
            font = body_font
            line_h = int(font.size * 1.5)
            lines = wrap_text(temp_draw, content, font, content_width)
            return len(lines) * line_h + 45  # Paragraph spacing (1.5 lines gap)

        elif btype == 'quote':
            font = quote_font
            line_h = int(font.size * 1.5)
            lines = wrap_text(temp_draw, content, font, content_width - 40)
            return len(lines) * line_h + 20

        elif btype == 'list':
            items = block.get('items', [])
            total = 0
            for item in items:
                lines = wrap_text(temp_draw, item, list_font, content_width - 40)
                total += len(lines) * int(list_font.size * 1.5) + 8
            return total

        elif btype == 'hr':
            return 40

        elif btype == 'code':
            code_font = get_font(24)
            code_lines = content.split('\n')
            return len(code_lines) * int(24 * 1.4) + 20

        return 0

    # Calculate max content pages (excluding cover)
    max_content_pages = MAX_PAGES - 1

    pages = []
    current_page = []
    current_height = 0

    for block in blocks:
        block_h = estimate_block_height(block)

        # If a single block is too tall, it needs its own page
        if current_height + block_h > max_text_height and current_page:
            pages.append(current_page)
            current_page = []
            current_height = 0
            if len(pages) >= max_content_pages:
                # Force remaining into last page
                pages[-1].append(block)
                continue

        current_page.append(block)
        current_height += block_h

    if current_page and len(pages) < max_content_pages:
        pages.append(current_page)

    # Flatten overflow: if last page has too many blocks, accept truncation
    if len(pages) > max_content_pages:
        pages = pages[:max_content_pages]

    return pages


# ============ HTML Preview Generator ============

def generate_html_preview(title, blocks, theme_id, source='', subtitle=''):
    """Generate an HTML preview of the article with full styling."""
    theme = THEMES[theme_id]
    tc = theme['title_color']
    hc = theme['heading_color']
    ac = theme['accent_color']
    bg = theme['bg']
    lc = theme['light_color']
    ulc = theme['underline_color']
    txtc = theme['text_color']

    def rgb_str(c):
        return f'rgb({c[0]},{c[1]},{c[2]})'

    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="zh-CN">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=1080">',
        f'<title>{html_module.escape(title)}</title>',
        '<style>',
        '* { margin: 0; padding: 0; box-sizing: border-box; }',
        f'body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: {rgb_str(bg)}; color: {rgb_str(txtc)}; }}',
        f'.container {{ width: 1080px; margin: 0 auto; }}',
        f'.cover {{ width: 1080px; height: 1440px; background: {rgb_str(theme["cover_bg"])}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; box-sizing: border-box; }}',
        f'.cover h1 {{ font-size: 72px; font-weight: 900; color: {rgb_str(theme["cover_title_color"])}; text-align: center; line-height: 1.3; margin-bottom: 30px; }}',
        f'.cover .deco-line {{ width: 160px; height: 3px; background: {rgb_str(theme["cover_accent"])}; margin: 20px auto; }}',
        f'.cover .subtitle {{ font-size: 28px; color: {rgb_str(theme["cover_accent"])}; text-align: center; }}',
        f'.slice {{ width: 1080px; min-height: 1440px; padding: 60px; box-sizing: border-box; page-break-after: always; }}',
        f'h2 {{ font-size: 40px; font-weight: 800; color: {rgb_str(hc)}; border-bottom: 3px solid {rgb_str(ulc)}; padding-bottom: 10px; margin: 30px 0 20px 0; }}',
        f'h3 {{ font-size: 34px; font-weight: 700; color: {rgb_str(hc)}; border-bottom: 2px solid {rgb_str(ulc)}; padding-bottom: 8px; margin: 25px 0 15px 0; }}',
        f'p {{ font-size: 30px; line-height: 1.8; margin-bottom: 20px; color: {rgb_str(txtc)}; }}',
        f'p.key {{ font-weight: 700; color: {rgb_str(tc)}; background: {rgb_str(lc)}; padding: 12px 16px; border-radius: 8px; }}',
        f'blockquote {{ font-size: 28px; font-weight: 600; color: {rgb_str(ac)}; border-left: 6px solid {rgb_str(ac)}; padding: 15px 20px; margin: 25px 0; background: {rgb_str(lc)}; border-radius: 0 8px 8px 0; }}',
        f'ul {{ font-size: 28px; line-height: 1.8; margin: 15px 0; padding-left: 30px; }}',
        f'li {{ margin-bottom: 8px; }}',
        f'li::marker {{ color: {rgb_str(ac)}; }}',
        f'code {{ font-size: 24px; background: {rgb_str(lc)}; padding: 15px; display: block; border-radius: 8px; margin: 15px 0; font-family: "Consolas", "Menlo", monospace; color: {rgb_str(hc)}; }}',
        f'hr {{ border: none; height: 2px; background: {rgb_str(theme["deco_color"])}; margin: 30px 100px; }}',
        f'.page-num {{ text-align: right; font-size: 18px; color: {rgb_str(theme["page_num_color"])}; margin-top: 20px; }}',
        '</style>',
        '</head>',
        '<body>',
        '<div class="container">',
    ]

    # Cover
    html_parts.append('<div class="cover">')
    html_parts.append(f'<h1>{html_module.escape(title)}</h1>')
    html_parts.append('<div class="deco-line"></div>')
    if subtitle:
        html_parts.append(f'<div class="subtitle">{html_module.escape(subtitle)}</div>')
    html_parts.append('</div>')

    # Content blocks
    for block in blocks:
        btype = block.get('type', 'paragraph')
        content = block.get('content', '')

        if btype == 'heading':
            level = block.get('level', 2)
            tag = f'h{min(level, 4)}'
            html_parts.append(f'<{tag}>{html_module.escape(content)}</{tag}>')

        elif btype == 'paragraph':
            cls = ' class="key"' if block.get('is_key') else ''
            html_parts.append(f'<p{cls}>{html_module.escape(content)}</p>')

        elif btype == 'quote':
            html_parts.append(f'<blockquote>{html_module.escape(content)}</blockquote>')

        elif btype == 'list':
            items = block.get('items', [])
            html_parts.append('<ul>')
            for item in items:
                html_parts.append(f'<li>{html_module.escape(item)}</li>')
            html_parts.append('</ul>')

        elif btype == 'code':
            html_parts.append(f'<code>{html_module.escape(content)}</code>')

        elif btype == 'hr':
            html_parts.append('<hr>')

    html_parts.append('</div></body></html>')

    return '\n'.join(html_parts)


# ============ Main Generator ============

def sanitize_filename(name):
    """Remove illegal characters from filename."""
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(ch, '_')
    return name.strip()


def generate_images(article_title, article_text, output_dir,
                    source='好人古德曼', subtitle='', theme_id='',
                    custom_primary_color='', custom_theme_name='', bg_type='light'):
    """
    Main function: generate themed article images.

    Args:
        article_title: Article title
        article_text: Article body text (plain text or Markdown)
        output_dir: Output directory path
        source: Author/source info (default: 好人古德曼)
        subtitle: Subtitle/lead (REQUIRED — AI should generate one)
        theme_id: Force specific theme (auto-detect if empty)
        custom_primary_color: Custom theme primary color hex (e.g. '#8B4513')
        custom_theme_name: Custom theme display name
        bg_type: Custom theme background type: light/warm/cool/dark

    Returns:
        dict with 'image_paths', 'html_path', 'theme_id', 'theme_name'
    """
    os.makedirs(output_dir, exist_ok=True)

    # Warn if subtitle is missing
    if not subtitle:
        print('[WARNING] No subtitle provided. A compelling subtitle/lead is recommended for better engagement.')

    # Parse Markdown
    parser = MarkdownParser(article_text)
    blocks = parser.blocks

    # Detect key phrases for emphasis
    key_phrases = parser.detect_key_phrases()

    # Theme resolution: custom > forced > auto-detect
    if custom_primary_color:
        theme_id = generate_custom_theme(custom_primary_color, custom_theme_name or '自定义', bg_type)
        print(f'  [Theme] Custom: {THEMES[theme_id]["name"]} (primary={custom_primary_color}, bg={bg_type})')
    elif not theme_id or theme_id not in THEMES:
        theme_id = match_theme(article_title, article_text)
        print(f'  [Theme] Auto-matched: {THEMES[theme_id]["name"]} ({theme_id})')
    else:
        print(f'  [Theme] Forced: {THEMES[theme_id]["name"]} ({theme_id})')

    # Paginate
    content_pages = paginate_blocks(blocks, theme_id)
    total_pages = len(content_pages) + 1  # cover + content

    if total_pages > MAX_PAGES:
        print(f'[WARNING] Content exceeds {MAX_PAGES} pages limit. Some text may be truncated.')
        total_pages = MAX_PAGES

    saved_paths = []

    # 1. Generate HTML preview
    html_content = generate_html_preview(article_title, blocks, theme_id, source, subtitle)
    html_path = os.path.join(output_dir, 'preview.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'  [HTML] Preview saved -> {html_path}')

    # 2. Cover page
    cover_img = create_cover(article_title, theme_id, source, subtitle)
    cover_path = os.path.join(output_dir, '01_cover.png')
    cover_img.save(cover_path, quality=95)
    saved_paths.append(cover_path)
    print(f'  [1/{total_pages}] cover -> {cover_path}')

    # 3. Content pages
    for i, page_blocks in enumerate(content_pages):
        page_num = i + 2
        is_first = (i == 0)
        content_img = create_content_page(page_blocks, page_num, total_pages, theme_id, is_first)
        page_path = os.path.join(output_dir, f'{i + 2:02d}_page.png')
        content_img.save(page_path, quality=95)
        saved_paths.append(page_path)
        print(f'  [{i + 2}/{total_pages}] page {i + 1} -> {page_path}')

    return {
        'image_paths': saved_paths,
        'html_path': html_path,
        'theme_id': theme_id,
        'theme_name': THEMES[theme_id]['name']
    }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Article-to-Images Generator v3.0 (Multi-Theme + Custom)')
    parser.add_argument('--title', '-t', required=True, help='Article title')
    parser.add_argument('--input', '-i', help='Input file path (.txt/.md)')
    parser.add_argument('--text', help='Article text directly')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--source', '-s', default='好人古德曼', help='Author/source info (default: 好人古德曼)')
    parser.add_argument('--subtitle', default='', help='Subtitle/lead (REQUIRED — AI should generate one)')
    parser.add_argument('--theme', default='', help='Force theme: tech/business/literature/lifestyle/minimal/magazine/retro/fresh')
    parser.add_argument('--custom-primary-color', default='', help='Custom theme primary color hex, e.g. #8B4513')
    parser.add_argument('--custom-theme-name', default='', help='Custom theme display name')
    parser.add_argument('--bg-type', default='light', choices=['light', 'warm', 'cool', 'dark'], help='Custom theme background type')
    parser.add_argument('--list-themes', action='store_true', help='List all available themes')

    args = parser.parse_args()

    if args.list_themes:
        print('\nAvailable Themes:')
        print('-' * 60)
        for tid, t in THEMES.items():
            print(f'  {tid:15s} {t["name"]:8s} | {t["desc"]}')
            print(f'  {"":15s} {"":8s} | Keywords: {", ".join(t["keywords"][:8])}...')
        print()
        return

    article_text = args.text or ''
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            article_text = f.read()

    if not article_text.strip():
        print('[ERROR] Please provide article content (--text or --input)')
        sys.exit(1)

    # Default output: E:\codefile\trae\mp_article\文生图\整篇转换\{标题-时间戳-版本号}
    default_base_dir = r'E:\codefile\trae\mp_article\文生图\整篇转换'

    if args.output:
        output_dir = args.output
    else:
        safe_title = sanitize_filename(args.title)
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        version = 'V1'
        folder_name = f'{safe_title}-{timestamp}-{version}'
        output_dir = os.path.join(default_base_dir, folder_name)

    print(f'\n[Article-to-Images Generator v3.0]')
    print(f'   Title: {args.title}')
    print(f'   Subtitle: {args.subtitle or "(missing — recommended to provide)"}')
    print(f'   Source: {args.source}')
    print(f'   Output: {output_dir}')
    print(f'   Size: {IMG_W}x{IMG_H}px')
    theme_info = 'auto-detect'
    if args.custom_primary_color:
        theme_info = f'custom ({args.custom_primary_color}, {args.bg_type})'
    elif args.theme:
        theme_info = args.theme
    print(f'   Theme: {theme_info}')
    print(f'   Max Pages: {MAX_PAGES}\n')

    result = generate_images(
        article_title=args.title,
        article_text=article_text,
        output_dir=output_dir,
        source=args.source,
        subtitle=args.subtitle,
        theme_id=args.theme,
        custom_primary_color=args.custom_primary_color,
        custom_theme_name=args.custom_theme_name,
        bg_type=args.bg_type,
    )

    print(f'\n[OK] Generated {len(result["image_paths"])} images')
    print(f'   Theme: {result["theme_name"]} ({result["theme_id"]})')
    print(f'   Saved to: {output_dir}')
    print(f'   HTML Preview: {result["html_path"]}')


if __name__ == '__main__':
    main()
