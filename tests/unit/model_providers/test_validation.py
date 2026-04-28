from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.models import (
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.validation import (
    ProviderConnectionDraft,
    ProviderValidationError,
    validate_connection_draft,
)


def test_validate_connection_draft_rejects_tenant_actor_mutation() -> None:
    draft = ProviderConnectionDraft(
        provider_type=ProviderType.OPENAI,
        display_name="Provider",
        base_url=None,
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(),
        models=(ProviderModel(model_id="gpt-test"),),
        credential_secret_reference_ids=("qa011/openai-placeholder",),
        active=True,
    )

    with pytest.raises(ProviderValidationError):
        validate_connection_draft(
            draft,
            principal=PrincipalContext(role_codes=("tenant_admin",)),
            allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        )


def test_validate_connection_draft_requires_allowlisted_local_url() -> None:
    draft = ProviderConnectionDraft(
        provider_type=ProviderType.LOCAL_OPENAI_COMPATIBLE,
        display_name="Provider",
        base_url="http://localhost:11434",
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(
            mode=VisibilityMode.TENANT_ALLOWLIST,
            tenant_ids=(uuid4(),),
        ),
        models=(ProviderModel(model_id="local-test"),),
        credential_secret_reference_ids=("qa011/local-placeholder",),
        active=True,
    )

    assert (
        validate_connection_draft(
            draft,
            principal=PrincipalContext(role_codes=("platform_admin",)),
            allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        )
        is draft
    )


def test_validate_connection_draft_wraps_allowlist_errors() -> None:
    draft = ProviderConnectionDraft(
        provider_type=ProviderType.LOCAL_OPENAI_COMPATIBLE,
        display_name="Unsafe",
        base_url="http://user:pass@192.0.2.10:9999/v1?token=value",
        timeout_policy=TimeoutPolicy(),
        visibility=TenantVisibility(),
        models=(ProviderModel(model_id="unsafe"),),
        credential_secret_reference_ids=("qa011/local-placeholder",),
        active=False,
    )

    with pytest.raises(ProviderValidationError) as exc_info:
        validate_connection_draft(
            draft,
            principal=PrincipalContext(role_codes=("platform_admin",)),
            allowlist=LocalEndpointAllowlist(("http",), ("localhost",), (11434,)),
        )

    assert exc_info.value.field == "base_url"
    assert str(exc_info.value) == "local provider URL cannot include userinfo"
