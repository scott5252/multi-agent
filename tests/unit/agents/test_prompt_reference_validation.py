from __future__ import annotations

from multi_agent_platform.agents.validation import validate_profile_prompt_references


def test_profile_prompt_reference_validation_blocks_unsafe_prompts() -> None:
    report = validate_profile_prompt_references(
        prompt_references=[
            {
                "prompt_version_id": "prompt-active",
                "purpose": "planner",
                "required_purpose": "planner",
            },
            {
                "prompt_version_id": "prompt-retired",
                "purpose": "planner",
                "required_purpose": "planner",
            },
            {
                "prompt_version_id": "prompt-platform",
                "purpose": "writer",
                "required_purpose": "reviewer",
            },
        ],
        prompt_versions={
            "prompt-active": {
                "status": "active",
                "scope_type": "tenant",
                "tenant_id": "tenant-a",
            },
            "prompt-retired": {
                "status": "retired",
                "scope_type": "tenant",
                "tenant_id": "tenant-a",
            },
            "prompt-platform": {
                "status": "active",
                "scope_type": "platform",
                "grants": ["tenant-b"],
            },
        },
        tenant_id="tenant-a",
    )

    assert report.status == "failed"
    assert {finding.code for finding in report.findings} == {
        "retired_prompt_blocked",
        "platform_prompt_grant_required",
        "prompt_purpose_mismatch",
    }


def test_profile_prompt_reference_validation_blocks_missing_ids_and_versions() -> None:
    report = validate_profile_prompt_references(
        prompt_references=[{}, {"prompt_version_id": "missing"}],
        prompt_versions={},
        tenant_id="tenant-a",
    )

    assert report.status == "failed"
    assert [finding.code for finding in report.findings] == [
        "missing_prompt_version_id",
        "prompt_version_not_found",
    ]
