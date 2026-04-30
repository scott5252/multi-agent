from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from multi_agent_platform.admin.skill_registry.manifest import (
    SkillManifest,
    SkillManifestError,
)

KNOWN_ACTION_CATEGORIES = {
    "read",
    "write",
    "notify",
    "admin",
    "search",
    "summarize",
    "calendar",
}
APPROVED_RUNTIME_PERMISSIONS = {
    "tool_access",
    "network_access",
    "credential_access",
    "tenant_data_access",
}


@dataclass(frozen=True, slots=True)
class SkillValidationFinding:
    code: str
    message: str
    severity: str = "blocking"
    field_path: str | None = None
    blocking: bool = True
    remediation: str | None = None


@dataclass(frozen=True, slots=True)
class SkillPackageValidationResult:
    status: str
    findings: tuple[SkillValidationFinding, ...] = ()
    manifest_digest: str | None = None
    safe_summary: dict[str, Any] = field(default_factory=dict)

    @property
    def blocking_issue_count(self) -> int:
        return sum(1 for finding in self.findings if finding.blocking)


def validate_manifest_payload(
    payload: dict[str, Any],
    *,
    approved_integration_refs: set[str] | None = None,
    known_action_categories: set[str] | None = None,
) -> SkillPackageValidationResult:
    findings: list[SkillValidationFinding] = []
    try:
        manifest = SkillManifest.model_validate(payload)
    except SkillManifestError as exc:
        return SkillPackageValidationResult(
            status="blocked",
            findings=(
                SkillValidationFinding(
                    code="manifest.secret_material",
                    message=str(exc),
                    field_path="manifest",
                ),
            ),
        )
    except ValueError as exc:
        return SkillPackageValidationResult(
            status="blocked",
            findings=(
                SkillValidationFinding(
                    code="manifest.invalid",
                    message=str(exc),
                    field_path="manifest",
                ),
            ),
        )

    approved_refs = approved_integration_refs or {
        manifest.entrypoint.approved_integration_ref,
        *(tool.approved_integration_ref for tool in manifest.tools),
    }
    vocabulary = known_action_categories or KNOWN_ACTION_CATEGORIES
    if manifest.entrypoint.approved_integration_ref not in approved_refs:
        findings.append(
            SkillValidationFinding(
                code="entrypoint.unapproved_ref",
                message="Entrypoint references an unapproved integration.",
                field_path="entrypoint.approved_integration_ref",
            )
        )
    for index, tool in enumerate(manifest.tools):
        if tool.approved_integration_ref not in approved_refs:
            findings.append(
                SkillValidationFinding(
                    code="tool.unapproved_ref",
                    message="Tool references an unapproved integration.",
                    field_path=f"tools[{index}].approved_integration_ref",
                )
            )
        unknown_categories = set(tool.action_categories) - vocabulary
        if unknown_categories:
            findings.append(
                SkillValidationFinding(
                    code="tool.unknown_action_category",
                    message="Tool declares unknown action categories.",
                    field_path=f"tools[{index}].action_categories",
                )
            )
    for index, permission in enumerate(manifest.runtime_permissions):
        if permission.permission_type not in APPROVED_RUNTIME_PERMISSIONS:
            findings.append(
                SkillValidationFinding(
                    code="permission.unsupported",
                    message="Runtime permission is not supported.",
                    field_path=f"runtime_permissions[{index}].permission_type",
                )
            )
    for index, docs in enumerate([manifest.safe_documentation]):
        if docs.redaction_classification not in {"safe", "restricted"}:
            findings.append(
                SkillValidationFinding(
                    code="documentation.unsafe",
                    message="Documentation must be classified safe or restricted.",
                    field_path=f"safe_documentation[{index}]",
                )
            )
    status = (
        "passed" if not any(finding.blocking for finding in findings) else "blocked"
    )
    return SkillPackageValidationResult(
        status=status,
        findings=tuple(findings),
        manifest_digest=manifest_digest(manifest),
        safe_summary=safe_manifest_summary(manifest),
    )


def manifest_digest(manifest: SkillManifest) -> str:
    from multi_agent_platform.admin.skill_registry.manifest import (
        canonical_manifest_digest,
    )

    return canonical_manifest_digest(manifest)


def safe_manifest_summary(manifest: SkillManifest) -> dict[str, Any]:
    return {
        "slug": manifest.slug,
        "semantic_version": manifest.semantic_version,
        "entrypoint_type": manifest.entrypoint.type,
        "tools": [tool.tool_id for tool in manifest.tools],
        "action_categories": list(manifest.action_categories),
        "credential_requirements": [
            requirement.requirement_key
            for requirement in manifest.credential_requirements
        ],
        "fixture_count": len(manifest.test_fixtures),
        "documentation_status": manifest.safe_documentation.redaction_classification,
    }
