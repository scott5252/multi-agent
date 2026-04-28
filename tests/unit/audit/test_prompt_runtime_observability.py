from __future__ import annotations

from multi_agent_platform.observability.metrics import record_prompt_runtime_action


def test_prompt_runtime_metric_recorder_accepts_safe_labels() -> None:
    record_prompt_runtime_action(
        action="validate",
        outcome="failed",
        reason="blocking_findings",
    )
