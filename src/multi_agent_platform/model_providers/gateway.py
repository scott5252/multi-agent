from __future__ import annotations

from typing import Protocol
from uuid import UUID

from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    ErrorCategory,
    GatewayInvocationContext,
    GatewayResult,
    HealthState,
    ProviderType,
    TestOutcome,
    TimeoutPolicy,
)
from multi_agent_platform.reliability.breakers import gateway_breaker_summary
from multi_agent_platform.reliability.retries import gateway_retry_summary


class ModelGateway:
    def __init__(
        self,
        *,
        repository: ModelProviderRepository,
        registry: ProviderAdapterRegistry,
        usage_recorder: GatewayUsageRecorder | None = None,
    ) -> None:
        self._repository = repository
        self._registry = registry
        self._usage_recorder = usage_recorder

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
            old_attempt = await self._repository.record_gateway_attempt(
                tenant_id=context.tenant_id,
                provider_type=connection.provider_type,
                provider_connection_id=connection.provider_connection_id,
                model_id=model_id,
                result=result,
                workflow_run_id=context.workflow_run_id,
                test_bench_run_id=context.test_bench_run_id,
                trace_id=context.trace_id,
                idempotency_key=context.idempotency_key,
                workflow_run_step_id=context.workflow_run_step_id,
                workflow_validation_id=context.workflow_validation_id,
                retry_decision_summary={
                    "category": "skipped",
                    "stop_reason": ErrorCategory.CATALOG_INACTIVE.value,
                },
                breaker_scope=_breaker_scope(
                    connection.provider_connection_id,
                    model_id,
                ),
                breaker_decision_summary=_breaker_summary(
                    context=context,
                    connection_id=connection.provider_connection_id,
                    model_id=model_id,
                ),
            )
            await self._record_operation_attempt(
                context=context,
                connection_id=connection.provider_connection_id,
                model_id=model_id,
                result=result,
                retry_summary={"category": "skipped"},
                breaker_summary=_breaker_summary(
                    context=context,
                    connection_id=connection.provider_connection_id,
                    model_id=model_id,
                ),
                old_attempt_id=old_attempt.gateway_invocation_attempt_id
                if old_attempt is not None
                else None,
            )
            await self._record_usage_event(
                context=context,
                connection_id=connection.provider_connection_id,
                provider_type=connection.provider_type,
                model_id=model_id,
                result=result,
                old_attempt_id=old_attempt.gateway_invocation_attempt_id
                if old_attempt is not None
                else None,
            )
            return result
        operation = None
        if context.operation_identity and hasattr(
            self._repository,
            "get_or_create_gateway_operation",
        ):
            operation, created = await self._repository.get_or_create_gateway_operation(
                operation_identity=context.operation_identity,
                tenant_id=context.tenant_id,
                workflow_run_id=context.workflow_run_id,
                workflow_run_step_id=context.workflow_run_step_id,
                test_bench_run_id=context.test_bench_run_id,
                workflow_validation_id=context.workflow_validation_id,
                trace_id=context.trace_id,
                idempotency_key=context.idempotency_key,
                agent_profile_version_id=context.agent_profile_version_id,
                prompt_version_ids=list(context.prompt_version_ids),
                prompt_reference_version_ids=list(context.prompt_reference_version_ids),
                model_routing_provenance=context.model_routing_provenance,
                provider_connection_id=connection.provider_connection_id,
                provider_model_definition_id=None,
                model_provider_entry_id=None,
                model_id=model_id,
                safe_summary=context.safe_summary(),
            )
            if (
                not created
                and operation.authoritative_outcome is not None
                and operation.status.value in {"completed", "recovered"}
            ):
                result = GatewayResult(
                    outcome=TestOutcome(operation.authoritative_outcome),
                    normalized_error_category=operation.normalized_error_category,
                    safe_audit_summary={
                        **operation.safe_summary_json,
                        "duplicate_suppressed": True,
                    },
                )
                breaker_summary = _breaker_summary(
                    context=context,
                    connection_id=connection.provider_connection_id,
                    model_id=model_id,
                )
                await self._repository.record_gateway_physical_attempt(
                    operation=operation,
                    gateway_invocation_attempt_id=None,
                    result=result,
                    retry_category="recovered",
                    retry_decision_summary={"category": "recovered"},
                    retry_budget_snapshot={},
                    breaker_scope=str(breaker_summary["scope"]),
                    breaker_decision_summary=breaker_summary,
                    duplicate_suppressed=True,
                )
                return result
        adapter = self._registry.get(connection.provider_type)
        breaker_summary = _breaker_summary(
            context=context,
            connection_id=connection.provider_connection_id,
            model_id=model_id,
        )
        response = await adapter.chat_completion(
            AdapterRequest(
                model_id=model_id,
                messages=messages,
                timeout_policy=TimeoutPolicy.model_validate(connection.timeout_policy),
                base_url=connection.base_url_safe,
                credential=credential,
            )
        )
        retry_summary = gateway_retry_summary(response.normalized_error_category)
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
                "normalized_error_category": response.normalized_error_category.value,
                "latency_ms": response.latency_ms,
                "usage_available": response.usage.availability.value,
            },
        )
        old_attempt = await self._repository.record_gateway_attempt(
            tenant_id=context.tenant_id,
            provider_type=connection.provider_type,
            provider_connection_id=connection.provider_connection_id,
            model_id=model_id,
            result=result,
            workflow_run_id=context.workflow_run_id,
            test_bench_run_id=context.test_bench_run_id,
            trace_id=context.trace_id,
            idempotency_key=context.idempotency_key,
            workflow_run_step_id=context.workflow_run_step_id,
            workflow_validation_id=context.workflow_validation_id,
            retry_decision_summary=retry_summary,
            breaker_scope=str(breaker_summary["scope"]),
            breaker_decision_summary=breaker_summary,
        )
        if operation is not None:
            await self._repository.record_gateway_physical_attempt(
                operation=operation,
                gateway_invocation_attempt_id=old_attempt.gateway_invocation_attempt_id,
                result=result,
                retry_category=str(retry_summary.get("category", "skipped")),
                retry_decision_summary=retry_summary,
                retry_budget_snapshot={
                    "tenant_retry_budget_remaining": retry_summary.get(
                        "tenant_retry_budget_remaining"
                    )
                },
                breaker_scope=str(breaker_summary.get("scope")),
                breaker_decision_summary=breaker_summary,
                duplicate_suppressed=False,
            )
        else:
            await self._record_operation_attempt(
                context=context,
                connection_id=connection.provider_connection_id,
                model_id=model_id,
                result=result,
                retry_summary=retry_summary,
                breaker_summary=breaker_summary,
                old_attempt_id=old_attempt.gateway_invocation_attempt_id
                if old_attempt is not None
                else None,
            )
        await self._record_usage_event(
            context=context,
            connection_id=connection.provider_connection_id,
            provider_type=connection.provider_type,
            model_id=model_id,
            result=result,
            old_attempt_id=old_attempt.gateway_invocation_attempt_id
            if old_attempt is not None
            else None,
        )
        return result

    async def _record_operation_attempt(
        self,
        *,
        context: GatewayInvocationContext,
        connection_id: UUID,
        model_id: str,
        result: GatewayResult,
        retry_summary: dict[str, object],
        breaker_summary: dict[str, object],
        old_attempt_id: UUID | None,
    ) -> None:
        if not context.operation_identity or not hasattr(
            self._repository,
            "get_or_create_gateway_operation",
        ):
            return
        operation, _created = await self._repository.get_or_create_gateway_operation(
            operation_identity=context.operation_identity,
            tenant_id=context.tenant_id,
            workflow_run_id=context.workflow_run_id,
            workflow_run_step_id=context.workflow_run_step_id,
            test_bench_run_id=context.test_bench_run_id,
            workflow_validation_id=context.workflow_validation_id,
            trace_id=context.trace_id,
            idempotency_key=context.idempotency_key,
            agent_profile_version_id=context.agent_profile_version_id,
            prompt_version_ids=list(context.prompt_version_ids),
            prompt_reference_version_ids=list(context.prompt_reference_version_ids),
            model_routing_provenance=context.model_routing_provenance,
            provider_connection_id=connection_id,
            provider_model_definition_id=None,
            model_provider_entry_id=None,
            model_id=model_id,
            safe_summary=context.safe_summary(),
        )
        await self._repository.record_gateway_physical_attempt(
            operation=operation,
            gateway_invocation_attempt_id=old_attempt_id,
            result=result,
            retry_category=str(retry_summary.get("category", "skipped")),
            retry_decision_summary=retry_summary,
            retry_budget_snapshot={
                "tenant_retry_budget_remaining": retry_summary.get(
                    "tenant_retry_budget_remaining"
                )
            },
            breaker_scope=str(breaker_summary.get("scope")),
            breaker_decision_summary=breaker_summary,
            duplicate_suppressed=False,
        )

    async def _record_usage_event(
        self,
        *,
        context: GatewayInvocationContext,
        connection_id: UUID,
        provider_type: ProviderType,
        model_id: str,
        result: GatewayResult,
        old_attempt_id: UUID | None,
    ) -> None:
        if self._usage_recorder is None:
            return
        try:
            await self._usage_recorder.record_gateway_result(
                context=context,
                provider_key=provider_type,
                model_id=model_id,
                result=result,
                provider_connection_id=connection_id,
                source_gateway_attempt_id=old_attempt_id,
            )
        except Exception:
            # Gateway response delivery remains authoritative; usage capture failures
            # are observable through tests/logs and must not leak request content.
            return


