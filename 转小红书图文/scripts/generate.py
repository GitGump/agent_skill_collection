#!/usr/bin/env python3
"""
转小红书图文 - 内容分析 + 切片计算 + HTML 生成
将完整文章转换为小红书 3:4 图文切片的 HTML

用法:
    python generate.py <输入文本文件> [选项]
    python generate.py --title "标题" --content "正文..." [选项]

选项:
    --title       文章标题
    --content     文章正文（直接传入）
    --out         输出 HTML 路径（默认: 当前目录 index.html）
    --max-slices  最大切片数（默认 16）
    --style       强制指定风格（默认自动匹配）

风格关键词:
    tech    暗色科技    business 商务简报    journal  手账笔记
    magazine 杂志编辑    newspaper 报纸新闻    memphis  孟菲斯波普
    nordic  极简北欧    retro    复古未来    lab      实验室蓝图
"""

import re
import math
import sys
import os
import argparse
import json

# ────────────────────────────────────────────
# 画布常量
# ────────────────────────────────────────────
SLICE_WIDTH = 1080
SLICE_HEIGHT = 1440
PADDING_TOP = 0
PADDING_BOTTOM = 0
PADDING_LEFT = 48
PADDING_RIGHT = 48
AVAILABLE_HEIGHT = SLICE_HEIGHT - PADDING_TOP - PADDING_BOTTOM   # 1440px（不留白，填满整张切片）
CONTENT_WIDTH = SLICE_WIDTH - PADDING_LEFT - PADDING_RIGHT       # 984px
MAX_SLICES = 16
LINE_HEIGHT_RATIO = 2.0                # 正文行间距 = 1 倍字体大小（行盒 = 2×字号）
PADDING_TOP_RATIO = 1.0              # 切片顶部留白 = 1 行字高度
PADDING_BOTTOM_RATIO = 1.0           # 切片底部留白 = 1 行字高度
PARAGRAPH_GAP_RATIO = 2.0            # 段落之间间隔 = 2 倍正文字号

# 字号范围（正文字号下限提升至24px，保证手机端清晰可读）
BODY_MIN = 24
BODY_MAX = 64
BODY_DEFAULT = 38
TITLE_MIN = 64
TITLE_MAX = 96
TITLE_DEFAULT = 84
H2_MIN = 40
H2_MAX = 56
H2_DEFAULT = 52
H3_MIN = 28
H3_MAX = 40
H3_DEFAULT = 32
QUOTE_MIN = 24
QUOTE_MAX = 48
QUOTE_DEFAULT = 28

