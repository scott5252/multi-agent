from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    ErrorCategory,
    GatewayResult,
    HealthState,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
)


@dataclass(frozen=True, slots=True)
class GatewayInvocationContext:
    tenant_id: UUID | None
    trace_id: str | None = None
    workflow_run_id: UUID | None = None
    test_bench_run_id: UUID | None = None
    idempotency_key: str | None = None


class ModelGateway:
    def __init__(
        self,
        *,
        repository: ModelProviderRepository,
        registry: ProviderAdapterRegistry,
    ) -> None:
        self._repository = repository
        self._registry = registry

    async def invoke(
        self,
        *,
        connection_id: UUID,
        model_id: str,
        messages: tuple[dict[str, str], ...],
        context: GatewayInvocationContext,
        credential: str | None = None,
    ) -> GatewayResult:
        connection = await self._repository.get_connection(connection_id)
        if not connection.active or connection.health_state is not HealthState.HEALTHY:
            result = GatewayResult(
                outcome=TestOutcome.FAILURE,
                normalized_error_category=ErrorCategory.CATALOG_INACTIVE,
                safe_audit_summary={
                    "tenant_id": str(context.tenant_id) if context.tenant_id else None,
                    "connection_id": str(connection.provider_connection_id),
                    "model_id": model_id,
                    "result": ErrorCategory.CATALOG_INACTIVE.value,
                },
            )
            await self._repository.record_gateway_attempt(
                tenant_id=context.tenant_id,
                provider_type=connection.provider_type,
                provider_connection_id=connection.provider_connection_id,
                model_id=model_id,
                result=result,
                workflow_run_id=context.workflow_run_id,
                test_bench_run_id=context.test_bench_run_id,
                trace_id=context.trace_id,
                idempotency_key=context.idempotency_key,
            )
            return result
        adapter = self._registry.get(connection.provider_type)
        response = await adapter.chat_completion(
            AdapterRequest(
                model_id=model_id,
                messages=messages,
                timeout_policy=TimeoutPolicy.model_validate(connection.timeout_policy),
                base_url=connection.base_url_safe,
                credential=credential,
            )
        )
        result = GatewayResult(
            outcome=response.outcome,
            content=response.content,
            normalized_error_category=response.normalized_error_category,
            latency_ms=response.latency_ms,
            usage=response.usage,
            safe_audit_summary={
                "tenant_id": str(context.tenant_id) if context.tenant_id else None,
                "connection_id": str(connection.provider_connection_id),
                "provider_type": connection.provider_type.value,
                "model_id": model_id,
                "outcome": response.outcome.value,
                "error_category": response.normalized_error_category.value,
                "latency_ms": response.latency_ms,
                "usage_available": response.usage.availability.value,
            },
        )
        await self._repository.record_gateway_attempt(
            tenant_id=context.tenant_id,
            provider_type=connection.provider_type,
            provider_connection_id=connection.provider_connection_id,
            model_id=model_id,
            result=result,
            workflow_run_id=context.workflow_run_id,
            test_bench_run_id=context.test_bench_run_id,
            trace_id=context.trace_id,
            idempotency_key=context.idempotency_key,
        )
        return result


def provider_type_for_catalog_key(provider_key: str) -> ProviderType:
    if provider_key == ProviderType.LOCAL_OPENAI_COMPATIBLE.value:
        return ProviderType.LOCAL_OPENAI_COMPATIBLE
    return ProviderType.OPENAI
