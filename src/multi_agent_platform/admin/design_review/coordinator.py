from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from uuid import UUID, uuid4

from multi_agent_platform.admin.design_review.models import (
    DesignReviewCoordinatorResult,
    DesignReviewCoordinatorReviewer,
    DesignReviewCoordinatorState,
    DesignReviewCoordinatorVerdict,
)
from multi_agent_platform.admin.design_review.redaction import (
    UnsafeDesignReviewContentError,
    digest_safe_text,
    safe_metadata,
    validate_safe_text,
)
from multi_agent_platform.admin.design_review.service import (
    DesignReviewAccessError,
    DesignReviewConflictError,
    DesignReviewNotFoundError,
    DesignReviewService,
    DesignReviewValidationError,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignManualDecisionType,
    DesignQuorumDecision,
    DesignQuorumDecisionStatus,
    DesignQuorumNextAction,
    DesignReviewerVerdict,
    DesignReviewerVerdictValue,
    DesignReviewRound,
    DesignReviewRoundStatus,
    DesignReviewSession,
    DesignReviewSessionStatus,
    DesignRevision,
)
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    RuntimeTimelineEventRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.observability.tracing import generate_trace_id
from multi_agent_platform.runtime.orchestration.contracts import sha256_digest

DEFAULT_MAX_ROUNDS = 3
TERMINAL_SESSION_STATUSES = {
    DesignReviewSessionStatus.APPROVED,
    DesignReviewSessionStatus.CANCELLED,
    DesignReviewSessionStatus.FAILED,
}
OPEN_ROUND_STATUSES = {
    DesignReviewRoundStatus.PENDING,
    DesignReviewRoundStatus.RUNNING,
}


@dataclass(slots=True, frozen=True)
class QuorumPolicy:
    key: str
    expected_reviewers: int
    required_approvals: int


QUORUM_POLICIES = {
    "four_of_five_no_blockers": QuorumPolicy(
        key="four_of_five_no_blockers",
        expected_reviewers=5,
        required_approvals=4,
    ),
    "three_of_four_no_blockers": QuorumPolicy(
        key="three_of_four_no_blockers",
        expected_reviewers=4,
        required_approvals=3,
    ),
}


DEFAULT_REVIEWERS = (
    DesignReviewCoordinatorReviewer(
        reviewer_key="product-fit",
        role_key="product-fit-reviewer",
    ),
    DesignReviewCoordinatorReviewer(
        reviewer_key="ux-interaction",
        role_key="ux-interaction-reviewer",
    ),
    DesignReviewCoordinatorReviewer(
        reviewer_key="visual-system",
        role_key="visual-design-system-reviewer",
    ),
    DesignReviewCoordinatorReviewer(
        reviewer_key="accessibility",
        role_key="accessibility-reviewer",
    ),
    DesignReviewCoordinatorReviewer(
        reviewer_key="engineering-api",
        role_key="engineering-api-reviewer",
    ),
)


