from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.config.settings import Settings


async def test_build_container_uses_selected_providers(settings: Settings) -> None:
    container = build_container(settings)
    try:
        assert container.secret_provider.provider_name == "static"
        assert container.storage_provider.provider_name == "filesystem"
        assert container.logger.name == "multi_agent_platform"
        search_path = container.workflow_ui_templates.env.loader.searchpath
        assert any(path.endswith("/templates") for path in search_path)
    finally:
        await container.dispose()