# ────────────────────────────────────────────
# 风格定义
# ────────────────────────────────────────────
STYLES = {
    "tech": {
        "name": "暗色科技",
        "bg": "#0A0A0F",
        "text_color": "#CCCCCC",
        "accent": "#00FFB2",
        "secondary": "#00CCFF",
        "secondary_light": "#66D9EF",
        "heading_color": "#00FFB2",
        "title_color": "#00FFB2",
        "card_bg": "#1A1A2E",
        "font": "'IBM Plex Mono', 'Noto Sans SC', monospace",
        "serif_font": "'IBM Plex Mono', 'Noto Sans SC', monospace",
        "keywords": ["科技", "AI", "编程", "代码", "互联网", "算法", "软件", "数据", "技术", "开源"],
    },
    "business": {
        "name": "商务简报",
        "bg": "#FFFFFF",
        "text_color": "#333333",
        "accent": "#1A56DB",
        "secondary": "#3F83F8",
        "secondary_light": "#76A9FA",
        "heading_color": "#1A56DB",
        "title_color": "#1A56DB",
        "card_bg": "#F8FAFC",
        "font": "'DM Sans', 'Noto Sans SC', sans-serif",
        "serif_font": "'DM Sans', 'Noto Sans SC', sans-serif",
        "keywords": ["商业", "财经", "股票", "投资", "企业", "市场", "经济", "管理", "营销", "创业"],
    },
    "journal": {
        "name": "手账笔记",
        "bg": "#FFF8E7",
        "text_color": "#4A3728",
        "accent": "#E07A5F",
        "secondary": "#81B29A",
        "secondary_light": "#F2CC8F",
        "heading_color": "#E07A5F",
        "title_color": "#E07A5F",
        "card_bg": "#FFF8E7",
        "font": "'ZCOOL KuaiLe', 'Noto Sans SC', cursive",
        "serif_font": "'ZCOOL KuaiLe', 'Noto Sans SC', cursive",
        "keywords": ["生活", "旅行", "美食", "日常", "手账", "日记", "家居", "菜谱", "穿搭", "护肤"],
    },
    "magazine": {
        "name": "杂志编辑",
        "bg": "#FAF8F5",
        "text_color": "#2D2D2D",
        "accent": "#C62828",
        "secondary": "#1565C0",
        "secondary_light": "#546E7A",
        "heading_color": "#1565C0",
        "title_color": "#C62828",
        "card_bg": "#FAF8F5",
        "font": "'Noto Serif SC', 'Playfair Display', serif",
        "serif_font": "'Playfair Display', 'Noto Serif SC', serif",
        "keywords": ["文学", "小说", "故事", "人物", "非虚构", "散文", "诗", "写作", "阅读", "书"],
    },
    "newspaper": {
        "name": "报纸新闻",
        "bg": "#F5F0E8",
        "text_color": "#1A1A1A",
        "accent": "#C62828",
        "secondary": "#263238",
        "secondary_light": "#546E7A",
        "heading_color": "#263238",
        "title_color": "#1A1A1A",
        "card_bg": "#F5F0E8",
        "font": "'Noto Serif SC', 'Lora', serif",
        "serif_font": "'Playfair Display', 'Noto Serif SC', serif",
        "keywords": ["新闻", "时事", "社会", "热点", "报道", "记者", "调查", "评论", "政策", "事件"],
    },
    "memphis": {
        "name": "孟菲斯波普",
        "bg": "#FFFBF0",
        "text_color": "#2D2D2D",
        "accent": "#EF476F",
        "secondary": "#118AB2",
        "secondary_light": "#06D6A0",
        "heading_color": "#EF476F",
        "title_color": "#EF476F",
        "card_bg": "#FFD166",
        "font": "'Rubik', 'Noto Sans SC', sans-serif",
        "serif_font": "'Rubik', 'Noto Sans SC', sans-serif",
        "keywords": ["设计", "艺术", "创意", "潮流", "时尚", "插画", "色彩", "潮", "视觉", "品牌"],
    },
    "nordic": {
        "name": "极简北欧",
        "bg": "#FAFAF6",
        "text_color": "#3D3D3D",
        "accent": "#6B8F71",
        "secondary": "#C77D4D",
        "secondary_light": "#A8B5A0",
        "heading_color": "#6B8F71",
        "title_color": "#6B8F71",
        "card_bg": "#FAFAF6",
        "font": "'Outfit', 'Noto Sans SC', sans-serif",
        "serif_font": "'Outfit', 'Noto Sans SC', sans-serif",
        "keywords": ["自然", "环保", "极简", "冥想", "健康", "运动", "瑜伽", "素食", "有机", "户外"],
    },
    "retro": {
        "name": "复古未来",
        "bg": "#2D1B0E",
        "text_color": "#D4A853",
        "accent": "#FFB800",
        "secondary": "#90EE90",
        "secondary_light": "#66BB6A",
        "heading_color": "#FFB800",
        "title_color": "#FFB800",
        "card_bg": "#3D2B1E",
        "font": "'Space Mono', 'Noto Sans SC', monospace",
        "serif_font": "'Space Mono', 'Noto Serif SC', monospace",
        "keywords": ["历史", "复古", "怀旧", "经典", "老物件", "记忆", "年代", "旧时光", "传统", "工艺"],
    },
    "lab": {
        "name": "实验室蓝图",
        "bg": "#F0F4F8",
        "text_color": "#334155",
        "accent": "#2563EB",
        "secondary": "#7C3AED",
        "secondary_light": "#8B5CF6",
        "heading_color": "#2563EB",
        "title_color": "#7C3AED",
        "card_bg": "#F0F4F8",
        "font": "'Noto Sans SC', system-ui, sans-serif",
        "serif_font": "'Noto Sans SC', system-ui, sans-serif",
        "keywords": ["教程", "学习", "笔记", "知识", "考试", "备考", "复习", "方法", "技能", "白皮书"],
    },
}


def match_style(text):
    """根据文章关键词匹配视觉风格，返回得分最高的风格 key"""
    scores = {}
    for key, style in STYLES.items():
        score = 0
        for kw in style["keywords"]:
            if kw in text:
                score += 1
        scores[key] = score
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "magazine"  # 默认杂志编辑
    return best


