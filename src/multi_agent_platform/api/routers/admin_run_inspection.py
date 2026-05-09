from __future__ import annotations

from dataclasses import asdict
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.schemas.admin_agent_graph import AgentCommunicationGraph
from multi_agent_platform.api.schemas.audit_debugging import (
    CreateDebugEvidenceExportRequest,
    DebugEvidenceExport,
    InspectionError,
    ReplayEvent,
    RunDebugSearchItem,
    RunDebugSearchResponse,
    RunLineageGraphResponse,
    RunReplayResponse,
    RunTimelineResponse,
    VersionBundleSnapshot,
    VersionBundleSummary,
)
from multi_agent_platform.audit.inspection import bundle_to_dict
from multi_agent_platform.audit.models import InspectionAction
from multi_agent_platform.audit.service import (
    AuditDebuggingAuthorizationError,
    AuditDebuggingRateLimitError,
    AuditDebuggingService,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.operations.runtime_agent_graph import (
    build_runtime_agent_graph,
)

router = APIRouter(prefix="/admin/runs", tags=["production-audit-debugging"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
TenantQuery = Annotated[UUID | None, Query()]
SEE_OTHER = status.HTTP_303_SEE_OTHER
RUN_QUERY_KEYS = frozenset(
    {
        "tenant_id",
        "status",
        "workflow_id",
        "workflow_lineage_id",
        "principal_id",
        "cursor",
        "limit",
        "from_sequence",
        "to_sequence",
        "saved_filter_id",
    }
)


def _service(session: AsyncSession) -> AuditDebuggingService:
    return AuditDebuggingService(AuditDebuggingRepository(session))


def build_combined_gateway_provenance_view(
    provenance: dict[str, object] | None,
) -> dict[str, object]:
    if provenance is None:
        return {
            "metadata_available": False,
            "metadata_status": "pre_v2_metadata_unavailable",
            "gateway_operation_id": None,
        }
    return provenance


def _error(exc: Exception, trace_id: str | None = None) -> HTTPException:
    if isinstance(exc, AuditDebuggingAuthorizationError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=InspectionError(
                category="forbidden",
                message=str(exc),
                trace_id=trace_id,
            ).model_dump(),
        )
    if isinstance(exc, AuditDebuggingRateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "category": "rate_limited",
                "message": str(exc),
                "retry_after_seconds": exc.retry_after_seconds,
                "trace_id": trace_id,
            },
        )
    return HTTPException(status_code=500, detail=str(exc))


@router.get("/debug-search", response_model=RunDebugSearchResponse)
async def debug_search(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
    workflow_run_id: UUID | None = None,
    workflow_id: str | None = None,
    status: str | None = None,
    failure_category: str | None = None,
    agent: str | None = None,
    tool: str | None = None,
    model_selection_source: str | None = None,
    notification_status: str | None = None,
    lineage_relationship: str | None = None,
    cursor: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> RunDebugSearchResponse:
    filters = {
        "workflow_run_id": workflow_run_id,
        "workflow_id": workflow_id,
        "status": status,
        "failure_category": failure_category,
        "agent": agent,
        "tool": tool,
        "model_selection_source": model_selection_source,
        "notification_status": notification_status,
        "lineage_relationship": lineage_relationship,
        "cursor": cursor,
    }
    try:
        rows = await _service(session).search_runs(
            principal=principal,
            tenant_id=tenant_id,
            filters={key: value for key, value in filters.items() if value is not None},
            limit=limit,
        )
    except Exception as exc:
        raise _error(exc, principal.trace_id) from exc
    return RunDebugSearchResponse(
        items=[
            RunDebugSearchItem(
                workflow_run_id=row.workflow_run_id,
                tenant_id=row.tenant_id,
                status=row.run_status_after,
                started_at=row.occurred_at,
                latest_event_at=row.occurred_at,
                trace_id=row.trace_id,
                failure_category=category
                if isinstance(category := row.safe_details.get("category"), str)
                else None,
                bundle=VersionBundleSummary(),
            )
            for row in rows
        ],
        next_cursor=None,
    )


@router.get("/{workflow_run_id}/timeline", response_model=RunTimelineResponse)
async def timeline(
    workflow_run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
) -> RunTimelineResponse:
    try:
        view = await _service(session).get_timeline(
            principal=principal, tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
    except Exception as exc:
        raise _error(exc, principal.trace_id) from exc
    if view is None:
        raise HTTPException(
            status_code=404,
            detail=InspectionError(
                category="not_found",
                message="run not found within authorized scope",
                trace_id=principal.trace_id,
            ).model_dump(),
        )
    return RunTimelineResponse.model_validate(asdict(view))


@router.get("/{workflow_run_id}/replay", response_model=RunReplayResponse)
async def replay(
    workflow_run_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
    include_children: bool = False,
    from_sequence: int | None = Query(default=None, ge=0),
    to_sequence: int | None = Query(default=None, ge=0),
) -> RunReplayResponse | RedirectResponse:
    if "text/html" in request.headers.get("accept", ""):
        _ = (principal, session)
        return _react_redirect(
            request,
            extra={"run_id": workflow_run_id, "panel": "replay"},
        )
    _ = include_children
    try:
        events = await _service(session).get_replay(
            principal=principal, tenant_id=tenant_id, workflow_run_id=workflow_run_id
        )
    except Exception as exc:
        raise _error(exc, principal.trace_id) from exc
    if events is None:
        raise HTTPException(status_code=404, detail="run not found")
    bounded = [
        event
        for event in events
        if isinstance(event["sequence"], int)
        and (from_sequence is None or event["sequence"] >= from_sequence)
        and (to_sequence is None or event["sequence"] <= to_sequence)
    ]
    return RunReplayResponse(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        events=[ReplayEvent.model_validate(event) for event in bounded],
    )


@router.get("/{workflow_run_id}/lineage", response_model=RunLineageGraphResponse)
async def lineage(
    workflow_run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
) -> RunLineageGraphResponse:
    view = await _service(session).get_timeline(
        principal=principal, tenant_id=tenant_id, workflow_run_id=workflow_run_id
    )
    if view is None:
        raise HTTPException(status_code=404, detail="run not found")
    return RunLineageGraphResponse.model_validate(view.lineage)


@router.get("/{workflow_run_id}/bundle", response_model=VersionBundleSnapshot)
async def bundle(
    workflow_run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
) -> VersionBundleSnapshot:
    record = await _service(session).get_bundle(
        principal=principal, tenant_id=tenant_id, workflow_run_id=workflow_run_id
    )
    if record is None:
        raise HTTPException(status_code=404, detail="bundle not found")
    return VersionBundleSnapshot.model_validate(bundle_to_dict(record))


@router.get("/{workflow_run_id}/agent-graph", response_model=AgentCommunicationGraph)
async def runtime_agent_graph(
    workflow_run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: TenantQuery = None,
) -> AgentCommunicationGraph:
    target_tenant_id = tenant_id if tenant_id is not None else principal.tenant_id
    try:
        await _service(session).ensure_authorized(
            principal=principal,
            tenant_id=target_tenant_id,
            workflow_run_id=workflow_run_id,
            action=InspectionAction.TIMELINE,
        )
    except Exception as exc:
        raise _error(exc, principal.trace_id) from exc

    graph = await build_runtime_agent_graph(
        repository=RuntimeOrchestrationRepository(session),
        workflow_run_id=workflow_run_id,
        tenant_id=target_tenant_id,
    )
    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=InspectionError(
                category="not_found",
                message="run not found within authorized scope",
                trace_id=principal.trace_id,
            ).model_dump(),
        )
    return graph


@router.post(
    "/{workflow_run_id}/exports",
    response_model=DebugEvidenceExport,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_export(
    workflow_run_id: UUID,
    payload: CreateDebugEvidenceExportRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> DebugEvidenceExport:
    tenant_id = payload.tenant_id or principal.tenant_id
    try:
        record = await _service(session).create_export(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            lineage_scope=payload.lineage_scope,
            recipient_scope=payload.recipient_scope,
            included_sections=payload.included_sections,
            excluded_sections=payload.excluded_sections,
        )
    except Exception as exc:
        raise _error(exc, principal.trace_id) from exc
    return DebugEvidenceExport.model_validate(record, from_attributes=True)


@router.get("", response_model=None)
async def admin_run_search_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = (principal, session)
    return _react_redirect(request, extra={"panel": "runs"})


@router.get("/{workflow_run_id}", response_model=None)
async def admin_run_detail_page(
    workflow_run_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = (principal, session)
    return _react_redirect(request, extra={"run_id": workflow_run_id})


def _react_redirect(
    request: Request,
    *,
    extra: dict[str, object] | None = None,
) -> RedirectResponse:
    query = {
        key: value
        for key, value in request.query_params.items()
        if key in RUN_QUERY_KEYS and value
    }
    if extra:
        for key, value in extra.items():
            if value is not None:
                query[key] = str(value)
    suffix = f"?{urlencode(query)}" if query else ""
    return RedirectResponse(f"/admin/app/operations{suffix}", status_code=SEE_OTHER)
