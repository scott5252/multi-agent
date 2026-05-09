from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.design_review.service import (
    DesignReviewAccessError,
    DesignReviewService,
    DesignReviewValidationError,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository
from multi_agent_platform.tenancy.context import ScopeType


def _tenant_admin(tenant_id):
    return PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        tenant_id=tenant_id,
        role_codes=("tenant_admin", "tenant_user"),
        scope_type=ScopeType.TENANT,
        trace_id="trace-service",
    )


async def test_service_creates_idempotent_session(session, seeded_tenant) -> None:
    service = DesignReviewService(DesignReviewRepository(session))
    principal = _tenant_admin(seeded_tenant.tenant_id)

    first, first_revision = await service.create_session(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="session-1",
    )
    second, second_revision = await service.create_session(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        request_summary="Review checkout redesign again.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="session-1",
    )

    assert first.replayed is False
    assert second.replayed is True
    assert (
        second.record.design_review_session_id == first.record.design_review_session_id
    )
    assert second_revision.design_revision_id == first_revision.design_revision_id


async def test_service_rejects_cross_tenant_access(session, seeded_tenant) -> None:
    service = DesignReviewService(DesignReviewRepository(session))
    principal = _tenant_admin(uuid4())

    with pytest.raises(DesignReviewAccessError):
        await service.create_session(
            principal=principal,
            tenant_id=seeded_tenant.tenant_id,
            request_summary="Review checkout redesign.",
            quorum_policy_key="four_of_five_no_blockers",
            idempotency_key="session-denied",
        )


async def test_service_rejects_unsafe_summary(session, seeded_tenant) -> None:
    service = DesignReviewService(DesignReviewRepository(session))

    with pytest.raises(DesignReviewValidationError):
        await service.create_session(
            principal=_tenant_admin(seeded_tenant.tenant_id),
            tenant_id=seeded_tenant.tenant_id,
            request_summary="Authorization: Bearer hidden",
            quorum_policy_key="four_of_five_no_blockers",
            idempotency_key="session-unsafe",
        )


async def test_service_records_manual_decision_append_only(
    session, seeded_tenant
) -> None:
    service = DesignReviewService(DesignReviewRepository(session))
    principal = _tenant_admin(seeded_tenant.tenant_id)
    created, _ = await service.create_session(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="session-manual",
    )

    first = await service.record_manual_decision(
        principal=principal,
        session_id=created.record.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
        decision_type="revise",
        safe_rationale="Ask for clearer accessibility notes.",
        idempotency_key="manual-1",
    )
    replay = await service.record_manual_decision(
        principal=principal,
        session_id=created.record.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
        decision_type="revise",
        safe_rationale="Ask for clearer accessibility notes.",
        idempotency_key="manual-1",
    )

    assert first.replayed is False
    assert replay.replayed is True
    assert (
        replay.record.design_manual_decision_id
        == first.record.design_manual_decision_id
    )


