from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import ScopeSelector, ToolPolicyCandidate
from multi_agent_platform.config.policy import evaluate_tool_policy


def test_tool_policy_denies_by_default() -> None:
    decision = evaluate_tool_policy(
        candidates=[],
        scope=ScopeSelector(tenant_id=uuid4()),
        skill_slug="web",
        tool_id="http.fetch",
        action_category="read",
    )

    assert not decision.allowed
    assert decision.denial_category is not None
    assert decision.denial_category.value == "tool_denied"


def test_tool_policy_requires_every_applicable_policy_to_allow_action() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    allow = ToolPolicyCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        allowed_action_categories=("read",),
    )
    broader_deny = ToolPolicyCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=scope,
        activation_reason="test",
        tool_id="http.fetch",
        allowed_action_categories=("write",),
    )

    decision = evaluate_tool_policy(
        candidates=[allow, broader_deny],
        scope=scope,
        skill_slug=None,
        tool_id="http.fetch",
        action_category="read",
    )

    assert not decision.allowed
