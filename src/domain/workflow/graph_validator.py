from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple, Optional
import logging

logger = logging.getLogger("document_intelligence.graph_validator")


@dataclass
class WorkflowNodeSpec:
    id: str
    type: str  # "import", "ocr", "classify", "rag", "approval", "export"
    name: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdgeSpec:
    id: str
    source_node_id: str
    target_node_id: str
    condition_expression: Optional[str] = None


class WorkflowGraphValidator:
    """Validates directed workflow graphs for cycles, orphan nodes, and schema compliance."""

    @staticmethod
    def validate_graph(nodes: List[WorkflowNodeSpec], edges: List[WorkflowEdgeSpec]) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not nodes:
            return False, ["Workflow graph contains no nodes."]

        node_ids: Set[str] = {n.id for n in nodes}

        # 1. Validate edge endpoint references
        adj_list: Dict[str, List[str]] = {n.id: [] for n in nodes}
        in_degree: Dict[str, int] = {n.id: 0 for n in nodes}

        for edge in edges:
            if edge.source_node_id not in node_ids:
                errors.append(f"Edge '{edge.id}' references non-existent source node '{edge.source_node_id}'.")
            if edge.target_node_id not in node_ids:
                errors.append(f"Edge '{edge.id}' references non-existent target node '{edge.target_node_id}'.")

            if edge.source_node_id in node_ids and edge.target_node_id in node_ids:
                adj_list[edge.source_node_id].append(edge.target_node_id)
                in_degree[edge.target_node_id] += 1

        if errors:
            return False, errors

        # 2. Check for start node (in_degree == 0)
        start_nodes = [nid for nid, deg in in_degree.items() if deg == 0]
        if not start_nodes:
            errors.append("Workflow graph has no entry/start node (potential cycle across all nodes).")

        # 3. Detect Cycles using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs_has_cycle(curr_id: str) -> bool:
            visited.add(curr_id)
            rec_stack.add(curr_id)

            for neighbor in adj_list.get(curr_id, []):
                if neighbor not in visited:
                    if dfs_has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(curr_id)
            return False

        for n in nodes:
            if n.id not in visited:
                if dfs_has_cycle(n.id):
                    errors.append(f"Circular dependency cycle detected involving node '{n.id}'.")
                    break

        # 4. Detect Orphan disconnected nodes
        for n in nodes:
            if len(nodes) > 1 and in_degree[n.id] == 0 and len(adj_list[n.id]) == 0:
                errors.append(f"Orphan disconnected node detected: '{n.id}' ({n.name}).")

        is_valid = len(errors) == 0
        return is_valid, errors