class DesignReviewCoordinator:
    def __init__(
        self,
        *,
        design_repository: DesignReviewRepository,
        runtime_repository: RuntimeOrchestrationRepository,
    ) -> None:
        self.design_repository = design_repository
        self.runtime_repository = runtime_repository
        self.design_service = DesignReviewService(design_repository)

    async def get_state(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        session_id: UUID,
    ) -> DesignReviewCoordinatorState:
        session = await self.design_service.require_session(
            principal=principal,
            tenant_id=tenant_id,
            session_id=session_id,
        )
        return await self._state_for_session(session)

    async def launch_round(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        session_id: UUID,
        idempotency_key: str,
        workflow_version_bundle_id: UUID | None = None,
        reviewers: Sequence[DesignReviewCoordinatorReviewer] = (),
        max_rounds: int = DEFAULT_MAX_ROUNDS,
        execution_mode: str = "deterministic",
    ) -> DesignReviewCoordinatorResult:
        session = await self.design_service.require_session(
            principal=principal,
            tenant_id=tenant_id,
            session_id=session_id,
        )
        safe_idempotency_key = _safe_key(idempotency_key, "idempotency_key")
        existing = await self.design_repository.get_round_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=safe_idempotency_key,
        )
        if existing is not None:
            if existing.design_review_session_id != session_id:
                raise DesignReviewConflictError(
                    "coordinator idempotency key belongs to another session"
                )
            active_revision = await self.design_repository.get_active_revision(
                session=session
            )
            return DesignReviewCoordinatorResult(
                session=session,
                round_record=existing,
                active_revision=active_revision,
                workflow_run_id=existing.workflow_run_id,
                replayed=True,
                next_action="inspect_round",
            )
        self._assert_launchable(session)
        if max_rounds < 1:
            raise DesignReviewValidationError("max rounds must be at least one")
        rounds = await self.design_repository.list_rounds(
            session_id=session_id,
            tenant_id=tenant_id,
        )
        if len(rounds) >= max_rounds:
            raise DesignReviewConflictError("coordinator max rounds reached")
        active_revision = await self.design_repository.get_active_revision(
            session=session
        )
        if active_revision is None:
            raise DesignReviewConflictError(
                "design review session has no active revision"
            )
        latest_round = rounds[-1] if rounds else None
        if (
            latest_round is not None
            and latest_round.design_revision_id == active_revision.design_revision_id
            and latest_round.status in OPEN_ROUND_STATUSES
        ):
            raise DesignReviewConflictError(
                "active revision already has an open review round"
            )
        workflow_bundle_id = (
            workflow_version_bundle_id or session.workflow_version_bundle_id
        )
        if workflow_bundle_id is None:
            raise DesignReviewValidationError(
                "coordinator launch requires a workflow version bundle"
            )
        workflow_bundle = await self._require_workflow_bundle(
            workflow_version_bundle_id=workflow_bundle_id,
            tenant_id=tenant_id,
        )
        enabled_reviewers = _enabled_reviewers(reviewers or DEFAULT_REVIEWERS)
        policy = _policy_for(session.quorum_policy_key)
        reviewer_count = len(enabled_reviewers)
        if reviewer_count < policy.required_approvals:
            raise DesignReviewValidationError(
                "enabled reviewer count cannot satisfy quorum policy"
            )

        workflow_run_id = uuid4()
        run_bundle_id = uuid4()
        workflow_version = _workflow_version_payload(
            workflow_bundle=workflow_bundle,
            session=session,
            revision=active_revision,
            execution_mode=execution_mode,
        )
        bundle_digest = sha256_digest(workflow_version)
        bundle = RuntimeExecutionBundleRecord(
            run_bundle_id=run_bundle_id,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            published_workflow_version_id=workflow_bundle_id,
            bundle_digest=bundle_digest,
            workflow_version=workflow_version,
            retry_policy={"max_attempts": 3},
            checkpoint_policy={"semantic_boundaries": True},
        )
        run = WorkflowRunRecord(
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            scope_type="tenant",
            initiating_principal_id=principal.principal_id,
            run_bundle_id=run_bundle_id,
            status=RuntimeRunStatus.RUNNABLE,
            idempotency_key=f"design-review:{safe_idempotency_key}",
            trace_id=principal.trace_id or generate_trace_id(),
        )
        await self.runtime_repository.create_run(run=run, bundle=bundle)
        round_result = await self.design_service.record_round(
            tenant_id=tenant_id,
            session_id=session_id,
            revision_id=active_revision.design_revision_id,
            round_number=(latest_round.round_number + 1) if latest_round else 1,
            reviewer_count=reviewer_count,
            quorum_count=policy.required_approvals,
            idempotency_key=safe_idempotency_key,
            workflow_run_id=workflow_run_id,
            status=DesignReviewRoundStatus.RUNNING.value,
        )
        for reviewer in enabled_reviewers:
            await self.design_service.record_assignment(
                tenant_id=tenant_id,
                round_id=round_result.record.design_review_round_id,
                reviewer_key=reviewer.reviewer_key,
                role_key=reviewer.role_key,
                prompt_version_id=reviewer.prompt_version_id,
                profile_version_id=reviewer.profile_version_id,
                provider_reference=reviewer.provider_reference,
                enabled=reviewer.enabled,
            )
        await self.design_repository.update_session_state(
            session=session,
            status=DesignReviewSessionStatus.REVIEWING,
            workflow_version_bundle_id=workflow_bundle_id,
        )
        await self.runtime_repository.create_timeline_event(
            RuntimeTimelineEventRecord(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_type="design_review_round_launched",
                severity="info",
                payload={
                    "design_review_session_id": str(session_id),
                    "design_review_round_id": str(
                        round_result.record.design_review_round_id
                    ),
                    "design_revision_id": str(active_revision.design_revision_id),
                    "quorum_policy_key": session.quorum_policy_key,
                },
                trace_id=run.trace_id,
            )
        )
        return DesignReviewCoordinatorResult(
            session=session,
            round_record=round_result.record,
            active_revision=active_revision,
            workflow_run_id=workflow_run_id,
            replayed=False,
            next_action="wait_for_runtime",
        )

    async def complete_round(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        round_id: UUID,
        verdicts: Sequence[DesignReviewCoordinatorVerdict],
        idempotency_key: str,
        safe_synthesis_summary: str,
        next_revision_summary: str | None = None,
        max_rounds: int = DEFAULT_MAX_ROUNDS,
    ) -> DesignReviewCoordinatorResult:
        round_record = await self.design_service.require_round(
            principal=principal,
            tenant_id=tenant_id,
            round_id=round_id,
        )
        session = await self.design_service.require_session(
            principal=principal,
            tenant_id=tenant_id,
            session_id=round_record.design_review_session_id,
        )
        existing_decision = await self.design_repository.get_quorum_decision_for_round(
            round_id=round_id,
            tenant_id=tenant_id,
        )
        if existing_decision is not None:
            return await self._completed_replay(
                session=session,
                round_record=round_record,
                decision=existing_decision,
            )
        active_revision = await self.design_repository.get_active_revision(
            session=session
        )
        if active_revision is None:
            raise DesignReviewConflictError(
                "design review session has no active revision"
            )
        if round_record.design_revision_id != active_revision.design_revision_id:
            raise DesignReviewConflictError("round does not review the active revision")
        safe_summary = _safe_text(safe_synthesis_summary, "safe_synthesis_summary")
        verdict_records = await self._record_verdicts(
            tenant_id=tenant_id,
            round_record=round_record,
            verdicts=verdicts,
            idempotency_key=_safe_key(idempotency_key, "idempotency_key"),
        )
        decision_status, next_action, rationale = await self._evaluate_completion(
            round_record=round_record,
            session=session,
            verdict_records=verdict_records,
            safe_synthesis_summary=safe_summary,
            max_rounds=max_rounds,
        )
        decision = await self.design_service.record_quorum_decision(
            tenant_id=tenant_id,
            round_id=round_id,
            status=decision_status.value,
            approval_count=_approval_count(verdict_records),
            blocking_issue_count=_blocking_issue_count(verdict_records),
            next_action=next_action.value,
            policy_version=session.quorum_policy_key,
            safe_rationale=rationale,
        )
        created_revision: DesignRevision | None = None
        handoff: DesignDevelopmentHandoff | None = None
        if decision_status is DesignQuorumDecisionStatus.PASSED:
            handoff_result = await self.design_service.record_handoff(
                tenant_id=tenant_id,
                session_id=session.design_review_session_id,
                approved_revision_id=active_revision.design_revision_id,
                safe_summary=safe_summary,
                output_digest=digest_safe_text(safe_summary),
                idempotency_key=f"coordinator-handoff-{round_id}",
            )
            handoff = handoff_result.record
            await self.design_repository.update_round_state(
                round_record=round_record,
                status=DesignReviewRoundStatus.COMPLETED,
            )
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.APPROVED,
            )
        elif decision_status is DesignQuorumDecisionStatus.REVISION_REQUIRED:
            revision_summary = _safe_text(
                next_revision_summary or safe_summary,
                "next_revision_summary",
            )
            created_revision = await self.design_repository.create_next_revision(
                session=session,
                author_role_key="coordinator",
                safe_summary=revision_summary,
                payload_digest=digest_safe_text(revision_summary),
                previous_revision_id=active_revision.design_revision_id,
            )
            await self.design_repository.update_round_state(
                round_record=round_record,
                status=DesignReviewRoundStatus.REVISION_REQUIRED,
            )
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.REVISION_REQUIRED,
            )
        else:
            await self.design_repository.update_round_state(
                round_record=round_record,
                status=DesignReviewRoundStatus.MANUAL_RESOLUTION,
            )
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.MANUAL_RESOLUTION,
            )
        return DesignReviewCoordinatorResult(
            session=session,
            round_record=round_record,
            active_revision=created_revision or active_revision,
            created_revision=created_revision,
            quorum_decision=decision,
            handoff=handoff,
            workflow_run_id=round_record.workflow_run_id,
            next_action=next_action.value,
        )

    async def apply_manual_decision(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID,
        session_id: UUID,
        decision_type: str,
        safe_rationale: str,
        idempotency_key: str,
        accepted_risk: bool = False,
        round_id: UUID | None = None,
        next_revision_summary: str | None = None,
    ) -> DesignReviewCoordinatorResult:
        session = await self.design_service.require_session(
            principal=principal,
            tenant_id=tenant_id,
            session_id=session_id,
        )
        existing = await self.design_repository.get_manual_decision_by_idempotency_key(
            tenant_id=tenant_id,
            idempotency_key=_safe_key(idempotency_key, "idempotency_key"),
        )
        if existing is not None:
            if existing.design_review_session_id != session_id:
                raise DesignReviewConflictError(
                    "manual decision idempotency key belongs to another session"
                )
            state = await self._state_for_session(session)
            return DesignReviewCoordinatorResult(
                session=state.session,
                active_revision=state.active_revision,
                round_record=state.latest_round,
                quorum_decision=state.latest_quorum_decision,
                handoff=state.handoff,
                manual_decision=existing,
                replayed=True,
                next_action=_next_action_for_session(state.session),
            )
        if session.status is not DesignReviewSessionStatus.MANUAL_RESOLUTION:
            raise DesignReviewConflictError(
                "manual coordinator decisions require manual-resolution state"
            )
        result = await self.design_service.record_manual_decision(
            principal=principal,
            tenant_id=tenant_id,
            session_id=session_id,
            round_id=round_id,
            decision_type=decision_type,
            safe_rationale=safe_rationale,
            accepted_risk=accepted_risk,
            idempotency_key=idempotency_key,
        )
        active_revision = await self.design_repository.get_active_revision(
            session=session
        )
        if active_revision is None:
            raise DesignReviewConflictError(
                "design review session has no active revision"
            )
        created_revision: DesignRevision | None = None
        handoff: DesignDevelopmentHandoff | None = None
        parsed = DesignManualDecisionType(decision_type)
        if parsed is DesignManualDecisionType.REVISE:
            revision_summary = _safe_text(
                next_revision_summary or safe_rationale,
                "next_revision_summary",
            )
            created_revision = await self.design_repository.create_next_revision(
                session=session,
                author_role_key="manual-resolution",
                safe_summary=revision_summary,
                payload_digest=digest_safe_text(revision_summary),
                previous_revision_id=active_revision.design_revision_id,
            )
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.REVISION_REQUIRED,
            )
            next_action = "launch_round"
        elif parsed is DesignManualDecisionType.APPROVE_EXCEPTION:
            if not accepted_risk:
                raise DesignReviewValidationError(
                    "approve-exception decisions must accept risk"
                )
            handoff_result = await self.design_service.record_handoff(
                tenant_id=tenant_id,
                session_id=session_id,
                approved_revision_id=active_revision.design_revision_id,
                safe_summary=safe_rationale,
                output_digest=digest_safe_text(safe_rationale),
                idempotency_key=f"manual-handoff-{idempotency_key}",
            )
            handoff = handoff_result.record
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.APPROVED,
            )
            next_action = "handoff"
        elif parsed is DesignManualDecisionType.RETRY:
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.REVIEWING,
            )
            next_action = "launch_round"
        else:
            await self.design_repository.update_session_state(
                session=session,
                status=DesignReviewSessionStatus.CANCELLED,
            )
            next_action = "none"
        return DesignReviewCoordinatorResult(
            session=session,
            active_revision=created_revision or active_revision,
            created_revision=created_revision,
            handoff=handoff,
            manual_decision=result.record,
            replayed=False,
            next_action=next_action,
        )

    async def _record_verdicts(
        self,
        *,
        tenant_id: UUID,
        round_record: DesignReviewRound,
        verdicts: Sequence[DesignReviewCoordinatorVerdict],
        idempotency_key: str,
    ) -> list[DesignReviewerVerdict]:
        if not verdicts:
            return []
        records: list[DesignReviewerVerdict] = []
        for verdict in verdicts:
            result = await self.design_service.record_verdict(
                tenant_id=tenant_id,
                round_id=round_record.design_review_round_id,
                reviewer_key=verdict.reviewer_key,
                verdict=verdict.verdict,
                score=verdict.score,
                blocking_issue_count=verdict.blocking_issue_count,
                safe_feedback_summary=verdict.safe_feedback_summary,
                artifact_id=verdict.artifact_id,
                output_digest=verdict.output_digest,
                usage_summary=safe_metadata(verdict.usage_summary),
                idempotency_key=f"{idempotency_key}:{verdict.reviewer_key}",
            )
            records.append(result.record)
        return records

    async def _evaluate_completion(
        self,
        *,
        round_record: DesignReviewRound,
        session: DesignReviewSession,
        verdict_records: Sequence[DesignReviewerVerdict],
        safe_synthesis_summary: str,
        max_rounds: int,
    ) -> tuple[DesignQuorumDecisionStatus, DesignQuorumNextAction, str]:
        policy = _policy_for(session.quorum_policy_key)
        assignments = await self.design_repository.list_assignments(
            round_id=round_record.design_review_round_id,
            tenant_id=session.tenant_id,
        )
        enabled_reviewer_keys = {
            assignment.reviewer_key for assignment in assignments if assignment.enabled
        }
        verdict_keys = {verdict.reviewer_key for verdict in verdict_records}
        missing = enabled_reviewer_keys - verdict_keys
        if missing or len(verdict_records) < policy.required_approvals:
            return (
                DesignQuorumDecisionStatus.MANUAL_RESOLUTION,
                DesignQuorumNextAction.MANUAL_DECISION,
                "Coordinator paused because runtime reviewer evidence was incomplete.",
            )
        if _blocking_issue_count(verdict_records) > 0:
            return (
                DesignQuorumDecisionStatus.MANUAL_RESOLUTION,
                DesignQuorumNextAction.MANUAL_DECISION,
                "Coordinator paused because blocking issues require manual resolution.",
            )
        if _approval_count(verdict_records) >= policy.required_approvals:
            return (
                DesignQuorumDecisionStatus.PASSED,
                DesignQuorumNextAction.HANDOFF,
                safe_synthesis_summary,
            )
        if round_record.round_number >= max_rounds:
            return (
                DesignQuorumDecisionStatus.MANUAL_RESOLUTION,
                DesignQuorumNextAction.MANUAL_DECISION,
                "Coordinator paused because max rounds were reached.",
            )
        return (
            DesignQuorumDecisionStatus.REVISION_REQUIRED,
            DesignQuorumNextAction.REVISE,
            safe_synthesis_summary,
        )

    async def _completed_replay(
        self,
        *,
        session: DesignReviewSession,
        round_record: DesignReviewRound,
        decision: DesignQuorumDecision,
    ) -> DesignReviewCoordinatorResult:
        active_revision = await self.design_repository.get_active_revision(
            session=session
        )
        handoff = await self.design_repository.get_handoff_for_session(
            session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
        )
        return DesignReviewCoordinatorResult(
            session=session,
            round_record=round_record,
            active_revision=active_revision,
            quorum_decision=decision,
            handoff=handoff,
            workflow_run_id=round_record.workflow_run_id,
            replayed=True,
            next_action=decision.next_action.value,
        )

    async def _state_for_session(
        self, session: DesignReviewSession
    ) -> DesignReviewCoordinatorState:
        active_revision = await self.design_repository.get_active_revision(
            session=session
        )
        latest_round = await self.design_repository.get_latest_round(
            session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
        )
        latest_decision = None
        if latest_round is not None:
            latest_decision = (
                await self.design_repository.get_quorum_decision_for_round(
                    round_id=latest_round.design_review_round_id,
                    tenant_id=session.tenant_id,
                )
            )
        handoff = await self.design_repository.get_handoff_for_session(
            session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
        )
        manual_decisions = await self.design_repository.list_manual_decisions(
            session_id=session.design_review_session_id,
            tenant_id=session.tenant_id,
        )
        return DesignReviewCoordinatorState(
            session=session,
            active_revision=active_revision,
            latest_round=latest_round,
            latest_quorum_decision=latest_decision,
            handoff=handoff,
            manual_decisions=tuple(manual_decisions),
        )

    async def _require_workflow_bundle(
        self, *, workflow_version_bundle_id: UUID, tenant_id: UUID
    ) -> WorkflowVersionBundle:
        bundle = await self.runtime_repository.get_workflow_version_bundle(
            workflow_version_bundle_id=workflow_version_bundle_id,
        )
        if bundle is None:
            raise DesignReviewNotFoundError("workflow version bundle not found")
        if bundle.scope_type == "tenant" and bundle.tenant_id != tenant_id:
            raise DesignReviewAccessError("workflow version bundle access denied")
        return bundle

    @staticmethod
    def _assert_launchable(session: DesignReviewSession) -> None:
        if session.status in TERMINAL_SESSION_STATUSES:
            raise DesignReviewConflictError(
                "terminal design review sessions cannot launch rounds"
            )
        if session.status is DesignReviewSessionStatus.MANUAL_RESOLUTION:
            raise DesignReviewConflictError(
                "manual-resolution sessions require a manual decision"
            )


