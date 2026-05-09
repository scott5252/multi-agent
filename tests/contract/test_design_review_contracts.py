from __future__ import annotations

from uuid import uuid4

from pydantic import ValidationError

from multi_agent_platform.api.schemas.design_review import (
    DesignManualDecisionCreateRequest,
    DesignReviewSessionCreateRequest,
    DesignReviewSessionListResponse,
    DesignReviewState,
)


def test_session_create_contract_requires_tenant_summary_and_idempotency() -> None:
    request = DesignReviewSessionCreateRequest(
        tenant_id=uuid4(),
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="create-session",
    )

    assert request.request_summary == "Review checkout redesign."
    assert request.initial_revision is None


def test_session_create_contract_rejects_empty_summary() -> None:
    try:
        DesignReviewSessionCreateRequest(
            tenant_id=uuid4(),
            request_summary="",
            quorum_policy_key="four_of_five_no_blockers",
            idempotency_key="create-session",
        )
    except ValidationError as exc:
        assert "String should have at least 1 character" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected validation error")


def test_manual_decision_contract_bounds_decision_type() -> None:
    request = DesignManualDecisionCreateRequest(
        tenant_id=uuid4(),
        decision_type="revise",
        safe_rationale="Request one more revision.",
        idempotency_key="manual-1",
    )

    assert request.decision_type == "revise"


def test_list_response_exposes_truthful_empty_state() -> None:
    response = DesignReviewSessionListResponse(
        items=[],
        state=DesignReviewState(
            kind="empty",
            summary="No design review sessions exist for this tenant.",
        ),
    )

    assert response.state.kind == "empty"
