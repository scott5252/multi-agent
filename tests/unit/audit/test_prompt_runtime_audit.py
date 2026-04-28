from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.classification import classify_field
from multi_agent_platform.audit.models import SensitivityLabel
from multi_agent_platform.prompts.audit import (
    aggregate_prompt_history,
    prompt_audit_summary,
)


def test_prompt_runtime_audit_summaries_exclude_raw_prompt_content() -> None:
    summary = prompt_audit_summary(
        action="publish",
        prompt_lineage_id=uuid4(),
        prompt_version_id=uuid4(),
        outcome="recorded",
        finding_codes=("passed",),
    )
    history = aggregate_prompt_history([{"action": "publish", "safe_summary": summary}])

    assert "template_content" not in summary
    assert history[0]["outcome"] == "recorded"
    assert classify_field("rendered_preview") is SensitivityLabel.PROMPT_CONTENT
