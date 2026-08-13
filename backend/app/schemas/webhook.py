"""Pydantic schemas for webhook events."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel


class WebhookOut(BaseModel):
    id: str
    source: str
    event_type: str | None = None
    processed_at: datetime | None = None
    error: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
