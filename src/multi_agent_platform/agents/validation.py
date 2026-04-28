from __future__ import annotations

from multi_agent_platform.agents.models import (
    ProfileValidationFinding,
    ProfileValidationReport,
)


def _missing(
    findings: list[ProfileValidationFinding],
    *,
    code: str,
    section: str,
    message: str,
) -> None:
    findings.append(
        ProfileValidationFinding(
            code=code,
            severity="blocking",
            message=message,
            section=section,
        )
    )


def validate_profile_contract(
    *,
    prompt_references: list[dict[str, object]],
    model_routing_hints: dict[str, object],
    memory_scope_policy: dict[str, object],
    skill_requirements: list[dict[str, object]],
    tool_policy_expectations: list[dict[str, object]],
    output_contract_expectations: dict[str, object],
    test_suite_requirements: list[dict[str, object]],
) -> ProfileValidationReport:
    findings: list[ProfileValidationFinding] = []
    if not prompt_references:
        _missing(
            findings,
            code="missing_prompt_reference",
            section="prompt_references",
            message="At least one active prompt reference is required.",
        )
    if not model_routing_hints:
        _missing(
            findings,
            code="missing_model_routing",
            section="model_routing_hints",
            message="Model routing hints are required.",
        )
    if not memory_scope_policy:
        _missing(
            findings,
            code="missing_memory_policy",
            section="memory_scope_policy",
            message="Memory scope policy is required.",
        )
    if not skill_requirements:
        _missing(
            findings,
            code="missing_skill_requirement",
            section="skill_requirements",
            message="At least one skill requirement is required.",
        )
    if not tool_policy_expectations:
        _missing(
            findings,
            code="missing_tool_policy",
            section="tool_policy_expectations",
            message="Tool policy expectations are required.",
        )
    if not output_contract_expectations:
        _missing(
            findings,
            code="missing_output_contract",
            section="output_contract_expectations",
            message="Output contract expectations are required.",
        )
    if not test_suite_requirements:
        _missing(
            findings,
            code="missing_test_suite",
            section="test_suite_requirements",
            message="Test suite requirements are required.",
        )
    return ProfileValidationReport(
        status="failed" if findings else "passed",
        findings=tuple(findings),
    )
