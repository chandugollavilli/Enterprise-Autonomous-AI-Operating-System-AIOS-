import pytest
from src.infrastructure.workflow.state_machine import WorkflowStateMachine, WorkflowState


def test_workflow_state_machine_transitions():
    assert WorkflowStateMachine.can_transition("draft", "published") is True
    assert WorkflowStateMachine.can_transition("published", "running") is True
    assert WorkflowStateMachine.can_transition("running", "paused") is True
    assert WorkflowStateMachine.can_transition("completed", "published") is False
