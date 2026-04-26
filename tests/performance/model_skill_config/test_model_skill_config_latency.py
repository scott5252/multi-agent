from __future__ import annotations

from time import perf_counter
from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import (
    ScopeSelector,
    ToolPolicyCandidate,
)
from multi_agent_platform.config.policy import evaluate_tool_policy


@pytest.mark.performance
def test_tool_policy_evaluation_stays_bounded_for_hundreds_of_versions() -> None:
    tenant_id = uuid4()
    scope = ScopeSelector(tenant_id=tenant_id)
    policies = [
        ToolPolicyCandidate(
            version_id=uuid4(),
            tenant_id=tenant_id,
            scope=scope,
            activation_reason="test",
            tool_id="http.fetch",
            allowed_action_categories=("read",),
        )
        for _ in range(300)
    ]

    started = perf_counter()
    decision = evaluate_tool_policy(
        candidates=policies,
        scope=scope,
        skill_slug=None,
        tool_id="http.fetch",
        action_category="read",
    )
    elapsed_ms = (perf_counter() - started) * 1000

    assert decision.allowed
    assert elapsed_ms < 50
