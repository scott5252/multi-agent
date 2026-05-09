from __future__ import annotations

from uuid import UUID, uuid4

from multi_agent_platform.admin.design_review.coordinator import (
    DesignReviewCoordinator,
)
from multi_agent_platform.admin.design_review.models import (
    DesignReviewCoordinatorReviewer,
    DesignReviewCoordinatorVerdict,
)
from multi_agent_platform.admin.design_review.service import DesignReviewService
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from multi_agent_platform.db.models.design_review import DesignReviewSessionStatus
from multi_agent_platform.db.models.runtime_orchestration import RuntimeRunStatus
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.runtime.orchestration.graph_execution import (
    GraphExecutionStatus,
)
from multi_agent_platform.tenancy.context import ScopeType
from multi_agent_platform.workers.orchestration import OrchestrationWorker
from tests.unit.runtime.orchestration.test_graph_execution import simple_graph_document


def _principal(tenant_id: UUID) -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        tenant_id=tenant_id,
        role_codes=("tenant_admin", "tenant_user"),
        scope_type=ScopeType.TENANT,
        trace_id="trace-coordinator-runtime",
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


def _reviewers() -> tuple[DesignReviewCoordinatorReviewer, ...]:
    return tuple(
        DesignReviewCoordinatorReviewer(
            reviewer_key=f"reviewer-{index}",
            role_key=f"reviewer-role-{index}",
        )
        for index in range(5)
    )


def _verdicts() -> tuple[DesignReviewCoordinatorVerdict, ...]:
    return tuple(
        DesignReviewCoordinatorVerdict(
            reviewer_key=f"reviewer-{index}",
            verdict="approved" if index < 4 else "changes_requested",
            score=5 if index < 4 else 3,
            blocking_issue_count=0,
            safe_feedback_summary=f"Safe reviewer {index} feedback.",
            output_digest=f"digest-{index}",
        )
        for index in range(5)
    )


async def test_coordinator_launches_worker_visible_runtime_run(
    session, settings, seeded_tenant
) -> None:
    tenant_id = seeded_tenant.tenant_id
    workflow_version_bundle_id = await _workflow_bundle(session, tenant_id)
    service = DesignReviewService(DesignReviewRepository(session))
    created, _ = await service.create_session(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        request_summary="Review checkout redesign through runtime worker.",
        quorum_policy_key="four_of_five_no_blockers",
        workflow_version_bundle_id=workflow_version_bundle_id,
        idempotency_key="coordinator-runtime-session",
    )
    coordinator = DesignReviewCoordinator(
        design_repository=DesignReviewRepository(session),
        runtime_repository=RuntimeOrchestrationRepository(session),
    )
    launched = await coordinator.launch_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        session_id=created.record.design_review_session_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        reviewers=_reviewers(),
        idempotency_key="coordinator-runtime-launch",
    )
    run = await RuntimeOrchestrationRepository(session).get_run_by_id(
        workflow_run_id=launched.workflow_run_id
    )

    worker_result = await OrchestrationWorker(
        session=session,
        settings=settings,
        worker_id="worker-design-review-coordinator",
    ).poll_once()

    completed = await coordinator.complete_round(
        principal=_principal(tenant_id),
        tenant_id=tenant_id,
        round_id=launched.round_record.design_review_round_id,
        verdicts=_verdicts(),
        idempotency_key="coordinator-runtime-complete",
        safe_synthesis_summary="Council approves runtime-backed handoff.",
    )

    assert run is not None
    assert worker_result.claimed
    assert worker_result.workflow_run_id == str(launched.workflow_run_id)
    assert worker_result.graph_status is GraphExecutionStatus.SUCCEEDED
    assert run.status is RuntimeRunStatus.SUCCEEDED
    assert completed.session.status is DesignReviewSessionStatus.APPROVED
    assert completed.handoff is not None
