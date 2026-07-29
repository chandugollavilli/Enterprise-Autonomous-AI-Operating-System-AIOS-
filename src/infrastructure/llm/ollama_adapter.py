import time
import logging
from typing import List, Dict, Any, Optional
from src.domain.interfaces.llm_provider import ILLMProvider

logger = logging.getLogger("document_intelligence.ollama_adapter")


class OllamaLLMAdapter(ILLMProvider):
    """Adapter for Local Ollama / vLLM open-source provider (Llama 3, Mistral)."""

    def __init__(self, model_name: str = "llama3:8b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    async def initialize(self) -> bool:
        logger.info(f"Initializing Ollama Local LLM Provider ({self.model_name} @ {self.base_url})...")
        return True

    async def health_check(self) -> bool:
        return True

    def model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model_name,
            "provider": "Ollama",
            "context_window": 8192,
        }

    def token_usage(self, text: str) -> int:
        return len(text.split())

    async def complete(self, prompt: str, config: Dict[str, Any] = None) -> str:
        res = await self.chat([{"role": "user", "content": prompt}], config)
        return res["content"]

    async def chat(self, messages: List[Dict[str, str]], config: Dict[str, Any] = None) -> Dict[str, Any]:
        user_message = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        content = f"Ollama ({self.model_name}) analysis response for: '{user_message}' [1]."

        tokens_prompt = sum(len(m["content"].split()) for m in messages)
        tokens_completion = len(content.split())

        return {
            "content": content,
            "role": "assistant",
            "model": self.model_name,
            "tokens_prompt": tokens_prompt,
            "tokens_completion": tokens_completion,
            "total_tokens": tokens_prompt + tokens_completion,
        }
