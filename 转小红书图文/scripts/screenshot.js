#!/usr/bin/env node
/**
 * 转小红书图文 - 逐切片独立截图
 * 遍历 HTML 中所有 .slice-card，对每张卡片独立截图
 * 直接输出小红书 3:4 切片图，无需拼接长图再切割
 *
 * 用法：node screenshot.js <html文件> <输出目录>
 *
 * 依赖：puppeteer-core（全局安装）
 *       Chrome 浏览器（C:/Program Files/Google/Chrome/Application/chrome.exe）
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const htmlPath = process.argv[2];
const outputDir = process.argv[3];

if (!htmlPath || !outputDir) {
  console.error('用法: node screenshot.js <html文件> <输出目录>');
  console.error('  例: node screenshot.js index.html ./output');
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();

  // 使用 file:// 协议打开
  const fileUrl = 'file:///' + path.resolve(htmlPath).replace(/\\/g, '/');
  console.log('📄 打开:', fileUrl);

  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 30000 });

  // 等待字体加载
  await new Promise(r => setTimeout(r, 3000));

  // 清除 body 背景和边距
  await page.evaluate(() => {
    document.body.style.cssText = 'background:transparent;padding:0;margin:0;display:block;min-height:auto';
    const c = document.querySelector('.container');
    if (c) c.style.margin = '0';
  });

  // 获取所有切片卡片
  const cardCount = await page.evaluate(() => {
    return document.querySelectorAll('.slice-card').length;
  });

  console.log(`📐 共 ${cardCount} 张切片`);

  // 确保输出目录存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 逐张截图
  const cards = await page.$$('.slice-card');
  for (let i = 0; i < cards.length; i++) {
    const box = await cards[i].boundingBox();
    if (!box) {
      console.error(`  ❌ 切片 ${i + 1}: 无法获取位置信息`);
      continue;
    }

    const outputFile = path.join(outputDir, `index_slice_${String(i + 1).padStart(2, '0')}.png`);

    await page.screenshot({
      path: outputFile,
      type: 'png',
      clip: {
        x: box.x,
        y: box.y,
        width: box.width,
        height: box.height
      }
    });

    console.log(`  ✅ 切片 ${i + 1}/${cardCount}: ${outputFile} (${Math.round(box.width)}×${Math.round(box.height)}px)`);
  }

  await browser.close();
  console.log(`\n🎉 完成！共生成 ${cardCount} 张小红书 3:4 切片图`);
  console.log(`📁 输出目录: ${path.resolve(outputDir)}`);

  // 输出文件列表（供外部调用）
  const sliceFiles = Array.from({ length: cardCount }, (_, i) =>
    path.join(outputDir, `index_slice_${String(i + 1).padStart(2, '0')}.png`)
  );
  console.log('\n📋 产物清单:');
  sliceFiles.forEach(f => console.log(`   ${f}`));

})().catch(e => {
  console.error('❌ 截图失败:', e.message);
  process.exit(1);
});
