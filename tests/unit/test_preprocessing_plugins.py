import cv2
import numpy as np
import pytest

from src.infrastructure.image_processing.plugins.deskew import DeskewPlugin
from src.infrastructure.image_processing.plugins.denoise import NoiseReductionPlugin
from src.infrastructure.image_processing.plugins.contrast import ContrastEnhancerPlugin
from src.infrastructure.image_processing.plugins.shadow_removal import ShadowRemovalPlugin
from src.infrastructure.image_processing.plugins.sharpen import SharpenPlugin
from src.infrastructure.image_processing.pipeline import PreprocessingPipeline


@pytest.fixture
def sample_bgr_image():
    # Create synthetic 200x200 BGR document image with text rectangle
    img = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.putText(img, "TEST OCR", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    return img


def test_deskew_plugin(sample_bgr_image):
    plugin = DeskewPlugin()
    out, metrics = plugin.process(sample_bgr_image, {})
    assert out.shape == sample_bgr_image.shape
    assert metrics["plugin"] == "DeskewPlugin"
    assert "skew_angle" in metrics


def test_denoise_plugin(sample_bgr_image):
    plugin = NoiseReductionPlugin(method="median", kernel_size=3)
    out, metrics = plugin.process(sample_bgr_image, {})
    assert out.shape == sample_bgr_image.shape
    assert metrics["status"] == "success"


def test_contrast_plugin(sample_bgr_image):
    plugin = ContrastEnhancerPlugin(clip_limit=2.0)
    out, metrics = plugin.process(sample_bgr_image, {})
    assert out.shape == sample_bgr_image.shape
    assert metrics["status"] == "success"


def test_shadow_removal_plugin(sample_bgr_image):
    plugin = ShadowRemovalPlugin()
    out, metrics = plugin.process(sample_bgr_image, {})
    assert out.shape == sample_bgr_image.shape
    assert metrics["status"] == "success"


def test_sharpen_plugin(sample_bgr_image):
    plugin = SharpenPlugin(amount=1.5)
    out, metrics = plugin.process(sample_bgr_image, {})
    assert out.shape == sample_bgr_image.shape
    assert metrics["status"] == "success"


def test_preprocessing_pipeline_execution(sample_bgr_image):
    pipeline = PreprocessingPipeline([
        DeskewPlugin(),
        NoiseReductionPlugin(),
        ContrastEnhancerPlugin(),
        SharpenPlugin(),
    ])
    processed, metrics = pipeline.execute(sample_bgr_image)
    assert processed.shape == sample_bgr_image.shape
    assert len(metrics["plugins_executed"]) == 4
