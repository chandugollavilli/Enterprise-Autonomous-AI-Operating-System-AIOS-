import pytest
from src.infrastructure.workflow.workflow_engine import WorkflowEngine, WorkflowDefinition, WorkflowStep


@pytest.mark.asyncio
async def test_workflow_engine_execution():
    pipeline = WorkflowDefinition(
        workflow_id="test_pipeline",
        name="Test Pipeline",
        steps=[
            WorkflowStep("s1", "Step 1", "action_1"),
            WorkflowStep("s2", "Step 2", "action_2"),
        ],
    )
    WorkflowEngine.register_workflow(pipeline)

    executed = []

    async def h1(ctx):
        executed.append("step_1")
        ctx["step1_done"] = True
        return ctx

    async def h2(ctx):
        executed.append("step_2")
        ctx["step2_done"] = True
        return ctx

    handlers = {"action_1": h1, "action_2": h2}
    context = await WorkflowEngine.execute_workflow("test_pipeline", {"document_id": "doc_1"}, handlers)

    assert executed == ["step_1", "step_2"]
    assert context["step1_done"] is True
    assert context["step2_done"] is True
    assert "_workflow_summary" in context
