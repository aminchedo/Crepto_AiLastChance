# Service Worker Implementation Guide

## Overview

This project implements a **robust, defensive Service Worker** that:
- ✅ Only runs in **production** (not in development)
- ✅ Handles fetch failures gracefully with proper fallbacks
- ✅ Prevents SW from interfering with Vite HMR and dev server
- ✅ Provides offline support with a custom offline page
- ✅ Includes defensive error handling to prevent fetch-fail storms

## 🚀 Quick Start

### Development Mode
The Service Worker is **automatically disabled** in development mode to prevent conflicts with Vite's Hot Module Replacement (HMR) and dev server.

```bash
npm run dev
# or
vite
```

**No Service Worker will be registered in dev mode** - you can develop freely without SW interference.

### Production Mode
Build and preview the production version to test the Service Worker:

```bash
npm run build
npm run preview
```

The Service Worker will be registered automatically and handle offline requests.

## 📁 File Structure

```
/workspace
├── public/
│   ├── sw.js              # Main service worker with defensive fetch handling
│   ├── offline.html       # Offline fallback page
│   └── unregister-sw.js   # Utility script to unregister SW
├── src/
│   └── main.tsx           # SW registration (production only)
└── vite.config.ts         # Updated to handle public assets
```

## 🛡️ Features

### 1. Network-First Strategy
The SW attempts to fetch from the network first, falling back to cache only if the network fails.

### 2. Defensive Error Handling
- All `fetch()` calls wrapped in `try/catch`
- Never leaves a rejected promise unhandled
- Returns proper fallback responses for all scenarios

### 3. Dev-Mode Safeguards
The SW skips handling these paths to avoid breaking dev tools:
- `/@vite` - Vite client code
- `/@fs` - Vite filesystem access
- `/__vite` - Vite internal routes
- `/node_modules` - Module resolution
- `/sockjs-node` - WebSocket connections
- `/@react-refresh` - React Fast Refresh
- `/ws` and `/websocket` - WebSocket endpoints

### 4. Smart Caching
- **API responses**: Network-first, cache successful responses
- **Static assets**: Cache JS, CSS, images, fonts after first fetch
- **Navigation requests**: Serve offline page if network unavailable

### 5. Offline Support
Beautiful, responsive offline page with:
- Connection status indicator
- Auto-reload on connection restored
- Manual retry and connection check buttons

## 🔧 Unregister Service Worker (Emergency Recovery)

If you're experiencing SW issues in development or testing, use this quick console command:

```javascript
// Short version - paste in DevTools Console:
navigator.serviceWorker.getRegistrations().then(regs => {
  regs.forEach(r => r.unregister());
  console.log('✅ SW unregistered');
}).then(() => location.reload());
```

Or use the comprehensive utility script:

1. Open your browser DevTools (F12)
2. Go to Console tab
3. Copy and paste the contents of `public/unregister-sw.js`
4. Press Enter
5. Hard refresh the page (Ctrl+F5 or Cmd+Shift+R)

## 🐛 Debugging

### Check Service Worker Status

**Chrome/Edge DevTools:**
1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Service Workers** in the left sidebar
4. View registered workers, their scope, and status

**Firefox DevTools:**
1. Open DevTools (F12)
2. Go to **Application** → **Service Workers**
3. View registered workers

### Common Issues & Solutions

#### Issue: "Failed to fetch" errors in development

**Cause:** Service Worker is intercepting dev server requests

**Solution:**
```bash
# Ensure you're running in dev mode (SW is disabled):
npm run dev

# If SW is still active, unregister it:
# Paste in console:
window.unregisterSW()
```

#### Issue: Old SW version cached

**Solution:**
1. Go to DevTools → Application → Service Workers
2. Check "Update on reload"
3. Click "Unregister" next to the SW
4. Hard refresh (Ctrl+F5)

#### Issue: CORS errors with SW active

**Cause:** SW trying to fetch cross-origin resources

