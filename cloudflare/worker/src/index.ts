/**
 * Hookline Cloudflare Worker
 *
 * Routes:
 *   /api/*     → proxy to backend (Railway/Render)
 *   /oauth/*   → proxy to backend (OAuth callbacks)
 *   /webhook/* → proxy to backend (Twilio, GHL, Dynamics)
 *   /health    → simple liveness check
 *
 * The landing page + dashboard are deployed via CF Pages separately.
 */

interface Env {
  BACKEND_URL: string;
  ENVIRONMENT: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Health check
    if (path === "/health") {
      return new Response(JSON.stringify({
        status: "ok",
        environment: env.ENVIRONMENT,
        backend: env.BACKEND_URL,
        timestamp: new Date().toISOString(),
      }), {
        headers: { "content-type": "application/json" },
      });
    }

    // Proxy /api/* to backend
    if (path.startsWith("/api/") || path.startsWith("/oauth/") || path.startsWith("/webhook/")) {
      return proxyToBackend(request, env.BACKEND_URL);
    }

    // Otherwise, the Pages project handles it
    return new Response("Not Found", { status: 404 });
  },
};

async function proxyToBackend(request: Request, backendUrl: string): Promise<Response> {
  const url = new URL(request.url);
  const targetUrl = `${backendUrl}${url.pathname}${url.search}`;

  // Clone the request with the new URL
  const init: RequestInit = {
    method: request.method,
    headers: new Headers(request.headers),
    body: request.body,
    redirect: "manual",
  };

  // Remove host header — backend will set its own
  (init.headers as Headers).delete("host");

  try {
    const response = await fetch(targetUrl, init);
    // Clone response so we can modify headers
    const newHeaders = new Headers(response.headers);
    // Add CORS headers
    newHeaders.set("Access-Control-Allow-Origin", "*");
    newHeaders.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    newHeaders.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  } catch (err) {
    return new Response(JSON.stringify({
      error: "backend_unreachable",
      message: err instanceof Error ? err.message : String(err),
      backend: backendUrl,
    }), {
      status: 502,
      headers: { "content-type": "application/json" },
    });
  }
}

// Handle CORS preflight
async function handleOptions(): Promise<Response> {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400",
    },
  });
}