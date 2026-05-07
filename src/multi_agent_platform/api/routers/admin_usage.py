from __future__ import annotations

from datetime import datetime
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.schemas.usage import (
    UsageEventsResponse,
    UsageExportCreateRequest,
    UsageExportResponse,
    UsageSummaryResponse,
)
from multi_agent_platform.api.ui.admin_console import is_platform_admin
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.usage import UsageExportRequest
from multi_agent_platform.db.repositories.usage import (
    UsageAccessDeniedError,
    UsageRepository,
)
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageFilters,
    UsageScopeType,
)
from multi_agent_platform.usage.service import UsageAnalyticsService

router = APIRouter(prefix="/admin/usage", tags=["usage-analytics"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
OptionalTenantForm = Form(default=None)
OptionalStringForm = Form(default=None)
GroupByForm = Form(default="day")
SEE_OTHER = status.HTTP_303_SEE_OTHER
USAGE_QUERY_KEYS = frozenset(
    {
        "tenant_id",
        "start",
        "end",
        "provider_key",
        "model_id",
        "workflow_lineage_id",
        "workflow_version_id",
        "workflow_run_id",
        "workflow_run_step_id",
        "agent_key",
        "sub_agent_key",
        "prompt_version_id",
        "execution_mode",
        "usage_status",
        "principal_id",
        "group_by",
        "saved_filter_id",
    }
)


@router.get("/api/summary", response_model=UsageSummaryResponse)
async def usage_summary_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    provider_key: str | None = None,
    model_id: str | None = None,
    workflow_lineage_id: UUID | None = None,
    workflow_version_id: UUID | None = None,
    workflow_run_id: UUID | None = None,
    workflow_run_step_id: UUID | None = None,
    agent_key: str | None = None,
    sub_agent_key: str | None = None,
    prompt_version_id: UUID | None = None,
    execution_mode: str | None = None,
    usage_status: UsageEventStatus | None = None,
    principal_id: str | None = None,
    group_by: str = "day",
) -> UsageSummaryResponse:
    filters = _filters_from_params(
        tenant_id=tenant_id,
        start=start,
        end=end,
        provider_key=provider_key,
        model_id=model_id,
        workflow_lineage_id=workflow_lineage_id,
        workflow_version_id=workflow_version_id,
        workflow_run_id=workflow_run_id,
        workflow_run_step_id=workflow_run_step_id,
        agent_key=agent_key,
        sub_agent_key=sub_agent_key,
        prompt_version_id=prompt_version_id,
        execution_mode=execution_mode,
        usage_status=usage_status,
        principal_id=principal_id,
        group_by=group_by,
    )
    scope = _access_scope(principal, tenant_id)
    summary = await UsageAnalyticsService(UsageRepository(session)).summarize_usage(
        access_scope=scope,
        filters=filters,
    )
    return UsageSummaryResponse.from_parts(
        totals=summary.totals,
        rollups=summary.rollups,
    )


@router.get("/api/events", response_model=UsageEventsResponse)
async def usage_events_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    provider_key: str | None = None,
    model_id: str | None = None,
    limit: int = Query(default=200, ge=1, le=500),
) -> UsageEventsResponse:
    filters = UsageFilters(
        tenant_id=tenant_id,
        provider_key=provider_key,
        model_id=model_id,
    )
    scope = _access_scope(principal, tenant_id)
    summary = await UsageAnalyticsService(UsageRepository(session)).summarize_usage(
        access_scope=scope,
        filters=filters,
        limit=limit,
    )
    return UsageEventsResponse(events=summary.events)


