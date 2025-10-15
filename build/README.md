# Build Assets

This directory contains build assets for the Electron application.

## Required Files

- `icon.ico` - Windows application icon (256x256 recommended)
- `icon.png` - macOS/Linux application icon (512x512 recommended)

## Creating Icons

You can use online tools or ImageMagick to create icons:

```bash
# Convert PNG to ICO (Windows)
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# Or use an online converter
# https://icoconvert.com/
# https://convertio.co/png-ico/
```

## Temporary Placeholder

For development, a placeholder icon is being used. Replace with your actual branding before production release.

