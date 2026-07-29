import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import Tenant, Organization, TenantQuota

logger = logging.getLogger("document_intelligence.tenant_service")


class TenantManagementService:
    """Service managing tenant provisioning, organization hierarchy, and quota limits."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_tenant(
        self,
        slug: str,
        name: str,
        contact_email: str,
        max_documents: int = 10000,
        max_pages_per_month: int = 50000,
    ) -> Tenant:
        """Provision new enterprise tenant and initial quota record."""
        stmt = select(Tenant).where(Tenant.slug == slug)
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise ValueError(f"Tenant with slug '{slug}' already exists.")

        tenant = Tenant(slug=slug, name=name, contact_email=contact_email)
        self.db.add(tenant)
        await self.db.flush()

        quota = TenantQuota(
            tenant_id=tenant.id,
            max_documents=max_documents,
            max_pages_per_month=max_pages_per_month,
        )
        self.db.add(quota)
        await self.db.commit()

        logger.info(f"Provisioned new Tenant: '{slug}' (ID: {tenant.id})")
        return tenant

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.slug == slug)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_tenants(self) -> List[Tenant]:
        stmt = select(Tenant)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
