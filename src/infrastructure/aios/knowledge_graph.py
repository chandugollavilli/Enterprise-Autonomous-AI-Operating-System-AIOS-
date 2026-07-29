import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("document_intelligence.knowledge_graph")


class EnterpriseKnowledgeGraph:
    """Enterprise Knowledge Graph representing Entities, Documents, Contracts, Departments, and Relationships."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, label: str, node_type: str, properties: Optional[Dict[str, Any]] = None):
        self.nodes[node_id] = {
            "node_id": node_id,
            "label": label,
            "type": node_type,
            "properties": properties or {},
        }

    def add_edge(self, source_id: str, target_id: str, relationship: str, properties: Optional[Dict[str, Any]] = None):
        self.edges.append({
            "source_id": source_id,
            "target_id": target_id,
            "relationship": relationship,
            "properties": properties or {},
        })

    def search_entity(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        matches = []
        for node in self.nodes.values():
            if query_lower in node["label"].lower() or query_lower in node["type"].lower():
                matches.append(node)
        return matches

    def traverse_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        connected = []
        for edge in self.edges:
            if edge["source_id"] == node_id:
                target_node = self.nodes.get(edge["target_id"])
                connected.append({"relationship": edge["relationship"], "target": target_node})
        return connected
