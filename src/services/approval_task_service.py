import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import ApprovalTask

logger = logging.getLogger("document_intelligence.approval_task_service")


class ApprovalTaskService:
    """Service managing human review and approval tasks within workflow executions."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_task(
        self,
        execution_id: uuid.UUID,
        node_id: str,
        title: str,
        assignee_role: str = "Reviewer",
        description: str = "",
    ) -> ApprovalTask:
        task = ApprovalTask(
            execution_id=execution_id,
            node_id=node_id,
            title=title,
            assignee_role=assignee_role,
            description=description,
            status="pending",
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        logger.info(f"Created Human Approval Task: '{title}' (Task ID: {task.id}, Assignee Role: {assignee_role})")
        return task

    async def resolve_task(
        self,
        task_id: uuid.UUID,
        resolution: str,  # "approved" or "rejected"
        user_id: Optional[uuid.UUID] = None,
        comments: str = "",
    ) -> ApprovalTask:
        stmt = select(ApprovalTask).where(ApprovalTask.id == task_id)
        task = (await self.db.execute(stmt)).scalar_one_or_none()

        if not task:
            raise ValueError(f"Approval Task '{task_id}' not found.")

        task.status = resolution
        task.resolver_user_id = user_id
        task.comments = comments

        await self.db.commit()
        logger.info(f"Resolved Approval Task '{task_id}' -> Resolution: '{resolution}', Resolver: {user_id}")
        return task

    async def list_pending_tasks(self, assignee_role: Optional[str] = None) -> List[ApprovalTask]:
        stmt = select(ApprovalTask).where(ApprovalTask.status == "pending")
        if assignee_role:
            stmt = stmt.where(ApprovalTask.assignee_role == assignee_role)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
