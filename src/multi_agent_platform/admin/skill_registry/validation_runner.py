from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from multi_agent_platform.admin.skill_registry.validation import (
    SkillPackageValidationResult,
    SkillValidationFinding,
    validate_manifest_payload,
)


@dataclass(frozen=True, slots=True)
class PackageValidationCandidate:
    manifest: dict[str, Any]
    artifact_digest: str
    documentation_digest: str | None
    approved_integration_refs: set[str]


class IsolatedPackageValidationRunner:
    def run(
        self, candidate: PackageValidationCandidate
    ) -> SkillPackageValidationResult:
        result = validate_manifest_payload(
            candidate.manifest,
            approved_integration_refs=candidate.approved_integration_refs,
        )
        findings = list(result.findings)
        artifact_digests = candidate.manifest.get("artifact_digests", {})
        if artifact_digests.get("package") not in {None, candidate.artifact_digest}:
            findings.append(
                SkillValidationFinding(
                    code="artifact.digest_mismatch",
                    message="Package artifact digest does not match manifest.",
                    field_path="artifact_digests.package",
                )
            )
        if candidate.documentation_digest is not None and artifact_digests.get(
            "documentation"
        ) not in {None, candidate.documentation_digest}:
            findings.append(
                SkillValidationFinding(
                    code="documentation.digest_mismatch",
                    message="Documentation digest does not match manifest.",
                    field_path="artifact_digests.documentation",
                )
            )
        status = (
            "passed" if not any(finding.blocking for finding in findings) else "blocked"
        )
        return SkillPackageValidationResult(
            status=status,
            findings=tuple(findings),
            manifest_digest=result.manifest_digest,
            safe_summary=result.safe_summary,
        )
