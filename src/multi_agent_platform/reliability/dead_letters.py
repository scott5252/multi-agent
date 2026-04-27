from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from multi_agent_platform.reliability.models import (
    DeadLetterStatus,
    FailureCategory,
    RecommendedAction,
)


@dataclass(slots=True)
class DeadLetterRecord:
    tenant_id: UUID
    source_kind: str
    source_id: UUID
    failure_category: FailureCategory
    latest_state: dict[str, object]
    recommended_action: RecommendedAction
    artifact_refs: list[dict[str, object]] = field(default_factory=list)
    dead_letter_id: UUID = field(default_factory=uuid4)
    status: DeadLetterStatus = DeadLetterStatus.OPEN


def recommended_action_for_failure(
    failure_category: FailureCategory,
) -> RecommendedAction:
    if failure_category in {
        FailureCategory.UNKNOWN_SIDE_EFFECT,
        FailureCategory.NON_REPEATABLE_AMBIGUOUS,
    }:
        return RecommendedAction.OPERATOR_INTERVENTION
    if failure_category is FailureCategory.ARTIFACT_UNAVAILABLE:
        return RecommendedAction.ESCALATE
    if failure_category in {
        FailureCategory.DEPENDENCY_UNAVAILABLE,
        FailureCategory.TIMEOUT,
    }:
        return RecommendedAction.REQUEUE
    return RecommendedAction.ESCALATE


def create_dead_letter(
    *,
    tenant_id: UUID,
    source_kind: str,
    source_id: UUID,
    failure_category: FailureCategory,
    latest_state: dict[str, object],
    artifact_refs: list[dict[str, object]] | None = None,
) -> DeadLetterRecord:
    if not latest_state:
        raise ValueError("dead letters require a safe latest-state summary")
    return DeadLetterRecord(
        tenant_id=tenant_id,
        source_kind=source_kind,
        source_id=source_id,
        failure_category=failure_category,
        latest_state=latest_state,
        recommended_action=recommended_action_for_failure(failure_category),
        artifact_refs=artifact_refs or [],
    )


def transition_dead_letter(
    record: DeadLetterRecord, status: DeadLetterStatus, *, actor_id: str
) -> DeadLetterRecord:
    if not actor_id:
        raise ValueError("dead-letter actions require an actor")
    record.status = status
    return record
