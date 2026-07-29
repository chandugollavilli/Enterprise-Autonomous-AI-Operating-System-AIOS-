from enum import Enum
from typing import Dict, Set
import logging

logger = logging.getLogger("document_intelligence.workflow_state_machine")


class WorkflowState(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class WorkflowStateMachine:
    """State Machine enforcing valid workflow lifecycle transitions."""

    ALLOWED_TRANSITIONS: Dict[WorkflowState, Set[WorkflowState]] = {
        WorkflowState.DRAFT: {WorkflowState.PUBLISHED, WorkflowState.CANCELLED},
        WorkflowState.PUBLISHED: {WorkflowState.RUNNING, WorkflowState.DRAFT, WorkflowState.CANCELLED},
        WorkflowState.RUNNING: {WorkflowState.PAUSED, WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED},
        WorkflowState.PAUSED: {WorkflowState.RUNNING, WorkflowState.CANCELLED},
        WorkflowState.COMPLETED: set(),
        WorkflowState.FAILED: {WorkflowState.RUNNING},  # Restart
        WorkflowState.CANCELLED: set(),
    }

    @classmethod
    def can_transition(cls, current: str, target: str) -> bool:
        try:
            curr_state = WorkflowState(current)
            target_state = WorkflowState(target)
        except ValueError:
            return False

        return target_state in cls.ALLOWED_TRANSITIONS.get(curr_state, set())
