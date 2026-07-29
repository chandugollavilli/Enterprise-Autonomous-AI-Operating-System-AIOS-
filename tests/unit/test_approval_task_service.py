import uuid
import pytest
import pytest_asyncio
from src.services.approval_task_service import ApprovalTaskService
from tests.conftest import TestingSessionFactory


@pytest.mark.asyncio
async def test_approval_task_service_flow():
    async with TestingSessionFactory() as session:
        task_service = ApprovalTaskService(session)
        exec_id = uuid.uuid4()

        # 1. Create Human Approval Task
        task = await task_service.create_task(
            execution_id=exec_id,
            node_id="node_approval_1",
            title="Review Invoice Payment",
            assignee_role="Manager",
        )
        assert task.status == "pending"

        # 2. List Pending Tasks
        pending = await task_service.list_pending_tasks("Manager")
        assert len(pending) == 1

        # 3. Resolve Task
        resolved = await task_service.resolve_task(task.id, "approved", comments="Verified invoice totals")
        assert resolved.status == "approved"
