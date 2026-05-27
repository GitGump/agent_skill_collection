#!/bin/bash
# 信息图 HTML 后处理 + 截图一键脚本（v6：产物分版本文件夹版）
# 用法: bash post-process.sh <html文件> <文章标题> [基础输出目录]
#
# 功能：
# 1. 根据标题生成「标题-时间戳-V版本号」文件夹
# 2. 复制 HTML 到新文件夹
# 3. 运行 fix-html.js 修复 CSS（差异化 padding + flex布局）
# 4. 注入运行时 CSS 覆盖（字号兜底放大）
# 5. 输出完整长图到新文件夹
# 6. 调用 slice-image.js 生成小红书 3:4 切片图到同一文件夹

set -e

HTML_FILE="$1"
ARTICLE_TITLE="$2"
OUTPUT_BASE="${3:-E:/codefile/trae/mp_article/文生图}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "$HTML_FILE" ] || [ -z "$ARTICLE_TITLE" ]; then
  echo "用法: bash post-process.sh <html文件> <文章标题> [基础输出目录]"
  echo "  例: bash post-process.sh article.html 'Modest Mouse 的深度乐队解析'"
  echo "  产物将保存到: E:/codefile/trae/mp_article/文生图/Modest Mouse 的深度乐队解析-202605211130-V1/"
  exit 1
fi

export PATH="/opt/homebrew/bin:$HOME/Library/pnpm:$PATH"

# ─────────────────────────────────────────────
# Step 1: 生成版本文件夹
# ─────────────────────────────────────────────
echo "→ Step 1: 生成版本文件夹"

# 清理标题中的非法字符（用于文件夹名）
clean_title=$(echo "$ARTICLE_TITLE" | sed \
  -e 's/[\\/:*?"<>|]/_/g' \
  -e 's/[[:space:]]*$//' \
  -e 's/^[[:space:]]*//' \
  -e 's/[[:space:]]*/-/g')

# 生成时间戳
timestamp=$(date +%Y%m%d%H%M)

# 版本号管理：使用锁文件确保并发安全
VERSION_FILE="$SKILL_DIR/.version_lock"
VERSION_LOCK="$SKILL_DIR/.version_counter"
lock_dir=$(dirname "$VERSION_LOCK")

mkdir -p "$lock_dir"

# 原子递增版本号（flock）
(
  flock -x 200
  if [ -f "$VERSION_LOCK" ]; then
    last_version=$(cat "$VERSION_LOCK")
    new_version=$((last_version + 1))
  else
    new_version=1
  fi
  echo "$new_version" > "$VERSION_LOCK"
  echo "$new_version"
) 200>"$VERSION_LOCK" > "$VERSION_FILE"

VERSION=$(cat "$VERSION_FILE")
version_str="V$VERSION"

# 组装文件夹名
FOLDER_NAME="${clean_title}-${timestamp}-${version_str}"
OUTPUT_DIR="$OUTPUT_BASE/$FOLDER_NAME"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
echo "   输出目录: $OUTPUT_DIR"

# 记录版本元信息
echo "title=$ARTICLE_TITLE" > "$OUTPUT_DIR/.meta.txt"
echo "timestamp=$timestamp" >> "$OUTPUT_DIR/.meta.txt"
echo "version=$VERSION" >> "$OUTPUT_DIR/.meta.txt"

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
echo "→ Step 3: fix-html.js（差异化留白 v5：flex布局自动填满版）"
node "$SCRIPT_DIR/fix-html.js" "$HTML_FILE"

# ─────────────────────────────────────────────
# Step 4: 注入运行时字号兜底
# ─────────────────────────────────────────────
echo "→ Step 4: 注入字号兜底 CSS"

if ! grep -q "POST-PROCESS" "$HTML_FILE"; then
  python3 -c "
import sys
html = open(sys.argv[1], encoding='utf-8').read()
css = '''/* === POST-PROCESS: 字号兜底 === */
.container { font-size: max(14px, 1em); }
.slice-card h1, .slice-card [class*=\"title\"]:first-child { font-size: max(48px, 1em) !important; }
.slice-card h2, .slice-card h3 { font-size: max(28px, 1em) !important; }
.slice-card p, .slice-card li, .slice-card td { font-size: max(20px, 0.9em) !important; }
.container .coord { display: none !important; }
'''
html = html.replace('</style>', css + '</style>', 1)
open(sys.argv[1], 'w', encoding='utf-8').write(html)
print('   注入完成')
" "$HTML_FILE"
else
  echo "   已注入过，跳过"
fi

# ─────────────────────────────────────────────
# Step 5: 输出提示
# ─────────────────────────────────────────────
echo ""
echo "✅ 后处理完成！"
echo ""
echo "📁 产物目录: $OUTPUT_DIR"
echo ""
echo "→ 后续步骤："
echo "  1. 截图：打开 $OUTPUT_DIR/index.html，截取完整长图"
echo "     截图完成后将图片保存到: $OUTPUT_DIR/index_full.png"
echo "  2. 切片：node $SCRIPT_DIR/slice-image.js $OUTPUT_DIR/index_full.png"
echo "     产物: $OUTPUT_DIR/index_slice_01.png, _02.png..."
echo ""
echo "→ 截图参考（rules/02-截图流程.md）："
echo "   - 浏览器视口宽度 1080px，高度 = 切片数量 × 1440px"
echo "   - 推荐使用截图工具全页截图"
