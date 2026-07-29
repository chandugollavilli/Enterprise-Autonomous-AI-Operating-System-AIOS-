import pytest
from src.infrastructure.workforce.digital_employees import FinanceDigitalEmployee, LegalDigitalEmployee, HRDigitalEmployee
from src.infrastructure.workforce.employee_registry import DigitalWorkforceRegistry


@pytest.mark.asyncio
async def test_digital_employees_execution():
    fin_emp = FinanceDigitalEmployee()
    task_res = await fin_emp.assign_task("Process Vendor Invoice", {"amount": 5000})
    assert task_res["status"] == "completed"

    leg_emp = LegalDigitalEmployee()
    esc_res = await leg_emp.escalate("High risk indemnification clause detected")
    assert esc_res["status"] == "pending_human_review"

    hr_emp = HRDigitalEmployee()
    profile = hr_emp.get_profile()
    assert profile["department"] == "Human Resources"


def test_workforce_registry():
    employees = DigitalWorkforceRegistry.list_employees()
    assert len(employees) >= 3
