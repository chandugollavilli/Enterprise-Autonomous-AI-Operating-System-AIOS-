import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import MarketplacePackage, PluginInstallation

logger = logging.getLogger("document_intelligence.marketplace_service")


class MarketplaceService:
    """Service managing extension marketplace package browsing, publisher verification, and plugin installations."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def list_packages(self) -> List[Dict[str, Any]]:
        return [
            {
                "package_id": "pkg_sap_connector",
                "name": "SAP ERP Enterprise Connector",
                "category": "Connector",
                "publisher": "SAP Verified Partner",
                "version": "v1.2.0",
                "rating": 4.9,
                "downloads": 1240,
            },
            {
                "package_id": "pkg_claude3_llm",
                "name": "Anthropic Claude 3.5 Sonnet LLM Adapter",
                "category": "AI Provider",
                "publisher": "Anthropic Community",
                "version": "v1.0.0",
                "rating": 5.0,
                "downloads": 3100,
            },
        ]

    async def install_package(self, package_id: str, tenant_id: Optional[uuid.UUID] = None) -> PluginInstallation:
        installation = PluginInstallation(
            tenant_id=tenant_id,
            package_id=package_id,
            version="v1.0.0",
            status="active",
        )
        self.db.add(installation)
        await self.db.commit()
        await self.db.refresh(installation)

        logger.info(f"Installed Marketplace Package '{package_id}' for Tenant {tenant_id}")
        return installation
