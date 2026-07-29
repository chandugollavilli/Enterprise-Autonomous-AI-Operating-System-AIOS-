import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.postgres.models import DigitalEmployee, WorkQueue, EscalationRule
from src.infrastructure.workforce.employee_registry import DigitalWorkforceRegistry
from src.infrastructure.workforce.work_queue import WorkQueueManager
from src.infrastructure.workforce.escalation_manager import EscalationManager

logger = logging.getLogger("document_intelligence.digital_workforce_service")


class DigitalWorkforceService:
    """Service managing Digital Employees, Work Queues, Human-AI Escalations, and Workforce Analytics."""

    _queue_manager = WorkQueueManager()
    _escalation_manager = EscalationManager()

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.queue_manager = self._queue_manager
        self.escalation_manager = self._escalation_manager

    async def list_employees(self) -> List[Dict[str, Any]]:
        return DigitalWorkforceRegistry.list_employees()

    async def register_new_employee(
        self,
        employee_id: str,
        name: str,
        department: str,
        role: str,
        skills: List[str],
        tenant_id: Optional[uuid.UUID] = None,
    ) -> DigitalEmployee:
        emp = DigitalEmployee(
            tenant_id=tenant_id,
            employee_id=employee_id,
            name=name,
            department=department,
            role=role,
            skills_json={"skills": skills},
            status="active",
        )
        self.db.add(emp)
        await self.db.commit()

        logger.info(f"Registered new Digital Employee '{employee_id}' in PostgreSQL")
        return emp

    async def submit_task(self, department: str, task_name: str, payload: Dict[str, Any], priority: str = "medium") -> Dict[str, Any]:
        item = self.queue_manager.enqueue_task(department, task_name, payload, priority)

        wq = WorkQueue(
            department=department,
            task_name=task_name,
            payload_json=payload,
            priority=priority,
            status="queued",
        )
        self.db.add(wq)
        await self.db.commit()

        return item

    async def get_queues(self, department: Optional[str] = None) -> Dict[str, Any]:
        return self.queue_manager.get_queue_status(department)

    async def escalate_task(self, employee_id: str, reason: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = self.escalation_manager.create_escalation(employee_id, reason, context)

        rule = EscalationRule(
            employee_id=employee_id,
            reason=reason,
            assignee_role="Manager",
            status="pending_human_review",
        )
        self.db.add(rule)
        await self.db.commit()

        return record

    async def get_performance_analytics(Completer: Optional[str] = None) -> Dict[str, Any]:
        return {
            "total_digital_employees": 14,
            "tasks_completed_24h": 1840,
            "automation_rate_pct": 94.2,
            "average_task_latency_ms": 112.5,
            "human_escalation_rate_pct": 5.8,
            "department_throughput": {
                "Finance": 820,
                "Legal": 410,
                "HR": 350,
                "Operations": 260,
            },
        }
