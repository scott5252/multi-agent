from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import ScopeSelector, SkillBindingCandidate
from multi_agent_platform.config.policy import evaluate_skill_access


def test_skill_access_denies_by_default_without_active_binding() -> None:
    decision = evaluate_skill_access(
        candidates=[],
        scope=ScopeSelector(tenant_id=uuid4()),
        skill_slug="web-research",
        skill_version="1.0.0",
        use_context="runtime_step",
    )

    assert not decision.allowed
    assert decision.denial_category is not None
    assert decision.denial_category.value == "skill_not_bound"
    assert decision.evaluated_version_ids == ()


def test_skill_access_requires_exact_skill_version_match() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    binding = SkillBindingCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        skill_slug="web-research",
        skill_version="1.0.0",
        allowed_contexts=("runtime_step",),
    )

    decision = evaluate_skill_access(
        candidates=[binding],
        scope=scope,
        skill_slug="web-research",
        skill_version="2.0.0",
        use_context="runtime_step",
    )

    assert not decision.allowed
    assert decision.denial_category is not None
    assert decision.denial_category.value == "skill_not_bound"
    assert binding.version_id not in decision.evaluated_version_ids


def test_skill_access_enforces_allowed_context_constraints() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    binding = SkillBindingCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        skill_slug="web-research",
        skill_version="1.0.0",
        allowed_contexts=("design_time",),
    )

    decision = evaluate_skill_access(
        candidates=[binding],
        scope=scope,
        skill_slug="web-research",
        skill_version="1.0.0",
        use_context="runtime_step",
    )

    assert not decision.allowed
    assert decision.denial_category is not None
    assert decision.denial_category.value == "skill_not_bound"
    assert decision.evaluated_version_ids == (binding.version_id,)


def test_skill_access_allows_matching_binding_and_reports_version() -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
    workflow_scope = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_id,
    )
    request_scope = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_id,
        agent_key="researcher",
    )
    binding = SkillBindingCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=workflow_scope,
        activation_reason="test",
        skill_slug="web-research",
        skill_version="1.0.0",
        allowed_contexts=("runtime_step",),
    )

    decision = evaluate_skill_access(
        candidates=[binding],
        scope=request_scope,
        skill_slug="web-research",
        skill_version="1.0.0",
        use_context="runtime_step",
    )

    assert decision.allowed
    assert decision.denial_category is None
    assert decision.evaluated_version_ids == (binding.version_id,)
    assert decision.winning_version_ids == (binding.version_id,)
