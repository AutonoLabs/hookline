"""Voice pipeline — abstract + stub implementation.

v0 uses StubVoicePipeline (canned responses).
v0.2 will implement real Pipecat + Twilio + Daily integration.
ponytail: Real pipeline ceiling is Pipecat + Daily.co + Twilio.
          Add when voice calls need to actually connect.
"""
from __future__ import annotations

import abc
import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.lib.log import get_logger

logger = get_logger(__name__)


class VoicePipeline(abc.ABC):
    """Abstract voice pipeline interface."""

    @abc.abstractmethod
    async def start_call(self, contact_id: str, companion_id: str, tenant_id: str) -> dict:
        ...

    @abc.abstractmethod
    async def end_call(self, call_id: str) -> dict:
        ...


class StubVoicePipeline(VoicePipeline):
    """Stub pipeline that logs calls and returns canned data — for v0 testing."""

    async def start_call(self, contact_id: str, companion_id: str, tenant_id: str) -> dict:
        logger.info("STUB CALL START: contact=%s companion=%s tenant=%s", contact_id, companion_id, tenant_id)
        return {
            "call_id": f"stub-{datetime.now(timezone.utc).isoformat()}",
            "status": "initiated",
            "message": "Stub pipeline — no real voice connection established.",
        }

    async def end_call(self, call_id: str) -> dict:
        logger.info("STUB CALL END: call_id=%s", call_id)
        return {
            "call_id": call_id,
            "status": "completed",
            "duration_sec": 60,
            "transcript": "[Stub transcript] Hello! This is a test call from your Hookline companion.",
            "summary": "Test call completed successfully (stub).",
        }


# Singleton stub instance
stub_pipeline = StubVoicePipeline()
