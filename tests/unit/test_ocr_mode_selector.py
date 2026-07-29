import numpy as np
import pytest

from src.infrastructure.ocr.mode_selector import OCRModeSelector


def test_mode_selector_base_mode():
    selector = OCRModeSelector()
    # Standard 800x600 image at 300 DPI -> Base Mode
    img_standard = np.zeros((600, 800, 3), dtype=np.uint8)
    engine, mode_name = selector.select_engine(img_standard, dpi=300)
    assert mode_name == "base"


def test_mode_selector_gundam_mode_high_dim():
    selector = OCRModeSelector()
    # High-Res 5000x3000 image -> Gundam Mode
    img_large = np.zeros((3000, 5000, 3), dtype=np.uint8)
    engine, mode_name = selector.select_engine(img_large, dpi=300)
    assert mode_name == "gundam"


def test_mode_selector_gundam_mode_high_dpi():
    selector = OCRModeSelector()
    # Standard dimensions but High DPI (600 DPI blueprint) -> Gundam Mode
    img_standard = np.zeros((1000, 1000, 3), dtype=np.uint8)
    engine, mode_name = selector.select_engine(img_standard, dpi=600)
    assert mode_name == "gundam"
