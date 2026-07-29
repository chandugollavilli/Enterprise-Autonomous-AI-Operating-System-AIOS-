import cv2
import numpy as np
import pytest

from src.infrastructure.ocr.base_engine import BaseOCREngine
from src.infrastructure.ocr.gundam_engine import GundamOCREngine


@pytest.mark.asyncio
async def test_base_ocr_engine_extraction():
    engine = BaseOCREngine()
    # Create synthetic image with text lines
    img = np.full((300, 400, 3), 255, dtype=np.uint8)
    cv2.putText(img, "Line 1 Header", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, "Line 2 Paragraph", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    res = await engine.extract_text(img, config={"page_number": 1})
    assert res.ocr_mode == "base"
    assert res.page_number == 1
    assert len(res.boxes) > 0
    assert 0.0 <= res.boxes[0].box[0] <= 1.0


@pytest.mark.asyncio
async def test_gundam_ocr_engine_tile_extraction():
    engine = GundamOCREngine(tile_size=512, overlap=64)
    img = np.full((1200, 1200, 3), 255, dtype=np.uint8)
    cv2.putText(img, "Gundam High Res Title", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    res = await engine.extract_text(img, config={"page_number": 1})
    assert res.ocr_mode == "gundam"
    assert res.page_number == 1
    assert res.raw_layout["tiles_processed"] > 1
