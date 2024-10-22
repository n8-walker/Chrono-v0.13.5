const CACHE_NAME = 'offline-cache-v1';
const OFFLINE_URL = '/dashboard/no_internet'; // Change to your offline page

// Install the service worker and cache the offline page
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll([OFFLINE_URL]);
        })
    );
});

// Fetch event to serve cached content when offline
self.addEventListener('fetch', event => {
    if (event.request.mode === 'navigate') {
        // Respond with the offline page for all navigation requests
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(OFFLINE_URL);
            })
        );
    }
});
