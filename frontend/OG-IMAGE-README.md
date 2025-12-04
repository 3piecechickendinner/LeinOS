# Open Graph Image for LienOS

## Current Status

✅ **SVG version created** at `public/og-image.svg` (1200x630)
✅ **Meta tags added** to `index.html` for Open Graph and Twitter Cards
✅ **Ready to deploy** - SVG works for most platforms

## Converting SVG to PNG (Optional)

Some platforms prefer PNG. Here are 3 ways to create `public/og-image.png`:

### Option 1: Browser Method (Easiest)

1. Open `og-image-generator.html` in your browser
2. Click the "Download OG Image" button
3. Move the downloaded file to `frontend/public/og-image.png`
4. Update `index.html` meta tags to use `.png` instead of `.svg`

### Option 2: Python Script

```bash
# Install Pillow
pip3 install Pillow

# Run the generator
python3 generate-og-image.py
```

### Option 3: Node.js Script

```bash
# Install canvas
npm install canvas

# Run the generator
node generate-og-image.cjs
```

### Option 4: ImageMagick (if installed)

```bash
convert public/og-image.svg public/og-image.png
```

## Testing Your OG Image

After deploying, test at:
- **https://www.opengraph.xyz/** - General OG testing
- **https://cards-dev.twitter.com/validator** - Twitter Card testing
- **https://developers.facebook.com/tools/debug/** - Facebook sharing testing

## Current Image Design

- **Size**: 1200x630px
- **Background**: Dark gradient (#0f172a → #1e293b)
- **Brand**: LienOS logo with "L" in blue box
- **Tagline**: "AI-Powered Tax Lien Management"
- **Features**: 7 agent boxes (Analytics, Interest, Deadlines, Reports, Payments, Alerts, Portfolio)
- **Footer**: "Automate operations • Track portfolios • Maximize returns"

## Updating the Design

To modify the design:

1. Edit `og-image-generator.html` - Update the canvas drawing code
2. Or edit `public/og-image.svg` - Modify SVG directly
3. Or edit `generate-og-image.py` / `generate-og-image.cjs` - Update the script

The design uses the same color scheme as the app (slate backgrounds, blue accents).
