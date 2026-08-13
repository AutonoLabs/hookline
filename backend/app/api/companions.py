"""Companion CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.lib.auth import require_api_key
from app.models.companion import Companion
from app.schemas.companion import CompanionCreate, CompanionOut, CompanionUpdate

router = APIRouter(prefix="/companions", tags=["companions"])


@router.get("", response_model=list[CompanionOut])
async def list_companions(
    tenant_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_api_key),
):
    result = await db.execute(select(Companion).where(Companion.tenant_id == tenant_id))
    return result.scalars().all()


@router.post("", response_model=CompanionOut, status_code=201)
async def create_companion(body: CompanionCreate, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    companion = Companion(**body.model_dump())
    db.add(companion)
    await db.commit()
    await db.refresh(companion)
    return companion


@router.get("/{companion_id}", response_model=CompanionOut)
async def get_companion(companion_id: str, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    companion = await db.get(Companion, companion_id)
    if not companion:
        raise HTTPException(404, "Companion not found")
    return companion


@router.patch("/{companion_id}", response_model=CompanionOut)
async def update_companion(companion_id: str, body: CompanionUpdate, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    companion = await db.get(Companion, companion_id)
    if not companion:
        raise HTTPException(404, "Companion not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(companion, k, v)
    await db.commit()
    await db.refresh(companion)
    return companion


@router.delete("/{companion_id}", status_code=204)
async def delete_companion(companion_id: str, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    companion = await db.get(Companion, companion_id)
    if not companion:
        raise HTTPException(404, "Companion not found")
    await db.delete(companion)
    await db.commit()
