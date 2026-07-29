import logging
import time
from typing import Dict, Any, List, Optional
from src.domain.workforce.employee_interface import IDigitalEmployee

logger = logging.getLogger("document_intelligence.digital_employees")


class BaseDigitalEmployee(IDigitalEmployee):
    """Base class for Governed Departmental Digital Employees."""

    def __init__(self, employee_id: str, name: str, department: str, role: str, skills: List[str]):
        self.employee_id = employee_id
        self.name = name
        self.department = department
        self.role = role
        self.skills = skills
        self.tasks_completed = 0

    async def assign_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.tasks_completed += 1
        logger.info(f"Digital Employee '{self.name}' ({self.department}) assigned task: '{task_name}'")
        return {
            "employee_id": self.employee_id,
            "task_name": task_name,
            "status": "completed",
            "result": f"Executed task '{task_name}' cleanly.",
        }

    async def execute_process(self, process_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "department": self.department,
            "process_name": process_name,
            "status": "completed",
            "output": f"Executed process '{process_name}' for department '{self.department}'.",
        }

    async def escalate(self, reason: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.warning(f"Digital Employee '{self.name}' escalated: '{reason}'")
        return {
            "employee_id": self.employee_id,
            "escalation_id": f"esc_{int(time.time())}",
            "reason": reason,
            "status": "pending_human_review",
        }

    def get_profile(self) -> Dict[str, Any]:
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "department": self.department,
            "role": self.role,
            "skills": self.skills,
            "tasks_completed": self.tasks_completed,
            "status": "active",
        }


class FinanceDigitalEmployee(BaseDigitalEmployee):
    def __init__(self, employee_id: str = "emp_fin_01", name: str = "Finance Auto-Specialist"):
        super().__init__(
            employee_id=employee_id,
            name=name,
            department="Finance",
            role="Senior Accounts Payable Analyst",
            skills=["invoice_processing", "po_matching", "tax_extraction", "duplicate_detection"],
        )


class LegalDigitalEmployee(BaseDigitalEmployee):
    def __init__(self, employee_id: str = "emp_leg_01", name: str = "Legal Counsel Assistant"):
        super().__init__(
            employee_id=employee_id,
            name=name,
            department="Legal",
            role="Contract Risk Analyst",
            skills=["contract_review", "clause_extraction", "liability_assessment", "renewal_tracking"],
        )


class HRDigitalEmployee(BaseDigitalEmployee):
    def __init__(self, employee_id: str = "emp_hr_01", name: str = "Talent Acquisition Assistant"):
        super().__init__(
            employee_id=employee_id,
            name=name,
            department="Human Resources",
            role="Resume Screening Specialist",
            skills=["resume_parsing", "candidate_ranking", "skills_extraction", "education_verification"],
        )
