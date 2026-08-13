"""Contact CRUD + sync endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.lib.auth import require_api_key
from app.lib.log import get_logger
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactOut, SyncRequest

router = APIRouter(prefix="/contacts", tags=["contacts"])
logger = get_logger(__name__)


@router.get("", response_model=list[ContactOut])
async def list_contacts(
    tenant_id: str = Query(...),
    source: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _key: str = Depends(require_api_key),
):
    stmt = select(Contact).where(Contact.tenant_id == tenant_id)
    if source:
        stmt = stmt.where(Contact.source == source)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{contact_id}", response_model=ContactOut)
async def get_contact(contact_id: str, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(404, "Contact not found")
    return contact


@router.post("/sync", status_code=202)
async def trigger_sync(body: SyncRequest, db: AsyncSession = Depends(get_db), _key: str = Depends(require_api_key)):
    """Trigger a CRM contact sync. Returns 202 Accepted; sync runs in background."""
    from app.integrations.ghl import GHLIntegration
    from app.integrations.dynamics import DynamicsIntegration

    # Find the active integration
    from app.models.integration import Integration
    result = await db.execute(
        select(Integration).where(
            Integration.tenant_id == body.tenant_id,
            Integration.provider == body.provider,
        )
    )
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(404, f"No active {body.provider} integration for tenant")

    # ponytail: real sync runs as a background task in production (Celery / arq).
    # For v0 we do an inline sync — acceptable for small contact sets.
    if body.provider == "ghl":
        ghl = GHLIntegration(integration)
        synced = await ghl.sync_contacts(db)
    elif body.provider == "dynamics":
        dyn = DynamicsIntegration(integration)
        synced = await dyn.sync_contacts(db)
    else:
        raise HTTPException(400, f"Unknown provider: {body.provider}")

    return {"status": "ok", "synced": synced}
