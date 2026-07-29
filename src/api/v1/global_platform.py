from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.global_platform_service import GlobalPlatformService
from src.api.schemas.global_platform import (
    RegionDTO,
    ClusterDTO,
    DigitalTwinTopologyDTO,
    FinOpsCostResponse,
    RunbookExecuteRequest,
    RunbookExecuteResponse,
)

router = APIRouter(prefix="/platform", tags=["Global Enterprise AI Cloud Platform & Digital Twin"])


@router.get("/regions", response_model=List[RegionDTO])
async def list_global_regions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List global multi-region cloud deployment nodes (AWS, Azure, GCP)."""
    service = GlobalPlatformService(db)
    regions = await service.get_regions()
    return [RegionDTO(**r) for r in regions]


@router.get("/clusters", response_model=List[ClusterDTO])
async def list_cloud_clusters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List registered multi-cloud Kubernetes clusters."""
    service = GlobalPlatformService(db)
    clusters = await service.get_clusters()
    return [ClusterDTO(**c) for c in clusters]


@router.get("/digital-twin", response_model=DigitalTwinTopologyDTO)
async def get_digital_twin_topology(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Digital Twin live infrastructure and dependency topology graph."""
    service = GlobalPlatformService(db)
    topology = await service.get_digital_twin_topology()
    return DigitalTwinTopologyDTO(**topology)


@router.get("/costs", response_model=FinOpsCostResponse)
async def get_finops_costs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve FinOps cost breakdown, GPU/token analytics, and budget alerts."""
    service = GlobalPlatformService(db)
    costs = await service.get_cost_analytics()
    return FinOpsCostResponse(**costs)


@router.get("/incidents")
async def list_sre_incidents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List SRE incident history and auto-remediation logs."""
    service = GlobalPlatformService(db)
    return await service.list_incidents()


@router.post("/runbooks/execute", response_model=RunbookExecuteResponse, status_code=status.HTTP_200_OK)
async def execute_sre_runbook(
    payload: RunbookExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger automated SRE remediation runbook."""
    service = GlobalPlatformService(db)
    res = await service.execute_runbook(payload.runbook_name, payload.target)
    return RunbookExecuteResponse(**res)
