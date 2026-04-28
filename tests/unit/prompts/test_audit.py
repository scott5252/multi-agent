from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.prompts.audit import prompt_audit_summary


def test_prompt_audit_summary_omits_raw_prompt_and_fixture_values() -> None:
    summary = prompt_audit_summary(
        action="preview",
        prompt_lineage_id=uuid4(),
        prompt_version_id=None,
        outcome="denied",
        finding_codes=("unsafe_fixture_value",),
        redaction_categories=("credential",),
    )

    assert "template_content" not in summary
    assert "fixture_values" not in summary
    assert summary["finding_codes"] == ["unsafe_fixture_value"]
