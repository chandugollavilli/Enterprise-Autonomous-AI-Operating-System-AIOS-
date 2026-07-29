import pytest
from src.domain.sdk.plugin_sdk import IPluginSDK
from src.infrastructure.plugins.sandbox_manager import PluginSandboxManager


class MockPlugin(IPluginSDK):
    async def on_load(self) -> bool:
        return True

    async def on_unload(self) -> bool:
        return True

    async def on_event(self, event_name: str, payload: dict) -> bool:
        return True

    def manifest_info(self) -> dict:
        return {
            "id": "mock_plugin",
            "name": "Mock Sample Plugin",
            "permissions": ["document:read", "ocr:process"],
        }


@pytest.mark.asyncio
async def test_plugin_sandbox_manager():
    plugin = MockPlugin()
    assert PluginSandboxManager.validate_permissions(plugin) is True
    res = await PluginSandboxManager.execute_in_sandbox(plugin, "document.uploaded", {"doc_id": "123"})
    assert res is True
