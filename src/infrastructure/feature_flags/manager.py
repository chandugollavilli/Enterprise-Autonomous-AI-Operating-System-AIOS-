from typing import Dict, Any
import logging

logger = logging.getLogger("document_intelligence.feature_flags")


class FeatureFlagManager:
    """Environment and runtime-configurable Feature Flag Manager."""

    _flags: Dict[str, bool] = {
        "ocr.gundam_mode_enabled": True,
        "ocr.tesseract_enabled": True,
        "ocr.easyocr_enabled": True,
        "export.docx_enabled": False,
        "human_review.low_confidence_flagging": True,
        "analytics.enabled": True,
    }

    @classmethod
    def is_enabled(cls, flag_name: str, default: bool = False) -> bool:
        return cls._flags.get(flag_name, default)

    @classmethod
    def set_flag(cls, flag_name: str, enabled: bool):
        cls._flags[flag_name] = enabled
        logger.info(f"Feature Flag Updated: '{flag_name}' = {enabled}")

    @classmethod
    def list_flags(cls) -> Dict[str, bool]:
        return dict(cls._flags)
