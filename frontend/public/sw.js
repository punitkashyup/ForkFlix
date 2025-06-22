const CACHE_NAME = 'forkflix-v1';
const STATIC_CACHE_NAME = 'forkflix-static-v1';
const API_CACHE_NAME = 'forkflix-api-v1';
const IMAGE_CACHE_NAME = 'forkflix-images-v1';

// Static assets to cache
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  // Add other static assets as needed
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/v1/recipes',
  '/api/v1/categories',
  '/api/v1/ingredients'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service worker installing...');
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        console.log('Caching static assets');
        return cache.addAll([
          '/',
          '/manifest.json',
          '/favicon.ico'
        ]);
      }),
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service worker activating...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && 
                cacheName !== STATIC_CACHE_NAME &&
                cacheName !== API_CACHE_NAME &&
                cacheName !== IMAGE_CACHE_NAME) {
              console.log('Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Take control of all pages
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin && !url.href.includes('api')) {
    return;
  }

  // Handle different types of requests
  if (request.method === 'GET') {
    if (isStaticAsset(request)) {
      // Cache first strategy for static assets
      event.respondWith(cacheFirstStrategy(request, STATIC_CACHE_NAME));
    } else if (isAPIRequest(request)) {
      // Network first strategy for API requests
      event.respondWith(networkFirstStrategy(request, API_CACHE_NAME));
    } else if (isImageRequest(request)) {
      // Cache first strategy for images
      event.respondWith(cacheFirstStrategy(request, IMAGE_CACHE_NAME));
    } else {
      // Default strategy for other requests
      event.respondWith(staleWhileRevalidateStrategy(request, CACHE_NAME));
    }
  }
});

// Background sync for recipe uploads
self.addEventListener('sync', (event) => {
  console.log('Background sync event:', event.tag);
  
  if (event.tag === 'recipe-upload') {
    event.waitUntil(
      syncRecipeUploads()
    );
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('Push event received:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'New recipe available!',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Recipe',
        icon: '/icon-192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icon-192.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('ForkFlix', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('Notification click received:', event);

  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/recipes')
    );
  }
});

// Helper functions

function isStaticAsset(request) {
  return request.url.includes('/static/') || 
         request.url.endsWith('.js') || 
         request.url.endsWith('.css') ||
         request.url.endsWith('.html') ||
         request.url.includes('manifest.json') ||
         request.url.includes('favicon.ico');
}

function isAPIRequest(request) {
  return request.url.includes('/api/');
}

function isImageRequest(request) {
  return request.destination === 'image' || 
         /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(request.url);
}

// Cache first strategy - good for static assets
async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('Cache hit for:', request.url);
      return cachedResponse;
    }
    
    console.log('Cache miss for:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Cache first strategy failed:', error);
    return new Response('Offline - Resource not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Network first strategy - good for API calls
async function networkFirstStrategy(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      console.log('Network response cached for:', request.url);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache for:', request.url);
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for API requests
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'This feature requires an internet connection'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Stale while revalidate strategy - good for frequently updated content
async function staleWhileRevalidateStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// Background sync for recipe uploads
async function syncRecipeUploads() {
  try {
    // Get pending uploads from IndexedDB or localStorage
    const pendingUploads = await getPendingUploads();
    
    for (const upload of pendingUploads) {
      try {
        const response = await fetch('/api/v1/recipes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(upload.data)
        });
        
        if (response.ok) {
          await removePendingUpload(upload.id);
          console.log('Recipe upload synced:', upload.id);
        }
      } catch (error) {
        console.error('Failed to sync recipe upload:', error);
      }
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Helper functions for background sync
async function getPendingUploads() {
  // In a real implementation, you'd get this from IndexedDB
  // For now, return empty array
  return [];
}

async function removePendingUpload(id) {
  // In a real implementation, you'd remove from IndexedDB
  console.log('Removing pending upload:', id);
}