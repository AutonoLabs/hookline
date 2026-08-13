"""Call list + detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.lib.auth import require_api_key
from app.models.call import Call
from app.schemas.call import CallOut

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("", response_model=list[CallOut])
async def list_calls(
    tenant_id: str = Query(...),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_api_key),
):
    result = await db.execute(
        select(Call).where(Call.tenant_id == tenant_id).limit(limit).offset(offset)
    )
    return result.scalars().all()


@router.get("/{call_id}", response_model=CallOut)
async def get_call(call_id: str, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    call = await db.get(Call, call_id)
    if not call:
        raise HTTPException(404, "Call not found")
    return call
