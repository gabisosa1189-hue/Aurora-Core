const CACHE_NAME = 'aurora-v2-limpio';

self.addEventListener('install', (e) => {
    self.skipWaiting(); // Obliga a instalar la nueva versión al instante
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key); // Borra la memoria vieja y rota
                }
            }));
        })
    );
    return self.clients.claim();
});

self.addEventListener('fetch', (e) => {
    // Siempre busca en internet primero, si no hay internet, usa el caché
    e.respondWith(
        fetch(e.request).catch(() => caches.match(e.request))
    );
});
