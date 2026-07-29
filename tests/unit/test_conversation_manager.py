import pytest
from src.infrastructure.memory.conversation_manager import ConversationManager


def test_conversation_manager_memory_window():
    memory = ConversationManager(max_history_messages=4)
    session_id = "session_test_123"

    memory.add_message(session_id, "user", "Hello 1")
    memory.add_message(session_id, "assistant", "Hi 1")
    memory.add_message(session_id, "user", "Hello 2")
    memory.add_message(session_id, "assistant", "Hi 2")
    memory.add_message(session_id, "user", "Hello 3")

    history = memory.get_history(session_id)
    assert len(history) == 4
    assert history[0].content == "Hi 1"
    assert history[-1].content == "Hello 3"