def count_chars(text):
    """统计文本中 CJK、ASCII 和宽符号（emoji 等）字符数"""
    cjk = 0
    ascii_chars = 0
    wide_symbols = 0  # emoji / 特殊宽符号，浏览器渲染宽度 ≈ CJK
    for ch in text:
        cp = ord(ch)
        if 0x4e00 <= cp <= 0x9fff or 0x3000 <= cp <= 0x303f or 0xff00 <= cp <= 0xffef:
            cjk += 1
        elif ch.isascii() and not ch.isspace():
            ascii_chars += 1
        elif cp > 0x2000:
            # 补充平面字符（emoji、特殊符号等），浏览器渲染为宽字符
            wide_symbols += 1
    return cjk, ascii_chars, wide_symbols


def estimate_width(text, font_size):
    """
    估算文本在给定字号下的像素宽度
    基于浏览器实际渲染校正：
    - CJK 字符 ≈ font_size * 0.88（Noto Serif SC 等字体实际 em 宽度）
    - 宽符号（emoji 等）≈ font_size * 0.88（与 CJK 相同渲染宽度）
    - ASCII ≈ font_size * 0.48（等比例缩小）
    - 标点和空格 ≈ font_size * 0.25
    """
    cjk, ascii_chars, wide_symbols = count_chars(text)
    others = len(text) - cjk - ascii_chars - wide_symbols
    width = (cjk + wide_symbols) * font_size * 0.88 + ascii_chars * font_size * 0.48 + others * font_size * 0.25
    return width


def wrap_text(text, font_size, content_width=CONTENT_WIDTH):
    """
    将文本按指定字号和宽度折行
    返回 (行列表, 总高度)
    """
    lines = []
    current_line = ""
    for ch in text:
        test_line = current_line + ch
        if estimate_width(test_line, font_size) > content_width * 0.95:
            lines.append(current_line)
            current_line = ch
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    line_height = font_size * LINE_HEIGHT_RATIO
    total_height = len(lines) * line_height
    return lines, total_height


def estimate_block_height(block, font_size, content_width=CONTENT_WIDTH):
    """
    估算一个文本块在给定字号下的像素高度
    block: (type, text) 元组
    """
    btype, text = block
    if btype == "blank":
        return font_size * LINE_HEIGHT_RATIO  # 空行
    _, height = wrap_text(text, font_size, content_width)
    return height


def estimate_title_height(text, font_size):
    """估算标题渲染高度"""
    _, height = wrap_text(text, font_size, CONTENT_WIDTH - 20)
    return height + font_size * 0.5  # margin


