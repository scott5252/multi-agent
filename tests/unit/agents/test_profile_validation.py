from __future__ import annotations

from multi_agent_platform.agents.validation import validate_profile_contract


def test_profile_validation_reports_missing_required_contract_sections() -> None:
    report = validate_profile_contract(
        prompt_references=[],
        model_routing_hints={},
        memory_scope_policy={},
        skill_requirements=[],
        tool_policy_expectations=[],
        output_contract_expectations={},
        test_suite_requirements=[],
    )

    codes = {finding.code for finding in report.findings}
    assert report.status == "failed"
    assert {
        "missing_prompt_reference",
        "missing_model_routing",
        "missing_memory_policy",
        "missing_skill_requirement",
        "missing_tool_policy",
        "missing_output_contract",
        "missing_test_suite",
    } <= codes
