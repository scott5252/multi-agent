from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.design_review.coordinator import (
    DesignReviewCoordinator,
)
from multi_agent_platform.admin.design_review.models import (
    DesignReviewCoordinatorState,
)
from multi_agent_platform.admin.design_review.service import (
    DesignReviewError,
    DesignReviewService,
)
from multi_agent_platform.admin.design_review.template import (
    COUNCIL_TEMPLATE_KEY,
    DesignReviewTemplateService,
    DesignReviewTemplateState,
)
from multi_agent_platform.api.schemas.admin_design_review_workspace import (
    DesignReviewQuorumPolicyOption,
    DesignReviewWorkflowOption,
    DesignReviewWorkspaceActions,
    DesignReviewWorkspaceEnvelope,
    DesignReviewWorkspaceRoundDetail,
    DesignReviewWorkspaceSessionDetail,
    DesignReviewWorkspaceStatusCard,
    DesignReviewWorkspaceTemplateSetup,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminScopeType,
    ReactAdminShellState,
    ReactAdminShellStateKind,
    ReactAdminSourceKind,
)
from multi_agent_platform.api.schemas.design_review import (
    DesignDevelopmentHandoffResponse,
    DesignManualDecisionResponse,
    DesignQuorumDecisionResponse,
    DesignReviewCoordinatorStateResponse,
    DesignReviewerAssignmentResponse,
    DesignReviewerVerdictResponse,
    DesignReviewRoundResponse,
    DesignReviewSessionResponse,
    DesignReviewState,
    DesignRevisionResponse,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.design_review import (
    DesignDevelopmentHandoff,
    DesignManualDecision,
    DesignQuorumDecision,
    DesignReviewerAssignment,
    DesignReviewerVerdict,
    DesignReviewRound,
    DesignReviewSession,
    DesignRevision,
)
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository


async def build_design_review_workspace(
    *,
    db_session: AsyncSession,
    repository: DesignReviewRepository,
    service: DesignReviewService,
    coordinator: DesignReviewCoordinator,
    template_service: DesignReviewTemplateService,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    selected_session_id: UUID | None = None,
) -> DesignReviewWorkspaceEnvelope:
    provenance = _live_provenance()
    if scope.scope_type is not ReactAdminScopeType.TENANT or scope.tenant_id is None:
        template_setup = _template_setup(
            DesignReviewTemplateState(
                status="denied",
                template_key=COUNCIL_TEMPLATE_KEY,
                publish_gate_status="not_evaluated",
                safe_summary="Tenant scope is required for council template setup.",
            ),
            tenant_id=scope.tenant_id,
            enabled=False,
        )
        return _empty_envelope(
            scope=scope,
            state=ReactAdminShellState(
                state=ReactAdminShellStateKind.DENIED,
                title="Tenant scope required",
                summary="Choose a tenant scope to review design council sessions.",
                provenance=provenance,
            ),
            provenance=provenance,
            template_setup=template_setup,
        )

    tenant_id = scope.tenant_id
    template_setup = _template_setup(
        await template_service.get_council_template_state(
            principal=principal,
            tenant_id=tenant_id,
        ),
        tenant_id=tenant_id,
        enabled=True,
    )
    sessions = await service.list_sessions(
        principal=principal,
        tenant_id=tenant_id,
    )
    selected = _select_session(sessions, selected_session_id)
    selected_detail = (
        await _session_detail(
            repository=repository,
            service=service,
            coordinator=coordinator,
            principal=principal,
            tenant_id=tenant_id,
            record=selected,
        )
        if selected is not None
        else None
    )
    workflow_options = await _workflow_options(db_session, tenant_id=tenant_id)
    empty_state = _empty_state_metadata() if not sessions else None
    session_summaries: list[DesignReviewSessionResponse] = []
    for item in sessions:
        session_summaries.append(
            _session_response(
                item,
                revision=await repository.get_active_revision(session=item),
            )
        )
    return DesignReviewWorkspaceEnvelope(
        title="Design reviews",
        description=(
            "Live council sessions, round decisions, manual actions, "
            "and handoff references."
        ),
        active_scope=scope,
        state=ReactAdminShellState(
            state=ReactAdminShellStateKind.EMPTY
            if not sessions
            else ReactAdminShellStateKind.PARTIAL_DATA
            if selected_session_id is not None and selected is None
            else ReactAdminShellStateKind.PARTIAL_DATA,
            title="No design reviews" if not sessions else "Design reviews loaded",
            summary="No live design review sessions exist for this tenant."
            if not sessions
            else "Live design review sessions and council decisions loaded.",
            provenance=provenance,
            empty_state=empty_state,
        ),
        provenance=provenance,
        empty_state=empty_state,
        summary_cards=_summary_cards(sessions, template_setup=template_setup),
        sessions=tuple(session_summaries),
        selected_session=selected_detail,
        workflow_options=workflow_options,
        quorum_policies=_quorum_policies(),
        template_setup=template_setup,
        actions=_actions(
            tenant_id=tenant_id,
            selected=selected,
            workflow_options=workflow_options,
            manual_required=bool(
                selected_detail
                and selected_detail.coordinator
                and selected_detail.coordinator.manual_resolution_required
            ),
        ),
    )


async def _session_detail(
    *,
    repository: DesignReviewRepository,
    service: DesignReviewService,
    coordinator: DesignReviewCoordinator,
    principal: PrincipalContext,
    tenant_id: UUID,
    record: DesignReviewSession,
) -> DesignReviewWorkspaceSessionDetail:
    session_id = record.design_review_session_id
    revisions = await service.list_revisions(
        principal=principal,
        session_id=session_id,
        tenant_id=tenant_id,
    )
    rounds = await service.list_rounds(
        principal=principal,
        session_id=session_id,
        tenant_id=tenant_id,
    )
    manual_decisions = await service.list_manual_decisions(
        principal=principal,
        session_id=session_id,
        tenant_id=tenant_id,
    )
    handoff = await service.get_handoff(
        principal=principal,
        session_id=session_id,
        tenant_id=tenant_id,
    )
    coordinator_state: DesignReviewCoordinatorStateResponse | None
    try:
        coordinator_state = _coordinator_state_response(
            await coordinator.get_state(
                principal=principal,
                tenant_id=tenant_id,
                session_id=session_id,
            )
        )
    except DesignReviewError:
        coordinator_state = None
    active_revision = _current_revision(record, revisions)
    round_details: list[DesignReviewWorkspaceRoundDetail] = []
    for item in rounds:
        round_details.append(
            await _round_detail(
                repository=repository,
                tenant_id=tenant_id,
                round=item,
            )
        )
    return DesignReviewWorkspaceSessionDetail(
        session=_session_response(record, revision=active_revision),
        revisions=tuple(_revision_response(item) for item in revisions),
        rounds=tuple(round_details),
        manual_decisions=tuple(
            _manual_decision_response(item) for item in manual_decisions
        ),
        handoff=_handoff_response(handoff),
        coordinator=coordinator_state,
    )


async def _round_detail(
    *,
    repository: DesignReviewRepository,
    tenant_id: UUID,
    round: DesignReviewRound,
) -> DesignReviewWorkspaceRoundDetail:
    assignments = await repository.list_assignments(
        round_id=round.design_review_round_id,
        tenant_id=tenant_id,
    )
    verdicts = await repository.list_verdicts(
        round_id=round.design_review_round_id,
        tenant_id=tenant_id,
    )
    quorum = await repository.get_quorum_decision_for_round(
        round_id=round.design_review_round_id,
        tenant_id=tenant_id,
    )
    return DesignReviewWorkspaceRoundDetail(
        round=_round_response(round),
        assignments=tuple(_assignment_response(item) for item in assignments),
        verdicts=tuple(_verdict_response(item) for item in verdicts),
        quorum_decision=_quorum_decision_response(quorum),
    )


async def _workflow_options(
    db_session: AsyncSession,
    *,
    tenant_id: UUID,
) -> tuple[DesignReviewWorkflowOption, ...]:
    stmt = (
        select(WorkflowVersionBundle)
        .where(
            WorkflowVersionBundle.status == WorkflowVersionStatus.PUBLISHED,
            (
                (WorkflowVersionBundle.tenant_id == tenant_id)
                | (WorkflowVersionBundle.tenant_id.is_(None))
            ),
        )
        .order_by(
            WorkflowVersionBundle.updated_at.desc(),
            WorkflowVersionBundle.created_at.desc(),
        )
        .limit(25)
    )
    records = list((await db_session.execute(stmt)).scalars().all())
    return tuple(_workflow_option(item) for item in records)


def _workflow_option(record: WorkflowVersionBundle) -> DesignReviewWorkflowOption:
    document = record.summary_json.get("document", {})
    workflow_key = (
        document.get("workflow_key") if isinstance(document, dict) else None
    ) or "published-workflow"
    return DesignReviewWorkflowOption(
        workflow_version_bundle_id=record.workflow_version_bundle_id,
        label=f"{workflow_key} {record.display_version}",
        workflow_key=str(workflow_key),
        display_version=record.display_version,
        tenant_id=record.tenant_id,
        status=record.status.value,
    )


def _select_session(
    sessions: list[DesignReviewSession],
    selected_session_id: UUID | None,
) -> DesignReviewSession | None:
    if selected_session_id is None:
        return sessions[0] if sessions else None
    for session in sessions:
        if session.design_review_session_id == selected_session_id:
            return session
    return None


def _summary_cards(
    sessions: list[DesignReviewSession],
    *,
    template_setup: DesignReviewWorkspaceTemplateSetup | None = None,
) -> tuple[DesignReviewWorkspaceStatusCard, ...]:
    reviewing = sum(1 for item in sessions if item.status.value == "reviewing")
    manual = sum(1 for item in sessions if item.status.value == "manual_resolution")
    approved = sum(1 for item in sessions if item.status.value == "approved")
    cards = [
        DesignReviewWorkspaceStatusCard(
            card_id="total",
            label="Sessions",
            value=str(len(sessions)),
            summary="Live sessions in this tenant scope.",
            tone="neutral",
        ),
        DesignReviewWorkspaceStatusCard(
            card_id="reviewing",
            label="In review",
            value=str(reviewing),
            summary="Sessions with active council rounds.",
            tone="warning" if reviewing else "neutral",
        ),
        DesignReviewWorkspaceStatusCard(
            card_id="manual",
            label="Needs decision",
            value=str(manual),
            summary="Sessions paused for a human decision.",
            tone="danger" if manual else "neutral",
        ),
        DesignReviewWorkspaceStatusCard(
            card_id="approved",
            label="Approved",
            value=str(approved),
            summary="Sessions with a development handoff.",
            tone="success" if approved else "neutral",
        ),
    ]
    if template_setup is not None:
        cards.append(
            DesignReviewWorkspaceStatusCard(
                card_id="template",
                label="Template",
                value=template_setup.status.replace("_", " "),
                summary=template_setup.safe_summary,
                tone="success"
                if template_setup.status in {"ready", "published"}
                else "warning"
                if template_setup.status in {"stale", "evidence_pending"}
                else "neutral",
            )
        )
    return tuple(cards)


def _template_setup(
    state: DesignReviewTemplateState,
    *,
    tenant_id: UUID | None,
    enabled: bool,
) -> DesignReviewWorkspaceTemplateSetup:
    return DesignReviewWorkspaceTemplateSetup(
        status=state.status,
        template_key=state.template_key,
        publish_gate_status=state.publish_gate_status,
        required_evidence_status=state.required_evidence_status,
        safe_summary=state.safe_summary,
        workflow_draft_id=state.workflow_draft_id,
        workflow_lineage_id=state.workflow_lineage_id,
        workflow_draft_revision_id=state.workflow_draft_revision_id,
        workflow_key=state.workflow_key,
        display_name=state.display_name,
        agent_test_suite_id=state.agent_test_suite_id,
        latest_run_id=state.latest_run_id,
        deterministic_run_id=state.deterministic_run_id,
        model_safe_run_id=state.model_safe_run_id,
        evidence_modes=state.evidence_modes,
        ready_to_publish=state.ready_to_publish,
        install_action=AdminAction(
            action_id="install-template",
            label="Install council template",
            method=AdminActionMethod.POST,
            href="/admin/design-reviews/templates/council/install",
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            enabled=enabled,
            disabled_reason=None if enabled else "Choose a tenant scope.",
        ),
    )


def _quorum_policies() -> tuple[DesignReviewQuorumPolicyOption, ...]:
    return (
        DesignReviewQuorumPolicyOption(
            policy_key="four_of_five_no_blockers",
            label="Four of five, no blockers",
            summary="At least four approved verdicts and zero blockers.",
            reviewer_count=5,
            approval_count=4,
        ),
        DesignReviewQuorumPolicyOption(
            policy_key="three_of_four_no_blockers",
            label="Three of four, no blockers",
            summary="At least three approved verdicts and zero blockers.",
            reviewer_count=4,
            approval_count=3,
        ),
    )


def _actions(
    *,
    tenant_id: UUID,
    selected: DesignReviewSession | None,
    workflow_options: tuple[DesignReviewWorkflowOption, ...],
    manual_required: bool,
) -> DesignReviewWorkspaceActions:
    query = f"?tenant_id={tenant_id}"
    return DesignReviewWorkspaceActions(
        create_session=AdminAction(
            action_id="create-session",
            label="Create session",
            method=AdminActionMethod.POST,
            href="/admin/design-reviews/sessions",
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
        ),
        refresh=AdminAction(
            action_id="refresh",
            label="Refresh",
            method=AdminActionMethod.GET,
            href=f"/admin/app/design-reviews/bootstrap.json{query}",
        ),
        launch_round=AdminAction(
            action_id="launch-round",
            label="Launch round",
            method=AdminActionMethod.POST,
            href=(
                f"/admin/design-reviews/sessions/"
                f"{selected.design_review_session_id}/coordinator/launch-round"
            )
            if selected
            else "/admin/design-reviews/sessions",
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            enabled=bool(selected and workflow_options),
            disabled_reason=None
            if selected and workflow_options
            else "Select a session with an authorized workflow.",
        )
        if selected
        else None,
        manual_decision=AdminAction(
            action_id="manual-decision",
            label="Record decision",
            method=AdminActionMethod.POST,
            href=(
                f"/admin/design-reviews/sessions/"
                f"{selected.design_review_session_id}/coordinator/manual-decisions"
            )
            if selected
            else "/admin/design-reviews/sessions",
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            enabled=manual_required,
            disabled_reason=None
            if manual_required
            else "Manual action is available only when the session needs a decision.",
        )
        if selected
        else None,
    )


def _empty_envelope(
    *,
    scope: ReactAdminScope,
    state: ReactAdminShellState,
    provenance: ReactAdminPageProvenance,
    template_setup: DesignReviewWorkspaceTemplateSetup | None = None,
) -> DesignReviewWorkspaceEnvelope:
    resolved_template_setup = template_setup or _template_setup(
        DesignReviewTemplateState(
            status="not_installed",
            template_key=COUNCIL_TEMPLATE_KEY,
            publish_gate_status="not_evaluated",
            safe_summary="Council template is not installed for this tenant.",
        ),
        tenant_id=scope.tenant_id,
        enabled=scope.tenant_id is not None,
    )
    return DesignReviewWorkspaceEnvelope(
        title="Design reviews",
        description=(
            "Live council sessions, round decisions, manual actions, "
            "and handoff references."
        ),
        active_scope=scope,
        state=state,
        provenance=provenance,
        empty_state=_empty_state_metadata(),
        summary_cards=_summary_cards([], template_setup=resolved_template_setup),
        template_setup=resolved_template_setup,
        actions=_actions(
            tenant_id=scope.tenant_id or UUID("00000000-0000-0000-0000-000000000000"),
            selected=None,
            workflow_options=(),
            manual_required=False,
        ),
    )


def _empty_state_metadata() -> ReactAdminEmptyStateMetadata:
    return ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title="No design reviews",
        summary="No live design review sessions exist for this tenant.",
        setup_hint="Create a session from a safe request summary.",
        provenance=ReactAdminPageProvenance(
            source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
            source_label="Design review records",
            source_detail="No live rows were found for the active tenant scope.",
        ),
    )


