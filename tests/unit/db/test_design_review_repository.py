from __future__ import annotations

from multi_agent_platform.db.models.design_review import (
    DesignManualDecisionType,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerVerdictValue,
)
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository


async def test_repository_replays_session_creation(session, seeded_tenant) -> None:
    repository = DesignReviewRepository(session)
    (
        first_session,
        first_revision,
        first_replayed,
    ) = await repository.create_session_with_revision(
        tenant_id=seeded_tenant.tenant_id,
        owner_principal_id="tenant-admin-acme",
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="create-1",
        revision_safe_summary="Review checkout redesign.",
        revision_payload_digest="digest-1",
    )
    (
        second_session,
        second_revision,
        second_replayed,
    ) = await repository.create_session_with_revision(
        tenant_id=seeded_tenant.tenant_id,
        owner_principal_id="tenant-admin-acme",
        request_summary="Different summary should replay.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="create-1",
        revision_safe_summary="Different summary should replay.",
        revision_payload_digest="digest-2",
    )

    assert first_replayed is False
    assert second_replayed is True
    assert (
        second_session.design_review_session_id
        == first_session.design_review_session_id
    )
    assert second_revision.design_revision_id == first_revision.design_revision_id


async def test_repository_records_evidence_for_one_tenant(
    session, seeded_tenant
) -> None:
    repository = DesignReviewRepository(session)
    review_session, revision, _ = await repository.create_session_with_revision(
        tenant_id=seeded_tenant.tenant_id,
        owner_principal_id="tenant-admin-acme",
        request_summary="Review checkout redesign.",
        quorum_policy_key="four_of_five_no_blockers",
        idempotency_key="evidence-session",
        revision_safe_summary="Review checkout redesign.",
        revision_payload_digest="digest-1",
    )
    round_record, _ = await repository.create_round(
        session_id=review_session.design_review_session_id,
        revision_id=revision.design_revision_id,
        tenant_id=seeded_tenant.tenant_id,
        round_number=1,
        reviewer_count=5,
        quorum_count=4,
        idempotency_key="round-1",
    )
    assignment = await repository.create_assignment(
        round_id=round_record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
        reviewer_key="accessibility",
        role_key="accessibility_reviewer",
    )
    verdict, replayed = await repository.create_verdict(
        round_id=round_record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
        reviewer_key="accessibility",
        verdict=DesignReviewerVerdictValue.APPROVED,
        score=5,
        blocking_issue_count=0,
        safe_feedback_summary="Accessibility concerns addressed.",
        output_digest="digest-verdict",
        idempotency_key="verdict-1",
    )
    decision = await repository.create_quorum_decision(
        round_id=round_record.design_review_round_id,
        tenant_id=seeded_tenant.tenant_id,
        status=DesignQuorumDecisionStatus.PASSED,
        approval_count=4,
        blocking_issue_count=0,
        next_action=DesignQuorumNextAction.HANDOFF,
        policy_version="qa060-v1",
        safe_rationale="Quorum passed.",
    )
    manual, manual_replayed = await repository.create_manual_decision(
        session_id=review_session.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
        round_id=round_record.design_review_round_id,
        decision_type=DesignManualDecisionType.REVISE,
        actor_principal_id="tenant-admin-acme",
        safe_rationale="Record follow-up notes.",
        accepted_risk=False,
        idempotency_key="manual-1",
    )
    handoff, handoff_replayed = await repository.create_handoff(
        session_id=review_session.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
        approved_revision_id=revision.design_revision_id,
        safe_summary="Ready for implementation.",
        output_digest="digest-handoff",
        idempotency_key="handoff-1",
    )

    assert assignment.reviewer_key == "accessibility"
    assert replayed is False
    assert verdict.output_digest == "digest-verdict"
    assert decision.next_action is DesignQuorumNextAction.HANDOFF
    assert manual_replayed is False
    assert handoff_replayed is False
    assert manual.design_review_round_id == round_record.design_review_round_id
    assert handoff.approved_revision_id == revision.design_revision_id
    assert await repository.get_session_for_tenant(
        session_id=review_session.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
    )
    assert await repository.list_rounds(
        session_id=review_session.design_review_session_id,
        tenant_id=seeded_tenant.tenant_id,
    )
