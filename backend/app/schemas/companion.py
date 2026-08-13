"""Pydantic schemas for Companion CRUD."""
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CompanionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    voice_id: str | None = None
    system_prompt: str | None = None


class CompanionCreate(CompanionBase):
    tenant_id: str = Field(..., min_length=1)


class CompanionUpdate(BaseModel):
    name: str | None = None
    voice_id: str | None = None
    system_prompt: str | None = None


class CompanionOut(CompanionBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