class GatewayUsageRecorder(Protocol):
    async def record_gateway_result(
        self,
        *,
        context: GatewayInvocationContext,
        provider_key: ProviderType,
        model_id: str,
        result: GatewayResult,
        provider_connection_id: UUID | None = None,
        source_gateway_attempt_id: UUID | None = None,
    ) -> object:
        raise NotImplementedError


def provider_type_for_catalog_key(provider_key: str) -> ProviderType:
    if provider_key == ProviderType.LOCAL_OPENAI_COMPATIBLE.value:
        return ProviderType.LOCAL_OPENAI_COMPATIBLE
    return ProviderType.OPENAI


def _breaker_scope(connection_id: UUID, model_id: str) -> str:
    return str(
        gateway_breaker_summary(
            provider_connection_id=str(connection_id),
            model_id=model_id,
        )["scope"]
    )


def _breaker_summary(
    *,
    context: GatewayInvocationContext,
    connection_id: UUID,
    model_id: str,
) -> dict[str, object]:
    return gateway_breaker_summary(
        provider_connection_id=str(connection_id),
        model_id=model_id,
        tenant_id=str(context.tenant_id) if context.tenant_id else None,
        workflow_run_id=str(context.workflow_run_id)
        if context.workflow_run_id
        else None,
        workflow_run_step_id=str(context.workflow_run_step_id)
        if context.workflow_run_step_id
        else None,
        trace_id=context.trace_id,
    )
