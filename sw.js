const CACHE = 'cramit-v2';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/subjects/index.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS))
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

  // For GET requests — network first, fall back to cache
  e.respondWith(
    fetch(e.request)
      .then(res => {
        // Only cache same-origin successful responses
        if (res.ok && url.origin === self.location.origin) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});