"""Pydantic schemas for Contact CRUD."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


class ContactCreate(ContactBase):
    tenant_id: str
    external_id: str
    source: str  # 'ghl' | 'dynamics'


class ContactOut(ContactBase):
    id: str
    tenant_id: str
    external_id: str
    source: str
    last_synced_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncRequest(BaseModel):
    tenant_id: str
    provider: str = Field(..., pattern="^(ghl|dynamics)$")
