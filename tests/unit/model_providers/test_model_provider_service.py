from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.model_providers import (
    ModelProviderRepository,
)
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.models import (
    AdapterRequest,
    AdapterResponse,
    ErrorCategory,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.probes import ProviderProbeRunner
from multi_agent_platform.model_providers.secrets import ProviderSecretResolver
from multi_agent_platform.model_providers.service import ModelProviderService
from multi_agent_platform.secrets.providers.static import StaticSecretProvider


class FakeProbeRunner:
    async def run_probe(self, **_kwargs: object) -> ProviderTestSummary:
        return ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=12,
            tested_model_id="gpt-test",
            safe_diagnostic_summary="safe",
        )


class CountingAdapter:
    provider_type = ProviderType.OPENAI

    def __init__(self) -> None:
        self.calls = 0

    async def chat_completion(self, request: AdapterRequest) -> AdapterResponse:
        self.calls += 1
        return AdapterResponse(outcome=TestOutcome.SUCCESS)


@pytest.mark.asyncio
async def test_model_provider_service_saves_tests_and_syncs(session) -> None:
    principal = PrincipalContext(
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    service = ModelProviderService(
        repository=ModelProviderRepository(session),
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        probe_runner=FakeProbeRunner(),
    )
    connection = await service.save_connection(
        principal=principal,
        connection_id=None,
        provider_type=ProviderType.LOCAL_OPENAI_COMPATIBLE,
        display_name="Provider",
        base_url="http://localhost:11434",
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(
            mode=VisibilityMode.TENANT_ALLOWLIST,
            tenant_ids=(uuid4(),),
        ),
        models=(ProviderModel(model_id="gpt-test"),),
        credential_secret_reference_ids=("qa011/local-placeholder",),
        active=True,
    )

    visible = await service.list_connections(principal=principal)
    result = await service.test_connection(
        principal=principal,
        connection_id=connection.provider_connection_id,
    )
    sync = await service.sync_catalog(
        principal=principal,
        connection_id=connection.provider_connection_id,
    )
    deactivated = await service.set_active(
        principal=principal,
        connection_id=connection.provider_connection_id,
        active=False,
    )

    assert visible[0].display_name == "Provider"
    assert result.outcome is TestOutcome.SUCCESS
    assert sync.updated == 1
    assert deactivated.active is False


@pytest.mark.asyncio
async def test_model_provider_service_persists_safe_secret_resolution_failure(
    session,
) -> None:
    principal = PrincipalContext(
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    adapter = CountingAdapter()
    service = ModelProviderService(
        repository=ModelProviderRepository(session),
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        probe_runner=ProviderProbeRunner(
            ProviderAdapterRegistry({ProviderType.OPENAI: adapter}),
            secret_resolver=ProviderSecretResolver(StaticSecretProvider({})),
        ),
    )
    connection = await service.save_connection(
        principal=principal,
        connection_id=None,
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        base_url=None,
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(mode=VisibilityMode.PLATFORM_DEFAULT),
        models=(ProviderModel(model_id="gpt-test"),),
        credential_secret_reference_ids=("qa025/missing",),
        active=True,
    )

    result = await service.test_connection(
        principal=principal,
        connection_id=connection.provider_connection_id,
    )

    assert result.outcome is TestOutcome.FAILURE
    assert result.normalized_reason is ErrorCategory.SECRET_REFERENCE_INVALID
    assert adapter.calls == 0
    assert "qa025/missing" not in result.safe_diagnostic_summary
