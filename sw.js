const CACHE_NAME = 'aurora-cache-v3'; // Subimos a V3 para que se entere del cambio

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // 🚨 LA LLAVE MÁGICA: Si es el video .mp4 o pide transmisión en vivo (range), el guardián lo deja pasar libremente.
  if (e.request.url.endsWith('.mp4') || e.request.headers.has('range')) {
    return; // Esto hace que tu celular cargue el video naturalmente sin bloqueos
  }

  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
