from __future__ import annotations

from multi_agent_platform.admin.design_review.models import (
    DesignManualDecisionType,
    DesignReviewMutationResult,
    DesignReviewSessionStatus,
)


def test_design_review_domain_enums_are_stable_strings() -> None:
    assert DesignReviewSessionStatus.DRAFT.value == "draft"
    assert DesignManualDecisionType.APPROVE_EXCEPTION.value == "approve_exception"


def test_design_review_mutation_result_tracks_replay() -> None:
    result = DesignReviewMutationResult(record="record-id", replayed=True)

    assert result.record == "record-id"
    assert result.replayed is True
