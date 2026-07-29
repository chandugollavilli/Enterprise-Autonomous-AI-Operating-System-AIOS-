from typing import Tuple, Dict, Any
import cv2
import numpy as np
from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin


class DeskewPlugin(IPreprocessingPlugin):
    """Deskew plugin using minimum area bounding rectangle angle detection."""

    def __init__(self, enabled: bool = True, max_skew_angle: float = 45.0):
        super().__init__(name="DeskewPlugin", enabled=enabled)
        self.max_skew_angle = max_skew_angle

    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Convert to Grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Threshold to binary inverted image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Find non-zero pixel coordinates
        coords = np.column_stack(np.where(thresh > 0))
        if coords.shape[0] == 0:
            return image, {"skew_angle": 0.0, "deskewed": False}

        # Calculate minimum bounding rectangle
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]

        # Normalize angle to [-45, 45] range
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # If angle exceeds max skew threshold or is negligible, skip rotation
        if abs(angle) < 0.2 or abs(angle) > self.max_skew_angle:
            return image, {"skew_angle": round(float(angle), 2), "deskewed": False}

        # Apply Affine Rotation Matrix
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )

        return deskewed, {
            "skew_angle": round(float(angle), 2),
            "deskewed": True,
        }
