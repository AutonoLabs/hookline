"""OAuth callback endpoints for GHL and Dynamics 365."""
from __future__ import annotations

import urllib.parse

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.lib.log import get_logger
from app.models.integration import Integration

router = APIRouter(prefix="/oauth", tags=["oauth"])
logger = get_logger(__name__)


# ── GoHighLevel OAuth ──

@router.get("/ghl/start")
async def ghl_oauth_start(tenant_id: str, state: str = ""):
    """Redirect user to GHL OAuth consent screen."""
    params = {
        "response_type": "code",
        "client_id": settings.ghl_client_id,
        "redirect_uri": settings.ghl_redirect_uri,
        "scope": "contacts.write contacts.read users.write users.read",
        "state": state or tenant_id,
    }
    url = f"{settings.ghl_oauth_base}/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/ghl/callback")
async def ghl_oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle GHL OAuth code exchange + store tokens."""
    if error:
        logger.error("GHL OAuth error: %s", error)
        return {"status": "error", "detail": error}

    if not code:
        return {"status": "error", "detail": "No authorization code received"}

    tenant_id = state or "default"

    from app.integrations.ghl import GHLIntegration

    integration = await GHLIntegration.exchange_code(db, tenant_id, code)
    logger.info("GHL integration connected for tenant %s", tenant_id)
    return {"status": "ok", "tenant_id": tenant_id, "integration_id": integration.id}


# ── Dynamics 365 OAuth ──

@router.get("/dynamics/start")
async def dynamics_oauth_start(tenant_id: str, state: str = ""):
    """Redirect user to Azure AD OAuth consent screen."""
    params = {
        "response_type": "code",
        "client_id": settings.dynamics_client_id,
        "redirect_uri": settings.dynamics_redirect_uri,
        "scope": settings.dynamics_scope,
        "state": state or tenant_id,
        "response_mode": "query",
    }
    url = f"{settings.dynamics_oauth_base}/{settings.dynamics_tenant_id}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/dynamics/callback")
async def dynamics_oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle Dynamics 365 OAuth code exchange + store tokens."""
    if error:
        logger.error("Dynamics OAuth error: %s", error)
        return {"status": "error", "detail": error}

    if not code:
        return {"status": "error", "detail": "No authorization code received"}

    tenant_id = state or "default"

    from app.integrations.dynamics import DynamicsIntegration

    integration = await DynamicsIntegration.exchange_code(db, tenant_id, code)
    logger.info("Dynamics integration connected for tenant %s", tenant_id)
    return {"status": "ok", "tenant_id": tenant_id, "integration_id": integration.id}
