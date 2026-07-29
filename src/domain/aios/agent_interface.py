from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IAIOSAgent(ABC):
    """Abstract Interface for Autonomous AIOS Specialized Agents."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize agent weights, tools, and memory scope."""
        pass

    @abstractmethod
    async def plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Decompose complex goal into step-by-step task execution plan."""
        pass

    @abstractmethod
    async def reason(self, problem: str, evidence: List[str]) -> Dict[str, Any]:
        """Execute Tree-of-Thought reasoning, reflection, and evidence aggregation."""
        pass

    @abstractmethod
    async def execute_task(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute assigned autonomous task."""
        pass

    @abstractmethod
    def agent_info(self) -> Dict[str, Any]:
        """Return agent identity, role, capabilities, and permissions."""
        pass
