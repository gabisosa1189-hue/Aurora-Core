const CACHE_NAME = 'aurora-cache-v5'; // Subimos a v5 para forzar limpieza

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(keys.map(key => {
        // Borramos absolutamente todas las cachés viejas
        return caches.delete(key);
      }));
    })
  );
  return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // No cacheamos nada por ahora para poder debuguear la barra negra
  // Dejamos que todo pase directo al servidor
  return; 
});
