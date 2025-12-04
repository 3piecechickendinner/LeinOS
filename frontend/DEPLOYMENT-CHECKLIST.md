# LienOS Deployment Checklist

## ✅ Open Graph / Social Media Sharing

### Files Created:
- ✅ `public/og-image.svg` - 1200x630 social media preview image
- ✅ `og-image-generator.html` - Browser-based PNG generator
- ✅ `generate-og-image.py` - Python script for PNG generation
- ✅ `generate-og-image.cjs` - Node.js script for PNG generation
- ✅ `OG-IMAGE-README.md` - Instructions for image generation

### Meta Tags Added to `index.html`:
- ✅ Open Graph tags (Facebook, LinkedIn)
- ✅ Twitter Card tags
- ✅ SEO description
- ✅ Image dimensions (1200x630)

### What Links Will Show:
- **Title**: "LienOS - AI Tax Lien Management Platform"
- **Description**: "Automate tax lien operations with 7 specialized AI agents..."
- **Image**: Professional dark-themed design with LienOS branding

## Testing After Deployment

1. **Open Graph Testing**:
   ```
   https://www.opengraph.xyz/
   Enter: https://lienos-frontend.onrender.com
   ```

2. **Twitter Card Testing**:
   ```
   https://cards-dev.twitter.com/validator
   Enter: https://lienos-frontend.onrender.com
   ```

3. **Facebook Sharing Debugger**:
   ```
   https://developers.facebook.com/tools/debug/
   Enter: https://lienos-frontend.onrender.com
   ```

## Optional: Convert SVG to PNG

The SVG works on most platforms, but if you need PNG:

1. Open `og-image-generator.html` in browser
2. Click "Download OG Image"
3. Move to `public/og-image.png`
4. Update meta tags to use `.png` instead of `.svg`

## Deployment Steps

1. Commit all changes:
   ```bash
   git add .
   git commit -m "Add Open Graph images and meta tags for social sharing"
   git push
   ```

2. Render will auto-deploy frontend

3. Test OG image at testing URLs above

4. Share on social media to verify!

## Image Design

The OG image includes:
- **LienOS branding** (logo + name)
- **Tagline**: "AI-Powered Tax Lien Management"
- **7 AI Agents** displayed as boxes
- **Professional dark theme** matching app design
- **Size**: 1200x630px (optimal for all platforms)
