import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.tenant_service import TenantManagementService
from src.api.schemas.tenant import TenantCreateRequest, TenantResponse

router = APIRouter(prefix="/tenants", tags=["Multi-Tenant Administration"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def provision_tenant(
    payload: TenantCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Provision new enterprise tenant and initial quota limit bounds."""
    tenant_service = TenantManagementService(db)
    try:
        tenant = await tenant_service.create_tenant(
            slug=payload.slug,
            name=payload.name,
            contact_email=payload.contact_email,
            max_documents=payload.max_documents,
            max_pages_per_month=payload.max_pages_per_month,
        )
        return TenantResponse(
            id=str(tenant.id),
            slug=tenant.slug,
            name=tenant.name,
            status=tenant.status,
            contact_email=tenant.contact_email,
            created_at=tenant.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all enterprise tenants."""
    tenant_service = TenantManagementService(db)
    tenants = await tenant_service.list_tenants()
    return [
        TenantResponse(
            id=str(t.id),
            slug=t.slug,
            name=t.name,
            status=t.status,
            contact_email=t.contact_email,
            created_at=t.created_at.isoformat(),
        )
        for t in tenants
    ]
