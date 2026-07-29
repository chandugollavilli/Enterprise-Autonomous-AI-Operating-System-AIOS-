from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np


@dataclass
class OCRBox:
    box: List[float]  # [x1, y1, x2, y2] normalized 0.0 - 1.0
    text: str
    confidence: float
    line_num: int = 1


@dataclass
class OCRPageResult:
    page_number: int
    full_text: str
    boxes: List[OCRBox] = field(default_factory=list)
    ocr_mode: str = "base"  # "base" or "gundam"
    processing_time_ms: int = 0
    raw_layout: Dict[str, Any] = field(default_factory=dict)
    tables: Dict[str, Any] = field(default_factory=dict)


class IOCREngine(ABC):
    """Standardized Abstract Interface for Enterprise Multi-OCR Engines."""

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize engine resources."""
        pass

    @abstractmethod
    async def extract_text(self, image: np.ndarray, config: Dict[str, Any] = None) -> OCRPageResult:
        """Execute text detection and recognition on image."""
        pass

    @abstractmethod
    async def process_page(self, image: np.ndarray, config: Dict[str, Any] = None) -> OCRPageResult:
        """Process page alias."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check engine health and readiness."""
        pass

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported image formats."""
        pass

    @abstractmethod
    def version(self) -> str:
        """Return engine version string."""
        pass
