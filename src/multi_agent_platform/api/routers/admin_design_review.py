from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.design_review.coordinator import (
    DesignReviewCoordinator,
)
from multi_agent_platform.admin.design_review.models import (
    DesignReviewCoordinatorResult,
    DesignReviewCoordinatorReviewer,
    DesignReviewCoordinatorState,
    DesignReviewCoordinatorVerdict,
)
from multi_agent_platform.admin.design_review.service import (
    DesignReviewAccessError,
    DesignReviewError,
    DesignReviewNotFoundError,
    DesignReviewService,
    DesignReviewValidationError,
)
from multi_agent_platform.admin.design_review.template import (
    DesignReviewTemplateInstallResult,
    build_design_review_template_service,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.schemas.design_review import (
    DesignDevelopmentHandoffResponse,
    DesignManualDecisionCreateRequest,
    DesignManualDecisionListResponse,
    DesignManualDecisionResponse,
    DesignQuorumDecisionResponse,
    DesignReviewCoordinatorCompleteRequest,
    DesignReviewCoordinatorCompleteResponse,
    DesignReviewCoordinatorLaunchRequest,
    DesignReviewCoordinatorLaunchResponse,
    DesignReviewCoordinatorManualDecisionRequest,
    DesignReviewCoordinatorManualDecisionResponse,
    DesignReviewCoordinatorReviewerRequest,
    DesignReviewCoordinatorStateResponse,
    DesignReviewCoordinatorVerdictRequest,
    DesignReviewerAssignmentResponse,
    DesignReviewerVerdictResponse,
    DesignReviewRoundDetailResponse,
    DesignReviewRoundListResponse,
    DesignReviewRoundResponse,
    DesignReviewSessionCreateRequest,
    DesignReviewSessionDetailResponse,
    DesignReviewSessionListResponse,
    DesignReviewSessionResponse,
    DesignReviewState,
    DesignReviewTemplateActionResponse,
    DesignReviewTemplateInstallRequest,
    DesignReviewTemplateInstallResponse,
    DesignRevisionListResponse,
    DesignRevisionResponse,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
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
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.design_review import DesignReviewRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)

router = APIRouter(prefix="/admin/design-reviews", tags=["design-reviews"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _service(session: AsyncSession) -> DesignReviewService:
    return DesignReviewService(DesignReviewRepository(session))


def _coordinator(session: AsyncSession) -> DesignReviewCoordinator:
    return DesignReviewCoordinator(
        design_repository=DesignReviewRepository(session),
        runtime_repository=RuntimeOrchestrationRepository(session),
    )


@router.post(
    "/templates/council/install",
    response_model=DesignReviewTemplateInstallResponse,
    status_code=status.HTTP_201_CREATED,
)
async def install_design_review_council_template(
    payload: DesignReviewTemplateInstallRequest,
    response: Response,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> DesignReviewTemplateInstallResponse:
    service = build_design_review_template_service(
        session=session,
        storage_provider=container.storage_provider,
        workflow_registry_artifact_prefix=(
            container.settings.workflow_registry_artifact_prefix
        ),
        logger=container.logger,
    )
    try:
        result = await service.install_council_template(
            principal=principal,
            tenant_id=payload.tenant_id,
            template_key=payload.template_key,
            idempotency_key=payload.idempotency_key,
            run_required_tests=payload.run_required_tests,
            safe_mode=payload.safe_mode,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    else:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.template_installed",
            entity_id=str(result.state.workflow_draft_id),
            payload_redacted={"template_key": result.state.template_key},
        )
    return _template_install_response(
        tenant_id=payload.tenant_id,
        result=result,
    )


@router.post(
    "/sessions",
    response_model=DesignReviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_review_session(
    payload: DesignReviewSessionCreateRequest,
    response: Response,
    principal: PrincipalDep,
    session: SessionDep,
) -> DesignReviewSessionResponse:
    initial_revision = payload.initial_revision
    service = _service(session)
    try:
        result, revision = await service.create_session(
            principal=principal,
            tenant_id=payload.tenant_id,
            request_summary=payload.request_summary,
            quorum_policy_key=payload.quorum_policy_key,
            workflow_version_bundle_id=payload.workflow_version_bundle_id,
            idempotency_key=payload.idempotency_key,
            revision_author_role_key=(
                initial_revision.author_role_key if initial_revision else "requester"
            ),
            revision_safe_summary=(
                initial_revision.safe_summary if initial_revision else None
            ),
            revision_artifact_id=(
                initial_revision.artifact_id if initial_revision else None
            ),
            revision_payload_digest=(
                initial_revision.payload_digest if initial_revision else None
            ),
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    else:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.session_created",
            entity_id=str(result.record.design_review_session_id),
            payload_redacted={"quorum_policy_key": payload.quorum_policy_key},
        )
    return _session_response(result.record, replayed=result.replayed, revision=revision)


@router.get("/sessions", response_model=DesignReviewSessionListResponse)
async def list_design_review_sessions(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> DesignReviewSessionListResponse:
    try:
        items = await _service(session).list_sessions(
            principal=principal,
            tenant_id=tenant_id,
            status=status_filter,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return DesignReviewSessionListResponse(
        items=[_session_response(item) for item in items],
        state=_state("ready", "Design review sessions loaded.")
        if items
        else _state("empty", "No design review sessions exist for this tenant."),
    )


@router.get(
    "/sessions/{session_id}",
    response_model=DesignReviewSessionDetailResponse,
)
async def get_design_review_session(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignReviewSessionDetailResponse:
    service = _service(session)
    try:
        record = await service.require_session(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
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
    except DesignReviewError as exc:
        _raise_http(exc)
    current_revision = _current_revision(record, revisions)
    base = _session_response(record, revision=current_revision)
    return DesignReviewSessionDetailResponse(
        **base.model_dump(),
        revisions=[_revision_response(item) for item in revisions],
        rounds=[_round_response(item) for item in rounds],
        manual_decisions=[_manual_decision_response(item) for item in manual_decisions],
        handoff=_handoff_response(handoff),
    )


@router.get(
    "/sessions/{session_id}/coordinator",
    response_model=DesignReviewCoordinatorStateResponse,
)
async def get_design_review_coordinator_state(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignReviewCoordinatorStateResponse:
    try:
        state = await _coordinator(session).get_state(
            principal=principal,
            tenant_id=tenant_id,
            session_id=session_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return _coordinator_state_response(state)


@router.post(
    "/sessions/{session_id}/coordinator/launch-round",
    response_model=DesignReviewCoordinatorLaunchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def launch_design_review_coordinator_round(
    session_id: UUID,
    payload: DesignReviewCoordinatorLaunchRequest,
    response: Response,
    principal: PrincipalDep,
    session: SessionDep,
) -> DesignReviewCoordinatorLaunchResponse:
    try:
        result = await _coordinator(session).launch_round(
            principal=principal,
            tenant_id=payload.tenant_id,
            session_id=session_id,
            workflow_version_bundle_id=payload.workflow_version_bundle_id,
            reviewers=tuple(_reviewer_request(item) for item in payload.reviewers),
            max_rounds=payload.max_rounds,
            execution_mode=payload.execution_mode,
            idempotency_key=payload.idempotency_key,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    else:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.coordinator_round_launched",
            entity_id=str(result.round_record.design_review_round_id)
            if result.round_record
            else str(session_id),
            payload_redacted={"next_action": result.next_action},
        )
    return _coordinator_launch_response(result)


@router.get(
    "/sessions/{session_id}/revisions",
    response_model=DesignRevisionListResponse,
)
async def list_design_review_revisions(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignRevisionListResponse:
    try:
        revisions = await _service(session).list_revisions(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return DesignRevisionListResponse(
        items=[_revision_response(item) for item in revisions],
    )


@router.get(
    "/sessions/{session_id}/rounds",
    response_model=DesignReviewRoundListResponse,
)
async def list_design_review_rounds(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignReviewRoundListResponse:
    try:
        rounds = await _service(session).list_rounds(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return DesignReviewRoundListResponse(
        items=[_round_response(item) for item in rounds],
    )


@router.get(
    "/rounds/{round_id}",
    response_model=DesignReviewRoundDetailResponse,
)
async def get_design_review_round(
    round_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignReviewRoundDetailResponse:
    service = _service(session)
    try:
        round_record = await service.require_round(
            principal=principal,
            round_id=round_id,
            tenant_id=tenant_id,
        )
        assignments = await service.round_assignments(
            principal=principal,
            round_id=round_id,
            tenant_id=tenant_id,
        )
        verdicts = await service.round_verdicts(
            principal=principal,
            round_id=round_id,
            tenant_id=tenant_id,
        )
        decision = await service.get_quorum_decision(
            principal=principal,
            round_id=round_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    base = _round_response(round_record)
    return DesignReviewRoundDetailResponse(
        **base.model_dump(),
        assignments=[_assignment_response(item) for item in assignments],
        verdicts=[_verdict_response(item) for item in verdicts],
        quorum_decision=_quorum_decision_response(decision),
    )


@router.get(
    "/rounds/{round_id}/quorum-decision",
    response_model=DesignQuorumDecisionResponse,
)
async def get_design_review_quorum_decision(
    round_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignQuorumDecisionResponse:
    try:
        decision = await _service(session).get_quorum_decision(
            principal=principal,
            round_id=round_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return _quorum_decision_response(decision)


@router.post(
    "/rounds/{round_id}/coordinator/complete",
    response_model=DesignReviewCoordinatorCompleteResponse,
)
async def complete_design_review_coordinator_round(
    round_id: UUID,
    payload: DesignReviewCoordinatorCompleteRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> DesignReviewCoordinatorCompleteResponse:
    try:
        result = await _coordinator(session).complete_round(
            principal=principal,
            tenant_id=payload.tenant_id,
            round_id=round_id,
            verdicts=tuple(_verdict_request(item) for item in payload.verdicts),
            idempotency_key=payload.idempotency_key,
            safe_synthesis_summary=payload.safe_synthesis_summary,
            next_revision_summary=payload.next_revision_summary,
            max_rounds=payload.max_rounds,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if not result.replayed:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.coordinator_round_completed",
            entity_id=str(round_id),
            payload_redacted={"next_action": result.next_action},
        )
    return _coordinator_complete_response(result)


@router.get(
    "/sessions/{session_id}/manual-decisions",
    response_model=DesignManualDecisionListResponse,
)
async def list_design_review_manual_decisions(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignManualDecisionListResponse:
    try:
        decisions = await _service(session).list_manual_decisions(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return DesignManualDecisionListResponse(
        items=[_manual_decision_response(item) for item in decisions],
        state=_state("ready", "Manual decisions loaded.")
        if decisions
        else _state("empty", "No manual decisions have been recorded."),
    )


@router.post(
    "/sessions/{session_id}/manual-decisions",
    response_model=DesignManualDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_review_manual_decision(
    session_id: UUID,
    payload: DesignManualDecisionCreateRequest,
    response: Response,
    principal: PrincipalDep,
    session: SessionDep,
) -> DesignManualDecisionResponse:
    try:
        result = await _service(session).record_manual_decision(
            principal=principal,
            session_id=session_id,
            tenant_id=payload.tenant_id,
            round_id=payload.round_id,
            decision_type=payload.decision_type,
            safe_rationale=payload.safe_rationale,
            accepted_risk=payload.accepted_risk,
            idempotency_key=payload.idempotency_key,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    else:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.manual_decision_recorded",
            entity_id=str(result.record.design_manual_decision_id),
            payload_redacted={"decision_type": payload.decision_type},
        )
    return _manual_decision_response(result.record, replayed=result.replayed)


@router.post(
    "/sessions/{session_id}/coordinator/manual-decisions",
    response_model=DesignReviewCoordinatorManualDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_review_coordinator_manual_decision(
    session_id: UUID,
    payload: DesignReviewCoordinatorManualDecisionRequest,
    response: Response,
    principal: PrincipalDep,
    session: SessionDep,
) -> DesignReviewCoordinatorManualDecisionResponse:
    try:
        result = await _coordinator(session).apply_manual_decision(
            principal=principal,
            tenant_id=payload.tenant_id,
            session_id=session_id,
            round_id=payload.round_id,
            decision_type=payload.decision_type,
            safe_rationale=payload.safe_rationale,
            accepted_risk=payload.accepted_risk,
            next_revision_summary=payload.next_revision_summary,
            idempotency_key=payload.idempotency_key,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    else:
        await _record_audit(
            session=session,
            principal=principal,
            tenant_id=payload.tenant_id,
            action="design_review.coordinator_manual_decision_applied",
            entity_id=str(result.manual_decision.design_manual_decision_id)
            if result.manual_decision
            else str(session_id),
            payload_redacted={"next_action": result.next_action},
        )
    return _coordinator_manual_response(result)


@router.get(
    "/sessions/{session_id}/handoff",
    response_model=DesignDevelopmentHandoffResponse,
)
async def get_design_review_handoff(
    session_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID,
) -> DesignDevelopmentHandoffResponse:
    try:
        handoff = await _service(session).get_handoff(
            principal=principal,
            session_id=session_id,
            tenant_id=tenant_id,
        )
    except DesignReviewError as exc:
        _raise_http(exc)
    return _handoff_response(handoff)


async def _record_audit(
    *,
    session: AsyncSession,
    principal: PrincipalContext,
    tenant_id: UUID,
    action: str,
    entity_id: str,
    payload_redacted: dict[str, str],
) -> None:
    await AuditService(AuditRepository(session)).record_workflow_event(
        principal=principal,
        scope_type="tenant",
        tenant_id=tenant_id,
        action=action,
        entity_type="design_review",
        entity_id=entity_id,
        trace_id=principal.trace_id,
        request_id=principal.request_id,
        payload_redacted=payload_redacted,
    )


def _raise_http(exc: DesignReviewError) -> None:
    if isinstance(exc, DesignReviewAccessError):
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if isinstance(exc, DesignReviewNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, DesignReviewValidationError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


def _reviewer_request(
    item: DesignReviewCoordinatorReviewerRequest,
) -> DesignReviewCoordinatorReviewer:
    return DesignReviewCoordinatorReviewer(
        reviewer_key=item.reviewer_key,
        role_key=item.role_key,
        prompt_version_id=item.prompt_version_id,
        profile_version_id=item.profile_version_id,
        provider_reference=item.provider_reference,
        enabled=item.enabled,
    )


def _verdict_request(
    item: DesignReviewCoordinatorVerdictRequest,
) -> DesignReviewCoordinatorVerdict:
    return DesignReviewCoordinatorVerdict(
        reviewer_key=item.reviewer_key,
        verdict=item.verdict,
        score=item.score,
        blocking_issue_count=item.blocking_issue_count,
        safe_feedback_summary=item.safe_feedback_summary,
        artifact_id=item.artifact_id,
        output_digest=item.output_digest,
        usage_summary=item.usage_summary,
    )


def _state(
    kind: str,
    summary: str,
) -> DesignReviewState:
    return DesignReviewState(kind=kind, summary=summary)  # type: ignore[arg-type]


def _template_install_response(
    *,
    tenant_id: UUID,
    result: DesignReviewTemplateInstallResult,
) -> DesignReviewTemplateInstallResponse:
    state = result.state
    return DesignReviewTemplateInstallResponse(
        template_key=state.template_key,
        tenant_id=tenant_id,
        workflow_draft_id=state.workflow_draft_id,
        workflow_lineage_id=state.workflow_lineage_id,
        workflow_draft_revision_id=state.workflow_draft_revision_id,
        workflow_key=state.workflow_key,
        display_name=state.display_name,
        agent_test_suite_id=state.agent_test_suite_id,
        agent_test_run_id=state.latest_run_id,
        deterministic_run_id=state.deterministic_run_id,
        model_safe_run_id=state.model_safe_run_id,
        required_evidence_status=state.required_evidence_status,
        publish_gate_status=state.publish_gate_status,
        ready_to_publish=state.ready_to_publish,
        evidence_modes=list(state.evidence_modes),
        replayed=result.replayed,
        safe_summary=state.safe_summary,
        actions=[
            DesignReviewTemplateActionResponse(
                label="Open design reviews",
                href="/admin/app/design-reviews",
                method="get",
            )
        ],
    )


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


def _coordinator_launch_response(
    result: DesignReviewCoordinatorResult,
) -> DesignReviewCoordinatorLaunchResponse:
    if result.round_record is None:
        raise RuntimeError("coordinator launch response requires a round")
    return DesignReviewCoordinatorLaunchResponse(
        state=_state("ready", "Coordinator round launched."),
        session=_session_response(result.session, revision=result.active_revision),
        active_revision=_revision_response(result.active_revision)
        if result.active_revision
        else None,
        round=_round_response(result.round_record),
        workflow_run_id=result.workflow_run_id,
        replayed=result.replayed,
        next_action=result.next_action,
    )


def _coordinator_complete_response(
    result: DesignReviewCoordinatorResult,
) -> DesignReviewCoordinatorCompleteResponse:
    if result.round_record is None or result.quorum_decision is None:
        raise RuntimeError("coordinator completion response requires round decision")
    return DesignReviewCoordinatorCompleteResponse(
        state=_state("ready", "Coordinator round completion recorded."),
        session=_session_response(result.session, revision=result.active_revision),
        round=_round_response(result.round_record),
        active_revision=_revision_response(result.active_revision)
        if result.active_revision
        else None,
        created_revision=_revision_response(result.created_revision)
        if result.created_revision
        else None,
        quorum_decision=_quorum_decision_response(result.quorum_decision),
        handoff=_handoff_response(result.handoff),
        workflow_run_id=result.workflow_run_id,
        replayed=result.replayed,
        next_action=result.next_action,
    )


def _coordinator_manual_response(
    result: DesignReviewCoordinatorResult,
) -> DesignReviewCoordinatorManualDecisionResponse:
    if result.manual_decision is None:
        raise RuntimeError("coordinator manual response requires a decision")
    return DesignReviewCoordinatorManualDecisionResponse(
        state=_state("ready", "Coordinator manual decision applied."),
        session=_session_response(result.session, revision=result.active_revision),
        active_revision=_revision_response(result.active_revision)
        if result.active_revision
        else None,
        created_revision=_revision_response(result.created_revision)
        if result.created_revision
        else None,
        manual_decision=_manual_decision_response(
            result.manual_decision,
            replayed=result.replayed,
        ),
        handoff=_handoff_response(result.handoff),
        replayed=result.replayed,
        next_action=result.next_action,
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
    *,
    replayed: bool = False,
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
        replayed=replayed,
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
    *,
    replayed: bool = False,
) -> DesignManualDecisionResponse:
    return DesignManualDecisionResponse(
        design_manual_decision_id=record.design_manual_decision_id,
        design_review_session_id=record.design_review_session_id,
        design_review_round_id=record.design_review_round_id,
        decision_type=record.decision_type.value,
        actor_principal_id=record.actor_principal_id,
        safe_rationale=record.safe_rationale,
        accepted_risk=record.accepted_risk,
        replayed=replayed,
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
