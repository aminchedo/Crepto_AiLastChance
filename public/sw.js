const CACHE_NAME = 'crypto-ai-cache-v1';
const OFFLINE_URL = '/offline.html';

// Assets to cache on install
const PRECACHE_ASSETS = [
  OFFLINE_URL,
  '/',
  '/index.html',
];

self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('[SW] Failed to cache some assets during install:', err);
        // Don't fail the install if precaching fails - better to have a SW than none
      });
    })
  );
  // Skip waiting to activate immediately
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    // Clean up old caches
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  const request = event.request;
  const url = new URL(request.url);

  // Don't let SW handle dev server magic paths (Vite HMR, websockets, etc.)
  const devPaths = [
    '/@vite',
    '/@fs',
    '/__vite',
    '__vite_ping',
    '/__webpack_hmr',
    '/node_modules',
    '/sockjs-node',
    '/@react-refresh',
    '/ws',
    '/websocket'
  ];
  
  if (devPaths.some(path => url.pathname.includes(path))) {
    console.log('[SW] Skipping dev path:', url.pathname);
    return;
  }

  // Don't cache cross-origin requests (unless explicitly whitelisted)
  if (url.origin !== location.origin) {
    // You can add whitelisted origins here if needed
    const allowedOrigins = [
      // 'https://api.example.com'
    ];
    
    if (!allowedOrigins.includes(url.origin)) {
      return;
    }
  }

  event.respondWith((async () => {
    try {
      // Network-first strategy for API calls
      if (url.pathname.startsWith('/api/')) {
        try {
          const networkResponse = await fetch(request);
          
          // Only cache successful responses
          if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            // Clone the response before caching
            cache.put(request, networkResponse.clone()).catch(err => {
              console.warn('[SW] Failed to cache API response:', err);
            });
          }
          
          return networkResponse;
        } catch (networkError) {
          console.warn('[SW] API fetch failed, trying cache:', request.url, networkError);
          
          // Try to serve from cache if network fails
          const cached = await caches.match(request);
          if (cached) {
            console.log('[SW] Serving API response from cache');
            return cached;
          }
          
          // Return error response for API calls
          return new Response(
            JSON.stringify({ 
              error: 'Network error occurred', 
              offline: true,
              message: 'Unable to reach server. Please check your connection.'
            }),
            {
              status: 503,
              statusText: 'Service Unavailable',
              headers: {
                'Content-Type': 'application/json',
                'X-Offline-Response': 'true'
              }
            }
          );
        }
      }

      // For non-API requests: Try network first, fall back to cache
      try {
        const networkResponse = await fetch(request);
        
        // Cache successful responses for static assets
        if (networkResponse.ok && (
          url.pathname.endsWith('.js') ||
          url.pathname.endsWith('.css') ||
          url.pathname.endsWith('.png') ||
          url.pathname.endsWith('.jpg') ||
          url.pathname.endsWith('.svg') ||
          url.pathname.endsWith('.woff') ||
          url.pathname.endsWith('.woff2')
        )) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(request, networkResponse.clone()).catch(err => {
            console.warn('[SW] Failed to cache asset:', err);
          });
        }
        
        return networkResponse;
      } catch (err) {
        // Network failed - try cache
        console.warn('[SW] Network fetch failed for', request.url, err);
        
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(request);
        
        if (cached) {
          console.log('[SW] Serving from cache:', request.url);
          return cached;
        }

        // If this is a navigation request (HTML page), return offline page
        if (request.mode === 'navigate' || 
            (request.headers && request.headers.get('accept')?.includes('text/html'))) {
          console.log('[SW] Serving offline page for navigation');
          const offlineResp = await cache.match(OFFLINE_URL);
          if (offlineResp) {
            return offlineResp;
          }
        }

        // Last resort: return a basic error response
        // This prevents unhandled promise rejections
        return new Response(
          'Network error occurred. Please check your connection and try again.',
          {
            status: 504,
            statusText: 'Gateway Timeout',
            headers: {
              'Content-Type': 'text/plain',
              'X-Offline-Response': 'true'
            }
          }
        );
      }
    } catch (err) {
      // Catch any unexpected errors to prevent SW from breaking
      console.error('[SW] Unexpected error in fetch handler:', err);
      return new Response(
        'An unexpected error occurred in the service worker.',
        {
          status: 500,
          statusText: 'Internal Server Error',
          headers: { 'Content-Type': 'text/plain' }
        }
      );
    }
  })());
});

// Listen for messages from the client
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME).then(cache => {
        return cache.addAll(event.data.urls).catch(err => {
          console.warn('[SW] Failed to cache URLs:', err);
        });
      })
    );
  }
});

console.log('[SW] Service worker script loaded');
