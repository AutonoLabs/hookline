"""Microsoft Dynamics 365 / Dataverse integration.

API docs: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/perform-operations-web-api (checked 2025-08-13)
OAuth: Azure AD v2 endpoint, client_credentials or authorization_code flow
Token: POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
Web API: https://{org}.crm.dynamics.com/api/data/v9.2/
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

DYNAMICS_API_VERSION = "v9.2"


class DynamicsIntegration(BaseIntegration):
    """Microsoft Dynamics 365 integration with OAuth2, contact/lead sync, and webhook support."""

    provider = "dynamics"

    @property
    def _access_token(self) -> str:
        if not self.integration.access_token:
            raise RuntimeError("Dynamics integration has no access token")
        return decrypt_token(self.integration.access_token)

    @property
    def _web_api_base(self) -> str:
        """Returns the Dynamics Web API base URL (org-specific)."""
        # Stored in settings.dynamics_resource_url or integration metadata
        if settings.dynamics_resource_url:
            return f"{settings.dynamics_resource_url}/api/data/{DYNAMICS_API_VERSION}"
        meta = json.loads(self.integration.metadata_json or "{}")
        resource = meta.get("resource_url", "")
        return f"{resource}/api/data/{DYNAMICS_API_VERSION}"

    @classmethod
    async def exchange_code(cls, db: AsyncSession, tenant_id: str, code: str) -> Integration:
        """Exchange an OAuth authorization code for access + refresh tokens."""
        token_url = f"{settings.dynamics_oauth_base}/{settings.dynamics_tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": settings.dynamics_client_id,
            "client_secret": settings.dynamics_client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.dynamics_redirect_uri,
            "scope": settings.dynamics_scope,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(token_url, data=data)
            resp.raise_for_status()
            token_data = resp.json()

        logger.info("Dynamics token exchange successful for tenant %s", tenant_id)

        integration = Integration(
            tenant_id=tenant_id,
            provider="dynamics",
            access_token=encrypt_token(token_data["access_token"]),
            refresh_token=encrypt_token(token_data.get("refresh_token", "")),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600)),
            scope=token_data.get("scope", ""),
            account_id=settings.dynamics_tenant_id,
            metadata_json=json.dumps({
                "resource_url": settings.dynamics_resource_url,
                "raw": token_data,
            }),
        )
        db.add(integration)
        await db.commit()
        await db.refresh(integration)
        return integration

    async def refresh_access_token(self, db: AsyncSession) -> None:
        """Refresh the Dynamics access token using the stored refresh token."""
        if not self.integration.refresh_token:
            raise RuntimeError("No refresh token stored")

        token_url = f"{settings.dynamics_oauth_base}/{settings.dynamics_tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": settings.dynamics_client_id,
            "client_secret": settings.dynamics_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": decrypt_token(self.integration.refresh_token),
            "scope": settings.dynamics_scope,
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
        logger.info("Dynamics token refreshed for integration %s", self.integration.id)

    async def sync_contacts(self, db: AsyncSession) -> int:
        """Fetch contacts from Dynamics 365 and upsert into the contacts table.

        Web API: GET /api/data/v9.2/contacts?$select=contactid,firstname,lastname,emailaddress1,telephone1
        Ref: https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/developer/entities/contact
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }

        # Select only the fields we need
        select_fields = "contactid,firstname,lastname,emailaddress1,telephone1"
        synced = 0
        url = f"{self._web_api_base}/contacts?$select={select_fields}"

        async with httpx.AsyncClient(timeout=30) as client:
            while url:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                for dyn_contact in data.get("value", []):
                    await self._upsert_contact(db, dyn_contact)
                    synced += 1

                # Handle OData pagination (@odata.nextLink)
                url = data.get("@odata.nextLink")

        await db.commit()
        logger.info("Dynamics contact sync complete: %d contacts for tenant %s", synced, self.integration.tenant_id)
        return synced

    async def sync_leads(self, db: AsyncSession) -> int:
        """Fetch leads from Dynamics 365 and upsert into the contacts table.

        Web API: GET /api/data/v9.2/leads?$select=leadid,firstname,lastname,emailaddress1,telephone1
        Ref: https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/developer/entities/lead
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
        }

        select_fields = "leadid,firstname,lastname,emailaddress1,telephone1"
        synced = 0
        url = f"{self._web_api_base}/leads?$select={select_fields}"

        async with httpx.AsyncClient(timeout=30) as client:
            while url:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()

                for dyn_lead in data.get("value", []):
                    await self._upsert_lead(db, dyn_lead)
                    synced += 1

                url = data.get("@odata.nextLink")

        await db.commit()
        logger.info("Dynamics lead sync complete: %d leads for tenant %s", synced, self.integration.tenant_id)
        return synced

    async def _upsert_contact(self, db: AsyncSession, dyn_contact: dict) -> Contact:
        """Upsert a Dynamics contact into the contacts table."""
        external_id = dyn_contact.get("contactid", "")
        if not external_id:
            return None

        result = await db.execute(
            select(Contact).where(
                Contact.tenant_id == self.integration.tenant_id,
                Contact.external_id == external_id,
                Contact.source == "dynamics",
            )
        )
        contact = result.scalars().first()

        name_parts = [
            dyn_contact.get("firstname", ""),
            dyn_contact.get("lastname", ""),
        ]
        full_name = " ".join(p for p in name_parts if p).strip() or None
        email = dyn_contact.get("emailaddress1") or None
        phone = dyn_contact.get("telephone1") or None

        if contact:
            contact.name = full_name
            contact.phone = phone
            contact.email = email
            contact.last_synced_at = datetime.now(timezone.utc)
        else:
            contact = Contact(
                tenant_id=self.integration.tenant_id,
                external_id=external_id,
                source="dynamics",
                name=full_name,
                email=email,
                phone=phone,
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(contact)

        return contact

    async def _upsert_lead(self, db: AsyncSession, dyn_lead: dict) -> Contact:
        """Upsert a Dynamics lead into the contacts table (leads map to contacts in Hookline)."""
        external_id = f"lead_{dyn_lead.get('leadid', '')}"
        lead_id = dyn_lead.get("leadid", "")
        if not lead_id:
            return None

        result = await db.execute(
            select(Contact).where(
                Contact.tenant_id == self.integration.tenant_id,
                Contact.external_id == external_id,
                Contact.source == "dynamics",
            )
        )
        contact = result.scalars().first()

        name_parts = [dyn_lead.get("firstname", ""), dyn_lead.get("lastname", "")]
        full_name = " ".join(p for p in name_parts if p).strip() or None
        email = dyn_lead.get("emailaddress1") or None
        phone = dyn_lead.get("telephone1") or None

        if contact:
            contact.name = full_name
            contact.phone = phone
            contact.email = email
            contact.last_synced_at = datetime.now(timezone.utc)
        else:
            contact = Contact(
                tenant_id=self.integration.tenant_id,
                external_id=external_id,
                source="dynamics",
                name=full_name,
                email=email,
                phone=phone,
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(contact)

        return contact

    async def create_note(self, db: AsyncSession, contact_id: str, body: str) -> dict:
        """Create an annotation (note) linked to a contact in Dynamics.

        Web API: POST /api/data/v9.2/annotations
        Ref: https://learn.microsoft.com/en-us/dynamics365/customerengagement/on-premises/developer/entities/annotation
        """
        await self._ensure_token_valid(db)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Content-Type": "application/json",
        }

        payload = {
            "subject": "Hookline Note",
            "notetext": body,
            # Link to contact via @odata.id navigation property
            "objectid_contact@odata.bind": f"/contacts({contact_id})",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._web_api_base}/annotations",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
