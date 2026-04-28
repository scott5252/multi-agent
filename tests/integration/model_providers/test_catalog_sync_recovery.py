from __future__ import annotations

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.models import (
    HealthState,
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.service import ModelProviderService


async def test_catalog_sync_duplicate_reuses_authoritative_summary(session) -> None:
    principal = PrincipalContext(
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    service = ModelProviderService(
        repository=ModelProviderRepository(session),
        allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
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
    connection.health_state = HealthState.HEALTHY

    first = await service.sync_catalog(
        principal=principal,
        connection_id=connection.provider_connection_id,
        operation_identity="catalog:duplicate",
    )
    second = await service.sync_catalog(
        principal=principal,
        connection_id=connection.provider_connection_id,
        operation_identity="catalog:duplicate",
    )

    assert first.updated == 1
    assert second.updated == 1
    assert second.safe_summary == "Recovered previous catalog sync result"
