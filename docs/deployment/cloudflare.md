# Hookline Cloudflare Deployment

**Goal:** Deploy the Hookline MVP to `hookline.autonolabs.ai`.

## Architecture

```
hookline.autonolabs.ai/
├── /             → CF Pages (landing page from frontend/landing.html)
├── /dashboard    → CF Pages (dashboard SPA)
├── /api/*        → CF Worker → backend (Railway)
├── /oauth/*      → CF Worker → backend (GHL + Dynamics callbacks)
└── /webhook/*    → CF Worker → backend (Twilio, GHL, Dynamics)
```

## Prerequisites

1. **Cloudflare account** with Editor access to `autonolabs.ai` zone
2. **CF API token** with:
   - `Zone:DNS:Edit` (for `hookline` A/CNAME record)
   - `Account:Cloudflare Pages:Edit` (for Pages project)
   - `Account:Workers Scripts:Edit` (for Worker deploy)
3. **Railway account** (or Render) for the backend
4. **Postgres host** (Neon free tier works)
5. **GHL Marketplace app credentials** (or skip GHL integration for v0)
6. **Dynamics 365 Azure AD app** (or skip Dynamics integration for v0)
7. **Twilio + OpenAI + Daily keys** (or skip voice for v0)

## Step 1: CF API token

Go to https://dash.cloudflare.com/profile/api-tokens → Create Token → Custom Token.

Add permissions:
- `Zone:DNS:Edit` (for `autonolabs.ai`)
- `Account:Cloudflare Pages:Edit`
- `Account:Workers Scripts:Edit`

Restrict to zone: `autonolabs.ai`.

Save the token to Bitwarden as item "Hookline Cloudflare Token".

## Step 2: Authenticate wrangler

```bash
export CLOUDFLARE_API_TOKEN=***
wrangler login
```

Or use API token directly:
```bash
export CLOUDFLARE_API_TOKEN=***
wrangler whoami
```

## Step 3: Get the zone ID for autonolabs.ai

```bash
wrangler zones list --name autonolabs.ai
```

Update `wrangler.toml`:
```toml
[[routes]]
pattern = "hookline.autonolabs.ai/api/*"
zone_id = "<zone-id-from-step-3>"
```

## Step 4: Deploy the Worker

```bash
cd cloudflare/worker
npm install
wrangler deploy
```

Output: `Published hookline (X.XX sec)` + URL.

## Step 5: Create Pages project + deploy landing

```bash
wrangler pages project create hookline-landing --production-branch=main
wrangler pages deploy ../../frontend/landing.html --project-name=hookline-landing
```

Output: Pages URL `https://hookline-landing.pages.dev`.

## Step 6: Add custom domain to Pages project

```bash
wrangler pages domain add hookline.autonolabs.ai --project-name=hookline-landing
```

This creates a CNAME record automatically.

## Step 7: Deploy backend to Railway

```bash
# Install Railway CLI
brew install railway

# Login
railway login

# Init + deploy
cd backend
railway init
railway up
```

## Step 8: Wire backend URL to Worker

```bash
wrangler secret put BACKEND_URL
# Enter: https://hookline-backend-production.up.railway.app
```

Re-deploy:
```bash
wrangler deploy
```

## Step 9: Test

```bash
# Health check
curl https://hookline.autonolabs.ai/health

# API
curl https://hookline.autonolabs.ai/api/companions
```

## DNS records

CF should auto-create:
- `hookline.autonolabs.ai` → CNAME to `hookline-landing.pages.dev` (Pages)
- For Worker route, CF uses the `routes` config in `wrangler.toml`

If Pages + Worker routing conflict, use `_worker.js` in Pages to redirect `/api/*` to the Worker.

## Smoke test checklist

- [ ] `curl https://hookline.autonolabs.ai/` returns landing page HTML
- [ ] `curl https://hookline.autonolabs.ai/health` returns `{"status":"ok",...}`
- [ ] `curl https://hookline.autonolabs.ai/api/companions` returns 200 (or 401 if auth required)
- [ ] OAuth callback URLs configured in GHL Marketplace app point to `https://hookline.autonolabs.ai/oauth/ghl/callback`
- [ ] OAuth callback URLs configured in Azure AD app point to `https://hookline.autonolabs.ai/oauth/dynamics/callback`

## Troubleshooting

- **"Worker not found"** — check the route + zone ID
- **"Backend unreachable"** — check Railway logs + `BACKEND_URL` env var
- **CORS errors** — Worker adds `Access-Control-Allow-Origin: *` by default, tighten if needed
- **DNS not resolving** — wait 1-2 minutes for CF DNS propagation

## Vault

- This file: `autonobrain/30 - Resources/Hookline/hookline-deployment-guide-2026-08-13.md`
- Mirror in repo: `/Users/elibernstein/Code/hookline/docs/deployment/cloudflare.md`