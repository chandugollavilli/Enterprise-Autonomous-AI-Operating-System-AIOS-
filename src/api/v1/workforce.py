from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.digital_workforce_service import DigitalWorkforceService
from src.api.schemas.workforce import (
    DigitalEmployeeDTO,
    EmployeeCreateRequest,
    TaskSubmitRequest,
    TaskSubmitResponse,
    EscalationCreateRequest,
    EscalationResponse,
    PerformanceAnalyticsResponse,
)

router = APIRouter(prefix="/workforce", tags=["Enterprise Digital Workforce Platform"])


@router.get("/employees", response_model=List[DigitalEmployeeDTO])
async def list_digital_employees(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List registered governed Digital Employees across departments."""
    service = DigitalWorkforceService(db)
    employees = await service.list_employees()
    return [DigitalEmployeeDTO(**e) for e in employees]


@router.post("/employees", status_code=status.HTTP_201_CREATED)
async def register_digital_employee(
    payload: EmployeeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register new Digital Employee entity."""
    service = DigitalWorkforceService(db)
    emp = await service.register_new_employee(
        employee_id=payload.employee_id,
        name=payload.name,
        department=payload.department,
        role=payload.role,
        skills=payload.skills,
    )
    return {"message": f"Successfully registered Digital Employee '{emp.employee_id}'", "status": emp.status}


@router.post("/tasks", response_model=TaskSubmitResponse, status_code=status.HTTP_201_CREATED)
async def submit_workforce_task(
    payload: TaskSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit business task to departmental work queue."""
    service = DigitalWorkforceService(db)
    res = await service.submit_task(
        department=payload.department,
        task_name=payload.task_name,
        payload=payload.payload,
        priority=payload.priority or "medium",
    )
    return TaskSubmitResponse(
        task_id=res["task_id"],
        task_name=res["task_name"],
        department=res["department"],
        priority=res["priority"],
        status=res["status"],
    )


@router.get("/queues")
async def get_work_queues(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve status of departmental work queues."""
    service = DigitalWorkforceService(db)
    return await service.get_queues(department)


@router.post("/escalations", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation_gate(
    payload: EscalationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger Human-in-the-Loop approval escalation gate."""
    service = DigitalWorkforceService(db)
    res = await service.escalate_task(
        employee_id=payload.employee_id,
        reason=payload.reason,
        context=payload.context,
    )
    return EscalationResponse(**res)


@router.get("/performance", response_model=PerformanceAnalyticsResponse)
async def get_workforce_performance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve Digital Workforce performance telemetry analytics."""
    service = DigitalWorkforceService(db)
    metrics = await service.get_performance_analytics()
    return PerformanceAnalyticsResponse(**metrics)
