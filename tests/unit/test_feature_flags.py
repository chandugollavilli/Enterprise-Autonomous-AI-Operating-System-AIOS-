import pytest
from src.infrastructure.feature_flags.manager import FeatureFlagManager


def test_feature_flags_toggle():
    flag_name = "experimental.new_ocr_mode"
    assert FeatureFlagManager.is_enabled(flag_name, default=False) is False

    FeatureFlagManager.set_flag(flag_name, True)
    assert FeatureFlagManager.is_enabled(flag_name) is True

    flags = FeatureFlagManager.list_flags()
    assert flag_name in flags
    assert flags[flag_name] is True
