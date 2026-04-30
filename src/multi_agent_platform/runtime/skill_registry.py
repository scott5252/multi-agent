from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.admin.skill_registry.eligibility import (
    InstalledSkillEvidence,
    SkillEligibilityDecision,
    evaluate_binding_eligibility,
)


@dataclass(frozen=True, slots=True)
class RuntimeSkillDecision:
    allowed: bool
    reason_codes: tuple[str, ...]
    pinned_evidence: dict[str, object]


def evaluate_runtime_skill_use(
    evidence: InstalledSkillEvidence,
) -> RuntimeSkillDecision:
    decision: SkillEligibilityDecision = evaluate_binding_eligibility(evidence)
    return RuntimeSkillDecision(
        allowed=decision.allowed,
        reason_codes=decision.reason_codes,
        pinned_evidence=decision.evidence,
    )
