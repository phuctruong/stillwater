'use strict';

const MERMAID_CACHE = 'stillwater-mermaid-v1';
const MERMAID_PATH_PREFIX = '/api/mermaid/';

self.addEventListener('install', event => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.startsWith(MERMAID_PATH_PREFIX)) return;

  event.respondWith(handleMermaidRequest(request));
});

async function handleMermaidRequest(request) {
  const cache = await caches.open(MERMAID_CACHE);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (_) {
    const cachedResponse = await cache.match(request);
    if (!cachedResponse) {
      return new Response(
        JSON.stringify({
          error: 'offline',
          detail: 'No cached diagram available.',
        }),
        {
          status: 503,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }

    try {
      const payload = await cachedResponse.clone().json();
      payload._sw_cached = true;
      return new Response(
        JSON.stringify(payload),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'X-Stillwater-Cache': 'HIT',
          },
        }
      );
    } catch (_) {
      return cachedResponse;
    }
  }
}
