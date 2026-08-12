# Hookline — Architecture (DRAFT)

**Status:** DRAFT. Author: Herschel (Hershel's review of the Yapper Care → Hookline derivative positioning).

**Goal:** Define what Hookline IS, what it's NOT, and what stack it should ship with.

---

## What Hookline is

A programmable voice companion platform. Customers wire their data (CRM, EHR-adjacent, support system) and get:
- An always-on AI voice companion for end users (caregivers, family, etc. — non-clinical positioning)
- Programmatic APIs (REST + WebSocket) for integration
- A simple dashboard for ops + monitoring
- Billing + plan tier management

## What Hookline is NOT

- ❌ NOT a clinical device (no FDA / TGA / CE marking claims)
- ❌ NOT a Yapper rebrand (different product, different name, different positioning)
- ❌ NOT a research project (commercial-grade from day one)
- ❌ NOT a full LMS / EHR (just the companion + integration layer)

## Stack (proposed)

### Backend (Python)

- **FastAPI** — REST + WebSocket
- **Postgres** — primary store
- **Redis** — session state + pub/sub
- **MinIO/S3** — audio + transcript storage
- **Pipecat** — voice pipeline (STT → LLM → TTS)
- **Alembic** — migrations
- **Docker Compose** — local dev

### Frontend (TypeScript)

- **Next.js** — dashboard
- **Tailwind CSS** — styling
- **Radix UI** — primitives
- **Vercel** — hosting

### Voice providers (one of, by region)

- **Twilio** — telephony
- **Daily** — WebRTC
- **LiveKit** — WebRTC alternative
- **VAPI / Retell / Dograh / Bland** — managed AI voice

### LLM providers

- **OpenAI / Anthropic / Gemini** — primary
- **Local ollama** — privacy mode (optional)

## Product surface (proposed)

```
hookline.io/
├── /api/v1/         REST API (companion lifecycle, billing, accounts)
├── /ws/             WebSocket (live voice sessions)
├── /dashboard/      Customer admin UI
├── /docs/           API docs (OpenAPI auto-generated)
└── /sdk/            TypeScript + Python SDKs
```

## Phases

- **Phase 0** (now) — scaffold + architecture
- **Phase 1** — voice pipeline (Twilio + OpenAI Realtime)
- **Phase 2** — dashboard + billing (Stripe)
- **Phase 3** — CRM integrations (HubSpot, Salesforce, Zoho)
- **Phase 4** — partner portal + marketplace

## Differentiation vs Yapper

| Aspect | Yapper Care | Hookline |
|---|---|---|
| Positioning | Caregiver copilot | Voice companion platform |
| Brand | yapper.care (trademark) | hookline.io (NEW) |
| Customers | Caregivers, families | Developers, integrators |
| Distribution | Direct sales | API-first, self-serve |
| Voice provider | Pipecat + Daily + Hume | Pipecat + Twilio (managed) |
| Stance on clinical | Anti (caregiver only) | Anti (wellness only) |

## What we keep from Yapper (inspiration only)

- **Voice pipeline architecture** — pipecat-based, STT → LLM → TTS
- **Companion persistence model** — session memory, voice profile
- **Dashboard conventions** — simple, ops-first
- **Webhook/event design** — extensibility for integrations

## What we DON'T take

- ❌ Brand assets (logos, colors, fonts)
- ❌ Customer lists / contracts
- ❌ Caregiver positioning / clinical language
- ❌ Specific facility contracts
- ❌ Trademark strings ("YAPPER", "yapper.care", etc.)

## Open architectural questions

1. **Multi-tenancy model** — single-tenant vs multi-tenant vs hybrid?
2. **Voice provider abstraction** — direct Twilio integration or managed VAPI/Bland layer?
3. **Audio storage** — own (S3/MinIO) or rely on provider's storage?
4. **Billing** — Stripe? Self-hosted? Custom?
5. **Auth** — own (NextAuth) or Auth0/Clerk?

See `docs/architecture-decisions.md` (pending) for the decision log.