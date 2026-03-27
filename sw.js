const CACHE_NAME = 'aurora-cache-v4';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) return caches.delete(key);
      }));
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // 🚨 REGLA DE ORO: Si es un video, NO lo cachees. Dejalo pasar libre.
  if (e.request.url.includes('.mp4')) {
    return; 
  }

  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
