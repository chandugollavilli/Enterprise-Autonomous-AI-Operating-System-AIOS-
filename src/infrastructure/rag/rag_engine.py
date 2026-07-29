import time
import logging
from typing import Dict, Any, List, Optional
from src.domain.interfaces.llm_provider import ILLMProvider
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter
from src.infrastructure.llm.prompt_registry import PromptRegistry
from src.infrastructure.rag.context_builder import ContextBuilder
from src.infrastructure.rag.citation_generator import CitationGenerator, CitationDTO

logger = logging.getLogger("document_intelligence.rag_engine")


class EnterpriseRAGEngine:
    """
    Enterprise RAG Engine orchestrating hybrid retrieval -> context assembly -> prompt template rendering -> LLM invocation -> inline citation generation.
    """

    def __init__(self, llm_provider: Optional[ILLMProvider] = None):
        self.llm = llm_provider or OpenAILLMAdapter()

    async def answer_question(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        prompt_id: str = "qa_default",
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # 1. Assemble Context from Search Results
        context_str, referenced_items = ContextBuilder.build_context(retrieved_chunks)

        # 2. Render Prompt Template
        rendered_prompt = PromptRegistry.render_prompt(prompt_id, context=context_str, question=question)

        # 3. Construct Chat Messages
        messages: List[Dict[str, str]] = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": rendered_prompt})

        # 4. Invoke LLM Provider
        llm_response = await self.llm.chat(messages)

        # 5. Extract Citations
        citations = CitationGenerator.generate_citations(referenced_items)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "answer": llm_response["content"],
            "model_used": llm_response.get("model", "default"),
            "citations": citations,
            "tokens_prompt": llm_response.get("tokens_prompt", 0),
            "tokens_completion": llm_response.get("tokens_completion", 0),
            "total_tokens": llm_response.get("total_tokens", 0),
            "duration_ms": elapsed_ms,
        }
