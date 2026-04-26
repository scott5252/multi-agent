from __future__ import annotations

from multi_agent_platform.observability.logging import model_skill_policy_log_context
from multi_agent_platform.observability.metrics import (
    record_model_skill_policy_decision,
)


def test_model_skill_policy_metrics_accept_bounded_labels() -> None:
    record_model_skill_policy_decision(
        decision_category="tool",
        outcome="deny",
        denial_category="tool_denied",
    )


def test_model_skill_policy_log_context_redacts_to_safe_identifiers() -> None:
    context = model_skill_policy_log_context(
        action="preview_tool",
        decision_category="credential",
        outcome="deny",
        tenant_id="tenant-1",
        denial_category="credential_unsatisfied",
        evaluated_version_count=2,
    )

    assert context["extra"]["decision_category"] == "credential"
    assert context["extra"]["evaluated_version_count"] == "2"
    assert "secret" not in context["extra"]
