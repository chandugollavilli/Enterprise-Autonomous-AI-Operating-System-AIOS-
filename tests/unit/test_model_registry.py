import pytest
from src.infrastructure.models.model_registry import ModelRegistry, ModelMetadata


def test_model_registry_registration_and_lookup():
    meta = ModelMetadata(
        name="custom_ocr_model",
        category="ocr",
        provider="CustomAI",
        version="v1.0",
        capabilities=["text_detection"],
    )
    ModelRegistry.register_model(meta)

    retrieved = ModelRegistry.get_model("ocr", "custom_ocr_model")
    assert retrieved is not None
    assert retrieved.name == "custom_ocr_model"
    assert retrieved.provider == "CustomAI"


def test_model_registry_default_selection():
    ModelRegistry.set_default("ocr", "custom_ocr_model")
    default_model = ModelRegistry.get_default("ocr")
    assert default_model is not None
    assert default_model.name == "custom_ocr_model"
