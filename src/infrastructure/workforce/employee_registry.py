from typing import Dict, Any, List, Optional
import logging
from src.domain.workforce.employee_interface import IDigitalEmployee
from src.infrastructure.workforce.digital_employees import (
    FinanceDigitalEmployee,
    LegalDigitalEmployee,
    HRDigitalEmployee,
)

logger = logging.getLogger("document_intelligence.employee_registry")


class DigitalWorkforceRegistry:
    """Centralized Registry for Enterprise Digital Employees."""

    _employees: Dict[str, IDigitalEmployee] = {}

    @classmethod
    def register_employee(cls, employee: IDigitalEmployee):
        profile = employee.get_profile()
        cls._employees[profile["employee_id"]] = employee
        logger.info(f"Registered Digital Employee: '{profile['employee_id']}' ({profile['name']} - {profile['department']})")

    @classmethod
    def get_employee(cls, employee_id: str) -> Optional[IDigitalEmployee]:
        return cls._employees.get(employee_id)

    @classmethod
    def list_employees(cls) -> List[Dict[str, Any]]:
        return [e.get_profile() for e in cls._employees.values()]


# Auto-register Default Digital Employees
DigitalWorkforceRegistry.register_employee(FinanceDigitalEmployee())
DigitalWorkforceRegistry.register_employee(LegalDigitalEmployee())
DigitalWorkforceRegistry.register_employee(HRDigitalEmployee())