def pack_slices(blocks, style, max_slices=MAX_SLICES):
    """
    核心算法：将文章块分配到切片中，每张切片自适应字号

    blocks: [(type, text), ...]
      type: "h1" | "h2" | "h3" | "p" | "quote" | "blank"
    style: 风格字典

    返回: slices = [{font_sizes: {h1, h2, h3, p, quote}, blocks: [...], height: float}, ...]
    """
    slices = []
    slice_idx = 0

    # 每个元素类型在当前切片中的默认字号
    font_config = {
        "h1": TITLE_DEFAULT,
        "h2": H2_DEFAULT,
        "h3": H3_DEFAULT,
        "p": BODY_DEFAULT,
        "quote": QUOTE_DEFAULT,
        "blank": BODY_DEFAULT,
    }

    current_slice = {
        "blocks": [],
        "font_sizes": font_config.copy(),
    }

    # 字号边界
    font_bounds = {
        "h1": (TITLE_MIN, TITLE_MAX),
        "h2": (H2_MIN, H2_MAX),
        "h3": (H3_MIN, H3_MAX),
        "p": (BODY_MIN, BODY_MAX),
        "quote": (QUOTE_MIN, QUOTE_MAX),
        "blank": (BODY_MIN, BODY_MAX),
    }

    def block_height(block, fs, is_last=False):
        """计算单个块的高度（含段落间距）"""
        btype, text = block
        body_fs = fs["p"]
        # 段落间距 = 2 倍正文字号（最后一段和 blank 不加）
        para_gap = body_fs * PARAGRAPH_GAP_RATIO if (not is_last and btype != "blank") else 0
        if btype in ("h1", "h2", "h3"):
            return estimate_title_height(text, fs[btype]) + para_gap
        elif btype == "quote":
            _, h = wrap_text(text, fs["quote"], CONTENT_WIDTH - 48)
            return h + 48 + para_gap
        elif btype == "blank":
            return fs["p"] * LINE_HEIGHT_RATIO * 0.5  # 空白行无段间距
        else:  # p
            _, h = wrap_text(text, fs["p"])
            return h + para_gap

    def calc_slice_total_height(slice_data):
        """计算切片总高度 = 顶部留白 + 所有块(含段间距) + 底部留白"""
        fs = slice_data["font_sizes"]
        body_fs = fs["p"]
        total = body_fs * PADDING_TOP_RATIO + body_fs * PADDING_BOTTOM_RATIO
        blocks = slice_data["blocks"]
        for i, b in enumerate(blocks):
            is_last = (i == len(blocks) - 1)
            total += block_height(b, fs, is_last)
        return total

    def try_shrink_font(slice_data, target_height):
        """
        尝试缩小字号使内容适应目标高度
        返回 (能否适应, 新的font_sizes)
        """
        fs = dict(slice_data["font_sizes"])
        # 优先缩小正文字号
        for attempt in range(30):
            current_total = 0
            for b in slice_data["blocks"]:
                current_total += block_height(b, fs)
            if current_total <= target_height:
                return True, fs
            # 缩小字号
            reduced = False
            for btype in ["p", "quote", "h3", "h2", "h1"]:
                if btype in fs:
                    cur = fs[btype]
                    min_val = font_bounds[btype][0]
                    if cur > min_val:
                        # 步长: 大字号步长大，小字号步长小
                        step = max(1, int(cur * 0.08))
                        fs[btype] = max(min_val, cur - step)
                        reduced = True
                        break
            if not reduced:
                return False, fs
        return False, fs

    def finalize_slice(slice_data, idx):
        """完成一张切片：字号微调使内容适配画布（仅缩小，不放大填充）"""
        slice_data["font_sizes"] = font_config.copy()
        total = calc_slice_total_height(slice_data)
        target = AVAILABLE_HEIGHT

        if total > target:
            # 内容过多，尝试缩小字号
            ok, new_fs = try_shrink_font(slice_data, target)
            slice_data["font_sizes"] = new_fs

        # 确保正文不小于最小值
        if slice_data["font_sizes"].get("p", BODY_DEFAULT) < BODY_MIN:
            slice_data["font_sizes"]["p"] = BODY_MIN

        return slice_data

    # ── 主打包循环 ──
    for i, block in enumerate(blocks):
        btype, text = block

        # 当前切片的 font_sizes 始终使用 font_config 副本（在 finalize 时才最终调整）
        if not current_slice.get("font_sizes"):
            current_slice["font_sizes"] = font_config.copy()

        # 估算加入当前块后的切片总高度 = 上下留白 + 已有块 + 新块（均含段间距）
        test_fs = font_config.copy()
        current_blocks = current_slice["blocks"]
        # 已有块的高度（最后一个不加段间距，新块会顶替为最后一个）
        existing_h = sum(block_height(b, test_fs, is_last=False) for b in current_blocks)
        # 新块加入后的总高度：已有块(含段间距) + 新块(作为最后一块不含段间距) + 上下留白
        new_block_h = block_height(block, test_fs, is_last=True)
        padding_h = test_fs["p"] * (PADDING_TOP_RATIO + PADDING_BOTTOM_RATIO)
        projected_height = padding_h + existing_h + new_block_h

        if projected_height <= AVAILABLE_HEIGHT and len(current_slice["blocks"]) < 50:
            # 可以放入当前切片
            current_slice["blocks"].append(block)
        else:
            # 当前切片已满或块数过多
            if current_slice["blocks"]:
                # 完成当前切片
                finalized = finalize_slice(current_slice, slice_idx)
                slices.append(finalized)
                slice_idx += 1

                if slice_idx >= max_slices:
                    # 已达上限，剩余内容强制打包到最后一张
                    overflow_slice = {
                        "blocks": blocks[i:],
                        "font_sizes": {"h1": TITLE_MIN, "h2": H2_MIN, "h3": H3_MIN, "p": BODY_MIN, "quote": QUOTE_MIN},
                    }
                    slices.append(overflow_slice)
                    print(f"⚠️  切片数达到上限 {max_slices}，剩余 {len(blocks) - i} 个段落以最小字号放入最后一张")
                    break

                # 开始新切片
                current_slice = {"blocks": [], "font_sizes": font_config.copy()}
                current_slice["blocks"].append(block)

    # 处理最后一张切片
    if current_slice["blocks"] and slice_idx < max_slices:
        finalized = finalize_slice(current_slice, slice_idx)
        slices.append(finalized)

    # 后处理：重新微调每张切片的字号 + 溢出安全防护
    for idx, sl in enumerate(slices):
        sl["font_sizes"] = finalize_slice(sl, idx)["font_sizes"]
        sl["total_height"] = calc_slice_total_height(sl)

        # 溢出安全防护：如果仍超限，强制逐级缩到最小字号
        safety_attempts = 0
        while sl["total_height"] > AVAILABLE_HEIGHT and safety_attempts < 10:
            fs = sl["font_sizes"]
            shrunk = False
            for btype in ["p", "quote", "h3", "h2", "h1"]:
                if btype in fs and fs[btype] > font_bounds[btype][0]:
                    fs[btype] = max(font_bounds[btype][0], fs[btype] - 2)
                    shrunk = True
                    break
            if not shrunk:
                break
            sl["total_height"] = calc_slice_total_height(sl)
            safety_attempts += 1

        fill_rate = sl["total_height"] / AVAILABLE_HEIGHT * 100
        status = "⚠️ 溢" if sl["total_height"] > AVAILABLE_HEIGHT else ""
        # 新增：显示上下留白
        pad_info = f"留白={sl['font_sizes']['p']}px"
        print(f"  切片 {idx + 1}: {len(sl['blocks'])} 个段落, 字号 p={sl['font_sizes']['p']}px, h2={sl['font_sizes'].get('h2','-')}px, {pad_info}, 总高 {sl['total_height']:.0f}px {status}")

    return slices


