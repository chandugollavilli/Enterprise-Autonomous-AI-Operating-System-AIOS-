from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("document_intelligence.prompt_registry")


@dataclass
class PromptTemplate:
    id: str
    name: str
    template_text: str
    variables: List[str]
    version: str = "v1.0"
    category: str = "qa"

    def render(self, **kwargs) -> str:
        text = self.template_text
        for var in self.variables:
            val = kwargs.get(var, "")
            text = text.replace(f"{{{var}}}", str(val))
        return text


class PromptRegistry:
    """Centralized Versioned Prompt Registry for Question Answering, Summarization, and Entity Extraction."""

    _prompts: Dict[str, PromptTemplate] = {}

    @classmethod
    def register_prompt(cls, prompt: PromptTemplate):
        cls._prompts[prompt.id] = prompt
        logger.info(f"Registered Prompt Template: '{prompt.id}' ({prompt.name}, version: {prompt.version})")

    @classmethod
    def get_prompt(cls, prompt_id: str) -> Optional[PromptTemplate]:
        return cls._prompts.get(prompt_id)

    @classmethod
    def render_prompt(cls, prompt_id: str, **kwargs) -> str:
        prompt = cls.get_prompt(prompt_id)
        if not prompt:
            raise ValueError(f"Prompt Template '{prompt_id}' not found in registry.")
        return prompt.render(**kwargs)


# Register Default System Prompts
PromptRegistry.register_prompt(
    PromptTemplate(
        id="qa_default",
        name="Default RAG Question Answering Prompt",
        category="qa",
        variables=["context", "question"],
        template_text=(
            "You are an Enterprise AI Document Assistant. "
            "Answer the user's question accurately using ONLY the provided document context below.\n"
            "Include inline citation markers like [1], [2] corresponding to context references.\n\n"
            "--- DOCUMENT CONTEXT ---\n{context}\n----------------------\n\n"
            "QUESTION: {question}\n\n"
            "ANSWER:"
        ),
    )
)

PromptRegistry.register_prompt(
    PromptTemplate(
        id="summarization",
        name="Document Executive Summarization Prompt",
        category="summarization",
        variables=["context"],
        template_text=(
            "Generate a comprehensive Executive Summary of the following document content.\n"
            "Highlight key objectives, financial metrics, deliverable dates, and risk items.\n\n"
            "--- DOCUMENT CONTEXT ---\n{context}\n----------------------\n\n"
            "EXECUTIVE SUMMARY:"
        ),
    )
)
