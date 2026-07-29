import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import Conversation, ConversationMessage, Citation, TokenUsage
from src.services.vector_search_service import VectorSearchService
from src.infrastructure.rag.rag_engine import EnterpriseRAGEngine
from src.infrastructure.memory.conversation_manager import ConversationManager
from src.domain.interfaces.llm_provider import ILLMProvider
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter

logger = logging.getLogger("document_intelligence.rag_service")


class RAGService:
    """Service orchestrating multi-document Chat, RAG retrieval, Citation creation, and Conversation persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        rag_engine: Optional[EnterpriseRAGEngine] = None,
        search_service: Optional[VectorSearchService] = None,
    ):
        self.db = db_session
        self.search_service = search_service or VectorSearchService(db_session)
        self.rag_engine = rag_engine or EnterpriseRAGEngine()
        self.memory = ConversationManager()

    async def chat(
        self,
        session_id: str,
        user_message: str,
        document_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Full Chat & RAG Workflow:
        1. Retrieve relevant vector chunks via Hybrid Search.
        2. Format Context & Prompt Template.
        3. Invoke LLM Provider.
        4. Generate Inline Citations & Metadata.
        5. Persist ConversationMessage, Citations, and TokenUsage in PostgreSQL.
        """
        filters = {"document_id": str(document_id)} if document_id else None

        # 1. Retrieve Chunks via Hybrid Search Engine
        retrieved_chunks = await self.search_service.search(query=user_message, top_k=top_k, filters=filters)

        # 2. Get Memory Session History
        history = self.memory.format_history_for_llm(session_id)

        # 3. RAG Answer Generation
        rag_result = await self.rag_engine.answer_question(
            question=user_message,
            retrieved_chunks=retrieved_chunks,
            conversation_history=history,
        )

        answer_text = rag_result["answer"]
        citations = rag_result["citations"]

        # 4. Save Session Messages to Memory
        self.memory.add_message(session_id, "user", user_message)
        self.memory.add_message(
            session_id,
            "assistant",
            answer_text,
            citations=[{"page": c.page_number, "text": c.source_text} for c in citations],
        )

        # 5. Persist TokenUsage in PostgreSQL
        t_usage = TokenUsage(
            user_id=user_id,
            model_name=rag_result.get("model_used", "gpt-4o"),
            prompt_tokens=rag_result.get("tokens_prompt", 0),
            completion_tokens=rag_result.get("tokens_completion", 0),
            total_tokens=rag_result.get("total_tokens", 0),
            estimated_cost_usd=round(rag_result.get("total_tokens", 0) * 0.00001, 6),
        )
        self.db.add(t_usage)
        await self.db.commit()

        return {
            "session_id": session_id,
            "answer": answer_text,
            "citations": [
                {
                    "citation_index": c.citation_index,
                    "document_id": c.document_id,
                    "chunk_id": c.chunk_id,
                    "page_number": c.page_number,
                    "heading_context": c.heading_context,
                    "bbox": c.bbox,
                    "confidence": c.confidence,
                    "source_text": c.source_text,
                }
                for c in citations
            ],
            "tokens_used": rag_result.get("total_tokens", 0),
        }