async def test_service_records_round_evidence_and_handoff(
    session, seeded_tenant
) -> None:
    service = DesignReviewService(DesignReviewRepository(session))
    principal = _tenant_admin(seeded_tenant.tenant_id)
    created, revision = await service.create_session(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="session-evidence",
    )

    round_result = await service.record_round(
        tenant_id=seeded_tenant.tenant_id,
        session_id=created.record.design_review_session_id,
        revision_id=revision.design_revision_id,
        round_number=1,
        reviewer_count=2,
        quorum_count=1,
        idempotency_key="round-evidence",
        status="completed",
    )
    round_replay = await service.record_round(
        tenant_id=seeded_tenant.tenant_id,
        session_id=created.record.design_review_session_id,
        revision_id=revision.design_revision_id,
        round_number=1,
        reviewer_count=2,
        quorum_count=1,
        idempotency_key="round-evidence",
        status="completed",
    )
    assignment = await service.record_assignment(
        tenant_id=seeded_tenant.tenant_id,
        round_id=round_result.record.design_review_round_id,
        reviewer_key="accessibility",
        role_key="accessibility_reviewer",
        provider_reference="qa060 provider reference",
    )
    verdict = await service.record_verdict(
        tenant_id=seeded_tenant.tenant_id,
        round_id=round_result.record.design_review_round_id,
        reviewer_key="accessibility",
        verdict="approved",
        score=5,
        blocking_issue_count=0,
        safe_feedback_summary="Accessibility passed.",
        output_digest="digest-verdict",
        usage_summary={"tokens": 10, "provider": "local safe provider"},
        idempotency_key="verdict-evidence",
    )
    decision = await service.record_quorum_decision(
        tenant_id=seeded_tenant.tenant_id,
        round_id=round_result.record.design_review_round_id,
        status="passed",
        approval_count=1,
        blocking_issue_count=0,
        next_action="handoff",
        policy_version="qa060-v1",
        safe_rationale="Quorum passed.",
    )
    manual = await service.record_manual_decision(
        principal=principal,
        session_id=created.record.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
        round_id=round_result.record.design_review_round_id,
        decision_type="approve_exception",
        safe_rationale="Approved with explicit risk acceptance.",
        accepted_risk=True,
        idempotency_key="manual-round-evidence",
    )
    handoff = await service.record_handoff(
        tenant_id=seeded_tenant.tenant_id,
        session_id=created.record.design_review_session_id,
        approved_revision_id=revision.design_revision_id,
        safe_summary="Ready for implementation.",
        output_digest="digest-handoff",
        idempotency_key="handoff-evidence",
    )

    assert round_result.replayed is False
    assert round_replay.replayed is True
    assert assignment.provider_reference == "qa060 provider reference"
    assert verdict.record.usage_summary["tokens"] == 10
    assert decision.next_action.value == "handoff"
    assert manual.record.accepted_risk is True
    assert handoff.record.status.value == "ready"
    assert await service.round_assignments(
        principal=principal,
        round_id=round_result.record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
    )
    assert await service.round_verdicts(
        principal=principal,
        round_id=round_result.record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
    )
    assert await service.get_quorum_decision(
        principal=principal,
        round_id=round_result.record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
    )
    assert await service.get_handoff(
        principal=principal,
        session_id=created.record.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
    )


async def test_service_validates_evidence_counts_and_keys(
    session, seeded_tenant
) -> None:
    service = DesignReviewService(DesignReviewRepository(session))
    principal = _tenant_admin(seeded_tenant.tenant_id)
    created, revision = await service.create_session(
        principal=principal,
        tenant_id=seeded_tenant.tenant_id,
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="session-validation",
    )

    with pytest.raises(DesignReviewValidationError):
        await service.list_sessions(
            principal=principal,
            tenant_id=seeded_tenant.tenant_id,
            status="unsupported",
        )
    with pytest.raises(DesignReviewValidationError):
        await service.record_round(
            tenant_id=seeded_tenant.tenant_id,
            session_id=created.record.design_review_session_id,
            revision_id=revision.design_revision_id,
            round_number=1,
            reviewer_count=1,
            quorum_count=2,
        )
    with pytest.raises(DesignReviewValidationError):
        await service.record_verdict(
            tenant_id=seeded_tenant.tenant_id,
            round_id=uuid4(),
            reviewer_key="accessibility",
            verdict="approved",
            score=-1,
            blocking_issue_count=0,
            safe_feedback_summary="Invalid score.",
            output_digest="digest",
        )
    with pytest.raises(DesignReviewValidationError):
        await service.record_quorum_decision(
            tenant_id=seeded_tenant.tenant_id,
            round_id=uuid4(),
            status="passed",
            approval_count=-1,
            blocking_issue_count=0,
            next_action="handoff",
            policy_version="qa060-v1",
            safe_rationale="Invalid decision.",
        )
    with pytest.raises(DesignReviewValidationError):
        await service.create_session(
            principal=principal,
            tenant_id=seeded_tenant.tenant_id,
            request_summary="Review checkout redesign.",
            quorum_policy_key="x" * 161,
            idempotency_key="session-long-key",
        )
