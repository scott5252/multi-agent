from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.model_providers.models import ProviderType


async def test_adapter_registry_lifecycle_is_owned_by_container(settings) -> None:
    container = build_container(settings)
    registry = container.provider_adapter_registry_factory()

    assert registry.get(ProviderType.OPENAI).provider_type is ProviderType.OPENAI
    assert registry.closed is False

    await container.dispose()

    assert registry.closed is True


async def test_container_secret_resolver_resolves_gateway_adapter_references(
    settings,
) -> None:
    container = build_container(settings)
    try:
        async with container.session_factory() as session:
            resolver = container.provider_secret_resolver_factory(session)
            credential = await resolver.resolve("example/api-key")

        assert credential.reference == "example/api-key"
        assert credential.value == "fixture-secret"
    finally:
        await container.dispose()
