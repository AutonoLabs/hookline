"""GoHighLevel CRM integration.

API docs: https://highlevel.stoplight.io/docs/integrations/ (checked 2025-08-13)
OAuth flow: https://marketplace.leadconnectorhq.com/oauth/authorize
Token endpoint: https://marketplace.leadconnectorhq.com/oauth/token
Contacts API: GET /contacts (paginated)
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.integrations.base import BaseIntegration
from app.lib.auth import decrypt_token, encrypt_token
from app.lib.log import get_logger
from app.models.contact import Contact
from app.models.integration import Integration

logger = get_logger(__name__)

GHL_API_VERSION = "2021-07-28"


class GHLIntegration(BaseIntegration):
    """GoHighLevel integration with OAuth2, contact sync, and webhook support."""

    provider = "ghl"

    def __init__(self, integration: Integration):
        super().__init__(integration)

    @property
    def _location_id(self) -> str:
        return self.integration.account_id or ""

    @property
    def _access_token(self) -> str:
        if not self.integration.access_token:
            raise RuntimeError("GHL integration has no access token")
        return decrypt_token(self.integration.access_token)

    @classmethod
    async def exchange_code(cls, db: AsyncSession, tenant_id: str, code: str) -> Integration:
        """Exchange an OAuth authorization code for access + refresh tokens."""
        token_url = f"{settings.ghl_oauth_base}/token"
        data = {
            "client_id": settings.ghl_client_id,
            "client_secret": settings.ghl_client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.ghl_redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()

        logger.info("GHL token exchange successful for tenant %s", tenant_id)

        integration = Integration(
            tenant_id=tenant_id,
            provider="ghl",
            access_token=encrypt_token(token_data["access_token"]),
            refresh_token=encrypt_token(token_data.get("refresh_token", "")),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600)),
            scope=token_data.get("scope", ""),
            account_id=token_data.get("locationId", ""),
            metadata_json=json.dumps(token_data),
        )
        db.add(integration)
        await db.commit()
        await db.refresh(integration)
        return integration

    async def refresh_access_token(self, db: AsyncSession) -> None:
        """Refresh the GHL access token using the stored refresh token."""
        if not self.integration.refresh_token:
            raise RuntimeError("No refresh token stored")

        token_url = f"{settings.ghl_oauth_base}/token"
        data = {
            "client_id": settings.ghl_client_id,
            "client_secret": settings.ghl_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": decrypt_token(self.integration.refresh_token),
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()

        self.integration.access_token = encrypt_token(token_data["access_token"])
        if token_data.get("refresh_token"):
            self.integration.refresh_token = encrypt_token(token_data["refresh_token"])
        self.integration.expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
        await db.commit()
        logger.info("GHL token refreshed for integration %s", self.integration.id)

    async def sync_contacts(self, db: AsyncSession) -> int:
        """Fetch contacts from GHL and upsert into the contacts table.

        GHL Contacts API: GET /contacts/?locationId=xxx
        Returns: number of contacts synced.
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Version": GHL_API_VERSION,
            "Accept": "application/json",
        }

        synced = 0
        next_page_token = None
        base_url = f"{settings.ghl_api_base}/contacts/"

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                params: dict[str, str] = {"locationId": self._location_id}
                if next_page_token:
                    params["startAfter"] = next_page_token
                params["limit"] = "100"

                resp = await client.get(base_url, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()

                contacts = data.get("contacts", [])
                if not contacts:
                    break

                for ghl_contact in contacts:
                    await self._upsert_contact(db, ghl_contact)
                    synced += 1

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

        await db.commit()
        logger.info("GHL contact sync complete: %d contacts for tenant %s", synced, self.integration.tenant_id)
        return synced

    async def _upsert_contact(self, db: AsyncSession, ghl_contact: dict) -> Contact:
        """Upsert a GHL contact into the contacts table."""
        external_id = ghl_contact.get("id", "")
        if not external_id:
            return None

        # Check if contact already exists
        result = await db.execute(
            select(Contact).where(
                Contact.tenant_id == self.integration.tenant_id,
                Contact.external_id == external_id,
                Contact.source == "ghl",
            )
        )
        contact = result.scalars().first()

        name_parts = [
            ghl_contact.get("firstName", ""),
            ghl_contact.get("lastName", ""),
        ]
        full_name = " ".join(p for p in name_parts if p).strip() or None

        phone = ghl_contact.get("phone") or None
        email = ghl_contact.get("email") or None

        if contact:
            contact.name = full_name
            contact.phone = phone
            contact.email = email
            contact.last_synced_at = datetime.now(timezone.utc)
        else:
            contact = Contact(
                tenant_id=self.integration.tenant_id,
                external_id=external_id,
                source="ghl",
                name=full_name,
                email=email,
                phone=phone,
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(contact)

        return contact

    async def add_note(self, db: AsyncSession, contact_id: str, body: str) -> dict:
        """Add a note to a GHL contact.

        API: POST /contacts/{contactId}/notes
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Version": GHL_API_VERSION,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.ghl_api_base}/contacts/{contact_id}/notes",
                headers=headers,
                json={"body": body, "userId": ""},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pipelines(self, db: AsyncSession) -> list[dict]:
        """Fetch GHL opportunities pipelines.

        API: GET /opportunities/pipelines
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Version": GHL_API_VERSION,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.ghl_api_base}/opportunities/pipelines",
                headers=headers,
                params={"locationId": self._location_id},
            )
            resp.raise_for_status()
            return resp.json().get("pipelines", [])
