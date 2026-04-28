from __future__ import annotations

from uuid import UUID

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.catalog_sync import (
    CatalogSynchronizer,
    CatalogSyncSummary,
)
from multi_agent_platform.model_providers.health import derive_health_state
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    OperationStatus,
    ProviderConnectionSummary,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
)
from multi_agent_platform.model_providers.probes import ProviderProbeRunner
from multi_agent_platform.model_providers.redaction import safe_url
from multi_agent_platform.model_providers.validation import (
    ProviderConnectionDraft,
    validate_connection_draft,
)


class ModelProviderPermissionError(PermissionError):
    pass


class ModelProviderService:
    def __init__(
        self,
        *,
        repository: ModelProviderRepository,
        allowlist: LocalEndpointAllowlist,
        probe_runner: ProviderProbeRunner | None = None,
    ) -> None:
        self._repository = repository
        self._allowlist = allowlist
        self._probe_runner = probe_runner

    async def list_connections(
        self,
        *,
        principal: PrincipalContext,
    ) -> list[ProviderConnectionSummary]:
        platform_scope = "platform_admin" in principal.role_codes
        return await self._repository.list_connections(
            tenant_id=principal.tenant_id,
            platform_scope=platform_scope,
        )

    async def get_connection(
        self,
        *,
        connection_id: UUID,
        principal: PrincipalContext,
    ) -> ModelProviderConnection:
        connection = await self._repository.get_connection(connection_id)
        if "platform_admin" in principal.role_codes:
            return connection
        if connection.provider_connection_id not in {
            summary.provider_connection_id
            for summary in await self.list_connections(principal=principal)
        }:
            raise ModelProviderPermissionError("connection is not visible")
        return connection

    async def save_connection(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID | None,
        provider_type: ProviderType,
        display_name: str,
        base_url: str | None,
        timeout_policy: TimeoutPolicy,
        visibility: TenantVisibility,
        models: tuple[ProviderModel, ...],
        credential_secret_reference_ids: tuple[str, ...],
        active: bool,
    ) -> ModelProviderConnection:
        draft = validate_connection_draft(
            ProviderConnectionDraft(
                provider_type=provider_type,
                display_name=display_name,
                base_url=base_url,
                timeout_policy=timeout_policy,
                visibility=visibility,
                models=models,
                credential_secret_reference_ids=credential_secret_reference_ids,
                active=active,
            ),
            principal=principal,
            allowlist=self._allowlist,
        )
        connection = await self._repository.save_connection(
            connection_id=connection_id,
            provider_type=draft.provider_type,
            display_name=draft.display_name.strip(),
            base_url_safe=safe_url(draft.base_url),
            timeout_policy=draft.timeout_policy,
            visibility=draft.visibility,
            credential_secret_reference_ids=draft.credential_secret_reference_ids,
            models=draft.models,
            active=draft.active,
            principal_id=principal.principal_id,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=None,
            health_state=connection.health_state,
            selectable=False,
            reason="connection metadata saved",
        )
        return connection

    async def set_active(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
        active: bool,
    ) -> ModelProviderConnection:
        if "platform_admin" not in principal.role_codes:
            raise ModelProviderPermissionError("platform administrator required")
        connection = await self._repository.get_connection(connection_id)
        connection.active = active
        connection.deactivated_at = None if active else utcnow()
        health_state, selectable, reason = derive_health_state(
            active=active,
            latest_test=None,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=None,
            health_state=health_state,
            selectable=selectable,
            reason=reason,
        )
        return connection

    async def test_connection(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
        operation_identity: str | None = None,
        rate_limit_allowed: bool = True,
        bounded_operation_allowed: bool = True,
    ) -> ProviderTestSummary:
        connection = await self._repository.get_connection(connection_id)
        models = await self._repository.list_models(connection_id)
        if not models:
            raise LookupError("connection has no models")
        operation = None
        if operation_identity:
            (
                operation,
                created,
            ) = await self._repository.get_or_create_provider_probe_operation(
                operation_identity=operation_identity,
                provider_connection_id=connection.provider_connection_id,
                provider_model_definition_id=models[0].provider_model_definition_id,
                tenant_id=principal.tenant_id,
                actor_principal_id=principal.principal_id,
                rate_limit_scope={
                    "actor_principal_id": principal.principal_id,
                    "provider_connection_id": str(connection.provider_connection_id),
                },
                bounded_operation_decision={"allowed": True},
                safe_summary={"decision": "accepted"},
            )
            if not created and operation.status is OperationStatus.COMPLETED:
                return ProviderTestSummary(
                    outcome=TestOutcome.SUCCESS,
                    normalized_reason=operation.normalized_reason,
                    latency_ms=0,
                    tested_model_id=models[0].model_id,
                    safe_diagnostic_summary="Recovered previous provider probe result",
                )
        if "platform_admin" not in principal.role_codes:
            if operation is not None:
                await self._repository.complete_provider_probe_operation(
                    operation=operation,
                    outcome=TestOutcome.FAILURE,
                    reason=ErrorCategory.AUTHORIZATION_FAILURE,
                    safe_summary={"decision_category": "denied"},
                    status=OperationStatus.DENIED,
                )
            raise ModelProviderPermissionError("platform administrator required")
        if not rate_limit_allowed or not bounded_operation_allowed:
            if operation is not None:
                await self._repository.complete_provider_probe_operation(
                    operation=operation,
                    outcome=TestOutcome.FAILURE,
                    reason=ErrorCategory.RATE_LIMIT
                    if not rate_limit_allowed
                    else ErrorCategory.POLICY_OR_VISIBILITY_DENIAL,
                    safe_summary={
                        "decision_category": "throttled"
                        if not rate_limit_allowed
                        else "denied",
                        "provider_connection_id": str(
                            connection.provider_connection_id
                        ),
                    },
                    status=OperationStatus.THROTTLED
                    if not rate_limit_allowed
                    else OperationStatus.DENIED,
                )
            raise ModelProviderPermissionError("provider probe throttled")
        if self._probe_runner is None:
            raise RuntimeError("provider probe runner is not configured")
        started_at = utcnow()
        result = await self._probe_runner.run_probe(
            provider_type=connection.provider_type,
            model_id=models[0].model_id,
            timeout_policy=TimeoutPolicy.model_validate(connection.timeout_policy),
            base_url=connection.base_url_safe,
            credential=None,
        )
        record = await self._repository.append_test_result(
            connection=connection,
            model_definition_id=models[0].provider_model_definition_id,
            actor_principal_id=principal.principal_id,
            started_at=started_at,
            result=result,
        )
        health_state, selectable, reason = derive_health_state(
            active=connection.active,
            latest_test=result,
        )
        await self._repository.update_health(
            connection=connection,
            test_result_id=record.connection_test_result_id,
            health_state=health_state,
            selectable=selectable,
            reason=reason,
        )
        if operation is not None:
            await self._repository.complete_provider_probe_operation(
                operation=operation,
                outcome=result.outcome,
                reason=result.normalized_reason,
                safe_summary={
                    "decision": result.outcome.value,
                    "normalized_reason": result.normalized_reason.value,
                },
                test_result_id=record.connection_test_result_id,
            )
        return result

    async def sync_catalog(
        self,
        *,
        principal: PrincipalContext,
        connection_id: UUID,
        operation_identity: str | None = None,
    ) -> CatalogSyncSummary:
        if "platform_admin" not in principal.role_codes:
            raise ModelProviderPermissionError("platform administrator required")
        connection = await self._repository.get_connection(connection_id)
        operation = None
        if operation_identity:
            (
                operation,
                created,
            ) = await self._repository.get_or_create_catalog_sync_operation(
                operation_identity=operation_identity,
                provider_connection_id=connection.provider_connection_id,
                tenant_id=principal.tenant_id,
                actor_principal_id=principal.principal_id,
                checkpoint={
                    "provider_connection_id": str(connection.provider_connection_id)
                },
                safe_summary={"decision": "accepted"},
            )
            if not created and operation.status is OperationStatus.COMPLETED:
                result_json = operation.authoritative_result_json
                return CatalogSyncSummary(
                    created=_safe_int(result_json.get("created")),
                    updated=_safe_int(result_json.get("updated")),
                    blocked=_safe_int(result_json.get("blocked")),
                    marked_unavailable=_safe_int(result_json.get("marked_unavailable")),
                    safe_summary="Recovered previous catalog sync result",
                )
        summary = await CatalogSynchronizer(self._repository).sync_connection(
            connection=connection,
            principal_id=principal.principal_id,
        )
        if operation is not None:
            await self._repository.complete_catalog_sync_operation(
                operation=operation,
                result={
                    "created": summary.created,
                    "updated": summary.updated,
                    "blocked": summary.blocked,
                    "marked_unavailable": summary.marked_unavailable,
                },
                reason=ErrorCategory.NONE,
                safe_summary={"decision": "completed"},
            )
        return summary


def _safe_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0
