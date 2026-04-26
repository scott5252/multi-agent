from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import (
    CredentialRequirementCandidate,
    ScopeSelector,
    SecretReferenceCandidate,
    SkillBindingCandidate,
)
from multi_agent_platform.config.policy import (
    evaluate_credential_requirements,
    evaluate_skill_access,
)


def test_skill_policy_allows_exact_binding_and_context() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    binding = SkillBindingCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        skill_slug="web",
        skill_version="1.0.0",
        allowed_contexts=("runtime_step",),
    )

    decision = evaluate_skill_access(
        candidates=[binding],
        scope=scope,
        skill_slug="web",
        skill_version="1.0.0",
        use_context="runtime_step",
    )

    assert decision.allowed


def test_credential_policy_denies_missing_secret_reference() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    requirement = CredentialRequirementCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        credential_kind="secret_reference",
        secret_reference_version_id=uuid4(),
    )

    decision = evaluate_credential_requirements(
        requirements=[requirement],
        secret_references=[],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
    )

    assert not decision.allowed
    assert decision.denial_category is not None


def test_credential_policy_allows_active_secret_reference() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    secret_version_id = uuid4()
    requirement = CredentialRequirementCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        credential_kind="secret_reference",
        secret_reference_version_id=secret_version_id,
    )
    secret = SecretReferenceCandidate(
        version_id=secret_version_id,
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        secret_reference_id="ref",
        provider_key="vault",
        external_reference="path",
    )

    decision = evaluate_credential_requirements(
        requirements=[requirement],
        secret_references=[secret],
        scope=scope,
        tool_id="http.fetch",
        action_category="read",
    )

    assert decision.allowed
