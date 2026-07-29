from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
import logging

logger = logging.getLogger("document_intelligence.agent_registry")


class ITool(ABC):
    """Abstract Interface for AI Agent Tools."""

    name: str
    description: str

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class ToolRegistry:
    """Centralized Registry for AI Agent Tools."""

    _tools: Dict[str, ITool] = {}

    @classmethod
    def register_tool(cls, tool: ITool):
        cls._tools[tool.name] = tool
        logger.info(f"Registered Agent Tool: '{tool.name}' ({tool.description})")

    @classmethod
    def get_tool(cls, name: str) -> Optional[ITool]:
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t.values() in [cls._tools]]


@dataclass
class AgentDefinition:
    agent_id: str
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str] = field(default_factory=list)


class AgentRegistry:
    """Centralized Registry for Specialized Enterprise AI Agents."""

    _agents: Dict[str, AgentDefinition] = {}

    @classmethod
    def register_agent(cls, agent: AgentDefinition):
        cls._agents[agent.agent_id] = agent
        logger.info(f"Registered Specialized AI Agent: '{agent.agent_id}' ({agent.name})")

    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[AgentDefinition]:
        return cls._agents.get(agent_id)

    @classmethod
    def list_agents(cls) -> List[AgentDefinition]:
        return list(cls._agents.values())


# Register Default Enterprise Specialized AI Agents
AgentRegistry.register_agent(
    AgentDefinition(
        agent_id="document_qa_agent",
        name="Document QA Agent",
        description="Answers questions across multi-page PDF documents and financial invoices.",
        system_prompt="You are an expert Document QA Assistant. Use tools to search and answer user queries with citations.",
        allowed_tools=["hybrid_search", "document_lookup"],
    )
)

AgentRegistry.register_agent(
    AgentDefinition(
        agent_id="contract_review_agent",
        name="Contract Review & Analysis Agent",
        description="Analyzes legal agreements, contracts, clauses, risks, and payment obligations.",
        system_prompt="You are a Legal Contract Analysis Agent. Review contracts and highlight liabilities and payment terms.",
        allowed_tools=["hybrid_search", "summary_tool"],
    )
)
