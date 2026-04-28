from __future__ import annotations

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.models import (
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.service import (
    ModelProviderPermissionError,
    ModelProviderService,
)
from tests.integration.api.test_admin_provider_probe_recovery import CountingProbeRunner


async def test_provider_probe_throttles_before_provider_activity(session) -> None:
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

    with pytest.raises(ModelProviderPermissionError, match="throttled"):
        await service.test_connection(
            principal=principal,
            connection_id=connection.provider_connection_id,
            operation_identity="probe:throttled",
            rate_limit_allowed=False,
        )

    assert runner.calls == 0
