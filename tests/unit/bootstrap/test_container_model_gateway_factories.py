from __future__ import annotations

from pathlib import Path

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.service import ModelProviderService


async def test_container_exposes_managed_model_gateway_factories(settings) -> None:
    container = build_container(settings)
    try:
        async with container.session_factory() as session:
            repository = container.model_provider_repository_factory(session)
            service = container.model_provider_service_factory(session)
            gateway = container.model_gateway_factory(session)
            secret_resolver = container.provider_secret_resolver_factory(session)

        assert isinstance(repository, ModelProviderRepository)
        assert isinstance(service, ModelProviderService)
        assert isinstance(gateway, ModelGateway)
        assert isinstance(
            container.provider_adapter_registry_factory(),
            ProviderAdapterRegistry,
        )
        assert secret_resolver is not None
        assert container.gateway_metrics_hooks is not None
        assert container.gateway_tracing_hooks is not None
        assert container.gateway_audit_hooks is not None
        assert container.retry_decision_helper is not None
        assert container.breaker_decision_helper is not None
    finally:
        await container.dispose()


def test_admin_provider_routes_do_not_create_unmanaged_http_clients() -> None:
    source = Path(
        "src/multi_agent_platform/api/routers/admin_model_providers.py"
    ).read_text()

    assert "httpx.AsyncClient(" not in source
