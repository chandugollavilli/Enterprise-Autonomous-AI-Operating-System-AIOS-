from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("document_intelligence.model_registry")


@dataclass
class ModelMetadata:
    name: str
    category: str  # "ocr", "embedding", "llm", "reranker"
    provider: str
    version: str
    capabilities: List[str] = field(default_factory=list)
    is_default: bool = False
    health_status: str = "healthy"


class ModelRegistry:
    """Centralized Model Registry for dynamic selection and lookup of AI models."""

    _models: Dict[str, ModelMetadata] = {}

    @classmethod
    def register_model(cls, metadata: ModelMetadata):
        key = f"{metadata.category}:{metadata.name}"
        cls._models[key] = metadata
        logger.info(f"Registered AI Model: {key} (Provider: {metadata.provider}, Version: {metadata.version})")

    @classmethod
    def get_model(cls, category: str, name: str) -> Optional[ModelMetadata]:
        key = f"{category}:{name}"
        return cls._models.get(key)

    @classmethod
    def list_models(cls, category: Optional[str] = None) -> List[ModelMetadata]:
        if category:
            return [m for m in cls._models.values() if m.category == category]
        return list(cls._models.values())

    @classmethod
    def set_default(cls, category: str, name: str):
        for m in cls._models.values():
            if m.category == category:
                m.is_default = (m.name == name)

    @classmethod
    def get_default(cls, category: str) -> Optional[ModelMetadata]:
        for m in cls._models.values():
            if m.category == category and m.is_default:
                return m
        # Fallback to first model in category if no default set
        models_in_cat = cls.list_models(category)
        return models_in_cat[0] if models_in_cat else None


# Register Default System Models
ModelRegistry.register_model(
    ModelMetadata(
        name="baidu_unlimited_ocr",
        category="ocr",
        provider="Baidu",
        version="v2.8",
        capabilities=["text_detection", "text_recognition", "table_parsing", "gundam_multitile"],
        is_default=True,
    )
)
ModelRegistry.register_model(
    ModelMetadata(
        name="tesseract_ocr",
        category="ocr",
        provider="OpenSource",
        version="v5.3",
        capabilities=["text_detection", "text_recognition"],
        is_default=False,
    )
)
ModelRegistry.register_model(
    ModelMetadata(
        name="bge_m3_embedding",
        category="embedding",
        provider="BAAI",
        version="v1.0",
        capabilities=["dense_embeddings", "sparse_embeddings", "multi_linguality"],
        is_default=True,
    )
)
