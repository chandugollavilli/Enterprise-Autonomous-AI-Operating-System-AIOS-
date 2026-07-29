import pytest
from src.infrastructure.llm.openai_adapter import OpenAILLMAdapter
from src.infrastructure.llm.ollama_adapter import OllamaLLMAdapter


@pytest.mark.asyncio
async def test_openai_llm_adapter():
    adapter = OpenAILLMAdapter()
    await adapter.initialize()

    info = adapter.model_info()
    assert info["provider"] == "OpenAI"

    messages = [{"role": "user", "content": "What are the payment terms in section 2?"}]
    res = await adapter.chat(messages)

    assert "content" in res
    assert res["role"] == "assistant"
    assert res["total_tokens"] > 0


@pytest.mark.asyncio
async def test_ollama_llm_adapter():
    adapter = OllamaLLMAdapter()
    res = await adapter.chat([{"role": "user", "content": "Summarize key contract risks."}])
    assert "Ollama" in res["content"]