def _policy_for(policy_key: str) -> QuorumPolicy:
    policy = QUORUM_POLICIES.get(policy_key)
    if policy is None:
        raise DesignReviewValidationError("unsupported coordinator quorum policy")
    return policy


def _enabled_reviewers(
    reviewers: Iterable[DesignReviewCoordinatorReviewer],
) -> tuple[DesignReviewCoordinatorReviewer, ...]:
    enabled = tuple(reviewer for reviewer in reviewers if reviewer.enabled)
    if not enabled:
        raise DesignReviewValidationError("at least one reviewer must be enabled")
    return enabled


def _workflow_version_payload(
    *,
    workflow_bundle: WorkflowVersionBundle,
    session: DesignReviewSession,
    revision: DesignRevision,
    execution_mode: str,
) -> dict[str, object]:
    summary_json = workflow_bundle.summary_json
    workflow_version: dict[str, object] = (
        dict(summary_json) if isinstance(summary_json, Mapping) else {}
    )
    workflow_version["design_review"] = {
        "design_review_session_id": str(session.design_review_session_id),
        "design_revision_id": str(revision.design_revision_id),
        "revision_number": revision.revision_number,
        "safe_summary": revision.safe_summary,
        "payload_digest": revision.payload_digest,
        "execution_mode": _safe_key(execution_mode, "execution_mode"),
    }
    return workflow_version


def _approval_count(verdicts: Sequence[DesignReviewerVerdict]) -> int:
    return sum(
        1
        for verdict in verdicts
        if verdict.verdict is DesignReviewerVerdictValue.APPROVED
        and verdict.blocking_issue_count == 0
    )


def _blocking_issue_count(verdicts: Sequence[DesignReviewerVerdict]) -> int:
    return sum(verdict.blocking_issue_count for verdict in verdicts)


def _safe_text(value: str, field_name: str) -> str:
    try:
        return validate_safe_text(value, field_name=field_name)
    except UnsafeDesignReviewContentError as exc:
        raise DesignReviewValidationError(str(exc)) from exc


def _safe_key(value: str, field_name: str) -> str:
    safe_value = _safe_text(value, field_name)
    if len(safe_value) > 160:
        raise DesignReviewValidationError(f"{field_name} exceeds the key length limit")
    return safe_value


def _next_action_for_session(session: DesignReviewSession) -> str:
    if session.status is DesignReviewSessionStatus.REVISION_REQUIRED:
        return "launch_round"
    if session.status is DesignReviewSessionStatus.REVIEWING:
        return "launch_round"
    if session.status is DesignReviewSessionStatus.APPROVED:
        return "handoff"
    return "none"
