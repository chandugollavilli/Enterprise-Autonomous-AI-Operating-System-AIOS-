from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Type, Tuple
import logging

logger = logging.getLogger("document_intelligence.plugin_registry")


@dataclass
class PluginMetadata:
    name: str
    category: str  # "preprocessing", "ocr", "layout", "exporter", "connector"
    version: str
    description: str = ""
    author: str = "Enterprise OCR Team"


class PluginRegistry:
    """Centralized Plugin Registry with auto-registration, versioning, and discovery."""

    _plugins: Dict[str, Tuple[PluginMetadata, Type]] = {}

    @classmethod
    def register(cls, metadata: PluginMetadata, plugin_cls: Type):
        key = f"{metadata.category}:{metadata.name}"
        cls._plugins[key] = (metadata, plugin_cls)
        logger.info(f"Registered Plugin: {key} (Version: {metadata.version})")

    @classmethod
    def get_plugin(cls, category: str, name: str) -> Optional[Tuple[PluginMetadata, Type]]:
        key = f"{category}:{name}"
        return cls._plugins.get(key)

    @classmethod
    def list_plugins(cls, category: Optional[str] = None) -> List[PluginMetadata]:
        if category:
            return [meta for meta, _ in cls._plugins.values() if meta.category == category]
        return [meta for meta, _ in cls._plugins.values()]
