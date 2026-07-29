import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.marketplace_service import MarketplaceService
from src.infrastructure.webhooks.webhook_service import WebhookSubscriptionService
from src.api.schemas.marketplace import (
    MarketplacePackageDTO,
    PluginInstallResponse,
    WebhookCreateRequest,
    WebhookSubscriptionResponse,
)

router = APIRouter(tags=["Enterprise AI Ecosystem & Marketplace"])


@router.get("/marketplace/packages", response_model=List[MarketplacePackageDTO])
async def list_marketplace_packages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Browse extension marketplace packages (connectors, LLMs, AI agents)."""
    service = MarketplaceService(db)
    packages = await service.list_packages()
    return [MarketplacePackageDTO(**p) for p in packages]


@router.post("/marketplace/packages/{package_id}/install", response_model=PluginInstallResponse, status_code=status.HTTP_201_CREATED)
async def install_marketplace_package(
    package_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Install extension package from marketplace for active tenant workspace."""
    service = MarketplaceService(db)
    installation = await service.install_package(package_id)
    return PluginInstallResponse(
        installation_id=str(installation.id),
        package_id=installation.package_id,
        status=installation.status,
        installed_at=installation.created_at.isoformat(),
    )


@router.post("/webhooks", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_subscription(
    payload: WebhookCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create HTTP POST Webhook Subscription for platform events."""
    service = WebhookSubscriptionService(db)
    sub = await service.create_subscription(
        target_url=payload.target_url,
        event_types=payload.event_types,
        secret=payload.secret or "whsec_default123",
    )
    return WebhookSubscriptionResponse(
        id=str(sub.id),
        target_url=sub.target_url,
        event_types=sub.event_types_json.get("events", []),
        status=sub.status,
        created_at=sub.created_at.isoformat(),
    )
