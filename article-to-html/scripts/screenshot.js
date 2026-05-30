const puppeteer = require('puppeteer-core');
const path = require('path');

const htmlPath = process.argv[2];
const outputPath = process.argv[3];

if (!htmlPath || !outputPath) {
  console.error('Usage: node screenshot.js <html_file> <output_png>');
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();

  const filePath = 'file:///' + path.resolve(htmlPath).replace(/\\/g, '/');
  console.log('Opening:', filePath);

  await page.goto(filePath, { waitUntil: 'networkidle0', timeout: 30000 });

  // 等待字体加载
  await new Promise(r => setTimeout(r, 3000));

  // 清除背景
  await page.evaluate(() => {
    document.body.style.cssText = 'background:transparent;padding:0;margin:0;display:block;min-height:auto';
    const c = document.querySelector('.container');
    if (c) c.style.margin = '0';
  });

  // 计算切片数量和总高度
  const info = await page.evaluate(() => {
    const cards = document.querySelectorAll('.slice-card');
    return { count: cards.length, height: cards.length * 1440 };
  });
  console.log('Slices:', info.count, 'Total height:', info.height);

  await page.setViewport({ width: 1080, height: Math.min(info.height, 32767) });

  const resolvedOutput = path.resolve(outputPath);
  console.log('Output:', resolvedOutput);

  await page.screenshot({
    path: resolvedOutput,
    type: 'png',
    fullPage: false,
    clip: { x: 0, y: 0, width: 1080, height: info.height }
  });

  console.log('Screenshot done:', resolvedOutput);
  await browser.close();
})().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
