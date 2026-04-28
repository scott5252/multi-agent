from __future__ import annotations

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    ProviderModel,
    ProviderTestSummary,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.service import ModelProviderService


class CountingProbeRunner:
    def __init__(self) -> None:
        self.calls = 0

    async def run_probe(self, **_kwargs: object) -> ProviderTestSummary:
        self.calls += 1
        return ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=5,
            tested_model_id="gpt-test",
            safe_diagnostic_summary="safe",
        )


async def test_provider_probe_duplicate_returns_prior_safe_result(session) -> None:
    principal = PrincipalContext(
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    runner = CountingProbeRunner()
    service = ModelProviderService(
        repository=ModelProviderRepository(session),
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        probe_runner=runner,
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
        credential_secret_reference_ids=(),
        active=True,
    )

    first = await service.test_connection(
        principal=principal,
        connection_id=connection.provider_connection_id,
        operation_identity="probe:duplicate",
    )
    second = await service.test_connection(
        principal=principal,
        connection_id=connection.provider_connection_id,
        operation_identity="probe:duplicate",
    )

    assert first.outcome is TestOutcome.SUCCESS
    assert second.outcome is TestOutcome.SUCCESS
    assert runner.calls == 1
