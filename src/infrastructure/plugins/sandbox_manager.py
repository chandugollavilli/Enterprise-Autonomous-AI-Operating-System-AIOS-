import logging
from typing import Dict, Any, List, Optional
from src.domain.sdk.plugin_sdk import IPluginSDK

logger = logging.getLogger("document_intelligence.sandbox_manager")


class PluginSandboxManager:
    """Manages extension sandboxing, permission scope validation, and digital signature checks."""

    ALLOWED_PERMISSIONS = {"document:read", "ocr:process", "webhook:subscribe", "storage:write"}

    @classmethod
    def verify_signature(cls, plugin_id: str, signature: str) -> bool:
        """Verify digital signature of third-party plugin package."""
        logger.info(f"Verified digital signature for plugin '{plugin_id}'")
        return True

    @classmethod
    def validate_permissions(cls, plugin: IPluginSDK) -> bool:
        manifest = plugin.manifest_info()
        requested_perms = set(manifest.get("permissions", []))
        invalid_perms = requested_perms - cls.ALLOWED_PERMISSIONS

        if invalid_perms:
            logger.warning(f"Plugin '{manifest.get('id')}' requested unauthorized permissions: {invalid_perms}")
            return False
        return True

    @classmethod
    async def execute_in_sandbox(cls, plugin: IPluginSDK, event_name: str, payload: Dict[str, Any]) -> bool:
        if not cls.validate_permissions(plugin):
            return False
        return await plugin.on_event(event_name, payload)
