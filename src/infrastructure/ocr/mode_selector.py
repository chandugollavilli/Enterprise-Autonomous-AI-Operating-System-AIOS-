import logging
from typing import Tuple
import numpy as np

from src.domain.interfaces.ocr_engine import IOCREngine
from src.infrastructure.ocr.base_engine import BaseOCREngine
from src.infrastructure.ocr.gundam_engine import GundamOCREngine
from src.config import settings

logger = logging.getLogger("document_intelligence.ocr_mode_selector")


class OCRModeSelector:
    """Automatic Resolution-based OCR Mode Selector (Base vs Gundam Mode)."""

    def __init__(self):
        self.base_engine = BaseOCREngine()
        self.gundam_engine = GundamOCREngine()

    def select_engine(self, image: np.ndarray, dpi: int = 300) -> Tuple[IOCREngine, str]:
        """
        Inspect image resolution & DPI:
        - If width or height > 4096px OR DPI > 400 -> Gundam High-Res Tile Engine
        - Otherwise -> Base Mode OCR Engine
        """
        h, w = image.shape[:2]
        max_dim = max(w, h)

        if max_dim > settings.OCR_GUNDAM_MAX_IMAGE_SIDE or dpi > settings.OCR_MODE_AUTO_SWITCH_DPI_THRESHOLD:
            logger.info(f"Auto-selected [Gundam Mode] for High-Res Image ({w}x{h}, DPI: {dpi})")
            return self.gundam_engine, "gundam"

        logger.info(f"Auto-selected [Base Mode] for Standard Image ({w}x{h}, DPI: {dpi})")
        return self.base_engine, "base"