def _live_provenance() -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=ReactAdminSourceKind.LIVE_REPOSITORY,
        source_label="Design review records",
        source_detail=(
            "Sessions, revisions, rounds, decisions, and handoffs are loaded "
            "from durable records."
        ),
    )


def _state(kind: str, summary: str) -> DesignReviewState:
    return DesignReviewState(kind=kind, summary=summary)  # type: ignore[arg-type]


def _session_response(
    record: DesignReviewSession,
    *,
    replayed: bool = False,
    revision: DesignRevision | None = None,
) -> DesignReviewSessionResponse:
    return DesignReviewSessionResponse(
        design_review_session_id=record.design_review_session_id,
        tenant_id=record.tenant_id,
        status=record.status.value,
        request_summary=record.request_summary,
        active_revision_number=record.active_revision_number,
        quorum_policy_key=record.quorum_policy_key,
        workflow_version_bundle_id=record.workflow_version_bundle_id,
        owner_principal_id=record.owner_principal_id,
        replayed=replayed,
        current_revision=_revision_response(revision) if revision else None,
    )


def _current_revision(
    session: DesignReviewSession,
    revisions: list[DesignRevision],
) -> DesignRevision | None:
    for revision in revisions:
        if revision.revision_number == session.active_revision_number:
            return revision
    return revisions[-1] if revisions else None


