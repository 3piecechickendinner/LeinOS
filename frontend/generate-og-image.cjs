#!/usr/bin/env node

/**
 * Generate OG Image for LienOS
 *
 * This script creates a 1200x630 PNG image for Open Graph previews.
 * Run with: node generate-og-image.js
 *
 * If canvas module is not available, open og-image-generator.html in a browser
 * and click the download button.
 */

const fs = require('fs');
const path = require('path');

// Try to use canvas if available, otherwise provide instructions
let Canvas;
try {
    Canvas = require('canvas');
} catch (e) {
    console.log('\n⚠️  Canvas module not installed.');
    console.log('\nTo generate the OG image, you have two options:\n');
    console.log('1. Open og-image-generator.html in a browser and click "Download OG Image"');
    console.log('   Then move the downloaded file to: public/og-image.png\n');
    console.log('2. Install canvas module: npm install canvas');
    console.log('   Then run this script again: node generate-og-image.js\n');
    process.exit(0);
}

const { createCanvas } = Canvas;

// Create canvas
const canvas = createCanvas(1200, 630);
const ctx = canvas.getContext('2d');

// Draw background gradient (approximated with fills)
const bgGradient = [
    { y: 0, color: '#0f172a' },
    { y: 630, color: '#1e293b' }
];

for (let y = 0; y < 630; y++) {
    const ratio = y / 630;
    ctx.fillStyle = `rgb(${Math.floor(15 + (30 - 15) * ratio)}, ${Math.floor(23 + (41 - 23) * ratio)}, ${Math.floor(42 + (59 - 42) * ratio)})`;
    ctx.fillRect(0, y, 1200, 1);
}

// Add subtle pattern
ctx.fillStyle = '#334155';
ctx.globalAlpha = 0.1;
for (let i = 0; i < 50; i++) {
    const x = Math.random() * 1200;
    const y = Math.random() * 630;
    const size = Math.random() * 100 + 50;
    ctx.fillRect(x, y, size, size);
}
ctx.globalAlpha = 1;

// Draw main container
ctx.fillStyle = '#1e293b';
ctx.fillRect(80, 80, 1040, 470);

// Border
ctx.strokeStyle = '#475569';
ctx.lineWidth = 2;
ctx.strokeRect(80, 80, 1040, 470);

// Logo/Brand area
ctx.fillStyle = '#3b82f6';
ctx.fillRect(120, 120, 80, 80);

// "L" in logo
ctx.fillStyle = '#ffffff';
ctx.font = 'bold 60px sans-serif';
ctx.fillText('L', 140, 180);

// LienOS text
ctx.fillStyle = '#f1f5f9';
ctx.font = 'bold 80px sans-serif';
ctx.fillText('LienOS', 230, 185);

// Tagline
ctx.fillStyle = '#94a3b8';
ctx.font = '36px sans-serif';
ctx.fillText('AI-Powered Tax Lien Management', 120, 270);

// Features section
ctx.fillStyle = '#64748b';
ctx.font = '24px sans-serif';
ctx.fillText('7 Specialized AI Agents:', 120, 350);

// Agent boxes
const agents = [
    '📊 Analytics',
    '💰 Interest',
    '⏰ Deadlines',
    '📄 Reports',
    '💳 Payments',
    '🔔 Alerts',
    '📈 Portfolio'
];

const startX = 120;
const startY = 390;
const boxWidth = 130;
const boxHeight = 50;
const gap = 15;

agents.forEach((agent, index) => {
    const x = startX + (index * (boxWidth + gap));

    // Box
    ctx.fillStyle = '#334155';
    ctx.fillRect(x, startY, boxWidth, boxHeight);

    // Border
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 1;
    ctx.strokeRect(x, startY, boxWidth, boxHeight);

    // Text (simplified emoji rendering)
    ctx.fillStyle = '#e2e8f0';
    ctx.font = '16px sans-serif';
    const text = agent.replace(/[^\w\s]/gi, ''); // Remove emoji for canvas
    const textWidth = ctx.measureText(text).width;
    ctx.fillText(text, x + (boxWidth - textWidth) / 2, startY + 30);
});

// Bottom tagline
ctx.fillStyle = '#64748b';
ctx.font = 'italic 20px sans-serif';
ctx.fillText('Automate operations • Track portfolios • Maximize returns', 120, 500);

// Save the image
const buffer = canvas.toBuffer('image/png');
const outputPath = path.join(__dirname, 'public', 'og-image.png');

// Ensure public directory exists
if (!fs.existsSync(path.join(__dirname, 'public'))) {
    fs.mkdirSync(path.join(__dirname, 'public'));
}

fs.writeFileSync(outputPath, buffer);

console.log('✅ OG image generated successfully!');
console.log(`📁 Saved to: ${outputPath}`);
console.log('\n🔗 Next steps:');
console.log('1. Meta tags have been added to index.html');
console.log('2. Deploy to see the OG image in action');
console.log('3. Test at: https://www.opengraph.xyz/\n');
