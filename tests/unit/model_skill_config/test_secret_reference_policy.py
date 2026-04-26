from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import (
    CredentialRequirementCandidate,
    ScopeSelector,
    SecretReferenceCandidate,
    VersionStatus,
)
from multi_agent_platform.config.policy import (
    authorize_secret_reference_resolution,
    evaluate_credential_requirements,
)
from multi_agent_platform.secrets.base import SecretValue
from multi_agent_platform.secrets.providers.static import StaticSecretProvider


def _secret(
    *,
    tenant_id,
    version_id,
    scope,
    status=VersionStatus.ACTIVE,
    rotation_metadata=None,
    allowed_scopes=None,
) -> SecretReferenceCandidate:
    return SecretReferenceCandidate(
        version_id=version_id,
        tenant_id=tenant_id,
        scope=scope,
        status=status,
        activation_reason="test",
        secret_reference_id="example/api-key",
        provider_key="static",
        external_reference="example/api-key",
        allowed_scopes=allowed_scopes or {},
        rotation_metadata=rotation_metadata or {},
    )


def test_secret_reference_policy_rejects_inactive_revoked_and_cross_tenant() -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    secret_version_id = uuid4()
    requirement = CredentialRequirementCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        action_category="read",
        credential_kind="secret_reference",
        secret_reference_version_id=secret_version_id,
    )

    inactive = _secret(
        tenant_id=tenant_id,
        version_id=secret_version_id,
        scope=scope,
        status=VersionStatus.INACTIVE,
    )
    revoked = _secret(
        tenant_id=tenant_id,
        version_id=secret_version_id,
        scope=scope,
        rotation_metadata={"revoked": True},
    )
    cross_tenant = _secret(
        tenant_id=other_tenant_id,
        version_id=secret_version_id,
        scope=ScopeSelector(tenant_id=other_tenant_id),
    )

    for candidate in (inactive, revoked, cross_tenant):
        decision = evaluate_credential_requirements(
            requirements=[requirement],
            secret_references=[candidate],
            scope=scope,
            tool_id="http.fetch",
            action_category="read",
        )
        assert not decision.allowed
        assert decision.denial_category is not None
        assert decision.denial_category.value in {
            "secret_reference_invalid",
            "credential_unsatisfied",
        }


def test_credential_policy_enforces_allowed_scope_and_delegated_links() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    secret_version_id = uuid4()
    delegated_link_id = uuid4()
    secret_requirement = CredentialRequirementCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        action_category="read",
        credential_kind="secret_reference",
        secret_reference_version_id=secret_version_id,
        allowed_credential_scope={"host": "docs.example.com"},
    )
    delegated_requirement = CredentialRequirementCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="gmail.send",
        action_category="write",
        credential_kind="delegated_credential",
        delegated_credential_link_id=delegated_link_id,
    )
    secret = _secret(
        tenant_id=tenant_id,
        version_id=secret_version_id,
        scope=scope,
        allowed_scopes={"host": "docs.example.com"},
    )

    denied = evaluate_credential_requirements(
        requirements=[secret_requirement],
        secret_references=[secret],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
        credential_context={"host": "example.net"},
    )
    allowed_delegated = evaluate_credential_requirements(
        requirements=[delegated_requirement],
        secret_references=[],
        scope=scope,
        tool_id="gmail.send",
        action_category="write",
        authorized_delegated_credential_link_ids={delegated_link_id},
    )

    assert not denied.allowed
    assert allowed_delegated.allowed


async def test_secret_provider_resolution_returns_safe_summary_without_value() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    secret = _secret(tenant_id=tenant_id, version_id=uuid4(), scope=scope)
    provider = StaticSecretProvider({"example/api-key": "fixture-secret"})

    authorized = await authorize_secret_reference_resolution(
        secret_provider=provider,
        secret_reference=secret,
        scope=scope,
    )
    resolved = await provider.resolve("example/api-key")

    assert isinstance(resolved, SecretValue)
    assert resolved.value == "fixture-secret"
    assert "fixture-secret" not in str(authorized.safe_summary)


async def test_secret_provider_resolution_rejects_out_of_scope_reference() -> None:
    secret = _secret(
        tenant_id=uuid4(),
        version_id=uuid4(),
        scope=ScopeSelector(tenant_id=uuid4()),
    )
    provider = StaticSecretProvider({"example/api-key": "fixture-secret"})

    with pytest.raises(ValueError):
        await authorize_secret_reference_resolution(
            secret_provider=provider,
            secret_reference=secret,
            scope=ScopeSelector(tenant_id=uuid4()),
        )
