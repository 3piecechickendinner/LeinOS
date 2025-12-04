#!/usr/bin/env python3
"""
Generate OG Image for LienOS using Python PIL
Run with: python3 generate-og-image.py
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("\n⚠️  PIL/Pillow not installed.")
    print("\nInstall with: pip3 install Pillow")
    print("Then run: python3 generate-og-image.py\n")
    print("Alternative: Open og-image-generator.html in a browser")
    print("and click 'Download OG Image', then move to public/og-image.png\n")
    exit(0)

# Create image
width, height = 1200, 630
img = Image.new('RGB', (width, height), color='#0f172a')
draw = ImageDraw.Draw(img)

# Draw gradient background (approximated)
for y in range(height):
    ratio = y / height
    r = int(15 + (30 - 15) * ratio)
    g = int(23 + (41 - 23) * ratio)
    b = int(42 + (59 - 42) * ratio)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# Draw main container
draw.rectangle([80, 80, 1120, 550], fill='#1e293b', outline='#475569', width=2)

# Draw logo box
draw.rectangle([120, 120, 200, 200], fill='#3b82f6')

# Try to load fonts (fallback to default if not available)
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 80)
    font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 36)
    font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
    font_tiny = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
    font_logo = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
except:
    print("⚠️  Using default font (system fonts not found)")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_tiny = ImageFont.load_default()
    font_logo = ImageFont.load_default()

# Draw "L" in logo
draw.text((140, 120), 'L', fill='#ffffff', font=font_logo)

# Draw "LienOS" text
draw.text((230, 140), 'LienOS', fill='#f1f5f9', font=font_large)

# Draw tagline
draw.text((120, 240), 'AI-Powered Tax Lien Management', fill='#94a3b8', font=font_medium)

# Draw features section title
draw.text((120, 320), '7 Specialized AI Agents:', fill='#64748b', font=font_small)

# Draw agent boxes
agents = [
    'Analytics',
    'Interest',
    'Deadlines',
    'Reports',
    'Payments',
    'Alerts',
    'Portfolio'
]

start_x = 120
start_y = 370
box_width = 130
box_height = 50
gap = 15

for i, agent in enumerate(agents):
    x = start_x + (i * (box_width + gap))

    # Draw box
    draw.rectangle([x, start_y, x + box_width, start_y + box_height],
                   fill='#334155', outline='#475569', width=1)

    # Draw text (centered)
    text_bbox = draw.textbbox((0, 0), agent, font=font_tiny)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = x + (box_width - text_width) / 2
    draw.text((text_x, start_y + 18), agent, fill='#e2e8f0', font=font_tiny)

# Draw bottom tagline
draw.text((120, 480), 'Automate operations • Track portfolios • Maximize returns',
          fill='#64748b', font=font_tiny)

# Save image
output_path = os.path.join(os.path.dirname(__file__), 'public', 'og-image.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

img.save(output_path, 'PNG')

print('✅ OG image generated successfully!')
print(f'📁 Saved to: {output_path}')
print('\n🔗 Next steps:')
print('1. Meta tags will be added to index.html')
print('2. Deploy to see the OG image in action')
print('3. Test at: https://www.opengraph.xyz/\n')