def _coordinator_state_response(
    state: DesignReviewCoordinatorState,
) -> DesignReviewCoordinatorStateResponse:
    return DesignReviewCoordinatorStateResponse(
        state=_state("ready", "Coordinator state loaded."),
        session=_session_response(state.session, revision=state.active_revision),
        active_revision=_revision_response(state.active_revision)
        if state.active_revision
        else None,
        latest_round=_round_response(state.latest_round)
        if state.latest_round
        else None,
        latest_quorum_decision=_quorum_decision_response(state.latest_quorum_decision),
        handoff=_handoff_response(state.handoff),
        manual_resolution_required=(state.session.status.value == "manual_resolution"),
        next_action=_next_action_for_status(state.session.status.value),
    )


def _next_action_for_status(status_value: str) -> str:
    if status_value in {"revision_required", "reviewing"}:
        return "launch_round"
    if status_value == "manual_resolution":
        return "manual_decision"
    if status_value == "approved":
        return "handoff"
    return "none"


def _revision_response(record: DesignRevision) -> DesignRevisionResponse:
    return DesignRevisionResponse.model_validate(record)


def _round_response(record: DesignReviewRound) -> DesignReviewRoundResponse:
    return DesignReviewRoundResponse(
        design_review_round_id=record.design_review_round_id,
        design_review_session_id=record.design_review_session_id,
        design_revision_id=record.design_revision_id,
        round_number=record.round_number,
        status=record.status.value,
        workflow_run_id=record.workflow_run_id,
        reviewer_count=record.reviewer_count,
        quorum_count=record.quorum_count,
    )


