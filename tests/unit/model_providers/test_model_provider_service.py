from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.model_providers import (
    ModelProviderRepository,
)
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


class FakeProbeRunner:
    async def run_probe(self, **_kwargs: object) -> ProviderTestSummary:
        return ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=12,
            tested_model_id="gpt-test",
            safe_diagnostic_summary="safe",
        )


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
