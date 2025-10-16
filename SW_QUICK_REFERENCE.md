# Service Worker Quick Reference

> **TL;DR:** Service Worker only runs in production. It's disabled in dev mode to prevent conflicts with Vite HMR.

---

## 🚨 Emergency: Unregister SW Now

**Paste this in browser console (F12):**

```javascript
navigator.serviceWorker.getRegistrations().then(regs => {
  regs.forEach(r => r.unregister());
  console.log('✅ SW unregistered - now hard refresh (Ctrl+F5)');
});
```

---

## ✅ Quick Commands

| Action | Command |
|--------|---------|
| **Dev mode (no SW)** | `npm run dev` |
| **Build for production** | `npm run build` |
| **Test SW locally** | `npm run build && npm run preview` |
| **Unregister SW** | See emergency snippet above |
| **Check SW status** | DevTools (F12) → Application → Service Workers |

---

## 📍 File Locations

```
public/
├── sw.js              ← Main service worker
├── offline.html       ← Offline fallback page  
└── unregister-sw.js   ← Unregister utility

src/main.tsx           ← SW registration (PROD only)
```

---

## 🔍 How It Works

### Development Mode (`npm run dev`)
```
✅ Vite HMR works normally
✅ No SW interference
✅ Fast refresh enabled
❌ SW is NOT registered
```

### Production Mode (`npm run build`)
```
✅ SW registered and active
✅ Offline support enabled
✅ Assets cached
✅ Network-first strategy
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Failed to fetch" errors** | Unregister SW (see emergency snippet) |
| **Old SW cached** | DevTools → Service Workers → Unregister → Hard refresh |
| **HMR not working** | Make sure you're in dev mode (`npm run dev`) |
| **SW not registering in prod** | Check console for errors, verify you built the project |
| **Offline page not showing** | Check `public/offline.html` exists and is built |

---

## 🧪 Test Offline Behavior

1. Build: `npm run build && npm run preview`
2. Open DevTools (F12)
3. Network tab → Select "Offline"
4. Reload page → Should show offline.html

---

## 📊 Check What's Cached

**Paste in console:**

```javascript
caches.keys().then(console.log);
```

---

## 🔄 Update Service Worker

When you modify `sw.js`:

1. **Bump cache version:**
   ```javascript
   const CACHE_NAME = 'crypto-ai-cache-v2'; // Increment!
   ```

2. **Rebuild:**
   ```bash
   npm run build
   ```

3. **Users get update** on next visit (after closing all tabs)

---

## 🎯 Key Features

- ✅ **Production-only** - No dev conflicts
- ✅ **Defensive fetch handling** - Never crashes
- ✅ **Network-first** - Always tries fresh data
- ✅ **Cache fallback** - Works offline
- ✅ **Smart filtering** - Ignores Vite HMR paths
- ✅ **Proper error responses** - No unhandled promises

---

## 🚀 Pro Tips

1. **Always test SW in production mode** (`npm run preview` after build)
2. **Use "Update on reload"** in DevTools during SW development
3. **Hard refresh** (Ctrl+F5) to bypass cache when testing
4. **Check console** for `[SW]` prefixed logs
5. **Clear storage** in DevTools → Application → Clear storage for fresh start

---

## 📚 Full Guide

See `SERVICE_WORKER_GUIDE.md` for comprehensive documentation.

---

**Need help?** Check the console for `[SW]` logs or unregister the SW and start fresh!
