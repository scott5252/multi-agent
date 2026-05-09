from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from tests.unit.runtime.orchestration.test_graph_execution import simple_graph_document

from multi_agent_platform.admin.design_review.coordinator import (
    DesignReviewCoordinator,
)
from multi_agent_platform.admin.design_review.models import (
    DesignReviewCoordinatorReviewer,
    DesignReviewCoordinatorVerdict,
)
from multi_agent_platform.admin.design_review.service import (
    DesignReviewConflictError,
    DesignReviewService,
    DesignReviewValidationError,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from multi_agent_platform.db.models.design_review import (
    DesignQuorumDecisionStatus,
    DesignReviewSessionStatus,
)
from multi_agent_platform.db.models.runtime_orchestration import RuntimeRunStatus
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.tenancy.context import ScopeType


def _principal(tenant_id: UUID) -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        tenant_id=tenant_id,
        role_codes=("tenant_admin", "tenant_user"),
        scope_type=ScopeType.TENANT,
        trace_id="trace-coordinator",
    )


async def _workflow_bundle(session, tenant_id: UUID) -> UUID:
    version_id = uuid4()
    session.add(
        WorkflowVersionBundle(
            workflow_version_bundle_id=version_id,
            workflow_lineage_id=uuid4(),
            scope_type="tenant",
            tenant_id=tenant_id,
            version_sequence=1,
            display_version="v1",
            published_from_draft_id=uuid4(),
            published_from_revision_id=uuid4(),
            published_by_principal_id=uuid4(),
            summary_json={"document": simple_graph_document()},
        )
    )
    await session.flush()
    return version_id


async def _session_and_coordinator(session, tenant_id: UUID):
    service = DesignReviewService(DesignReviewRepository(session))
    workflow_version_bundle_id = await _workflow_bundle(session, tenant_id)
    created, revision = await service.create_session(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        request_summary="Review checkout redesign for clarity.",
        quorum_policy_key="four_of_five_no_blockers",
        workflow_version_bundle_id=workflow_version_bundle_id,
        idempotency_key=f"session-{uuid4()}",
    )
    coordinator = DesignReviewCoordinator(
        design_repository=DesignReviewRepository(session),
        runtime_repository=RuntimeOrchestrationRepository(session),
    )
    return coordinator, created.record, revision, workflow_version_bundle_id


def _reviewers() -> tuple[DesignReviewCoordinatorReviewer, ...]:
    return tuple(
        DesignReviewCoordinatorReviewer(
            reviewer_key=f"reviewer-{index}",
            role_key=f"reviewer-role-{index}",
        )
        for index in range(5)
    )


def _verdicts(
    approved_count: int,
    *,
    blockers: int = 0,
) -> tuple[DesignReviewCoordinatorVerdict, ...]:
    values: list[DesignReviewCoordinatorVerdict] = []
    for index in range(5):
        approved = index < approved_count
        values.append(
            DesignReviewCoordinatorVerdict(
                reviewer_key=f"reviewer-{index}",
                verdict="approved" if approved else "changes_requested",
                score=5 if approved else 3,
                blocking_issue_count=blockers if index == 0 else 0,
                safe_feedback_summary=f"Safe reviewer {index} feedback.",
                output_digest=f"digest-{index}",
            )
        )
    return tuple(values)


async def _manual_resolution_session(session, tenant_id: UUID):
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key=f"launch-manual-{uuid4()}",
    )
    await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=4, blockers=1),
        idempotency_key=f"complete-manual-{uuid4()}",
        safe_synthesis_summary="Manual review needed.",
    )
    return coordinator, design_session, launched.round_record


async def test_coordinator_launches_round_and_runtime_run(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        revision,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)

    result = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-round-1",
    )
    replay = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-round-1",
    )
    run = await RuntimeOrchestrationRepository(session).get_run_by_id(
        workflow_run_id=result.workflow_run_id
    )

    assert result.replayed is False
    assert replay.replayed is True
    assert replay.round_record.design_review_round_id == (
        result.round_record.design_review_round_id
    )
    assert result.round_record.design_revision_id == revision.design_revision_id
    assert run is not None
    assert run.status is RuntimeRunStatus.RUNNABLE
    assert design_session.status is DesignReviewSessionStatus.REVIEWING


async def test_coordinator_approval_creates_handoff(session, seeded_tenant) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-approval",
    )

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=4),
        idempotency_key="complete-approval",
        safe_synthesis_summary="Council approves implementation handoff.",
    )

    assert completed.quorum_decision.status is DesignQuorumDecisionStatus.PASSED
    assert completed.handoff is not None
    assert completed.session.status is DesignReviewSessionStatus.APPROVED
    assert completed.next_action == "handoff"


async def test_coordinator_revision_required_creates_next_revision(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        revision,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-revision",
    )

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=3),
        idempotency_key="complete-revision",
        safe_synthesis_summary="Council requests focused revision.",
        next_revision_summary="Revise hierarchy and accessibility notes.",
    )

    assert (
        completed.quorum_decision.status is DesignQuorumDecisionStatus.REVISION_REQUIRED
    )
    assert completed.created_revision is not None
    assert (
        completed.created_revision.previous_revision_id == revision.design_revision_id
    )
    assert completed.session.status is DesignReviewSessionStatus.REVISION_REQUIRED


