from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.solution_service import SolutionPackService
from src.infrastructure.solutions.solution_registry import SolutionPackRegistry
from src.api.schemas.solution import (
    SolutionPackDTO,
    SolutionExecuteRequest,
    SolutionExecuteResponse,
    DashboardResponse,
)

router = APIRouter(prefix="/solutions", tags=["Enterprise Industry Solution Packs"])


@router.get("", response_model=List[SolutionPackDTO])
async def list_solution_packs(
    current_user: User = Depends(get_current_user),
):
    """List available industry solution packs (Legal, Finance, HR, Healthcare, Research)."""
    packs = SolutionPackRegistry.list_packs()
    return [SolutionPackDTO(**p) for p in packs]


@router.post("/{pack_id}/install", status_code=status.HTTP_201_CREATED)
async def install_solution_pack(
    pack_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Install industry solution pack for tenant workspace."""
    service = SolutionPackService(db)
    try:
        installed = await service.install_pack(pack_id)
        return {"message": f"Successfully installed solution pack '{pack_id}'", "status": installed.status}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{pack_id}/execute", response_model=SolutionExecuteResponse)
async def execute_solution_pack(
    pack_id: str,
    payload: SolutionExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute solution pack domain intelligence pipeline and generate executive report."""
    service = SolutionPackService(db)
    try:
        res = await service.execute_pack_analysis(
            pack_id=pack_id,
            document_text=payload.document_text,
            filename=payload.filename,
            metadata=payload.metadata,
        )
        return SolutionExecuteResponse(
            pack_id=pack_id,
            document_type=res.get("document_type", "General"),
            report_id=res["report_id"],
            report_markdown=res["report_markdown"],
            analysis_details=res,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{pack_id}/dashboards", response_model=DashboardResponse)
async def get_solution_dashboard(
    pack_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve solution pack telemetry and analytics dashboard."""
    service = SolutionPackService(db)
    metrics = await service.get_dashboard(pack_id)
    return DashboardResponse(**metrics)
