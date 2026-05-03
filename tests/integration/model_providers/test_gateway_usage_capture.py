from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    GatewayInvocationContext,
    GatewayUsage,
    HealthState,
    ProviderType,
    TestOutcome,
    UsageAvailability,
    VisibilityMode,
)
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageFilters,
    UsageScopeType,
)
from multi_agent_platform.usage.service import UsageAnalyticsService


class UsageCaptureAdapter:
    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        return AdapterResponse(
            outcome=TestOutcome.SUCCESS,
            latency_ms=7,
            usage=GatewayUsage(
                availability=UsageAvailability.AVAILABLE,
                input_tokens=4,
                output_tokens=6,
                total_tokens=10,
            ),
        )


async def test_model_gateway_records_usage_event(session, seeded_tenant) -> None:
    connection = ModelProviderConnection(
        provider_connection_id=uuid4(),
        provider_type=ProviderType.OPENAI,
        display_name="OpenAI QA",
        timeout_policy={"connect_seconds": 5, "read_seconds": 30, "total_seconds": 45},
        visibility_mode=VisibilityMode.PLATFORM_DEFAULT,
        active=True,
        health_state=HealthState.HEALTHY,
        credential_secret_reference_ids=[],
        safe_metadata={},
        created_by_principal_id="platform-admin",
        updated_by_principal_id="platform-admin",
    )
    session.add(connection)
    await session.flush()
    usage_repository = UsageRepository(session)
    gateway = ModelGateway(
        repository=ModelProviderRepository(session),
        registry=ProviderAdapterRegistry({ProviderType.OPENAI: UsageCaptureAdapter()}),
        usage_recorder=UsageAnalyticsService(usage_repository),
    )

    result = await gateway.invoke(
        connection_id=connection.provider_connection_id,
        model_id="gpt-test",
        messages=({"role": "user", "content": "hello"},),
        context=GatewayInvocationContext(
            tenant_id=seeded_tenant.tenant_id,
            initiating_principal_id="tenant-admin",
            agent_key="writer",
            idempotency_key="gateway-capture-1",
            execution_mode="test",
        ),
    )

    events = await usage_repository.list_events(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.TENANT,
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        ),
        filters=UsageFilters(),
    )
    assert result.outcome is TestOutcome.SUCCESS
    assert len(events) == 1
    assert events[0].total_tokens == 10
    assert events[0].agent_key == "writer"
