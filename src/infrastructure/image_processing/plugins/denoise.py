from typing import Tuple, Dict, Any
import cv2
import numpy as np
from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin


class NoiseReductionPlugin(IPreprocessingPlugin):
    """Noise reduction plugin using median filtering or Non-Local Means Denoising."""

    def __init__(self, enabled: bool = True, method: str = "median", kernel_size: int = 3):
        super().__init__(name="NoiseReductionPlugin", enabled=enabled)
        self.method = method
        self.kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1

    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        if self.method == "median":
            denoised = cv2.medianBlur(image, self.kernel_size)
        elif self.method == "fastNlMeans":
            if len(image.shape) == 3:
                denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            else:
                denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        else:
            denoised = cv2.GaussianBlur(image, (self.kernel_size, self.kernel_size), 0)

        return denoised, {"denoise_method": self.method, "kernel_size": self.kernel_size}
