from typing import Tuple, Dict, Any
import cv2
import numpy as np
from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin


class ContrastEnhancerPlugin(IPreprocessingPlugin):
    """Contrast enhancement plugin using Contrast Limited Adaptive Histogram Equalization (CLAHE)."""

    def __init__(self, enabled: bool = True, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)):
        super().__init__(name="ContrastEnhancerPlugin", enabled=enabled)
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size

    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

        if len(image.shape) == 3:
            # Convert to LAB color space and apply CLAHE to L-channel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_enhanced = clahe.apply(l)
            enhanced_lab = cv2.merge((l_enhanced, a, b))
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        else:
            enhanced = clahe.apply(image)

        return enhanced, {"clip_limit": self.clip_limit, "grid_size": self.tile_grid_size}
