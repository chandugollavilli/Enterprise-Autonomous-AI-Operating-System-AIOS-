import cv2
import numpy as np
import pytest

from src.infrastructure.image_processing.quality_analyzer import ImageQualityAnalyzer, ImageClassifier
from src.infrastructure.image_processing.thumbnail_generator import ThumbnailGenerator


@pytest.fixture
def test_image():
    img = np.full((300, 400, 3), 240, dtype=np.uint8)
    cv2.circle(img, (150, 150), 50, (0, 0, 255), -1)
    return img


def test_quality_analyzer_metrics(test_image):
    metrics = ImageQualityAnalyzer.analyze(test_image)
    assert "blur_score" in metrics
    assert "brightness" in metrics
    assert "contrast" in metrics
    assert metrics["width"] == 400
    assert metrics["height"] == 300


def test_image_classifier(test_image):
    cls_type = ImageClassifier.classify(test_image, text_content="Payment Invoice Total: $500")
    assert cls_type == "invoice"

    drawing_img = np.zeros((4000, 2000, 3), dtype=np.uint8)
    drawing_type = ImageClassifier.classify(drawing_img)
    assert drawing_type == "engineering_drawing"


def test_thumbnail_generator(test_image):
    thumbs = ThumbnailGenerator.generate_thumbnails(test_image)
    assert "small" in thumbs
    assert "medium" in thumbs
    assert "large" in thumbs
    assert len(thumbs["small"]) > 0
    assert len(thumbs["medium"]) > 0
