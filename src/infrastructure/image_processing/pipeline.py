import logging
from typing import List, Dict, Any, Tuple
import numpy as np

from src.infrastructure.image_processing.plugins.base import IPreprocessingPlugin
from src.infrastructure.image_processing.plugins.deskew import DeskewPlugin
from src.infrastructure.image_processing.plugins.denoise import NoiseReductionPlugin
from src.infrastructure.image_processing.plugins.contrast import ContrastEnhancerPlugin
from src.infrastructure.image_processing.plugins.shadow_removal import ShadowRemovalPlugin
from src.infrastructure.image_processing.plugins.sharpen import SharpenPlugin

logger = logging.getLogger("document_intelligence.preprocessing_pipeline")


class PreprocessingPipeline:
    """Configurable plugin-based image preprocessing pipeline."""

    def __init__(self, plugins: List[IPreprocessingPlugin] = None):
        self.plugins: List[IPreprocessingPlugin] = plugins or [
            DeskewPlugin(enabled=True),
            NoiseReductionPlugin(enabled=True),
            ContrastEnhancerPlugin(enabled=True),
            ShadowRemovalPlugin(enabled=False),  # Optional background shadow removal
            SharpenPlugin(enabled=True),
        ]

    def add_plugin(self, plugin: IPreprocessingPlugin) -> None:
        self.plugins.append(plugin)

    def execute(self, image: np.ndarray, config: Dict[str, Any] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Sequentially execute registered plugin chain on image.
        Returns: (processed_image, accumulated_metrics)
        """
        config = config or {}
        current_image = image.copy()
        pipeline_metrics: Dict[str, Any] = {"plugins_executed": []}

        for plugin in self.plugins:
            current_image, plugin_metrics = plugin.process(current_image, config)
            pipeline_metrics["plugins_executed"].append(plugin_metrics)

        return current_image, pipeline_metrics
