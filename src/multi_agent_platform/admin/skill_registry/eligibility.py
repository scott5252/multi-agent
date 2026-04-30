from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class InstalledSkillEvidence:
    tenant_id: str
    installation_id: str
    installation_version: int
    package_slug: str
    semantic_version: str
    manifest_digest: str
    artifact_digest: str
    readiness_state: str
    credential_status: str = "ready"
    compatibility_status: str = "ready"
    permission_status: str = "ready"
    quarantine_state: str = "clear"
    runtime_blocked: bool = False
    action_categories: tuple[str, ...] = ()
    policy_summary: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SkillEligibilityDecision:
    allowed: bool
    reason_codes: tuple[str, ...]
    evidence: dict[str, object]


def evaluate_binding_eligibility(
    evidence: InstalledSkillEvidence,
    *,
    required_action_categories: set[str] | None = None,
) -> SkillEligibilityDecision:
    reasons: list[str] = []
    if evidence.readiness_state != "ready":
        reasons.append("installation.not_ready")
    if evidence.credential_status != "ready":
        reasons.append("credential.not_ready")
    if evidence.compatibility_status != "ready":
        reasons.append("compatibility.not_ready")
    if evidence.permission_status != "ready":
        reasons.append("permission.not_ready")
    if evidence.quarantine_state != "clear" or evidence.runtime_blocked:
        reasons.append("quarantine.runtime_blocked")
    if (
        required_action_categories is not None
        and not required_action_categories.issubset(set(evidence.action_categories))
    ):
        reasons.append("policy.action_category_mismatch")
    return SkillEligibilityDecision(
        allowed=not reasons,
        reason_codes=tuple(reasons),
        evidence={
            "tenant_id": evidence.tenant_id,
            "installation_id": evidence.installation_id,
            "installation_version": evidence.installation_version,
            "package_slug": evidence.package_slug,
            "semantic_version": evidence.semantic_version,
            "manifest_digest": evidence.manifest_digest,
            "artifact_digest": evidence.artifact_digest,
            "policy_summary": evidence.policy_summary,
        },
    )
