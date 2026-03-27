const CACHE_NAME = 'aurora-cache-v2';

// Instala el nuevo Service Worker y se activa inmediatamente
self.addEventListener('install', (e) => {
  self.skipWaiting();
});

// Borra cualquier memoria caché vieja que haya quedado
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

// Le dice al navegador: "Buscá SIEMPRE en internet primero. Si no hay internet, recién ahí usá la memoria"
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
