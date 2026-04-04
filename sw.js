const CACHE = 'cramit-v3';

// Only cache static assets — NEVER index.html
const STATIC_ASSETS = [
  '/manifest.json',
  '/subjects/index.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Never intercept POST requests or Netlify function calls
  if (e.request.method !== 'GET') return;
  if (url.pathname.startsWith('/.netlify/')) return;
  if (url.pathname.startsWith('/api/')) return;

  // Never cache index.html — always fetch fresh so auth state is correct
  if (url.pathname === '/' || url.pathname === '/index.html') {
    e.respondWith(fetch(e.request));
    return;
  }

  // For other static assets — cache first, fall back to network
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        if (res.ok && url.origin === self.location.origin) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      });
    })
  );
});
