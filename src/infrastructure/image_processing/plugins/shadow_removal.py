from typing import Tuple, Dict, Any
import cv2
import numpy as np
from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin


class ShadowRemovalPlugin(IPreprocessingPlugin):
    """Shadow removal plugin using morphological background estimation and division normalization."""

    def __init__(self, enabled: bool = True, kernel_size: int = 21):
        super().__init__(name="ShadowRemovalPlugin", enabled=enabled)
        self.kernel_size = kernel_size

    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Convert to Grayscale
        is_color = len(image.shape) == 3
        if is_color:
            planes = cv2.split(image)
            normalized_planes = []
            for plane in planes:
                dilated = cv2.dilate(plane, np.ones((self.kernel_size, self.kernel_size), np.uint8))
                bg = cv2.medianBlur(dilated, self.kernel_size)
                diff = 255 - cv2.absdiff(plane, bg)
                norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
                normalized_planes.append(norm)
            output = cv2.merge(normalized_planes)
        else:
            dilated = cv2.dilate(image, np.ones((self.kernel_size, self.kernel_size), np.uint8))
            bg = cv2.medianBlur(dilated, self.kernel_size)
            diff = 255 - cv2.absdiff(image, bg)
            output = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        return output, {"kernel_size": self.kernel_size, "shadow_suppressed": True}
