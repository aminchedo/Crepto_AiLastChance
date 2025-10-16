# Icons Directory

This directory should contain your PWA/app icons referenced by the service worker and manifest.

## Expected Files

Place your icon files here with standard sizes:
- `icon-16x16.png`
- `icon-32x32.png`
- `icon-144x144.png`
- `icon-192x192.png`
- `icon-512x512.png`

## Note

The service worker will automatically cache these icons when they're accessed. Make sure the files exist before referencing them in your manifest or HTML.

If you see 404 errors for icons in the console, add the actual icon files here.
