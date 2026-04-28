from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.model_providers import (
    ModelProviderRepository,
)
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    GatewayResult,
    HealthState,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    SyncAction,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)


async def test_model_provider_repository_persists_connection_lifecycle(
    session,
) -> None:
    repo = ModelProviderRepository(session)
    tenant_id = uuid4()
    connection = await repo.save_connection(
        connection_id=None,
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        base_url_safe=None,
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(
            mode=VisibilityMode.TENANT_ALLOWLIST,
            tenant_ids=(tenant_id,),
        ),
        credential_secret_reference_ids=("qa011/openai-placeholder",),
        models=(ProviderModel(model_id="gpt-test"),),
        active=True,
        principal_id="platform-admin",
    )

    models = await repo.list_models(connection.provider_connection_id)
    tenants = await repo.visible_tenant_ids(connection.provider_connection_id)
    summaries = await repo.list_connections(tenant_id=tenant_id, platform_scope=False)
    latest = await repo.append_test_result(
        connection=connection,
        model_definition_id=models[0].provider_model_definition_id,
        actor_principal_id="platform-admin",
        started_at=connection.created_at,
        result=ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=10,
            tested_model_id="gpt-test",
            safe_diagnostic_summary="safe",
        ),
    )
    snapshot = await repo.update_health(
        connection=connection,
        test_result_id=latest.connection_test_result_id,
        health_state=HealthState.HEALTHY,
        selectable=True,
        reason="probe succeeded",
    )
    sync = await repo.record_catalog_sync(
        connection_id=connection.provider_connection_id,
        model_definition_id=models[0].provider_model_definition_id,
        tenant_id=tenant_id,
        sync_action=SyncAction.UPDATED,
        outcome=TestOutcome.SUCCESS,
        reason=ErrorCategory.NONE,
        summary="synced",
        principal_id="platform-admin",
    )
    attempt = await repo.record_gateway_attempt(
        tenant_id=tenant_id,
        provider_type=ProviderType.OPENAI,
        provider_connection_id=connection.provider_connection_id,
        provider_model_definition_id=models[0].provider_model_definition_id,
        model_id="gpt-test",
        result=GatewayResult(outcome=TestOutcome.SUCCESS),
    )

    assert models[0].model_id == "gpt-test"
    assert tenants == (tenant_id,)
    assert summaries[0].provider_connection_id == connection.provider_connection_id
    assert snapshot.selectable is True
    assert sync.sync_action is SyncAction.UPDATED
    assert attempt.provider_connection_id == connection.provider_connection_id
