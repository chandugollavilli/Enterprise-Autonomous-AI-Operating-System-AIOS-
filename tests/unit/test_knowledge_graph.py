import pytest
from src.infrastructure.aios.knowledge_graph import EnterpriseKnowledgeGraph


def test_enterprise_knowledge_graph_traversal():
    kg = EnterpriseKnowledgeGraph()
    kg.add_node("doc_1", "Vendor Contract.pdf", "Contract")
    kg.add_node("party_1", "Acme Corp", "Company")
    kg.add_edge("doc_1", "party_1", "SIGNED_BY")

    matches = kg.search_entity("Vendor Contract")
    assert len(matches) == 1
    assert matches[0]["node_id"] == "doc_1"

    relationships = kg.traverse_relationships("doc_1")
    assert len(relationships) == 1
    assert relationships[0]["relationship"] == "SIGNED_BY"
    assert relationships[0]["target"]["label"] == "Acme Corp"
