// Service Worker for ForkFlix
// This is a basic service worker placeholder

self.addEventListener('install', (event) => {
  console.log('Service Worker: Installed');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activated');
});

self.addEventListener('fetch', (event) => {
  // For now, just let all requests pass through
  event.respondWith(fetch(event.request));
});