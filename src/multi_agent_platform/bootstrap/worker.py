from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.service import ModelProviderService


@dataclass(slots=True)
class WorkerBootstrap:
    container: Container
    worker_id: str
    gateway_dependencies_ready: bool
    gateway_dependency_status: dict[str, bool]
    model_gateway_factory: Callable[[AsyncSession], ModelGateway] | None
    model_provider_service_factory: (
        Callable[[AsyncSession], ModelProviderService] | None
    )
    retry_decision_helper: object | None
    breaker_decision_helper: object | None
    skill_registry_lifecycle_ready: bool = False


def build_worker_bootstrap(container: Container) -> WorkerBootstrap:
    status = {
        "model_provider_repository_factory": (
            container.model_provider_repository_factory is not None
        ),
        "model_provider_service_factory": (
            container.model_provider_service_factory is not None
        ),
        "provider_adapter_registry_factory": (
            container.provider_adapter_registry_factory is not None
        ),
        "model_gateway_factory": container.model_gateway_factory is not None,
        "provider_secret_resolver_factory": (
            container.provider_secret_resolver_factory is not None
        ),
        "gateway_metrics_hooks": container.gateway_metrics_hooks is not None,
        "gateway_tracing_hooks": container.gateway_tracing_hooks is not None,
        "gateway_audit_hooks": container.gateway_audit_hooks is not None,
        "retry_decision_helper": container.retry_decision_helper is not None,
        "breaker_decision_helper": container.breaker_decision_helper is not None,
    }
    return WorkerBootstrap(
        container=container,
        worker_id=f"worker-{uuid4().hex[:12]}",
        gateway_dependencies_ready=all(status.values()),
        gateway_dependency_status=status,
        model_gateway_factory=container.model_gateway_factory,
        model_provider_service_factory=container.model_provider_service_factory,
        retry_decision_helper=container.retry_decision_helper,
        breaker_decision_helper=container.breaker_decision_helper,
        skill_registry_lifecycle_ready=True,
    )