# ────────────────────────────────────────────
# 文章解析
# ────────────────────────────────────────────
def parse_article(text):
    """
    将文章文本解析为结构化块列表
    识别规则：
    - 第一行 → h1（标题）
    - ## ... → h2
    - ### ... → h3
    - > ... → quote
    - 空行 → blank
    - 其他 → p
    """
    lines = text.strip().split('\n')
    blocks = []
    current_p = []
    in_quote = False
    quote_text = []

    for line in lines:
        stripped = line.strip()

        # Markdown 标题
        if stripped.startswith('### '):
            if current_p:
                blocks.append(("p", '\n'.join(current_p)))
                current_p = []
            blocks.append(("h3", stripped[4:]))
            continue
        if stripped.startswith('## '):
            if current_p:
                blocks.append(("p", '\n'.join(current_p)))
                current_p = []
            blocks.append(("h2", stripped[3:]))
            continue
        if stripped.startswith('# '):
            if current_p:
                blocks.append(("p", '\n'.join(current_p)))
                current_p = []
            blocks.append(("h1", stripped[2:]))
            continue

        # 引用块
        if stripped.startswith('> '):
            if current_p:
                blocks.append(("p", '\n'.join(current_p)))
                current_p = []
            quote_text.append(stripped[2:])
            in_quote = True
            continue
        if in_quote and stripped.startswith('>'):
            quote_text.append(stripped[2:] if len(stripped) > 2 else stripped[1:])
            continue
        if in_quote and not stripped.startswith('>'):
            if quote_text:
                blocks.append(("quote", '\n'.join(quote_text)))
                quote_text = []
            in_quote = False

        # 空行
        if not stripped:
            if current_p:
                blocks.append(("p", '\n'.join(current_p)))
                current_p = []
            blocks.append(("blank", ""))
            continue

        # 普通段落
        current_p.append(stripped)

    # 收尾
    if current_p:
        blocks.append(("p", '\n'.join(current_p)))
    if quote_text:
        blocks.append(("quote", '\n'.join(quote_text)))

    # 如果没有识别到 h1，用第一个非空段落作为标题
    has_h1 = any(b[0] == "h1" for b in blocks)
    if not has_h1 and blocks:
        blocks.insert(0, ("h1", blocks[0][1] if blocks[0][0] == "p" else "未命名"))

    return blocks


