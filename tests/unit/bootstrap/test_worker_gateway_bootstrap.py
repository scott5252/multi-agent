from __future__ import annotations

from dataclasses import replace

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import build_worker_bootstrap


async def test_worker_bootstrap_exposes_gateway_ready_dependencies(settings) -> None:
    container = build_container(settings)
    try:
        bootstrap = build_worker_bootstrap(container)

        assert bootstrap.gateway_dependencies_ready is True
        assert all(bootstrap.gateway_dependency_status.values())
        assert bootstrap.model_gateway_factory is container.model_gateway_factory
        assert bootstrap.model_provider_service_factory is (
            container.model_provider_service_factory
        )
        assert bootstrap.retry_decision_helper is container.retry_decision_helper
        assert bootstrap.breaker_decision_helper is container.breaker_decision_helper
    finally:
        await container.dispose()


async def test_worker_bootstrap_fails_readiness_when_gateway_dependency_missing(
    settings,
) -> None:
    container = build_container(settings)
    try:
        broken = replace(container, model_gateway_factory=None)
        bootstrap = build_worker_bootstrap(broken)

        assert bootstrap.gateway_dependencies_ready is False
        assert bootstrap.gateway_dependency_status["model_gateway_factory"] is False
    finally:
        await container.dispose()
