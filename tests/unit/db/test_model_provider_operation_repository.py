from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    GatewayResult,
    OperationStatus,
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)


async def test_repository_reuses_gateway_operation_identity_and_numbers_attempts(
    session,
) -> None:
    repo = ModelProviderRepository(session)
    tenant_id = uuid4()
    operation, created = await repo.get_or_create_gateway_operation(
        operation_identity="run:step:1",
        tenant_id=tenant_id,
        workflow_run_id=uuid4(),
        workflow_run_step_id=uuid4(),
        trace_id="trace",
        idempotency_key="idem",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=[uuid4()],
        prompt_reference_version_ids=[uuid4()],
        model_routing_provenance={"resolver": "model_skill_config"},
        provider_connection_id=uuid4(),
        provider_model_definition_id=uuid4(),
        model_provider_entry_id=uuid4(),
        model_id="gpt-test",
        safe_summary={"kind": "runtime"},
    )
    duplicate, duplicate_created = await repo.get_or_create_gateway_operation(
        operation_identity="run:step:1",
        tenant_id=tenant_id,
        workflow_run_id=None,
        workflow_run_step_id=None,
        trace_id="trace",
        idempotency_key="idem",
        agent_profile_version_id=None,
        prompt_version_ids=[],
        prompt_reference_version_ids=[],
        model_routing_provenance={},
        provider_connection_id=None,
        provider_model_definition_id=None,
        model_provider_entry_id=None,
        model_id="gpt-test",
        safe_summary={},
    )

    assert created is True
    assert duplicate_created is False
    assert duplicate.gateway_operation_id == operation.gateway_operation_id

    attempt = await repo.record_gateway_physical_attempt(
        operation=operation,
        gateway_invocation_attempt_id=None,
        result=GatewayResult(outcome=TestOutcome.SUCCESS),
        retry_category="skipped",
        retry_decision_summary={"category": "skipped"},
        retry_budget_snapshot={},
        breaker_scope="provider_connection:pc:model:gpt-test",
        breaker_decision_summary={"allowed": True},
        duplicate_suppressed=False,
    )

    assert attempt.physical_attempt_number == 1
    assert operation.status is OperationStatus.COMPLETED


async def test_repository_reuses_probe_and_catalog_operation_identities(
    session,
) -> None:
    repo = ModelProviderRepository(session)
    connection = await repo.save_connection(
        connection_id=None,
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        base_url_safe=None,
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(mode=VisibilityMode.PLATFORM_DEFAULT),
        credential_secret_reference_ids=(),
        models=(ProviderModel(model_id="gpt-test"),),
        active=True,
        principal_id="platform-admin",
    )
    probe, probe_created = await repo.get_or_create_provider_probe_operation(
        operation_identity="probe:1",
        provider_connection_id=connection.provider_connection_id,
        provider_model_definition_id=None,
        tenant_id=None,
        actor_principal_id="platform-admin",
        rate_limit_scope={"actor": "platform-admin"},
        bounded_operation_decision={"allowed": True},
        safe_summary={"decision": "accepted"},
    )
    (
        duplicate_probe,
        duplicate_probe_created,
    ) = await repo.get_or_create_provider_probe_operation(
        operation_identity="probe:1",
        provider_connection_id=connection.provider_connection_id,
        provider_model_definition_id=None,
        tenant_id=None,
        actor_principal_id="platform-admin",
        rate_limit_scope={},
        bounded_operation_decision={},
        safe_summary={},
    )
    catalog, catalog_created = await repo.get_or_create_catalog_sync_operation(
        operation_identity="catalog:1",
        provider_connection_id=connection.provider_connection_id,
        tenant_id=None,
        actor_principal_id="platform-admin",
        checkpoint={"model": "gpt-test"},
        safe_summary={"decision": "accepted"},
    )

    await repo.complete_provider_probe_operation(
        operation=probe,
        outcome=TestOutcome.FAILURE,
        reason=ErrorCategory.RATE_LIMIT,
        safe_summary={"decision": "throttled"},
    )

    assert probe_created is True
    assert duplicate_probe_created is False
    assert (
        duplicate_probe.provider_probe_operation_id == probe.provider_probe_operation_id
    )
    assert catalog_created is True
    assert catalog.status is OperationStatus.PENDING
    assert probe.status is OperationStatus.FAILED
