#!/usr/bin/env node
/**
 * 小红书图片切片工具
 * 将完整长图按 1080×1440 (3:4) 切割为小红书切片图
 *
 * 用法：node slice-image.js <完整长图.png> [--out 输出目录] [--bg #颜色]
 *
 *   --out 指定输出目录（默认与原图同目录）
 *   --bg  指定背景填充色（默认自动检测）
 *
 * 输出：
 *   - 指定目录下生成 xxx_slice_01.png, xxx_slice_02.png, ...
 *   - 每张 1080×1440，最后一张不足时用背景色填充
 *
 * 依赖：sharp (npm install sharp)
 *       如果没有 sharp，回退到 ImageMagick (magick/convert 命令)
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');

const SLICE_WIDTH = 1080;
const SLICE_HEIGHT = 1440;

// ─────────────────────────────────────────────
// 解析参数
// ─────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('用法: node slice-image.js <完整长图.png> [--out 输出目录] [--bg #颜色]');
  console.error('  例: node slice-image.js ./output/index_full.png --out ./output');
  process.exit(1);
}

const inputFile = args[0];

// 解析 --out 参数：指定输出目录（默认与原图同目录）
const outIndex = args.indexOf('--out');
const outputDir = outIndex !== -1 && args[outIndex + 1] && !args[outIndex + 1].startsWith('--')
  ? args[outIndex + 1]
  : null;

const bgIndex = args.indexOf('--bg');
const bgColor = bgIndex !== -1 ? args[bgIndex + 1] : null; // 用 null 让程序自动检测

if (!fs.existsSync(inputFile)) {
  console.error(`文件不存在: ${inputFile}`);
  process.exit(1);
}

const ext = path.extname(inputFile);
const base = path.basename(inputFile, ext);
const inputDir = path.dirname(inputFile);
const finalOutputDir = outputDir || inputDir;

// ─────────────────────────────────────────────
// 尝试用 sharp（纯 JS，更可靠）
// ─────────────────────────────────────────────
async function sliceWithSharp() {
  const sharp = require('sharp');

  const metadata = await sharp(inputFile).metadata();
  const imgWidth = metadata.width;
  const imgHeight = metadata.height;

  console.log(`图片尺寸: ${imgWidth} × ${imgHeight}`);

  if (imgWidth !== SLICE_WIDTH) {
    console.warn(`⚠️  图片宽度 ${imgWidth}px，期望 ${SLICE_WIDTH}px，切片宽度将按原宽度处理`);
  }

  const totalSlices = Math.ceil(imgHeight / SLICE_HEIGHT);
  console.log(`共 ${totalSlices} 张切片`);

  // 自动检测背景色（取左上角像素）
  let fillColor = bgColor;
  if (!fillColor) {
    const { data } = await sharp(inputFile)
      .extract({ left: 0, top: 0, width: 1, height: 1 })
      .raw()
      .toBuffer({ resolveWithObject: true });
    const r = data[0], g = data[1], b = data[2];
    fillColor = `rgb(${r},${g},${b})`;
    console.log(`自动检测背景色: ${fillColor}`);
  }

  for (let i = 0; i < totalSlices; i++) {
    const top = i * SLICE_HEIGHT;
    const remaining = imgHeight - top;
    const sliceH = Math.min(SLICE_HEIGHT, remaining);
    const outputFile = path.join(finalOutputDir, `${base}_slice_${String(i + 1).padStart(2, '0')}${ext}`);

    if (sliceH === SLICE_HEIGHT) {
      // 完整切片
      await sharp(inputFile)
        .extract({ left: 0, top, width: imgWidth, height: SLICE_HEIGHT })
        .toFile(outputFile);
    } else {
      // 最后一张：填充背景色到 1440px
      console.log(`  最后一张内容高度 ${sliceH}px，填充 ${SLICE_HEIGHT - sliceH}px 背景色`);
      const croppedBuffer = await sharp(inputFile)
        .extract({ left: 0, top, width: imgWidth, height: sliceH })
        .toBuffer();

      await sharp({
        create: {
          width: imgWidth,
          height: SLICE_HEIGHT,
          channels: 3,
          background: parseCssColor(fillColor)
        }
      })
        .composite([{ input: croppedBuffer, top: 0, left: 0 }])
        .png()
        .toFile(outputFile);
    }

    console.log(`  ✅ 切片 ${i + 1}/${totalSlices}: ${outputFile}`);
  }

  console.log(`\n🎉 完成！共生成 ${totalSlices} 张切片图`);
  console.log(`📁 输出目录: ${finalOutputDir}`);

  // 输出文件列表，方便外部调用
  const sliceFiles = Array.from({ length: totalSlices }, (_, i) =>
    path.join(finalOutputDir, `${base}_slice_${String(i + 1).padStart(2, '0')}${ext}`)
  );
  return sliceFiles;
}

// ─────────────────────────────────────────────
// 回退方案：ImageMagick
// ─────────────────────────────────────────────
function sliceWithImageMagick() {
  // 检查 ImageMagick 是否可用
  const checkResult = spawnSync('magick', ['-version'], { encoding: 'utf-8' });
  const hasMagick = checkResult.status === 0;
  const convertCheck = spawnSync('convert', ['-version'], { encoding: 'utf-8' });
  const hasConvert = convertCheck.status === 0;

  if (!hasMagick && !hasConvert) {
    throw new Error('既没有 sharp 也没有 ImageMagick，无法切片。请运行: npm install sharp');
  }

  const cmd = hasMagick ? 'magick' : 'convert';

  // 获取图片尺寸
  const identify = spawnSync(cmd, ['identify', '-format', '%wx%h', inputFile], { encoding: 'utf-8' });
  const [imgWidth, imgHeight] = identify.stdout.trim().split('x').map(Number);
  console.log(`图片尺寸: ${imgWidth} × ${imgHeight}`);

  const totalSlices = Math.ceil(imgHeight / SLICE_HEIGHT);
  console.log(`共 ${totalSlices} 张切片`);

  const fill = bgColor || 'white';

  for (let i = 0; i < totalSlices; i++) {
    const top = i * SLICE_HEIGHT;
    const outputFile = path.join(finalOutputDir, `${base}_slice_${String(i + 1).padStart(2, '0')}${ext}`);

    // magick input.png -crop 1080x1440+0+{top} +repage -gravity South -extent 1080x1440 -background white output.png
    const args = [
      inputFile,
      '-crop', `${imgWidth}x${SLICE_HEIGHT}+0+${top}`,
      '+repage',
      '-background', fill,
      '-gravity', 'North',
      '-extent', `${imgWidth}x${SLICE_HEIGHT}`,
      outputFile
    ];

    const result = spawnSync(cmd, args, { encoding: 'utf-8' });
    if (result.status !== 0) {
      console.error(`ImageMagick 切片失败: ${result.stderr}`);
      throw new Error('ImageMagick 切片失败');
    }

    console.log(`  ✅ 切片 ${i + 1}/${totalSlices}: ${outputFile}`);
  }

  console.log(`\n🎉 完成！共生成 ${totalSlices} 张切片图`);
  console.log(`📁 输出目录: ${finalOutputDir}`);
}

// ─────────────────────────────────────────────
// 工具函数
// ─────────────────────────────────────────────
function parseCssColor(color) {
  if (!color) return { r: 255, g: 255, b: 255 };
  // rgb(r, g, b)
  const rgbMatch = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  if (rgbMatch) {
    return { r: parseInt(rgbMatch[1]), g: parseInt(rgbMatch[2]), b: parseInt(rgbMatch[3]) };
  }
  // #rrggbb
  const hexMatch = color.match(/^#([0-9a-fA-F]{6})$/);
  if (hexMatch) {
    const hex = hexMatch[1];
    return {
      r: parseInt(hex.slice(0, 2), 16),
      g: parseInt(hex.slice(2, 4), 16),
      b: parseInt(hex.slice(4, 6), 16)
    };
  }
  // #rgb
  const shortHexMatch = color.match(/^#([0-9a-fA-F]{3})$/);
  if (shortHexMatch) {
    const hex = shortHexMatch[1];
    return {
      r: parseInt(hex[0] + hex[0], 16),
      g: parseInt(hex[1] + hex[1], 16),
      b: parseInt(hex[2] + hex[2], 16)
    };
  }
  return { r: 255, g: 255, b: 255 };
}

// ─────────────────────────────────────────────
// 主入口
// ─────────────────────────────────────────────
(async () => {
  try {
    // 优先尝试 sharp
    try {
      require.resolve('sharp');
      await sliceWithSharp();
    } catch (e) {
      if (e.code === 'MODULE_NOT_FOUND') {
        console.log('sharp 未安装，尝试安装...');
        try {
          execSync('npm install sharp --prefix ' + path.join(__dirname, '..'), {
            stdio: 'pipe',
            timeout: 60000
          });
          console.log('sharp 安装成功，重新执行...');
          // 清除模块缓存后重试
          delete require.cache[require.resolve('sharp')];
          await sliceWithSharp();
        } catch (installErr) {
          console.log('sharp 安装失败，回退到 ImageMagick...');
          sliceWithImageMagick();
        }
      } else {
        throw e;
      }
    }
  } catch (err) {
    console.error('切片失败:', err.message);
    process.exit(1);
  }
})();
