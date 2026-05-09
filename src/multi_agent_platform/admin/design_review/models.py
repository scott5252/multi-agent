from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignDevelopmentHandoffStatus,
    DesignManualDecision,
    DesignManualDecisionType,
    DesignQuorumDecision,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerVerdictValue,
    DesignReviewRound,
    DesignReviewRoundStatus,
    DesignReviewSession,
    DesignReviewSessionStatus,
    DesignRevision,
)


@dataclass(frozen=True)
class DesignReviewMutationResult[T]:
    record: T
    replayed: bool = False


@dataclass(slots=True, frozen=True)
class DesignReviewCoordinatorReviewer:
    reviewer_key: str
    role_key: str
    prompt_version_id: UUID | None = None
    profile_version_id: UUID | None = None
    provider_reference: str | None = None
    enabled: bool = True


@dataclass(slots=True, frozen=True)
class DesignReviewCoordinatorVerdict:
    reviewer_key: str
    verdict: str
    score: int
    blocking_issue_count: int
    safe_feedback_summary: str
    output_digest: str
    artifact_id: UUID | None = None
    usage_summary: dict[str, object] | None = None


@dataclass(slots=True, frozen=True)
class DesignReviewCoordinatorState:
    session: DesignReviewSession
    active_revision: DesignRevision | None
    latest_round: DesignReviewRound | None
    latest_quorum_decision: DesignQuorumDecision | None
    handoff: DesignDevelopmentHandoff | None
    manual_decisions: tuple[DesignManualDecision, ...]


@dataclass(slots=True, frozen=True)
class DesignReviewCoordinatorResult:
    session: DesignReviewSession
    round_record: DesignReviewRound | None = None
    active_revision: DesignRevision | None = None
    created_revision: DesignRevision | None = None
    quorum_decision: DesignQuorumDecision | None = None
    handoff: DesignDevelopmentHandoff | None = None
    manual_decision: DesignManualDecision | None = None
    workflow_run_id: UUID | None = None
    replayed: bool = False
    next_action: str = "none"


__all__ = [
    "DesignDevelopmentHandoffStatus",
    "DesignReviewCoordinatorResult",
    "DesignReviewCoordinatorReviewer",
    "DesignReviewCoordinatorState",
    "DesignReviewCoordinatorVerdict",
    "DesignManualDecisionType",
    "DesignQuorumDecisionStatus",
    "DesignQuorumNextAction",
    "DesignReviewMutationResult",
    "DesignReviewerVerdictValue",
    "DesignReviewRoundStatus",
    "DesignReviewSessionStatus",
]
