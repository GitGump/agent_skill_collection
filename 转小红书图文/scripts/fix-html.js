#!/usr/bin/env node
/**
 * 转小红书图文 - HTML 后处理脚本
 * 修复常见 CSS 问题，确保：
 * 1. 切片固定 1080×1440px
 * 2. 上下不留白，内容填满整张切片
 * 3. 正文字号 ≥ 24px
 * 4. 标题必须加粗 + 变色
 * 5. overflow:hidden 防止溢出
 *
 * 用法: node fix-html.js <html文件>
 */

const fs = require('fs');
const path = require('path');

// 转小红书图文专用：padding 由各切片 inline style 动态设置，CSS 保持 0 48px 兜底
const PADDING_CONFIG = {
  default: '0px 48px',   // 左右48px保留，上下由 inline style 控制
};

function fixHTML(filePath) {
  let html = fs.readFileSync(filePath, 'utf-8');
  let fixes = [];

  // 1. 强制 body 无边距
  html = html.replace(
    /body\s*\{([^}]*)\}/g,
    (match, content) => {
      let fixed = content
        .replace(/padding\s*:\s*[^;]+;?/g, 'padding:0;')
        .replace(/margin\s*:\s*[^;]+;?/g, 'margin:0;')
        .replace(/display\s*:\s*flex\s*;?/g, '')
        .replace(/justify-content\s*:\s*center\s*;?/g, '')
        .replace(/min-height\s*:\s*100vh\s*;?/g, '');
      fixes.push('body: 清除 padding/margin/flex');
      return `body{${fixed}background:transparent;margin:0;padding:0;}`;
    }
  );

  // 2. container: 固定 1080px 宽，无边距
  html = html.replace(
    /\.container\s*\{([^}]*)\}/g,
    (match, content) => {
      let fixed = content
        .replace(/overflow\s*:\s*hidden\s*;?/g, '')
        .replace(/margin\s*:\s*0\s+auto\s*;?/g, 'margin:0;')
        .replace(/margin\s*:\s*auto\s*;?/g, 'margin:0;')
        .replace(/max-width\s*:\s*\d+px\s*;?/g, 'width:1080px;')
        .replace(/width\s*:\s*(?!1080)\d+px\s*;?/g, 'width:1080px;')
        .replace(/padding\s*:\s*[^;]+;?/g, 'padding:0;')
        .replace(/min-height\s*:\s*[^;]+;?/g, '');

      if (!fixed.includes('width:1080px') && !fixed.includes('width: 1080px')) {
        fixed = 'width:1080px;' + fixed;
      }
      fixes.push('container: 修复 width/margin/padding');
      return `.container{${fixed}}`;
    }
  );

  // 3. slice-card: 固定尺寸 + 无上下留白
  html = html.replace(
    /\.slice-card\s*\{([^}]*)\}/g,
    (match, content) => {
      let fixed = content;

      // 强制固定高度 1440px
      if (!fixed.includes('height:1440px') && !fixed.includes('height: 1440px')) {
        fixed = fixed.replace(/min-height\s*:\s*[^;]+;?/g, '');
        fixed = fixed.replace(/height\s*:\s*auto\s*;?/g, 'height:1440px;');
        if (!fixed.includes('height:')) {
          fixed = 'height:1440px;' + fixed;
        }
        fixes.push('slice-card: 强制 height:1440px');
      }

      // 确保 width:1080px
      if (!fixed.includes('width:1080px') && !fixed.includes('width: 1080px')) {
        fixed = fixed.replace(/width\s*:\s*\d+px\s*;?/g, 'width:1080px;');
        if (!fixed.includes('width:')) {
          fixed = 'width:1080px;' + fixed;
        }
        fixes.push('slice-card: 强制 width:1080px');
      }

      // 确保 overflow:hidden
      if (!fixed.includes('overflow')) {
        fixed += 'overflow:hidden;';
        fixes.push('slice-card: 添加 overflow:hidden');
      }

      // 确保 box-sizing:border-box
      if (!fixed.includes('box-sizing')) {
        fixed += 'box-sizing:border-box;';
      }

      // 统一 padding：上下 0，左右 48px（上下不留白）
      fixed = fixed.replace(/padding\s*:\s*[^;]+;?/g, `padding:${PADDING_CONFIG.default};`);
      if (!fixed.includes('padding:')) {
        fixed += `padding:${PADDING_CONFIG.default};`;
      }
      fixes.push('slice-card: 统一 padding 0 48px');

      // 确保 flex 布局（flex-start 自然流，padding 提供上下留白）
      if (!fixed.includes('display:flex') && !fixed.includes('display: flex')) {
        fixed += 'display:flex;flex-direction:column;justify-content:flex-start;';
        fixes.push('slice-card: 添加 flex 布局 + justify-content:flex-start');
      }

      // 确保 position:relative（用于 ::before/::after 过渡效果）
      if (!fixed.includes('position')) {
        fixed += 'position:relative;';
      }

      return `.slice-card{${fixed}}`;
    }
  );

  // 4. 强制标题加粗
  const titleBoldCSS = `
/* XHS-FIX: 标题强制加粗 */
.article-title { font-weight: 900 !important; }
.section-title { font-weight: 800 !important; }
.subsection-title { font-weight: 700 !important; }
/* 正文字号兜底：不小于 24px */
.body-text { font-size: max(24px, 1em); }
`;

  if (!html.includes('XHS-FIX')) {
    html = html.replace('</style>', titleBoldCSS + '</style>');
    fixes.push('注入标题加粗兜底 CSS');
  }

  // 5. 隐藏调试元素
  if (!html.includes('.coord') || !html.includes('display:none')) {
    html = html.replace('</style>', '.coord{display:none!important;}\n</style>');
    fixes.push('.coord: 强制 display:none');
  }

  // 6. 移除 "右滑查看" 等提示元素
  html = html.replace(/<div[^>]*class="[^"]*swipe-hint[^"]*"[^>]*>[\s\S]*?<\/div>/g, '');
  html = html.replace(/<div[^>]*class="[^"]*"[^>]*>\s*(?:←\s*)?(?:右滑|swipe)[^<]*(?:\s*→)?\s*<\/div>/gi, '');

  // 7. body 内联样式清理
  html = html.replace(
    /(<body[^>]*style="[^"]*)(padding\s*:\s*[^;"]+;?)/g,
    '$1padding:0;'
  );

  fs.writeFileSync(filePath, html, 'utf-8');
  console.log(`✅ ${path.basename(filePath)}: ${fixes.length} 项修复`);
  fixes.forEach(f => console.log(`   - ${f}`));
}

// 入口
const target = process.argv[2];
if (!target) {
  console.log('用法: node fix-html.js <html文件或目录>');
  process.exit(1);
}

const stat = fs.statSync(target);
if (stat.isDirectory()) {
  const files = fs.readdirSync(target).filter(f => f.endsWith('.html'));
  files.forEach(f => fixHTML(path.join(target, f)));
  console.log(`\n共修复 ${files.length} 个文件`);
} else {
  fixHTML(target);
}
