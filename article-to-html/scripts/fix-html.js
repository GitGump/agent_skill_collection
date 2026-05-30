#!/usr/bin/env node
/**
 * 信息图 HTML 后处理脚本（切片先行设计 + 差异化留白版）
 * 修复模型生成时常见的 CSS 问题：大边距、坐标可见、字号太小、overflow 截断
 * 新增：根据切片位置自动注入差异化 padding（首/中/尾）
 *
 * 用法：node fix-html.js <html文件路径>
 * 或：  node fix-html.js <目录>  （批量修复目录下所有 .html）
 */

const fs = require('fs');
const path = require('path');

// 差异化留白配置
const PADDING_CONFIG = {
  first: '60px 48px',   // 首切片：宽松留白，内容居中
  mid: '16px 48px',     // 中间切片：极简留白，flex填满
  last: '48px 48px'     // 尾切片：适中留白，顶部排列
};

// flex 布局配置
const FLEX_CONFIG = {
  first: 'display:flex;flex-direction:column;justify-content:center;align-items:stretch;',
  mid: 'display:flex;flex-direction:column;justify-content:space-between;align-items:stretch;',
  last: 'display:flex;flex-direction:column;justify-content:flex-start;align-items:stretch;'
};

function fixHTML(filePath) {
  let html = fs.readFileSync(filePath, 'utf-8');
  let fixes = [];

  // 1. 强制 body 无边距
  if (html.includes('<body')) {
    html = html.replace(
      /body\s*\{([^}]*)\}/g,
      (match, content) => {
        let fixed = content
          .replace(/padding\s*:\s*[^;]+;?/g, 'padding:0;')
          .replace(/margin\s*:\s*[^;]+;?/g, 'margin:0;')
          .replace(/display\s*:\s*flex\s*;?/g, '')
          .replace(/justify-content\s*:\s*center\s*;?/g, '')
          .replace(/align-items\s*:\s*[^;]+;?/g, '')
          .replace(/min-height\s*:\s*100vh\s*;?/g, '');
        fixes.push('body: 清除 padding/margin/flex');
        return `body{${fixed}background:transparent;margin:0;padding:0;}`;
      }
    );
  }

  // 2. 强制 .coord 隐藏
  if (!html.includes('.coord') || !html.includes('display: none') && !html.includes('display:none')) {
    html = html.replace(
      '</style>',
      '.coord{display:none!important;}\n</style>'
    );
    fixes.push('.coord: 强制 display:none');
  }
  // 确保已有的 .coord 规则是 display:none
  html = html.replace(
    /\.coord\s*\{([^}]*)\}/g,
    '.coord{display:none!important;}'
  );

  // 3. container: 强制 width:1080px, 移除 max-width, 修复 margin/padding
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
        fixes.push('container: 强制添加 width:1080px');
      }

      fixes.push('container: 修复 width/margin/padding');
      return `.container{${fixed}}`;
    }
  );

  // 4. slice-card: 确保固定尺寸，移除统一 padding（由差异化类控制）
  html = html.replace(
    /\.slice-card\s*\{([^}]*)\}/g,
    (match, content) => {
      let fixed = content;

      // 强制固定尺寸
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
        fixes.push('slice-card: 添加 box-sizing:border-box');
      }

      // padding: 使用默认值 16px 48px（中间切片），差异化由 .slice-first/.slice-mid/.slice-last 覆盖
      const paddingMatch = fixed.match(/padding\s*:\s*(\d+)px\s+(\d+)px/);
      if (paddingMatch) {
        fixed = fixed.replace(/padding\s*:\s*\d+px\s+\d+px/, 'padding:16px 48px');
        fixes.push('slice-card: padding 设置为默认 16px 48px（中间切片）');
      } else if (!fixed.includes('padding')) {
        fixed += 'padding:16px 48px;';
        fixes.push('slice-card: 添加 padding:16px 48px');
      }

      // 确保 display:flex + flex-direction:column
      if (!fixed.includes('display:flex') && !fixed.includes('display: flex')) {
        fixed += 'display:flex;flex-direction:column;justify-content:space-between;align-items:stretch;';
        fixes.push('slice-card: 添加 flex 布局');
      } else {
        // 如果已有 display 但不是 flex，强制替换
        fixed = fixed.replace(/display\s*:\s*block\s*;?/g, 'display:flex;flex-direction:column;justify-content:space-between;align-items:stretch;');
        fixed = fixed.replace(/display\s*:\s*flex\s*;?/g, 'display:flex;flex-direction:column;justify-content:space-between;align-items:stretch;');
      }

      // 确保 position:relative
      if (!fixed.includes('position')) {
        fixed += 'position:relative;';
        fixes.push('slice-card: 添加 position:relative');
      }

      return `.slice-card{${fixed}}`;
    }
  );

  // 5. 移除旧的统一 padding 样式（如 .slice-card + .slice-card 中的 padding 覆盖）
  html = html.replace(
    /\.slice-card\s*\+\s*\.slice-card\s*\{([^}]*)\}/g,
    (match, content) => {
      // 只保留 border-top，移除 padding/width/height/overflow/flex 等重复声明
      let fixed = content
        .replace(/padding\s*:\s*[^;]+;?/g, '')
        .replace(/width\s*:\s*[^;]+;?/g, '')
        .replace(/height\s*:\s*[^;]+;?/g, '')
        .replace(/overflow\s*:\s*[^;]+;?/g, '')
        .replace(/box-sizing\s*:\s*[^;]+;?/g, '')
        .replace(/position\s*:\s*[^;]+;?/g, '')
        .replace(/display\s*:\s*[^;]+;?/g, '')
        .replace(/flex-direction\s*:\s*[^;]+;?/g, '')
        .replace(/justify-content\s*:\s*[^;]+;?/g, '')
        .replace(/align-items\s*:\s*[^;]+;?/g, '');
      if (fixed.trim()) {
        return `.slice-card + .slice-card{${fixed}}`;
      }
      return '';
    }
  );

  // 6. 确保差异化留白 CSS 类存在（含 flex 布局）
  const diffPaddingCSS = `
/* 差异化留白+flex布局：首切片居中、中间flex填满、尾切片顶排 */
.slice-card{display:flex;flex-direction:column;justify-content:space-between;align-items:stretch;}
.slice-card.slice-first{padding:${PADDING_CONFIG.first};justify-content:center;}
.slice-card.slice-mid{padding:${PADDING_CONFIG.mid};justify-content:space-between;}
.slice-card.slice-last{padding:${PADDING_CONFIG.last};justify-content:flex-start;}
`;

  if (!html.includes('.slice-first') || !html.includes('.slice-mid') || !html.includes('.slice-last')) {
    html = html.replace('</style>', diffPaddingCSS + '</style>');
    fixes.push('注入差异化留白 CSS: .slice-first/.slice-mid/.slice-last');
  }

  // 7. 为每个 slice-card 自动添加位置类（如果还没有）
  // 统计 slice-card 数量
  const sliceCardMatches = html.match(/class="slice-card[^"]*"/g) || [];
  const totalSlices = sliceCardMatches.length;

  if (totalSlices > 0) {
    let sliceIndex = 0;
    html = html.replace(
      /class="slice-card([^"]*)"/g,
      (match, extraClasses) => {
        sliceIndex++;
        const isLast = sliceIndex === totalSlices;
        const positionClass = sliceIndex === 1 ? 'slice-first'
                            : isLast ? 'slice-last'
                            : 'slice-mid';

        // 如果已经有位置类，不重复添加
        if (extraClasses.includes('slice-first') || extraClasses.includes('slice-mid') || extraClasses.includes('slice-last')) {
          return match;
        }

        fixes.push(`slice-card #${sliceIndex}: 添加 .${positionClass}`);
        return `class="slice-card ${positionClass}${extraClasses}"`;
      }
    );
  }

  // 8. 移除 body 上的 padding 内联样式
  html = html.replace(
    /(<body[^>]*style="[^"]*)(padding\s*:\s*[^;"]+;?)/g,
    '$1padding:0;'
  );

  // 9. 移除 "右滑查看完整故事" 等提示元素
  const swipeRemoved = html.match(/<div[^>]*class="[^"]*swipe-hint[^"]*"[^>]*>[\s\S]*?<\/div>/g);
  if (swipeRemoved) {
    html = html.replace(/<div[^>]*class="[^"]*swipe-hint[^"]*"[^>]*>[\s\S]*?<\/div>/g, '');
    fixes.push('移除 swipe-hint 提示元素');
  }

  // 10. 移除任何包含"右滑""swipe"的提示文本
  html = html.replace(/<div[^>]*class="[^"]*"[^>]*>\s*(?:←\s*)?(?:右滑|swipe)[^<]*(?:\s*→)?\s*<\/div>/gi, '');

  fs.writeFileSync(filePath, html, 'utf-8');
  console.log(`✅ ${path.basename(filePath)}: ${fixes.length} fixes`);
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
  const files = fs.readdirSync(target).filter(f => f.endsWith('.html') && f !== 'gallery.html');
  files.forEach(f => fixHTML(path.join(target, f)));
  console.log(`\n共修复 ${files.length} 个文件`);
} else {
  fixHTML(target);
}
