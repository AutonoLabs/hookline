# Hookline Backend

FastAPI + SQLAlchemy async + Alembic + PostgreSQL.

## Quick start

```bash
# 1. Copy env
cp .env.example .env

# 2. Install deps
uv sync

# 3. Run migrations
uv run alembic upgrade head

# 4. Start dev server
uv run uvicorn app.main:app --reload --port 8000
```

API docs at http://localhost:8000/docs

## Docker

```bash
docker compose up --build
```

## Structure

- `app/` — FastAPI application
  - `models/` — SQLAlchemy ORM models
  - `schemas/` — Pydantic request/response schemas
  - `api/` — API route handlers
  - `integrations/` — CRM integrations (GHL, Dynamics)
  - `voice/` — Voice pipeline (stub in v0)
  - `lib/` — Auth, logging
- `alembic/` — Database migrations

## Integrations

- **GoHighLevel**: OAuth2 at `/oauth/ghl/start`, contacts sync, webhooks at `/webhook/ghl`
- **Dynamics 365**: OAuth2 at `/oauth/dynamics/start`, contacts/leads sync, webhooks at `/webhook/dynamics`
- **Twilio**: Voice webhooks at `/webhook/twilio`