@router.post(
    "/api/exports",
    response_model=UsageExportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_usage_export_api(
    request: UsageExportCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> UsageExportResponse:
    scope = _access_scope(principal, request.tenant_id)
    filters = UsageFilters.model_validate(
        {**request.filters, "tenant_id": request.tenant_id}
    )
    try:
        export = await UsageAnalyticsService(
            UsageRepository(session)
        ).create_csv_export(
            access_scope=scope,
            filters=filters,
            storage_provider=container.storage_provider,
        )
    except UsageAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return _export_response(export)


@router.get("", response_model=None, include_in_schema=False)
async def usage_dashboard_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    provider_key: str | None = None,
    model_id: str | None = None,
    group_by: str = "day",
) -> RedirectResponse:
    _ = (principal, session, tenant_id, provider_key, model_id, group_by)
    return _react_redirect(request, "/admin/app/usage")


@router.post("/exports", response_model=None, include_in_schema=False)
async def create_usage_export_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = OptionalTenantForm,
    provider_key: str | None = OptionalStringForm,
    model_id: str | None = OptionalStringForm,
    group_by: str = GroupByForm,
) -> RedirectResponse:
    filters = UsageFilters(
        tenant_id=tenant_id,
        provider_key=provider_key or None,
        model_id=model_id or None,
        group_by=group_by,  # type: ignore[arg-type]
    )
    scope = _access_scope(principal, tenant_id)
    try:
        export = await UsageAnalyticsService(
            UsageRepository(session)
        ).create_csv_export(
            access_scope=scope,
            filters=filters,
            storage_provider=container.storage_provider,
        )
    except UsageAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return RedirectResponse(
        _react_usage_export_href(export.usage_export_request_id, tenant_id=tenant_id),
        status_code=SEE_OTHER,
    )


@router.get(
    "/exports/{usage_export_request_id}",
    response_model=None,
    include_in_schema=False,
)
async def usage_export_detail_page(
    usage_export_request_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    tenant_id = _query_tenant_id(request)
    scope = _access_scope(principal, tenant_id)
    try:
        export = await UsageRepository(session).get_export_request(
            usage_export_request_id,
            access_scope=scope,
        )
    except UsageAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if export is None:
        raise HTTPException(status_code=404, detail="usage export not found")
    return RedirectResponse(
        _react_usage_export_href(
            usage_export_request_id,
            tenant_id=tenant_id,
            request=request,
        ),
        status_code=SEE_OTHER,
    )


def _access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> UsageAccessScope:
    platform = is_platform_admin(principal)
    if platform and tenant_id is None:
        return UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=True,
        )
    selected_tenant = tenant_id or principal.tenant_id
    if selected_tenant is None:
        raise HTTPException(status_code=403, detail="tenant usage scope required")
    if not platform and selected_tenant != principal.tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope is not authorized")
    return UsageAccessScope(
        scope_type=UsageScopeType.TENANT,
        tenant_id=selected_tenant,
        principal_id=principal.principal_id,
        platform_admin=platform,
    )


def _filters_from_params(**kwargs: object) -> UsageFilters:
    return UsageFilters.model_validate({key: value for key, value in kwargs.items()})


def _export_response(export: UsageExportRequest) -> UsageExportResponse:
    return UsageExportResponse(
        usage_export_request_id=export.usage_export_request_id,
        status=export.status.value,
        row_count=export.row_count,
        artifact_uri=export.artifact_uri,
        artifact_sha256=export.artifact_sha256,
        artifact_size_bytes=export.artifact_size_bytes,
        denial_reason=export.denial_reason,
        failure_reason=export.failure_reason,
        created_at=export.created_at,
        completed_at=export.completed_at,
    )


def _query_tenant_id(request: Request) -> UUID | None:
    raw = request.query_params.get("tenant_id")
    return UUID(raw) if raw else None


def _react_redirect(request: Request, destination: str) -> RedirectResponse:
    query = {
        key: value
        for key, value in request.query_params.items()
        if key in USAGE_QUERY_KEYS and value
    }
    suffix = f"?{urlencode(query)}" if query else ""
    return RedirectResponse(f"{destination}{suffix}", status_code=SEE_OTHER)


def _react_usage_export_href(
    usage_export_request_id: UUID,
    *,
    tenant_id: UUID | None,
    request: Request | None = None,
) -> str:
    query: dict[str, str] = {}
    if request is not None:
        query.update(
            {
                key: value
                for key, value in request.query_params.items()
                if key in USAGE_QUERY_KEYS and value
            }
        )
    if tenant_id is not None:
        query["tenant_id"] = str(tenant_id)
    suffix = f"?{urlencode(query)}" if query else ""
    return f"/admin/app/usage/exports/{usage_export_request_id}{suffix}"
