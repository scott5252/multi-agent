from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.design_review import (
    DesignReviewCoordinatorCompleteRequest,
    DesignReviewCoordinatorLaunchRequest,
    DesignReviewCoordinatorManualDecisionRequest,
    DesignReviewCoordinatorReviewerRequest,
    DesignReviewCoordinatorVerdictRequest,
)


def test_launch_request_accepts_reviewers_and_workflow_bundle() -> None:
    payload = DesignReviewCoordinatorLaunchRequest(
        tenant_id=uuid4(),
        workflow_version_bundle_id=uuid4(),
        idempotency_key="launch-1",
        reviewers=[
            DesignReviewCoordinatorReviewerRequest(
                reviewer_key="product-fit",
                role_key="product-fit-reviewer",
            )
        ],
    )

    assert payload.max_rounds == 3
    assert payload.execution_mode == "deterministic"
    assert payload.reviewers[0].enabled is True


def test_launch_request_rejects_zero_max_rounds() -> None:
    with pytest.raises(ValidationError):
        DesignReviewCoordinatorLaunchRequest(
            tenant_id=uuid4(),
            idempotency_key="launch-1",
            max_rounds=0,
        )


def test_complete_request_accepts_safe_verdicts() -> None:
    payload = DesignReviewCoordinatorCompleteRequest(
        tenant_id=uuid4(),
        idempotency_key="complete-1",
        safe_synthesis_summary="Council approves handoff.",
        verdicts=[
            DesignReviewCoordinatorVerdictRequest(
                reviewer_key="accessibility",
                verdict="approved",
                score=5,
                blocking_issue_count=0,
                safe_feedback_summary="Accessible and ready.",
                output_digest="digest-accessibility",
            )
        ],
    )

    assert payload.verdicts[0].verdict == "approved"
    assert payload.verdicts[0].usage_summary == {}


def test_complete_request_rejects_invalid_verdict() -> None:
    with pytest.raises(ValidationError):
        DesignReviewCoordinatorVerdictRequest(
            reviewer_key="accessibility",
            verdict="unsafe",
            score=5,
            blocking_issue_count=0,
            safe_feedback_summary="Accessible and ready.",
            output_digest="digest-accessibility",
        )


def test_manual_decision_request_requires_supported_action() -> None:
    payload = DesignReviewCoordinatorManualDecisionRequest(
        tenant_id=uuid4(),
        decision_type="approve_exception",
        safe_rationale="Accept the residual design risk.",
        accepted_risk=True,
        idempotency_key="manual-approve",
    )

    assert payload.decision_type == "approve_exception"
    assert payload.accepted_risk is True


def test_manual_decision_request_rejects_unknown_action() -> None:
    with pytest.raises(ValidationError):
        DesignReviewCoordinatorManualDecisionRequest(
            tenant_id=uuid4(),
            decision_type="override",
            safe_rationale="Unsafe action.",
            idempotency_key="manual-unknown",
        )
