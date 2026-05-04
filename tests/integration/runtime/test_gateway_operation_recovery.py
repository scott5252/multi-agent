from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from multi_agent_platform.db.models.model_providers import GatewayPhysicalAttempt
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    GatewayInvocationContext,
    HealthState,
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.secrets import ProviderSecretResolver
from multi_agent_platform.secrets.providers.static import StaticSecretProvider


class CountingAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self) -> None:
        self.calls = 0

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        self.calls += 1
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            content="ok",
            latency_ms=3,
        )


async def test_gateway_operation_duplicate_reuses_authoritative_outcome(
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
    connection.health_state = HealthState.HEALTHY
    adapter = CountingAdapter()
    gateway = ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
    )
    context = GatewayInvocationContext(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_run_step_id=uuid4(),
        trace_id="trace",
        idempotency_key="idem",
        operation_identity="gateway:duplicate",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(uuid4(),),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    first = await gateway.invoke(
        connection_id=connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=context,
    )
    second = await gateway.invoke(
        connection_id=connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=context,
    )
    attempts = (
        (await session.execute(select(GatewayPhysicalAttempt.duplicate_suppressed)))
        .scalars()
        .all()
    )

    assert first.outcome is TestOutcome.SUCCESS
    assert second.outcome is TestOutcome.SUCCESS
    assert adapter.calls == 1
    assert attempts == [False, True]


async def test_gateway_operation_records_safe_secret_resolution_failure(
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
        credential_secret_reference_ids=("qa025/missing",),
        models=(ProviderModel(model_id="gpt-test"),),
        active=True,
        principal_id="platform-admin",
    )
    connection.health_state = HealthState.HEALTHY
    adapter = CountingAdapter()
    gateway = ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
        secret_resolver=ProviderSecretResolver(StaticSecretProvider({})),
    )
    context = GatewayInvocationContext(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        workflow_run_step_id=uuid4(),
        trace_id="trace",
        idempotency_key="idem-secret-failure",
        operation_identity="gateway:secret-failure",
        agent_profile_version_id=uuid4(),
        prompt_version_ids=(uuid4(),),
        prompt_reference_version_ids=(uuid4(),),
        model_routing_provenance={"resolver": "model_skill_config"},
    )

    result = await gateway.invoke(
        connection_id=connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=context,
    )
    attempt = (
        (
            await session.execute(
                select(GatewayPhysicalAttempt).where(
                    GatewayPhysicalAttempt.normalized_error_category
                    == ErrorCategory.SECRET_REFERENCE_INVALID
                )
            )
        )
        .scalars()
        .one()
    )

    assert result.outcome is TestOutcome.FAILURE
    assert result.normalized_error_category is ErrorCategory.SECRET_REFERENCE_INVALID
    assert adapter.calls == 0
    assert attempt.safe_audit_summary_json["credential_reference_id"] == (
        "qa025/missing"
    )
    assert "secret-value" not in str(attempt.safe_audit_summary_json)
