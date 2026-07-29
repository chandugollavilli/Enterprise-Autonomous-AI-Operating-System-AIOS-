import logging
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger("document_intelligence.escalation_manager")


class EscalationManager:
    """Manages Human-in-the-Loop Escalation Gates, Approval Thresholds & Supervisor Overrides."""

    def __init__(self):
        self.escalations: Dict[str, Dict[str, Any]] = {}

    def create_escalation(
        self,
        employee_id: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
        assignee_role: str = "Manager",
    ) -> Dict[str, Any]:
        esc_id = f"esc_{int(time.time() * 1000)}"
        record = {
            "escalation_id": esc_id,
            "employee_id": employee_id,
            "reason": reason,
            "context": context or {},
            "assignee_role": assignee_role,
            "status": "pending_human_review",
            "created_at": time.time(),
        }
        self.escalations[esc_id] = record
        logger.info(f"Created Escalation '{esc_id}' for Employee '{employee_id}' -> Role '{assignee_role}'")
        return record

    def resolve_escalation(self, escalation_id: str, resolution: str, comments: str = "") -> Dict[str, Any]:
        if escalation_id not in self.escalations:
            raise ValueError(f"Escalation '{escalation_id}' not found.")

        record = self.escalations[escalation_id]
        record["status"] = resolution  # "approved", "rejected", "overridden"
        record["comments"] = comments
        record["resolved_at"] = time.time()

        logger.info(f"Resolved Escalation '{escalation_id}' -> '{resolution}'")
        return record