async def test_coordinator_blockers_pause_for_manual_resolution(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-blocker",
    )

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=4, blockers=1),
        idempotency_key="complete-blocker",
        safe_synthesis_summary="Council found one blocking issue.",
    )

    assert (
        completed.quorum_decision.status is DesignQuorumDecisionStatus.MANUAL_RESOLUTION
    )
    assert completed.session.status is DesignReviewSessionStatus.MANUAL_RESOLUTION
    assert completed.next_action == "manual_decision"


async def test_coordinator_incomplete_evidence_pauses_for_manual_resolution(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-incomplete",
    )

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=4)[:3],
        idempotency_key="complete-incomplete",
        safe_synthesis_summary="Council evidence was incomplete.",
    )

    assert (
        completed.quorum_decision.status is DesignQuorumDecisionStatus.MANUAL_RESOLUTION
    )
    assert completed.session.status is DesignReviewSessionStatus.MANUAL_RESOLUTION


async def test_coordinator_max_rounds_pause_for_manual_resolution(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-max-round",
    )

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(approved_count=3),
        idempotency_key="complete-max-round",
        safe_synthesis_summary="Council requests changes at max rounds.",
        max_rounds=1,
    )

    assert (
        completed.quorum_decision.status is DesignQuorumDecisionStatus.MANUAL_RESOLUTION
    )
    assert completed.next_action == "manual_decision"


async def test_coordinator_rejects_unsafe_completion_summary(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="launch-unsafe",
    )

    with pytest.raises(DesignReviewValidationError):
        await coordinator.complete_round(
            principal=_principal(tenant_id),
            tenant_id=tenant_id,
            round_id=launched.round_record.design_review_round_id,
            verdicts=_verdicts(approved_count=4),
            idempotency_key="complete-unsafe",
            safe_synthesis_summary="Authorization: Bearer hidden",
        )


async def test_coordinator_manual_revise_is_idempotent(session, seeded_tenant) -> None:
    tenant_id = seeded_tenant.tenant_id
    coordinator, design_session, round_record = await _manual_resolution_session(
        session, tenant_id
    )

    first = await coordinator.apply_manual_decision(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        round_id=round_record.design_review_round_id,
        decision_type="revise",
        safe_rationale="Create a focused revision from reviewer notes.",
        next_revision_summary="Manual revision requested.",
        idempotency_key="manual-revise",
    )
    replay = await coordinator.apply_manual_decision(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=design_session.design_review_session_id,
        round_id=round_record.design_review_round_id,
        decision_type="revise",
        safe_rationale="Create a focused revision from reviewer notes.",
        next_revision_summary="Manual revision requested.",
        idempotency_key="manual-revise",
    )

    assert first.created_revision is not None
    assert replay.replayed is True
    assert first.session.status is DesignReviewSessionStatus.REVISION_REQUIRED


async def test_coordinator_manual_approve_retry_and_cancel(
    session, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        approve_coordinator,
        approve_session,
        approve_round,
    ) = await _manual_resolution_session(session, tenant_id)
    approved = await approve_coordinator.apply_manual_decision(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=approve_session.design_review_session_id,
        round_id=approve_round.design_review_round_id,
        decision_type="approve_exception",
        safe_rationale="Accept residual design risk for handoff.",
        accepted_risk=True,
        idempotency_key="manual-approve-exception",
    )
    retry_coordinator, retry_session, retry_round = await _manual_resolution_session(
        session, tenant_id
    )
    retried = await retry_coordinator.apply_manual_decision(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=retry_session.design_review_session_id,
        round_id=retry_round.design_review_round_id,
        decision_type="retry",
        safe_rationale="Retry the same revision after transient evidence loss.",
        idempotency_key="manual-retry",
    )
    cancel_coordinator, cancel_session, cancel_round = await _manual_resolution_session(
        session, tenant_id
    )
    cancelled = await cancel_coordinator.apply_manual_decision(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=cancel_session.design_review_session_id,
        round_id=cancel_round.design_review_round_id,
        decision_type="cancel",
        safe_rationale="Cancel the design review session.",
        idempotency_key="manual-cancel",
    )

    assert approved.session.status is DesignReviewSessionStatus.APPROVED
    assert approved.handoff is not None
    assert retried.session.status is DesignReviewSessionStatus.REVIEWING
    assert retried.next_action == "launch_round"
    assert cancelled.session.status is DesignReviewSessionStatus.CANCELLED


async def test_coordinator_denies_terminal_launch(session, seeded_tenant) -> None:
    tenant_id = seeded_tenant.tenant_id
    (
        coordinator,
        design_session,
        _,
        workflow_version_bundle_id,
    ) = await _session_and_coordinator(session, tenant_id)
    await DesignReviewRepository(session).update_session_state(
        session=design_session,
        status=DesignReviewSessionStatus.APPROVED,
    )

    with pytest.raises(DesignReviewConflictError):
        await coordinator.launch_round(
            principal=_principal(tenant_id),
            tenant_id=tenant_id,
            session_id=design_session.design_review_session_id,
            workflow_version_bundle_id=workflow_version_bundle_id,
            reviewers=_reviewers(),
            idempotency_key="launch-terminal",
        )
