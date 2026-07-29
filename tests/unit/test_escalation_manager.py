import pytest
from src.infrastructure.workforce.escalation_manager import EscalationManager


def test_escalation_manager_flow():
    em = EscalationManager()
    esc = em.create_escalation("emp_leg_01", "Contract value exceeds $1M threshold")
    assert esc["status"] == "pending_human_review"

    resolved = em.resolve_escalation(esc["escalation_id"], "approved", comments="Supervisor approved contract value")
    assert resolved["status"] == "approved"
