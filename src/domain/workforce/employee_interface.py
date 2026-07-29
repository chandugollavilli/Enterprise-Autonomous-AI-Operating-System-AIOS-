from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IDigitalEmployee(ABC):
    """Abstract Interface for Governed Enterprise Digital Employees."""

    @abstractmethod
    async def assign_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assign business task to digital employee."""
        pass

    @abstractmethod
    async def execute_process(self, process_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute departmental business process."""
        pass

    @abstractmethod
    async def escalate(self, reason: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Escalate decision to human supervisor."""
        pass

    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Return digital employee identity, department, role, skills, and metrics."""
        pass
