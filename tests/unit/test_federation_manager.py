import pytest
from src.infrastructure.platform.federation_manager import GlobalFederationManager


def test_global_federation_manager():
    fed = GlobalFederationManager()
    regions = fed.get_regions()
    assert len(regions) >= 3

    routed_eu = fed.route_request("eu-west-1")
    assert routed_eu["region_id"] == "eu-west-1"
    assert routed_eu["cloud_provider"] == "Azure"