def _assignment_response(
    record: DesignReviewerAssignment,
) -> DesignReviewerAssignmentResponse:
    return DesignReviewerAssignmentResponse.model_validate(record)


def _verdict_response(
    record: DesignReviewerVerdict,
) -> DesignReviewerVerdictResponse:
    return DesignReviewerVerdictResponse(
        design_reviewer_verdict_id=record.design_reviewer_verdict_id,
        reviewer_key=record.reviewer_key,
        verdict=record.verdict.value,
        score=record.score,
        blocking_issue_count=record.blocking_issue_count,
        safe_feedback_summary=record.safe_feedback_summary,
        artifact_id=record.artifact_id,
        output_digest=record.output_digest,
        usage_summary=record.usage_summary,
    )


def _quorum_decision_response(
    record: DesignQuorumDecision | None,
) -> DesignQuorumDecisionResponse:
    if record is None:
        return DesignQuorumDecisionResponse(
            state=_state("pending", "No quorum decision has been recorded."),
        )
    return DesignQuorumDecisionResponse(
        state=_state("ready", "Quorum decision loaded."),
        design_quorum_decision_id=record.design_quorum_decision_id,
        status=record.status.value,
        approval_count=record.approval_count,
        blocking_issue_count=record.blocking_issue_count,
        next_action=record.next_action.value,
        policy_version=record.policy_version,
        safe_rationale=record.safe_rationale,
    )


def _manual_decision_response(
    record: DesignManualDecision,
) -> DesignManualDecisionResponse:
    return DesignManualDecisionResponse(
        design_manual_decision_id=record.design_manual_decision_id,
        design_review_session_id=record.design_review_session_id,
        design_review_round_id=record.design_review_round_id,
        decision_type=record.decision_type.value,
        actor_principal_id=record.actor_principal_id,
        safe_rationale=record.safe_rationale,
        accepted_risk=record.accepted_risk,
    )


def _handoff_response(
    record: DesignDevelopmentHandoff | None,
) -> DesignDevelopmentHandoffResponse:
    if record is None:
        return DesignDevelopmentHandoffResponse(
            state=_state("pending", "No development handoff has been recorded."),
        )
    return DesignDevelopmentHandoffResponse(
        state=_state("ready", "Development handoff loaded."),
        design_development_handoff_id=record.design_development_handoff_id,
        approved_revision_id=record.approved_revision_id,
        artifact_id=record.artifact_id,
        safe_summary=record.safe_summary,
        output_digest=record.output_digest,
        status=record.status.value,
    )
