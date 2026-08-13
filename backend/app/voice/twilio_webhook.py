"""Twilio voice webhook handler.

Ref: https://www.twilio.com/docs/voice/webhooks (checked 2025-08-13)
Twilio sends form-encoded data with fields: CallSid, From, To, CallStatus, etc.
Signature validation: X-Twilio-Signature header (HMAC-SHA256 of URL + params).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.lib.log import get_logger
from app.models.call import Call

logger = get_logger(__name__)


def _validate_twilio_signature(request: Request, body: bytes) -> bool:
    """Validate the X-Twilio-Signature header.

    Twilio computes: HMAC-SHA256(AUTH_TOKEN, url + sorted_params)
    Ref: https://www.twilio.com/docs/usage/webhooks/webhooks-security (checked 2025-08-13)
    """
    if not settings.twilio_auth_token:
        logger.warning("TWILIO_AUTH_TOKEN not set — skipping signature validation")
        return True

    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False

    import hashlib
    import hmac
    import urllib.parse

    # Reconstruct the URL Twilio called
    url = str(request.url)
    if settings.is_dev:
        url = url.replace("localhost", "127.0.0.1")

    # Parse form params
    params = urllib.parse.parse_qs(body.decode())

    # Twilio sorts params by key, concatenates key+value
    sorted_str = url
    for key in sorted(params.keys()):
        sorted_str += key + (params[key][0] if params[key] else "")

    expected = hmac.new(
        settings.twilio_auth_token.encode(),
        sorted_str.encode(),
        hashlib.sha256,
    ).digest()

    import base64
    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(signature, expected_b64)


async def handle_twilio_webhook(request: Request, db: AsyncSession) -> dict:
    """Handle an inbound Twilio voice webhook. Returns TwiML-like JSON response."""
    body = await request.body()

    # Validate signature
    if not _validate_twilio_signature(request, body):
        logger.error("Invalid Twilio signature")
        return {"error": "Invalid signature"}, 401

    # Parse form data
    import urllib.parse
    params = dict(urllib.parse.parse_qsl(body.decode()))

    call_sid = params.get("CallSid", "")
    call_status = params.get("CallStatus", "unknown")
    from_number = params.get("From", "")
    to_number = params.get("To", "")

    # Log the call
    call = Call(
        tenant_id=params.get("tenant_id", "default"),
        status=call_status,
        started_at=datetime.now(timezone.utc) if call_status == "ringing" else None,
        ended_at=datetime.now(timezone.utc) if call_status in ("completed", "failed") else None,
        transcript=None,
    )
    db.add(call)
    await db.commit()

    logger.info("Twilio webhook: sid=%s status=%s from=%s", call_sid, call_status, from_number)

    # Return a simple TwiML response for the call
    # In v0.2 this would <Connect> to a Daily.co/Pipecat room
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Hello, this is your Hookline companion. Voice connection will be available soon.</Say>
    <Pause length="2"/>
    <Hangup/>
</Response>"""

    from fastapi import Response
    return Response(content=twiml, media_type="text/xml")
