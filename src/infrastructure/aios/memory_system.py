import logging
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger("document_intelligence.memory_system")


class HierarchicalMemoryService:
    """Manages Conversation Memory, Workflow Memory, Department Memory, and Long-Term Semantic Memory."""

    def __init__(self):
        self._memory_records: List[Dict[str, Any]] = []

    def store_memory(
        self,
        memory_type: str,  # "conversation", "workflow", "department", "long_term"
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "record_id": f"mem_{len(self._memory_records) + 1}",
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self._memory_records.append(record)
        logger.info(f"Stored {memory_type} memory record '{record['record_id']}'")
        return record

    def query_memory(self, query: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        for rec in self._memory_records:
            if memory_type and rec["memory_type"] != memory_type:
                continue
            if query_lower in rec["content"].lower():
                results.append(rec)
        return results