**Solution:** Update `sw.js` to whitelist the origin:
```javascript
const allowedOrigins = [
  'https://your-api-domain.com'
];
```

### Console Logs

The Service Worker logs all major operations:
- `[SW] Installing service worker...`
- `[SW] Activating service worker...`
- `[SW] Serving from cache: <url>`
- `[SW] Network fetch failed for <url>`

Filter console by `[SW]` to see Service Worker activity.

## 📊 Testing

### Test Offline Behavior

**Chrome/Edge:**
1. Open DevTools (F12)
2. Go to **Network** tab
3. Select "Offline" from the throttling dropdown
4. Reload the page → should show offline.html

**Firefox:**
1. Open DevTools (F12)
2. Go to **Network** tab
3. Click the network conditions icon
4. Check "Offline"
5. Reload the page

### Test Cache Behavior

```javascript
// Check what's cached (paste in console):
caches.keys().then(keys => {
  console.log('Cache keys:', keys);
  return Promise.all(
    keys.map(key => 
      caches.open(key).then(cache => 
        cache.keys().then(requests => ({
          cache: key,
          urls: requests.map(r => r.url)
        }))
      )
    )
  );
}).then(console.log);
```

## 🔐 Security Considerations

### Cross-Origin Requests
The SW only handles same-origin requests by default. To handle cross-origin requests:

1. Edit `sw.js`
2. Add allowed origins to the whitelist:
```javascript
const allowedOrigins = [
  'https://api.yourdomain.com',
  'https://cdn.yourdomain.com'
];
```

### HTTPS Requirement
Service Workers **only work on HTTPS** (except `localhost` for development).

For production deployment:
- ✅ Ensure your domain has a valid SSL certificate
- ✅ Redirect HTTP to HTTPS
- ✅ Use secure cookies and headers

## 🚢 Production Deployment

### Build Checklist
- [x] Service Worker file (`sw.js`) in public directory
- [x] Offline fallback page (`offline.html`) in public directory
- [x] SW registration only happens in production (`import.meta.env.PROD`)
- [x] Public directory configured in `vite.config.ts`
- [x] Build command: `npm run build`

### Post-Deployment Testing
1. Visit your production site
2. Open DevTools → Application → Service Workers
3. Verify SW is registered with correct scope
4. Test offline: switch to offline mode and verify offline.html loads
5. Check cache: verify assets are cached after first load

## 🔄 Updating the Service Worker

When you make changes to `sw.js`:

1. **Update cache version:**
```javascript
const CACHE_NAME = 'crypto-ai-cache-v2'; // Increment version
```

2. **The old cache will be automatically cleaned up** in the `activate` event

3. **Users will get the new SW** on their next visit, and it will activate after all tabs are closed

4. **To force immediate activation**, users can:
   - Close all tabs of your site and reopen
   - Or: DevTools → Application → Service Workers → "skipWaiting"

## 📚 Additional Resources

- [Service Worker API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Workbox (Google's SW library)](https://developers.google.com/web/tools/workbox)
- [Service Worker Lifecycle](https://developers.google.com/web/fundamentals/primers/service-workers/lifecycle)
- [Debugging Service Workers](https://developers.google.com/web/fundamentals/codelabs/debugging-service-workers)

## 🆘 Support

If you encounter Service Worker issues:

1. **Check the browser console** for `[SW]` prefixed logs
2. **Unregister the SW** using the script in `public/unregister-sw.js`
3. **Hard refresh** (Ctrl+F5 or Cmd+Shift+R)
4. **Clear browser cache** in DevTools → Application → Clear storage

Still having issues? Check:
- Are you testing in production mode? (`npm run preview` after `npm run build`)
- Is SW registered? (DevTools → Application → Service Workers)
- Any console errors?
- Network tab showing failed requests?

---

**Remember:** Service Workers are powerful but can be tricky. The defensive implementation in this project prevents the most common issues (fetch-fail storms, dev server conflicts, unhandled promise rejections).

Happy coding! 🚀
