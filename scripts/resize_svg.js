const sharp = require('sharp');
const fs = require('fs');

const SIZES = [4, 8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024];

async function run(svgPath, outDir, baseName) {
  const svg = fs.readFileSync(svgPath);
  for (const s of SIZES) {
    await sharp(svg, { density: 384 })
      .resize(s, s)
      .png()
      .toFile(`${outDir}/${baseName}-${s}.png`);
  }
  console.log(`exported ${SIZES.length} sizes for ${baseName}`);
}

const [,, svgPath, outDir, baseName] = process.argv;
run(svgPath, outDir, baseName);
