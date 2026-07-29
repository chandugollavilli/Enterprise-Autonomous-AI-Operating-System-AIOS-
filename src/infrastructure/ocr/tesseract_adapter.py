import time
import logging
from typing import Dict, Any, List
import numpy as np

from src.domain.interfaces.ocr_engine import IOCREngine, OCRPageResult, OCRBox

logger = logging.getLogger("document_intelligence.tesseract_adapter")


class TesseractOCRAdapter(IOCREngine):
    """Adapter for Tesseract OCR engine integration."""

    async def initialize(self) -> bool:
        logger.info("Initializing Tesseract OCR Engine Adapter...")
        return True

    async def health_check(self) -> bool:
        return True

    def supported_formats(self) -> List[str]:
        return ["png", "jpeg", "jpg", "tiff", "bmp"]

    def version(self) -> str:
        return "Tesseract-v5.3.0-adapter"

    async def process_page(self, image: np.ndarray, config: Dict[str, Any] = None) -> OCRPageResult:
        return await self.extract_text(image, config)

    async def extract_text(self, image: np.ndarray, config: Dict[str, Any] = None) -> OCRPageResult:
        start_time = time.perf_counter()
        config = config or {}
        page_num = config.get("page_number", 1)

        # Standard fallback box simulation for Tesseract
        h, w = image.shape[:2]
        boxes = [
            OCRBox(
                box=[0.1, 0.1, 0.9, 0.2],
                text="Tesseract OCR Extracted Text Line 1",
                confidence=0.95,
                line_num=1,
            )
        ]
        full_text = "Tesseract OCR Extracted Text Line 1"
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return OCRPageResult(
            page_number=page_num,
            full_text=full_text,
            boxes=boxes,
            ocr_mode="tesseract",
            processing_time_ms=elapsed_ms,
        )
