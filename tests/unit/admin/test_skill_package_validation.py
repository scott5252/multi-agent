from __future__ import annotations

from multi_agent_platform.admin.skill_registry.validation import (
    validate_manifest_payload,
)
from multi_agent_platform.admin.skill_registry.validation_runner import (
    IsolatedPackageValidationRunner,
    PackageValidationCandidate,
)
from tests.fixtures.skill_registry import valid_skill_manifest


def test_package_validation_accepts_valid_manifest() -> None:
    manifest = valid_skill_manifest()
    result = validate_manifest_payload(
        manifest,
        approved_integration_refs={"tool:calendar:v1"},
    )

    assert result.status == "passed"
    assert result.blocking_issue_count == 0
    assert result.safe_summary["slug"] == "calendar-assistant"


def test_package_validation_blocks_unapproved_tool_reference() -> None:
    manifest = valid_skill_manifest()
    result = validate_manifest_payload(
        manifest,
        approved_integration_refs={"tool:other:v1"},
    )

    assert result.status == "blocked"
    assert {finding.code for finding in result.findings} >= {
        "entrypoint.unapproved_ref",
        "tool.unapproved_ref",
    }


def test_validation_runner_blocks_digest_mismatch() -> None:
    result = IsolatedPackageValidationRunner().run(
        PackageValidationCandidate(
            manifest=valid_skill_manifest(),
            artifact_digest="sha256:different",
            documentation_digest="sha256:docs",
            approved_integration_refs={"tool:calendar:v1"},
        )
    )

    assert result.status == "blocked"
    assert "artifact.digest_mismatch" in {finding.code for finding in result.findings}


def test_package_validation_blocks_unsafe_docs_and_unknown_action() -> None:
    manifest = valid_skill_manifest()
    manifest["safe_documentation"] = {
        "summary": "Restricted package notes.",
        "redaction_classification": "unsafe",
    }
    manifest["tools"][0]["action_categories"] = ["unknown"]

    result = validate_manifest_payload(
        manifest,
        approved_integration_refs={"tool:calendar:v1"},
    )

    assert result.status == "blocked"
    assert "documentation.unsafe" in {finding.code for finding in result.findings}
    assert "tool.unknown_action_category" in {
        finding.code for finding in result.findings
    }