# ────────────────────────────────────────────
# HTML 生成
# ────────────────────────────────────────────
def generate_html(title, slices, style):
    """根据切片数据生成完整 HTML"""
    s = style

    # Google Fonts 加载
    font_imports = []
    font_family = s["font"]
    if "Playfair Display" in font_family:
        font_imports.append("Playfair+Display:400,700,900")
    if "IBM Plex Mono" in font_family:
        font_imports.append("IBM+Plex+Mono:400,600,700")
    if "DM Sans" in font_family:
        font_imports.append("DM+Sans:400,500,700")
    if "ZCOOL KuaiLe" in font_family:
        font_imports.append("ZCOOL+KuaiLe")
    if "Lora" in font_family:
        font_imports.append("Lora:400,600,700")
    if "Space Mono" in font_family:
        font_imports.append("Space+Mono:400,700")
    if "Rubik" in font_family:
        font_imports.append("Rubik:400,500,700,900")
    if "Outfit" in font_family:
        font_imports.append("Outfit:400,500,700")
    if "Noto Sans SC" in font_family:
        font_imports.append("Noto+Sans+SC:400,500,700,900")
    if "Noto Serif SC" in font_family:
        font_imports.append("Noto+Serif+SC:400,600,700,900")

    font_import_str = "&family=".join(font_imports)
    google_fonts_url = f"https://fonts.googleapis.com/css2?family={font_import_str}&display=swap"

    html_parts = []

    # HTML 头部
    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<link href="{google_fonts_url}" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ margin: 0; padding: 0; background: transparent; }}
.container {{ width: 1080px; margin: 0; padding: 0; }}

.slice-card {{
  width: 1080px;
  height: 1440px;
  box-sizing: border-box;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background: {s["bg"]};
  /* padding 由各切片按字号动态设置 inline style */
}}

.article-title {{
  font-family: {s["serif_font"]};
  font-weight: 900;
  color: {s["title_color"]};
  line-height: 1.2;
  margin-bottom: 0;  /* 由 inline style 统一管理 */
}}

.section-title {{
  font-family: {s["serif_font"]};
  font-weight: 800;
  color: {s["heading_color"]};
  line-height: 1.3;
  margin-bottom: 0;
}}

.subsection-title {{
  font-family: {s["font"]};
  font-weight: 700;
  color: {s["secondary_light"]};
  line-height: 1.35;
  margin-bottom: 0;
}}

.body-text {{
  font-family: {s["font"]};
  font-weight: 400;
  color: {s["text_color"]};
  line-height: {LINE_HEIGHT_RATIO};
  margin: 0;
  text-align: justify;
  overflow-wrap: break-word;
  word-break: normal;
}}

.blockquote {{
  font-style: italic;
  font-weight: 600;
  color: {s["accent"]};
  border-left: 6px solid {s["accent"]};
  padding: 10px 20px;
  margin: 0;
  background: {s["card_bg"]};
  font-family: {s["serif_font"]};
  border-radius: 0 8px 8px 0;
}}

.slice-number {{
  position: absolute;
  bottom: 10px;
  right: 20px;
  font-size: 18px;
  color: {s["secondary_light"]};
  opacity: 0.5;
  font-family: {s["font"]};
  z-index: 2;
}}
</style>
</head>
<body>
<div class="container">
""")

    # 生成每张切片
    for idx, sl in enumerate(slices):
        fs = sl["font_sizes"]
        body_fs = fs["p"]
        # 动态 padding：上下各 1 行字高度 = body_fs px，左右 48px
        pad_top = body_fs
        pad_bottom = body_fs
        html_parts.append(
            f'  <div class="slice-card" data-slice="{idx + 1}" '
            f'style="padding:{pad_top}px {PADDING_LEFT}px {pad_bottom}px {PADDING_RIGHT}px;">'
        )

        blocks_in_slice = sl["blocks"]
        for bi, block in enumerate(blocks_in_slice):
            btype, text = block
            is_last_block = (bi == len(blocks_in_slice) - 1)
            # 段落间距 = 2 倍正文字号，最后一个块不加
            margin_bottom = 0 if is_last_block else int(body_fs * PARAGRAPH_GAP_RATIO)

            if not text and btype == "blank":
                # 空行渲染为占位 div（无段间距，仅自身高度）
                spacer_h = int(body_fs * LINE_HEIGHT_RATIO * 0.5)
                html_parts.append(f'    <div style="height:{spacer_h}px"></div>')
                continue
            if not text:
                continue

            if btype == "h1":
                html_parts.append(
                    f'    <div class="article-title" style="font-size:{fs["h1"]}px;font-weight:900;color:{s["title_color"]};margin-bottom:{margin_bottom}px;">{escape_html(text)}</div>'
                )
            elif btype == "h2":
                html_parts.append(
                    f'    <div class="section-title" style="font-size:{fs["h2"]}px;font-weight:800;color:{s["heading_color"]};margin-bottom:{margin_bottom}px;">{escape_html(text)}</div>'
                )
            elif btype == "h3":
                html_parts.append(
                    f'    <div class="subsection-title" style="font-size:{fs["h3"]}px;font-weight:700;color:{s["secondary_light"]};margin-bottom:{margin_bottom}px;">{escape_html(text)}</div>'
                )
            elif btype == "quote":
                html_parts.append(
                    f'    <div class="blockquote" style="font-size:{fs["quote"]}px;margin-bottom:{margin_bottom}px;">{escape_html(text)}</div>'
                )
            else:
                html_parts.append(
                    f'    <div class="body-text" style="font-size:{body_fs}px;margin-bottom:{margin_bottom}px;">{escape_html(text)}</div>'
                )

        html_parts.append(f'    <div class="slice-number">{idx + 1}/{len(slices)}</div>')
        html_parts.append('  </div>')

    html_parts.append('</div>\n</body>\n</html>')
    return '\n'.join(html_parts)


def escape_html(text):
    """转义 HTML 特殊字符"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# ────────────────────────────────────────────
