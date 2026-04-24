from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from multi_agent_platform.api.deps import get_scope
from multi_agent_platform.api.schemas.runtime_runs import (
    ApprovalDecisionResponse,
    ApprovalGateListResponse,
    ErrorResponse,
    HandoffEnvelopeListResponse,
    RunCancelRequest,
    RunLineageResponse,
    RunStartRequest,
    RunStartResponse,
    RunStatusResponse,
    RunTimelineResponse,
    SideEffectIntentListResponse,
    TimelineEvent,
)
from multi_agent_platform.api.schemas.runtime_runs import (
    RunStatus as ApiRunStatus,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.runtime.orchestration.models import WorkflowRun
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)
from multi_agent_platform.tenancy.context import ScopeContext

router = APIRouter(prefix="/runtime/runs", tags=["runtime"])


async def get_authorized_scope(
    request: Request,
    _principal: Annotated[object, Depends(require_authorized_principal)],
) -> ScopeContext:
    return get_scope(request)


ScopeDep = Annotated[ScopeContext, Depends(get_authorized_scope)]

_runtime_service = RuntimeOrchestrationService()


@router.post(
    "",
    response_model=RunStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
async def start_run(request: RunStartRequest, scope: ScopeDep) -> RunStartResponse:
    run = await _runtime_service.start_run(
        tenant_id=scope.tenant_id,
        scope_type=scope.scope_type.value,
        principal_id=scope.principal_id,
        published_workflow_version_id=request.published_workflow_version_id,
        input_payload=request.input,
        idempotency_key=request.idempotency_key,
        trace_id=request.trace_id or scope.trace_id,
    )
    return RunStartResponse(
        workflow_run_id=run.workflow_run_id,
        status=ApiRunStatus(run.status.value),
        run_bundle_id=run.run_bundle_id,
        bundle_digest=run.bundle_digest,
        created_at=run.created_at,
    )


@router.get("/{workflow_run_id}", response_model=RunStatusResponse)
async def inspect_run(workflow_run_id: UUID, scope: ScopeDep) -> RunStatusResponse:
    run = await _runtime_service.inspect_run(
        workflow_run_id=workflow_run_id, tenant_id=scope.tenant_id
    )
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return _status_response(run)


@router.post(
    "/{workflow_run_id}/cancel",
    response_model=RunStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def cancel_run(
    workflow_run_id: UUID, request: RunCancelRequest, scope: ScopeDep
) -> RunStatusResponse:
    try:
        run = await _runtime_service.cancel_run(
            workflow_run_id=workflow_run_id,
            tenant_id=scope.tenant_id,
            reason=request.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _status_response(run)


@router.get("/{workflow_run_id}/timeline", response_model=RunTimelineResponse)
async def list_timeline(
    workflow_run_id: UUID, scope: ScopeDep, limit: int = 100
) -> RunTimelineResponse:
    events = await _runtime_service.repository.list_timeline(
        workflow_run_id, scope.tenant_id, limit
    )
    return RunTimelineResponse(
        items=[
            TimelineEvent(
                runtime_timeline_event_id=event.runtime_timeline_event_id,
                event_type=event.event_type.value,
                severity=event.severity.value,
                payload=event.payload,
                trace_id=event.trace_id,
                created_at=event.created_at,
            )
            for event in events
        ]
    )


@router.get("/{workflow_run_id}/lineage", response_model=RunLineageResponse)
async def list_lineage(workflow_run_id: UUID, scope: ScopeDep) -> RunLineageResponse:
    run = await _runtime_service.inspect_run(
        workflow_run_id=workflow_run_id, tenant_id=scope.tenant_id
    )
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunLineageResponse(nodes=[], edges=[])


@router.get(
    "/{workflow_run_id}/approval-gates", response_model=ApprovalGateListResponse
)
async def list_approval_gates(
    workflow_run_id: UUID, scope: ScopeDep, status: str | None = None
) -> ApprovalGateListResponse:
    _ = (workflow_run_id, scope, status)
    return ApprovalGateListResponse(items=[])


@router.post(
    "/{workflow_run_id}/approval-gates/{approval_gate_id}/decisions",
    response_model=ApprovalDecisionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def decide_approval_gate(
    workflow_run_id: UUID,
    approval_gate_id: UUID,
    scope: ScopeDep,
) -> ApprovalDecisionResponse:
    _ = (workflow_run_id, scope)
    return ApprovalDecisionResponse(
        approval_gate_id=approval_gate_id,
        approval_decision_id=approval_gate_id,
        accepted=True,
        status="approved",
        resume_queued=True,
    )


@router.get("/{workflow_run_id}/handoffs", response_model=HandoffEnvelopeListResponse)
async def list_handoffs(
    workflow_run_id: UUID, scope: ScopeDep
) -> HandoffEnvelopeListResponse:
    _ = (workflow_run_id, scope)
    return HandoffEnvelopeListResponse(items=[])


@router.get(
    "/{workflow_run_id}/side-effects", response_model=SideEffectIntentListResponse
)
async def list_side_effects(
    workflow_run_id: UUID, scope: ScopeDep
) -> SideEffectIntentListResponse:
    _ = (workflow_run_id, scope)
    return SideEffectIntentListResponse(items=[])


def _status_response(run: WorkflowRun) -> RunStatusResponse:
    return RunStatusResponse(
        workflow_run_id=run.workflow_run_id,
        tenant_id=run.tenant_id,
        status=ApiRunStatus(run.status.value),
        bundle_digest=run.bundle_digest,
        created_at=run.created_at,
        current_checkpoint_id=run.current_checkpoint_id,
        pause_reason=run.pause_reason,
        terminal_reason=run.terminal_reason,
        updated_at=run.updated_at,
        finished_at=run.finished_at,
    )
