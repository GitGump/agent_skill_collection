#!/bin/bash
# 转小红书图文 - 后处理一键脚本
# 用法: bash post-process.sh <html文件> <文章标题> [基础输出目录]
#
# 功能：
# 1. 根据标题生成「标题-时间戳-V版本号」文件夹
# 2. 复制 HTML 到新文件夹
# 3. 运行 fix-html.js 修复 CSS（差异化 padding + flex布局）
# 4. 注入运行时 CSS 覆盖（字号兜底放大，正文≥24px）
# 5. 调用 screenshot.js 逐张切片截图，直接输出小红书 3:4 切片图

set -e

HTML_FILE="$1"
ARTICLE_TITLE="$2"
OUTPUT_BASE="${3:-E:/codefile/trae/mp_article/小红书图文}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "$HTML_FILE" ] || [ -z "$ARTICLE_TITLE" ]; then
  echo "用法: bash post-process.sh <html文件> <文章标题> [基础输出目录]"
  echo "  例: bash post-process.sh index.html '深圳湾的最后一盏灯'"
  echo "  产物将保存到: E:/codefile/trae/mp_article/小红书图文/深圳湾的最后一盏灯-202605221300-V1/"
  exit 1
fi

# ─────────────────────────────────────────────
# Step 1: 生成版本文件夹
# ─────────────────────────────────────────────
echo "→ Step 1: 生成版本文件夹"

# 用 Python 清理标题中的非法字符（避免 sed 在 Windows 下对非 ASCII 字符的错误处理）
clean_title=$(python3 -c "
import sys, re
title = sys.argv[1]
# 替换文件系统非法字符
title = re.sub(r'[\\\\/:*?\"<>|]', '_', title)
# 合并连续空格/制表符为单个连字符
title = re.sub(r'[\s]+', '-', title.strip())
# 去除首尾连字符
title = title.strip('-')
# 防止空标题
if not title: title = 'untitled'
print(title)
" "$ARTICLE_TITLE")

# 生成时间戳
timestamp=$(date +%Y%m%d%H%M)

# 版本号管理（原子递增）
VERSION_FILE="$SKILL_DIR/.version_file_tmp"
VERSION_LOCK="$SKILL_DIR/.version_counter"

mkdir -p "$(dirname "$VERSION_LOCK")"

(
  if command -v flock &>/dev/null; then
    flock -x 200
  fi
  if [ -f "$VERSION_LOCK" ]; then
    last_version=$(cat "$VERSION_LOCK")
    new_version=$((last_version + 1))
  else
    new_version=1
  fi
  echo "$new_version" > "$VERSION_LOCK"
  echo "$new_version"
) 200>"$VERSION_LOCK" > "$VERSION_FILE" 2>/dev/null || echo "1" > "$VERSION_FILE"

VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "1")
version_str="V$VERSION"

# 组装文件夹名：标题-时间戳-版本号
FOLDER_NAME="${clean_title}-${timestamp}-${version_str}"
OUTPUT_DIR="$OUTPUT_BASE/$FOLDER_NAME"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
echo "   输出目录: $OUTPUT_DIR"

# 记录版本元信息
echo "title=$ARTICLE_TITLE" > "$OUTPUT_DIR/.meta.txt"
echo "timestamp=$timestamp" >> "$OUTPUT_DIR/.meta.txt"
echo "version=$VERSION" >> "$OUTPUT_DIR/.meta.txt"
echo "skill=转小红书图文" >> "$OUTPUT_DIR/.meta.txt"

# ─────────────────────────────────────────────
# Step 2: 复制 HTML 到输出目录
# ─────────────────────────────────────────────
echo "→ Step 2: 复制 HTML 到输出目录"
cp "$HTML_FILE" "$OUTPUT_DIR/index.html"
echo "   已复制: $HTML_FILE → $OUTPUT_DIR/index.html"

HTML_FILE="$OUTPUT_DIR/index.html"

# ─────────────────────────────────────────────
# Step 3: fix-html.js 修复 CSS
# ─────────────────────────────────────────────
if [ -f "$SCRIPT_DIR/fix-html.js" ]; then
  echo "→ Step 3: fix-html.js（修复 CSS 差异化留白）"
  node "$SCRIPT_DIR/fix-html.js" "$HTML_FILE"
else
  echo "→ Step 3: fix-html.js 未找到，跳过"
fi

# ─────────────────────────────────────────────
# Step 4: 注入字号兜底 CSS（正文 ≥ 24px）
# ─────────────────────────────────────────────
echo "→ Step 4: 注入字号兜底 CSS（正文 ≥ 24px）"

if ! grep -q "XHS-POST-PROCESS" "$HTML_FILE"; then
  python3 -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read()
css = '''/* === XHS-POST-PROCESS: 字号兜底 === */
/* 确保正文字号不小于 24px */
.body-text { font-size: max(24px, var(--body-fs, 1em)) !important; }
/* 标题必须加粗、颜色区分 */
.article-title { font-weight: 900 !important; }
.section-title { font-weight: 800 !important; }
.subsection-title { font-weight: 700 !important; }
/* 切片号标记 */
.slice-number { font-size: 18px !important; }
/* 隐藏 coord 调试元素 */
.coord { display: none !important; }
/* 去除右滑提示 */
.swipe-hint { display: none !important; }
'''
html = html.replace('</style>', css + '</style>', 1)
open(sys.argv[1], 'w', encoding='utf-8').write(html)
print('   注入完成')
" "$HTML_FILE"
else
  echo "   已注入过，跳过"
fi

# ─────────────────────────────────────────────
# Step 5: 逐张切片截图（直接输出切片图）
# ─────────────────────────────────────────────
echo ""
echo "→ Step 5: 逐张切片截图"

SCREENSHOT_SCRIPT="$SCRIPT_DIR/screenshot.js"
if [ ! -f "$SCREENSHOT_SCRIPT" ]; then
  # 回退到 article-to-html 的截图脚本
  SCREENSHOT_SCRIPT="E:/codefile/trae/agent_skill/article-to-html/scripts/screenshot.js"
fi

echo "   截图脚本: $SCREENSHOT_SCRIPT"
echo "   HTML: $OUTPUT_DIR/index.html"
echo "   输出: $OUTPUT_DIR"

node "$SCREENSHOT_SCRIPT" "$OUTPUT_DIR/index.html" "$OUTPUT_DIR"

# ─────────────────────────────────────────────
# 输出结果
# ─────────────────────────────────────────────

SLICE_COUNT=$(ls -1 "$OUTPUT_DIR"/index_slice_*.png 2>/dev/null | wc -l)

echo ""
echo "✅ 后处理完成！"
echo ""
echo "📁 产物目录: $OUTPUT_DIR"
echo "🖼️  切片数量: $SLICE_COUNT 张"
echo ""
echo "→ 产物清单:"
echo "    $OUTPUT_DIR/.meta.txt"
echo "    $OUTPUT_DIR/index.html                    (源 HTML，保留参考)"
echo "    $OUTPUT_DIR/index_slice_01.png ~ index_slice_${SLICE_COUNT}.png  (小红书 3:4 切片图)"
