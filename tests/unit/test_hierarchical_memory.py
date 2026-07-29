import pytest
from src.infrastructure.aios.memory_system import HierarchicalMemoryService


def test_hierarchical_memory_storage_and_retrieval():
    mem = HierarchicalMemoryService()
    mem.store_memory("conversation", "User requested invoice total verification.")
    mem.store_memory("long_term", "Acme Corp payment terms are strictly Net 30.")

    res_all = mem.query_memory("verification")
    assert len(res_all) == 1

    res_lt = mem.query_memory("Net 30", memory_type="long_term")
    assert len(res_lt) == 1
    assert res_lt[0]["memory_type"] == "long_term"
