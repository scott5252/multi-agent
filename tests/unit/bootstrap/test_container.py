from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.config.settings import Settings


async def test_build_container_uses_selected_providers(settings: Settings) -> None:
    container = build_container(settings)
    try:
        assert container.secret_provider.provider_name == "static"
        assert container.storage_provider.provider_name == "filesystem"
        assert container.logger.name == "multi_agent_platform"
    finally:
        await container.dispose()
