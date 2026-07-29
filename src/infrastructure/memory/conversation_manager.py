import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("document_intelligence.conversation_manager")


@dataclass
class ChatMessageDTO:
    role: str  # "user", "assistant", "system"
    content: str
    citations: List[Dict[str, Any]] = field(default_factory=list)


class ConversationManager:
    """Manages chat session history memory, sliding context windows, and referenced documents."""

    def __init__(self, max_history_messages: int = 10):
        self.max_history_messages = max_history_messages
        self._sessions: Dict[str, List[ChatMessageDTO]] = {}

    def get_history(self, session_id: str) -> List[ChatMessageDTO]:
        return self._sessions.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str, citations: List[Dict[str, Any]] = None):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        msg = ChatMessageDTO(role=role, content=content, citations=citations or [])
        self._sessions[session_id].append(msg)

        # Enforce sliding memory window limit
        if len(self._sessions[session_id]) > self.max_history_messages:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history_messages :]

    def format_history_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        messages = self.get_history(session_id)
        return [{"role": m.role, "content": m.content} for m in messages]

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
