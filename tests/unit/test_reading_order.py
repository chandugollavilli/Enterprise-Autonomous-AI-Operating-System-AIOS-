import pytest
from src.domain.layout.canonical_model import CanonicalNode, NodeType
from src.infrastructure.layout.reading_order import ReadingOrderEngine


def test_single_column_reading_order():
    n1 = CanonicalNode(text="Header Line", bbox=[0.1, 0.1, 0.9, 0.2])
    n2 = CanonicalNode(text="Middle Paragraph", bbox=[0.1, 0.4, 0.9, 0.5])
    n3 = CanonicalNode(text="Footer Line", bbox=[0.1, 0.8, 0.9, 0.9])

    unordered = [n2, n3, n1]
    sorted_nodes = ReadingOrderEngine.sort_nodes(unordered)

    assert sorted_nodes[0].text == "Header Line"
    assert sorted_nodes[1].text == "Middle Paragraph"
    assert sorted_nodes[2].text == "Footer Line"
    assert sorted_nodes[0].reading_order == 1
    assert sorted_nodes[2].reading_order == 3


def test_two_column_reading_order():
    left1 = CanonicalNode(text="Left Col Top", bbox=[0.05, 0.2, 0.45, 0.3])
    left2 = CanonicalNode(text="Left Col Bottom", bbox=[0.05, 0.5, 0.45, 0.6])
    right1 = CanonicalNode(text="Right Col Top", bbox=[0.55, 0.2, 0.95, 0.3])
    right2 = CanonicalNode(text="Right Col Bottom", bbox=[0.55, 0.5, 0.95, 0.6])

    unordered = [right2, left2, right1, left1]
    sorted_nodes = ReadingOrderEngine.sort_nodes(unordered, column_threshold=0.5)

    assert sorted_nodes[0].text == "Left Col Top"
    assert sorted_nodes[1].text == "Left Col Bottom"
    assert sorted_nodes[2].text == "Right Col Top"
    assert sorted_nodes[3].text == "Right Col Bottom"
