from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, delete, false, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.model_providers import (
    CatalogSyncOperation,
    CatalogSyncRecord,
    ConnectionHealthSnapshot,
    ConnectionTenantVisibility,
    ConnectionTestResult,
    GatewayInvocationAttempt,
    GatewayOperation,
    GatewayPhysicalAttempt,
    ModelProviderConnection,
    ProviderModelDefinition,
    ProviderProbeOperation,
)
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    GatewayResult,
    HealthState,
    OperationStatus,
    ProviderConnectionSummary,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    SyncAction,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)


class ModelProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_connection(
        self,
        *,
        connection_id: UUID | None,
        provider_type: ProviderType,
        display_name: str,
        base_url_safe: str | None,
        timeout_policy: TimeoutPolicy,
        visibility: TenantVisibility,
        credential_secret_reference_ids: tuple[str, ...],
        models: tuple[ProviderModel, ...],
        active: bool,
        principal_id: str,
    ) -> ModelProviderConnection:
        now = utcnow()
        if connection_id is None:
            connection = ModelProviderConnection(
                provider_type=provider_type,
                display_name=display_name,
                base_url_safe=base_url_safe,
                timeout_policy=timeout_policy.model_dump(mode="json"),
                visibility_mode=visibility.mode,
                active=active,
                health_state=HealthState.UNTESTED if active else HealthState.DISABLED,
                credential_secret_reference_ids=list(credential_secret_reference_ids),
                safe_metadata={},
                created_by_principal_id=principal_id,
                updated_by_principal_id=principal_id,
            )
            self._session.add(connection)
            await self._session.flush()
        else:
            connection = await self.get_connection(connection_id)
            connection.provider_type = provider_type
            connection.display_name = display_name
            connection.base_url_safe = base_url_safe
            connection.timeout_policy = timeout_policy.model_dump(mode="json")
            connection.visibility_mode = visibility.mode
            connection.active = active
            connection.health_state = (
                HealthState.UNTESTED if active else HealthState.DISABLED
            )
            connection.credential_secret_reference_ids = list(
                credential_secret_reference_ids
            )
            connection.updated_by_principal_id = principal_id
            connection.deactivated_at = None if active else now
            await self._session.execute(
                delete(ProviderModelDefinition).where(
                    ProviderModelDefinition.provider_connection_id
                    == connection.provider_connection_id
                )
            )
            await self._session.execute(
                delete(ConnectionTenantVisibility).where(
                    ConnectionTenantVisibility.provider_connection_id
                    == connection.provider_connection_id
                )
            )
            await self._session.flush()

        for model in models:
            self._session.add(
                ProviderModelDefinition(
                    provider_connection_id=connection.provider_connection_id,
                    model_id=model.model_id,
                    display_name=model.display_name or model.model_id,
                    capability_metadata=model.capability_metadata,
                    cost_metadata=model.cost_metadata,
                    default_parameters=model.default_parameters,
                    available=model.available,
                )
            )
        for tenant_id in visibility.tenant_ids:
            self._session.add(
                ConnectionTenantVisibility(
                    provider_connection_id=connection.provider_connection_id,
                    tenant_id=tenant_id,
                    visible=True,
                    created_by_principal_id=principal_id,
                )
            )
        await self._session.flush()
        return connection

    async def get_connection(self, connection_id: UUID) -> ModelProviderConnection:
        connection = await self._session.get(ModelProviderConnection, connection_id)
        if connection is None:
            raise LookupError("model provider connection not found")
        return connection

    async def list_connections(
        self,
        *,
        tenant_id: UUID | None,
        platform_scope: bool,
    ) -> list[ProviderConnectionSummary]:
        stmt = select(ModelProviderConnection)
        if not platform_scope:
            stmt = _tenant_visible_stmt(stmt, tenant_id)
        stmt = stmt.order_by(ModelProviderConnection.updated_at.desc())
        result = await self._session.execute(stmt)
        summaries: list[ProviderConnectionSummary] = []
        for connection in result.scalars():
            models = await self.list_models(connection.provider_connection_id)
            latest = await self.latest_test(connection.provider_connection_id)
            summaries.append(
                ProviderConnectionSummary(
                    provider_connection_id=connection.provider_connection_id,
                    provider_type=connection.provider_type,
                    display_name=connection.display_name,
                    base_url_safe=connection.base_url_safe,
                    timeout_policy=TimeoutPolicy.model_validate(
                        connection.timeout_policy
                    ),
                    visibility=TenantVisibility(
                        mode=connection.visibility_mode,
                        tenant_ids=await self.visible_tenant_ids(
                            connection.provider_connection_id
                        ),
                    ),
                    active=connection.active,
                    health_state=connection.health_state,
                    model_count=len(models),
                    last_test_outcome=latest.outcome if latest else None,
                    last_test_reason=latest.normalized_reason if latest else None,
                    catalog_sync_status="synced"
                    if connection.health_state is HealthState.HEALTHY
                    else "not_selectable",
                    updated_at=connection.updated_at,
                )
            )
        return summaries

    async def list_models(self, connection_id: UUID) -> list[ProviderModelDefinition]:
        result = await self._session.execute(
            select(ProviderModelDefinition)
            .where(ProviderModelDefinition.provider_connection_id == connection_id)
            .order_by(ProviderModelDefinition.model_id)
        )
        return list(result.scalars())

    async def visible_tenant_ids(self, connection_id: UUID) -> tuple[UUID, ...]:
        result = await self._session.execute(
            select(ConnectionTenantVisibility.tenant_id).where(
                ConnectionTenantVisibility.provider_connection_id == connection_id,
                ConnectionTenantVisibility.visible.is_(True),
                ConnectionTenantVisibility.revoked_at.is_(None),
            )
        )
        return tuple(result.scalars())

    async def append_test_result(
        self,
        *,
        connection: ModelProviderConnection,
        model_definition_id: UUID | None,
        actor_principal_id: str,
        started_at: datetime,
        result: ProviderTestSummary,
    ) -> ConnectionTestResult:
        record = ConnectionTestResult(
            provider_connection_id=connection.provider_connection_id,
            provider_model_definition_id=model_definition_id,
            actor_principal_id=actor_principal_id,
            started_at=started_at,
            completed_at=result.completed_at,
            latency_ms=result.latency_ms,
            outcome=result.outcome,
            normalized_reason=result.normalized_reason,
            tested_model_id=result.tested_model_id,
            safe_diagnostic_summary=result.safe_diagnostic_summary,
            safe_provider_request_id=result.safe_provider_request_id,
            timeout_policy=connection.timeout_policy,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def update_health(
        self,
        *,
        connection: ModelProviderConnection,
        test_result_id: UUID | None,
        health_state: HealthState,
        selectable: bool,
        reason: str,
    ) -> ConnectionHealthSnapshot:
        connection.health_state = health_state
        snapshot = ConnectionHealthSnapshot(
            provider_connection_id=connection.provider_connection_id,
            health_state=health_state,
            latest_test_result_id=test_result_id,
            derived_reason=reason,
            derived_at=utcnow(),
            selectable=selectable,
        )
        self._session.add(snapshot)
        await self._session.flush()
        return snapshot

    async def latest_test(self, connection_id: UUID) -> ConnectionTestResult | None:
        result = await self._session.execute(
            select(ConnectionTestResult)
            .where(ConnectionTestResult.provider_connection_id == connection_id)
            .order_by(ConnectionTestResult.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def record_catalog_sync(
        self,
        *,
        connection_id: UUID,
        model_definition_id: UUID | None,
        tenant_id: UUID | None,
        sync_action: SyncAction,
        outcome: TestOutcome,
        reason: ErrorCategory,
        summary: str,
        principal_id: str,
        model_provider_entry_id: UUID | None = None,
    ) -> CatalogSyncRecord:
        record = CatalogSyncRecord(
            provider_connection_id=connection_id,
            provider_model_definition_id=model_definition_id,
            model_provider_entry_id=model_provider_entry_id,
            tenant_id=tenant_id,
            sync_action=sync_action,
            outcome=outcome,
            normalized_reason=reason,
            safe_summary=summary,
            actor_principal_id=principal_id,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def record_gateway_attempt(
        self,
        *,
        provider_type: ProviderType,
        model_id: str,
        result: GatewayResult,
        tenant_id: UUID | None = None,
        provider_connection_id: UUID | None = None,
        provider_model_definition_id: UUID | None = None,
        model_provider_entry_id: UUID | None = None,
        workflow_run_id: UUID | None = None,
        test_bench_run_id: UUID | None = None,
        trace_id: str | None = None,
        idempotency_key: str | None = None,
        workflow_run_step_id: UUID | None = None,
        workflow_validation_id: UUID | None = None,
        retry_decision_summary: dict[str, object] | None = None,
        breaker_scope: str | None = None,
        breaker_decision_summary: dict[str, object] | None = None,
    ) -> GatewayInvocationAttempt:
        now = utcnow()
        record = GatewayInvocationAttempt(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            test_bench_run_id=test_bench_run_id,
            trace_id=trace_id,
            idempotency_key=idempotency_key,
            model_provider_entry_id=model_provider_entry_id,
            provider_connection_id=provider_connection_id,
            provider_model_definition_id=provider_model_definition_id,
            provider_type=provider_type,
            model_id=model_id,
            started_at=now,
            completed_at=now,
            latency_ms=result.latency_ms,
            outcome=result.outcome,
            normalized_error_category=result.normalized_error_category,
            retry_decision_summary=retry_decision_summary or {},
            breaker_scope=breaker_scope,
            breaker_decision_summary=breaker_decision_summary or {},
            usage_metadata=result.usage.model_dump(mode="json"),
            usage_available=result.usage.availability.value == "available",
            safe_audit_summary=result.safe_audit_summary,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_or_create_gateway_operation(
        self,
        *,
        operation_identity: str,
        tenant_id: UUID | None,
        workflow_run_id: UUID | None,
        workflow_run_step_id: UUID | None,
        trace_id: str | None,
        idempotency_key: str | None,
        agent_profile_version_id: UUID | None,
        prompt_version_ids: list[UUID],
        prompt_reference_version_ids: list[UUID],
        model_routing_provenance: dict[str, object],
        provider_connection_id: UUID | None,
        provider_model_definition_id: UUID | None,
        model_provider_entry_id: UUID | None,
        model_id: str,
        safe_summary: dict[str, object],
        test_bench_run_id: UUID | None = None,
        workflow_validation_id: UUID | None = None,
    ) -> tuple[GatewayOperation, bool]:
        existing = await self._session.scalar(
            select(GatewayOperation).where(
                GatewayOperation.operation_identity == operation_identity
            )
        )
        if existing is not None:
            return existing, False
        operation = GatewayOperation(
            operation_identity=operation_identity,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            workflow_run_step_id=workflow_run_step_id,
            test_bench_run_id=test_bench_run_id,
            workflow_validation_id=workflow_validation_id,
            trace_id=trace_id,
            idempotency_key=idempotency_key or operation_identity,
            agent_profile_version_id=agent_profile_version_id,
            prompt_version_ids=[str(value) for value in prompt_version_ids],
            prompt_reference_version_ids=[
                str(value) for value in prompt_reference_version_ids
            ],
            model_routing_provenance_json=dict(model_routing_provenance),
            provider_connection_id=provider_connection_id,
            provider_model_definition_id=provider_model_definition_id,
            model_provider_entry_id=model_provider_entry_id,
            model_id=model_id,
            safe_summary_json=dict(safe_summary),
        )
        self._session.add(operation)
        await self._session.flush()
        return operation, True

    async def record_gateway_physical_attempt(
        self,
        *,
        operation: GatewayOperation,
        gateway_invocation_attempt_id: UUID | None,
        result: GatewayResult,
        retry_category: str,
        retry_decision_summary: dict[str, object],
        retry_budget_snapshot: dict[str, object],
        breaker_scope: str | None,
        breaker_decision_summary: dict[str, object],
        duplicate_suppressed: bool,
        provider_request_id_safe: str | None = None,
        recovered_from_attempt_id: UUID | None = None,
    ) -> GatewayPhysicalAttempt:
        now = utcnow()
        current = await self._session.scalar(
            select(func.max(GatewayPhysicalAttempt.physical_attempt_number)).where(
                GatewayPhysicalAttempt.gateway_operation_id
                == operation.gateway_operation_id
            )
        )
        attempt = GatewayPhysicalAttempt(
            gateway_operation_id=operation.gateway_operation_id,
            gateway_invocation_attempt_id=gateway_invocation_attempt_id,
            physical_attempt_number=int(current or 0) + 1,
            started_at=now,
            completed_at=now,
            latency_ms=result.latency_ms,
            outcome=result.outcome,
            normalized_error_category=result.normalized_error_category,
            retry_category=retry_category,
            retry_decision_summary_json=dict(retry_decision_summary),
            retry_budget_snapshot_json=dict(retry_budget_snapshot),
            breaker_scope=breaker_scope,
            breaker_decision_summary_json=dict(breaker_decision_summary),
            provider_request_id_safe=provider_request_id_safe,
            usage_metadata_json=result.usage.model_dump(mode="json"),
            usage_available=result.usage.availability.value == "available",
            duplicate_suppressed=duplicate_suppressed,
            recovered_from_attempt_id=recovered_from_attempt_id,
            safe_audit_summary_json=result.safe_audit_summary,
        )
        self._session.add(attempt)
        await self._session.flush()
        operation.authoritative_attempt_id = attempt.gateway_physical_attempt_id
        operation.authoritative_outcome = result.outcome.value
        operation.normalized_error_category = result.normalized_error_category
        operation.usage_available = attempt.usage_available
        operation.safe_summary_json = {
            **operation.safe_summary_json,
            "outcome": result.outcome.value,
            "normalized_error_category": result.normalized_error_category.value,
        }
        operation.status = (
            OperationStatus.COMPLETED
            if result.outcome is TestOutcome.SUCCESS
            else OperationStatus.FAILED
        )
        operation.completed_at = now
        await self._session.flush()
        return attempt

    async def get_or_create_provider_probe_operation(
        self,
        *,
        operation_identity: str,
        provider_connection_id: UUID,
        provider_model_definition_id: UUID | None,
        tenant_id: UUID | None,
        actor_principal_id: str,
        rate_limit_scope: dict[str, object],
        bounded_operation_decision: dict[str, object],
        safe_summary: dict[str, object],
    ) -> tuple[ProviderProbeOperation, bool]:
        existing = await self._session.scalar(
            select(ProviderProbeOperation).where(
                ProviderProbeOperation.operation_identity == operation_identity,
                ProviderProbeOperation.provider_connection_id == provider_connection_id,
                ProviderProbeOperation.actor_principal_id == actor_principal_id,
            )
        )
        if existing is not None:
            return existing, False
        operation = ProviderProbeOperation(
            operation_identity=operation_identity,
            provider_connection_id=provider_connection_id,
            provider_model_definition_id=provider_model_definition_id,
            tenant_id=tenant_id,
            actor_principal_id=actor_principal_id,
            rate_limit_scope_json=dict(rate_limit_scope),
            bounded_operation_decision_json=dict(bounded_operation_decision),
            safe_summary_json=dict(safe_summary),
        )
        self._session.add(operation)
        await self._session.flush()
        return operation, True

    async def complete_provider_probe_operation(
        self,
        *,
        operation: ProviderProbeOperation,
        outcome: TestOutcome,
        reason: ErrorCategory,
        safe_summary: dict[str, object],
        test_result_id: UUID | None = None,
        status: OperationStatus | None = None,
    ) -> ProviderProbeOperation:
        operation.authoritative_test_result_id = test_result_id
        operation.authoritative_outcome = outcome.value
        operation.normalized_reason = reason
        operation.safe_summary_json = dict(safe_summary)
        operation.status = status or (
            OperationStatus.COMPLETED
            if outcome is TestOutcome.SUCCESS
            else OperationStatus.FAILED
        )
        operation.completed_at = utcnow()
        await self._session.flush()
        return operation

    async def get_or_create_catalog_sync_operation(
        self,
        *,
        operation_identity: str,
        provider_connection_id: UUID,
        tenant_id: UUID | None,
        actor_principal_id: str,
        checkpoint: dict[str, object],
        safe_summary: dict[str, object],
    ) -> tuple[CatalogSyncOperation, bool]:
        existing = await self._session.scalar(
            select(CatalogSyncOperation).where(
                CatalogSyncOperation.operation_identity == operation_identity,
                CatalogSyncOperation.provider_connection_id == provider_connection_id,
            )
        )
        if existing is not None:
            return existing, False
        operation = CatalogSyncOperation(
            operation_identity=operation_identity,
            provider_connection_id=provider_connection_id,
            tenant_id=tenant_id,
            actor_principal_id=actor_principal_id,
            checkpoint_json=dict(checkpoint),
            safe_summary_json=dict(safe_summary),
        )
        self._session.add(operation)
        await self._session.flush()
        return operation, True

    async def complete_catalog_sync_operation(
        self,
        *,
        operation: CatalogSyncOperation,
        result: dict[str, object],
        reason: ErrorCategory,
        safe_summary: dict[str, object],
        status: OperationStatus = OperationStatus.COMPLETED,
    ) -> CatalogSyncOperation:
        operation.authoritative_result_json = dict(result)
        operation.normalized_reason = reason
        operation.safe_summary_json = dict(safe_summary)
        operation.status = status
        operation.completed_at = utcnow()
        await self._session.flush()
        return operation


def _tenant_visible_stmt(
    stmt: Select[tuple[ModelProviderConnection]],
    tenant_id: UUID | None,
) -> Select[tuple[ModelProviderConnection]]:
    if tenant_id is None:
        return stmt.where(false())
    return stmt.where(
        (ModelProviderConnection.visibility_mode == VisibilityMode.PLATFORM_DEFAULT)
        | ModelProviderConnection.provider_connection_id.in_(
            select(ConnectionTenantVisibility.provider_connection_id).where(
                ConnectionTenantVisibility.tenant_id == tenant_id,
                ConnectionTenantVisibility.visible.is_(True),
                ConnectionTenantVisibility.revoked_at.is_(None),
            )
        )
    )
