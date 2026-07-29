import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.automation_service import AutomationService
from src.api.schemas.automation import (
    ConnectorCreateRequest,
    ConnectorResponse,
    SyncJobResponse,
    AutomationRuleCreateRequest,
    AutomationRuleResponse,
)

router = APIRouter(tags=["Enterprise Connectors & Workflow Automation"])


@router.post("/connectors", response_model=ConnectorResponse, status_code=status.HTTP_201_CREATED)
async def register_connector(
    payload: ConnectorCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register new enterprise connector (Amazon S3, MinIO, SFTP, SharePoint)."""
    service = AutomationService(db)
    connector = await service.register_connector(
        name=payload.name,
        connector_type=payload.connector_type,
        config=payload.config,
    )
    return ConnectorResponse(
        id=str(connector.id),
        name=connector.name,
        connector_type=connector.connector_type,
        status=connector.status,
        config=connector.config_json,
    )


@router.post("/connectors/{connector_id}/sync", response_model=SyncJobResponse)
async def trigger_connector_sync(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger background document synchronization job for target connector."""
    service = AutomationService(db)
    try:
        job = await service.trigger_connector_sync(connector_id)
        return SyncJobResponse(
            job_id=str(job.id),
            connector_id=str(job.connector_id),
            status=job.status,
            documents_synced=job.documents_synced,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/rules", response_model=AutomationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_rule(
    payload: AutomationRuleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create automated conditional document routing & action rule."""
    service = AutomationService(db)
    rule = await service.create_automation_rule(
        name=payload.name,
        target_category=payload.target_category,
        field_name=payload.field_name,
        operator=payload.operator,
        threshold_value=payload.threshold_value,
        target_action=payload.target_action,
    )
    return AutomationRuleResponse(
        id=str(rule.id),
        name=rule.name,
        target_category=rule.target_category,
        field_name=rule.field_name,
        operator=rule.operator,
        threshold_value=rule.threshold_value,
        target_action=rule.target_action,
    )
