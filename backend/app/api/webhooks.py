"""Webhook receivers for GHL, Dynamics, and Twilio."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.lib.log import get_logger
from app.models.webhook import WebhookEvent

router = APIRouter(prefix="/webhook", tags=["webhooks"])
logger = get_logger(__name__)


# ── GoHighLevel Webhook ──
# GHL sends a signature header: 'X-Highlevel-Signature' (or key + token query param for older setups).
# Ref: https://highlevel.stoplight.io/docs/integrations/044b15d6bd2df-webhooks (2025-01)

@router.post("/ghl")
async def ghl_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive GHL webhook events. Verifies the hash signature if a secret is configured."""
    body = await request.body()
    payload = json.loads(body) if body else {}

    # GHL webhook signature verification
    # The hash is sent as 'X-Highlevel-Signature' header (HMAC-SHA256 of the body with the webhook secret).
    signature = request.headers.get("X-Highlevel-Signature", "")
    if settings.ghl_client_secret and signature:
        import hashlib
        import hmac
        expected = hmac.new(
            settings.ghl_client_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(401, "Invalid GHL webhook signature")

    event_type = payload.get("type", "unknown")
    tenant_id = payload.get("locationId", "")

    event = WebhookEvent(
        tenant_id=tenant_id,
        source="ghl",
        event_type=event_type,
        payload=json.dumps(payload),
        processed_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()

    # If a contact was created, trigger sync
    if "Contact" in event_type:
        logger.info("GHL contact event: %s — sync recommended for tenant %s", event_type, tenant_id)

    return {"status": "received", "event_id": event.id}


# ── Dynamics 365 Webhook ──
# Dynamics uses signed notification endpoints via Azure Service Bus or HTTP.
# Ref: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-webhooks (2025-01)

@router.post("/dynamics")
async def dynamics_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive Dynamics 365 webhook events (via Dataverse webhooks)."""
    body = await request.body()
    payload = json.loads(body) if body else {}

    # Dynamics sends a validation token on subscription creation
    # Ref: https://learn.microsoft.com/en-us/azure/event-grid/webhook-event-delivery (2025-01)
    validation_code = None
    if isinstance(payload, list):
        for item in payload:
            if item.get("eventType") == "Microsoft.EventGrid.SubscriptionValidation":
                validation_code = item.get("data", {}).get("validationCode")
                break

    event_type = payload.get("MessageName", payload.get("eventType", "unknown")) if not isinstance(payload, list) else "batch"
    tenant_id = payload.get("OrganizationId", payload.get("tenantId", "")) if not isinstance(payload, list) else ""

    event = WebhookEvent(
        tenant_id=str(tenant_id) if tenant_id else None,
        source="dynamics",
        event_type=str(event_type),
        payload=json.dumps(payload),
        processed_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()

    # If validation handshake, respond with the code
    if validation_code:
        return {"validationResponse": validation_code}

    logger.info("Dynamics webhook received: %s", event_type)
    return {"status": "received", "event_id": event.id}


# ── Twilio Voice Webhook ──
# Ref: https://www.twilio.com/docs/voice/webhooks (2025-01)

@router.post("/twilio")
async def twilio_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Receive Twilio voice webhook events."""
    from app.lib.auth import decrypt_token
    from app.voice.twilio_webhook import handle_twilio_webhook

    result = await handle_twilio_webhook(request, db)
    return result
