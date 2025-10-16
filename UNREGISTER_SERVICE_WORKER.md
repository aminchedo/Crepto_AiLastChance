# 🚨 Service Worker Quick Unregister Guide

## Immediate Fix (Run in DevTools Console)

If you're experiencing Service Worker fetch failures right now, run this in your browser's DevTools Console (F12):

```javascript
navigator.serviceWorker.getRegistrations()
  .then(regs => {
    regs.forEach(r => {
      console.log('Unregistering', r.scope);
      r.unregister();
    });
  })
  .catch(e => console.error(e));
```

Then **hard refresh** the page (Ctrl+F5 or Cmd+Shift+R).

## Alternative Methods

### Method 1: Use the Built-in Utility

Load the unregister script in your console:

```javascript
// Option A: Run the full script from public/unregister-sw.js
// Copy the contents of public/unregister-sw.js and paste into console

// Option B: Use the quick function
await window.unregisterSW();
```

### Method 2: DevTools UI

1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Service Workers** in the left sidebar
4. Click **Unregister** next to each registered worker
5. Optionally clear **Cache Storage** from the left sidebar
6. Hard refresh (Ctrl+F5)

## Verify It Worked

After unregistering:
1. Check DevTools Console - the fetch errors should stop
2. Check DevTools → Application → Service Workers - should show "No service workers found"
3. Reload the page normally

## Why This Happened

Service Workers persist across page reloads. If a SW was registered during development before the production-only guard was added, it continues to intercept requests even after the code changes.

## Current Protection

Your app now has these safeguards:

✅ **Production-only registration** (in `src/main.tsx`)
- Service Worker only registers when `import.meta.env.PROD === true`
- In development (Vite dev server), SW is skipped entirely

✅ **Defensive fetch handler** (in `public/sw.js`)
- Ignores Vite HMR paths (/@vite, __vite_ping, etc.)
- Catches all fetch errors and returns proper responses
- Never leaves unhandled promise rejections

✅ **Unregister utility** (in `public/unregister-sw.js`)
- Quick cleanup script for emergencies

## Prevention

To prevent this in the future:
1. Always develop with the production-only guard enabled (already done)
2. If you manually register a SW for testing, unregister it when done
3. Use Incognito/Private mode for SW testing (starts fresh each time)

## Still Having Issues?

If errors persist after unregistering:
1. Close all tabs of the app
2. Clear browser cache completely
3. Reopen the app
4. Check Network tab for actual source of errors (might not be SW-related)
