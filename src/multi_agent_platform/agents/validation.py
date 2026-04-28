from __future__ import annotations

from multi_agent_platform.agents.models import (
    ProfileValidationFinding,
    ProfileValidationReport,
)
from multi_agent_platform.memory.policy import validate_profile_memory_policy


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
    findings.extend(
        ProfileValidationFinding(
            code=finding.code,
            severity="blocking",
            message=finding.message,
            section="memory_scope_policy",
        )
        for finding in validate_profile_memory_policy(memory_scope_policy)
    )
    return ProfileValidationReport(
        status="failed" if findings else "passed",
        findings=tuple(findings),
    )


def validate_profile_prompt_references(
    *,
    prompt_references: list[dict[str, object]],
    prompt_versions: dict[str, dict[str, object]],
    tenant_id: str | None,
) -> ProfileValidationReport:
    findings: list[ProfileValidationFinding] = []
    for index, reference in enumerate(prompt_references):
        version_id = str(reference.get("prompt_version_id", "")).strip()
        purpose = str(reference.get("purpose", "")).strip()
        expected_purpose = str(reference.get("required_purpose", purpose)).strip()
        if not version_id:
            _missing(
                findings,
                code="missing_prompt_version_id",
                section=f"prompt_references[{index}]",
                message="Prompt references must include a prompt version id.",
            )
            continue
        version = prompt_versions.get(version_id)
        if version is None:
            _missing(
                findings,
                code="prompt_version_not_found",
                section=f"prompt_references[{index}]",
                message="Referenced prompt version was not found.",
            )
            continue
        if version.get("status") != "active":
            _missing(
                findings,
                code="retired_prompt_blocked",
                section=f"prompt_references[{index}]",
                message="Retired prompt versions cannot be selected for new use.",
            )
        raw_grants = version.get("grants", [])
        grants = raw_grants if isinstance(raw_grants, list) else []
        if (
            version.get("scope_type") == "platform"
            and tenant_id
            and tenant_id not in {str(value) for value in grants}
        ):
            _missing(
                findings,
                code="platform_prompt_grant_required",
                section=f"prompt_references[{index}]",
                message="Platform prompt version requires a tenant grant.",
            )
        if expected_purpose and purpose and expected_purpose != purpose:
            _missing(
                findings,
                code="prompt_purpose_mismatch",
                section=f"prompt_references[{index}]",
                message="Prompt reference purpose does not match the required purpose.",
            )
    return ProfileValidationReport(
        status="failed" if findings else "passed",
        findings=tuple(findings),
    )
