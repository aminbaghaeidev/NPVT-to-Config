const CACHE = "npvt-v2";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) =>
  e.waitUntil(
    caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim())
  )
);

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const sameOrigin = new URL(e.request.url).origin === self.location.origin;

  e.respondWith(
    caches.open(CACHE).then(async (cache) => {
      if (sameOrigin) {
        try {
          const res = await fetch(e.request, { cache: "no-cache" });
          if (res.ok) cache.put(e.request, res.clone());
          return res;
        } catch {
          return(await cache.match(e.request)) || Response.error();
        }
      }

      const hit = await cache.match(e.request);
      if (hit) return hit;
      const res = await fetch(e.request);
      if (res.ok) cache.put(e.request, res.clone());
      return res;
    })
  );
});
