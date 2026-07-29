from typing import Tuple, Dict, Any
import cv2
import numpy as np
from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin


class SharpenPlugin(IPreprocessingPlugin):
    """Sharpening plugin using Unsharp Masking kernel."""

    def __init__(self, enabled: bool = True, amount: float = 1.5):
        super().__init__(name="SharpenPlugin", enabled=enabled)
        self.amount = amount

    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Gaussian blur background for unsharp mask
        blurred = cv2.GaussianBlur(image, (0, 0), 3)
        sharpened = cv2.addWeighted(image, 1.0 + self.amount, blurred, -self.amount, 0)
        return sharpened, {"sharpen_amount": self.amount}
