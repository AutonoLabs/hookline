"""Pydantic schemas for Call records."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class CallOut(BaseModel):
    id: str
    tenant_id: str
    contact_id: str | None = None
    status: str
    duration_sec: int | None = None
    transcript: str | None = None
    summary: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
