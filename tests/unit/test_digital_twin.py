import pytest
from src.infrastructure.platform.digital_twin import DigitalTwinEngine


def test_digital_twin_topology():
    dt = DigitalTwinEngine()
    topology = dt.get_topology()

    assert topology["system_health"] == "operational"
    assert len(topology["nodes"]) >= 3
    assert len(topology["edges"]) >= 1
