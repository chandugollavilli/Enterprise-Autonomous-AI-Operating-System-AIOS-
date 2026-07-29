import pytest
from src.infrastructure.aios.multi_agent_collaborator import MultiAgentCollaborator, SpecializedAIOSAgent


@pytest.mark.asyncio
async def test_specialized_agent_lifecycle():
    agent = SpecializedAIOSAgent("planner", "Planner Agent", "Planning", ["decomposition"])
    await agent.initialize()

    plan_res = await agent.plan("Review Contract")
    assert plan_res["goal"] == "Review Contract"
    assert len(plan_res["subtasks"]) >= 1

    reason_res = await agent.reason("Is liability limited?", ["doc_ref_1"])
    assert reason_res["confidence_score"] > 0.9


@pytest.mark.asyncio
async def test_multi_agent_collaboration_flow():
    collaborator = MultiAgentCollaborator()
    res = await collaborator.collaborate_on_goal("Automate Supplier Risk Assessment")

    assert res["status"] == "consensus_achieved"
    assert res["consensus_vote"]["approve"] >= 4
    assert res["duration_ms"] > 0
