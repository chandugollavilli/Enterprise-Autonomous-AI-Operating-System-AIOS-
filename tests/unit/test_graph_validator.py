import pytest
from src.domain.workflow.graph_validator import WorkflowGraphValidator, WorkflowNodeSpec, WorkflowEdgeSpec


def test_valid_directed_graph():
    nodes = [
        WorkflowNodeSpec(id="n1", type="import", name="Import Node"),
        WorkflowNodeSpec(id="n2", type="ocr", name="OCR Node"),
        WorkflowNodeSpec(id="n3", type="export", name="Export Node"),
    ]
    edges = [
        WorkflowEdgeSpec(id="e1", source_node_id="n1", target_node_id="n2"),
        WorkflowEdgeSpec(id="e2", source_node_id="n2", target_node_id="n3"),
    ]

    is_valid, errors = WorkflowGraphValidator.validate_graph(nodes, edges)
    assert is_valid is True
    assert len(errors) == 0


def test_graph_cycle_detection():
    nodes = [
        WorkflowNodeSpec(id="n1", type="import", name="Import Node"),
        WorkflowNodeSpec(id="n2", type="ocr", name="OCR Node"),
    ]
    # Edge loop n1 -> n2 -> n1
    edges = [
        WorkflowEdgeSpec(id="e1", source_node_id="n1", target_node_id="n2"),
        WorkflowEdgeSpec(id="e2", source_node_id="n2", target_node_id="n1"),
    ]

    is_valid, errors = WorkflowGraphValidator.validate_graph(nodes, edges)
    assert is_valid is False
    assert any("cycle" in e.lower() for e in errors)