# 主入口
# ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="转小红书图文 - 将完整文章转换为 3:4 切片 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_file", nargs="?", help="输入文本文件路径")
    parser.add_argument("--title", help="文章标题（直接从参数传入）")
    parser.add_argument("--content", help="文章正文（直接从参数传入）")
    parser.add_argument("--out", default="index.html", help="输出 HTML 路径")
    parser.add_argument("--max-slices", type=int, default=16, help="最大切片数")
    parser.add_argument("--style", choices=list(STYLES.keys()), help="强制指定风格")

    args = parser.parse_args()

    # 获取输入
    if args.content:
        article_text = args.content
        article_title = args.title or "未命名"
    elif args.input_file:
        if not os.path.exists(args.input_file):
            print(f"❌ 文件不存在: {args.input_file}")
            sys.exit(1)
        with open(args.input_file, 'r', encoding='utf-8') as f:
            article_text = f.read()
        article_title = args.title or os.path.splitext(os.path.basename(args.input_file))[0]
    elif args.title:
        article_text = args.title
        article_title = args.title
    else:
        # 从 stdin 读取
        article_text = sys.stdin.read()
        article_title = "未命名"

    if not article_text.strip():
        print("❌ 文章内容为空")
        sys.exit(1)

    print(f"📝 文章标题: {article_title}")
    print(f"📊 文章长度: {len(article_text)} 字符")

    # ① 解析文章
    blocks = parse_article(article_text)
    type_counts = {}
    for btype, _ in blocks:
        type_counts[btype] = type_counts.get(btype, 0) + 1
    print(f"📋 解析结果: {type_counts}")
    print(f"   总段落数: {len(blocks)}")

    # ② 风格匹配
    if args.style:
        style_key = args.style
    else:
        full_text = article_title + " " + article_text[:2000]
        style_key = match_style(full_text)
    style = STYLES[style_key]
    print(f"🎨 匹配风格: {style['name']} ({style_key})")

    # ③ 切片计算
    print("📐 开始切片计算...")
    slices = pack_slices(blocks, style, max_slices=args.max_slices)

    if not slices:
        print("❌ 切片计算失败")
        sys.exit(1)

    print(f"✅ 共 {len(slices)} 张切片")

    if len(slices) > args.max_slices:
        print(f"⚠️  切片数 {len(slices)} 超过上限 {args.max_slices}, 部分内容可能被压缩")
        slices = slices[:args.max_slices]

    # ④ 生成 HTML
    print("🔨 生成 HTML...")
    html = generate_html(article_title, slices, style)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML 已保存: {os.path.abspath(args.out)}")
    print(f"   切片数: {len(slices)}")
    print(f"   长图尺寸: 1080 × {len(slices) * SLICE_HEIGHT}px")
    print()
    print("→ 下一步: 运行 post-process.sh 后处理 + 截图 + 切片")


if __name__ == "__main__":
    main()
