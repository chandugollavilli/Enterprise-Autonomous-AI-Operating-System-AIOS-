import time
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import numpy as np

logger = logging.getLogger("document_intelligence.preprocessing")


class IPreprocessingPlugin(ABC):
    """Abstract Base Class for OpenCV/NumPy Image Preprocessing Plugins."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def apply(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Execute image transformation algorithm.
        Input: numpy ndarray BGR or Grayscale image.
        Output: Tuple (transformed_image, plugin_metrics_dict).
        """
        pass

    def process(self, image: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Execution wrapper with timing and metrics tracing."""
        if not self.enabled:
            return image, {"plugin": self.name, "status": "skipped"}

        start_time = time.perf_counter()
        try:
            output_image, metrics = self.apply(image, config)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            metrics.update({
                "plugin": self.name,
                "status": "success",
                "execution_time_ms": elapsed_ms,
            })
            return output_image, metrics
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"Plugin '{self.name}' failed: {e}", exc_info=True)
            return image, {
                "plugin": self.name,
                "status": "failed",
                "error": str(e),
                "execution_time_ms": elapsed_ms,
            }
