import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.services.workflow_studio_service import WorkflowStudioService
from src.services.approval_task_service import ApprovalTaskService
from src.api.schemas.workflow_studio import (
    WorkflowCreateRequest,
    WorkflowResponse,
    ApprovalTaskResolveRequest,
    ApprovalTaskResponse,
)

router = APIRouter(prefix="/workflows", tags=["Visual No-Code Workflow Studio"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_definition(
    payload: WorkflowCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new Visual No-Code Workflow Definition and Initial Directed Graph Version."""
    service = WorkflowStudioService(db)
    try:
        nodes_dict = [n.model_dump() for n in payload.nodes]
        edges_dict = [e.model_dump() for e in payload.edges]

        definition, _ = await service.create_workflow(
            name=payload.name,
            category=payload.category,
            nodes=nodes_dict,
            edges=edges_dict,
        )
        return WorkflowResponse(
            id=str(definition.id),
            name=definition.name,
            category=definition.category,
            status=definition.status,
            created_at=definition.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[WorkflowResponse])
async def list_workflow_definitions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List visual workflow definitions."""
    service = WorkflowStudioService(db)
    workflows = await service.list_workflows()
    return [
        WorkflowResponse(
            id=str(w.id),
            name=w.name,
            category=w.category,
            status=w.status,
            created_at=w.created_at.isoformat(),
        )
        for w in workflows
    ]


@router.post("/{workflow_id}/publish", response_model=WorkflowResponse)
async def publish_workflow_version(
    workflow_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish workflow definition from draft state."""
    service = WorkflowStudioService(db)
    try:
        definition = await service.publish_workflow(workflow_id)
        return WorkflowResponse(
            id=str(definition.id),
            name=definition.name,
            category=definition.category,
            status=definition.status,
            created_at=definition.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/tasks/approval/{task_id}/resolve", response_model=ApprovalTaskResponse)
async def resolve_approval_task(
    task_id: uuid.UUID,
    payload: ApprovalTaskResolveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Resolve human review/approval task ('approved' or 'rejected')."""
    task_service = ApprovalTaskService(db)
    try:
        task = await task_service.resolve_task(
            task_id=task_id,
            resolution=payload.resolution,
            user_id=current_user.id,
            comments=payload.comments or "",
        )
        return ApprovalTaskResponse(
            task_id=str(task.id),
            execution_id=str(task.execution_id),
            node_id=task.node_id,
            title=task.title,
            assignee_role=task.assignee_role,
            status=task.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
