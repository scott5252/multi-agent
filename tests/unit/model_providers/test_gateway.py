from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.gateway import (
    GatewayInvocationContext,
    ModelGateway,
)
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    HealthState,
    ProviderType,
    TestOutcome,
    UsageAvailability,
    VisibilityMode,
)
from multi_agent_platform.model_providers.secrets import ProviderSecretResolver
from multi_agent_platform.secrets.base import SecretValue


class FakeGatewayRepository:
    def __init__(self, connection: ModelProviderConnection) -> None:
        self.connection = connection
        self.attempts: list[dict[str, object]] = []

    async def get_connection(self, _connection_id: UUID) -> ModelProviderConnection:
        return self.connection

    async def record_gateway_attempt(self, **kwargs: object) -> None:
        self.attempts.append(kwargs)


class FakeAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self) -> None:
        self.calls = 0
        self.credentials: list[str | None] = []

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        self.calls += 1
        self.credentials.append(request.credential)
        assert request.model_id == "gpt-test"
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            content="ok",
            latency_ms=5,
        )


class FakeSecretProvider:
    provider_name = "fake"

    async def resolve(self, reference: str) -> SecretValue:
        if reference == "missing":
            raise LookupError(reference)
        return SecretValue(reference=reference, value="resolved-gateway-secret")


def _gateway_connection(
    *,
    healthy: bool,
    references: list[str] | None = None,
) -> ModelProviderConnection:
    return ModelProviderConnection(
        provider_connection_id=uuid4(),
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        timeout_policy={"connect_seconds": 5, "read_seconds": 30, "total_seconds": 45},
        visibility_mode=VisibilityMode.PLATFORM_DEFAULT,
        active=healthy,
        health_state=HealthState.HEALTHY if healthy else HealthState.DISABLED,
        credential_secret_reference_ids=references or [],
        safe_metadata={},
        created_by_principal_id="admin",
        updated_by_principal_id="admin",
    )


@pytest.mark.asyncio
async def test_gateway_fails_closed_for_inactive_connection() -> None:
    repo = FakeGatewayRepository(_gateway_connection(healthy=False))
    result = await ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: FakeAdapter()}),
    ).invoke(
        connection_id=repo.connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=GatewayInvocationContext(tenant_id=uuid4()),
    )

    assert result.outcome is TestOutcome.FAILURE
    assert result.normalized_error_category is ErrorCategory.CATALOG_INACTIVE
    assert repo.attempts


@pytest.mark.asyncio
async def test_gateway_records_successful_attempt_metadata() -> None:
    repo = FakeGatewayRepository(_gateway_connection(healthy=True))
    adapter = FakeAdapter()
    result = await ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
    ).invoke(
        connection_id=repo.connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=GatewayInvocationContext(tenant_id=uuid4(), trace_id="trace"),
    )

    assert result.outcome is TestOutcome.SUCCESS
    assert result.usage.availability is UsageAvailability.UNAVAILABLE
    assert repo.attempts[0]["trace_id"] == "trace"


@pytest.mark.asyncio
async def test_gateway_resolves_configured_credential_reference() -> None:
    repo = FakeGatewayRepository(
        _gateway_connection(
            healthy=True,
            references=["qa025/openai-placeholder"],
        )
    )
    adapter = FakeAdapter()

    result = await ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
        secret_resolver=ProviderSecretResolver(FakeSecretProvider()),
    ).invoke(
        connection_id=repo.connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=GatewayInvocationContext(tenant_id=uuid4(), trace_id="trace"),
    )

    assert result.outcome is TestOutcome.SUCCESS
    assert adapter.credentials == ["resolved-gateway-secret"]
    assert "resolved-gateway-secret" not in str(result.safe_audit_summary)
    assert "resolved-gateway-secret" not in str(repo.attempts)


@pytest.mark.asyncio
async def test_gateway_fails_closed_when_secret_reference_missing() -> None:
    repo = FakeGatewayRepository(
        _gateway_connection(healthy=True, references=["missing"])
    )
    adapter = FakeAdapter()

    result = await ModelGateway(
        repository=repo,
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
        secret_resolver=ProviderSecretResolver(FakeSecretProvider()),
    ).invoke(
        connection_id=repo.connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "health"},),
        context=GatewayInvocationContext(tenant_id=uuid4(), trace_id="trace"),
    )

    assert result.outcome is TestOutcome.FAILURE
    assert result.normalized_error_category is ErrorCategory.SECRET_REFERENCE_INVALID
    assert result.safe_audit_summary["credential_reference_id"] == "missing"
    assert adapter.calls == 0
    assert repo.attempts
