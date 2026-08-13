"""Abstract base class for CRM integrations."""
from __future__ import annotations

import abc
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import Integration


class BaseIntegration(abc.ABC):
    """Abstract CRM integration. Each provider implements sync + token refresh."""

    def __init__(self, integration: Integration):
        self.integration = integration

    @property
    @abc.abstractmethod
    def provider(self) -> str:
        ...

    @abc.abstractmethod
    async def sync_contacts(self, db: AsyncSession) -> int:
        """Fetch contacts from the CRM and upsert into local DB. Returns count synced."""
        ...

    @abc.abstractmethod
    async def refresh_access_token(self, db: AsyncSession) -> None:
        """Refresh the access token if expired."""
        ...

    async def _ensure_token_valid(self, db: AsyncSession) -> None:
        """Check token expiry and refresh if needed."""
        if self.integration.expires_at:
            now = datetime.now(self.integration.expires_at.tzinfo or None)
            if self.integration.expires_at <= now:
                await self.refresh_access_token(db)
