from __future__ import annotations

from datetime import datetime
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.usage import (
    UsageEventsResponse,
    UsageExportCreateRequest,
    UsageExportResponse,
    UsageSummaryResponse,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    build_common_state,
    is_platform_admin,
)
from multi_agent_platform.api.ui.usage import (
    UsageDashboardPage,
    UsageExportPage,
    redaction_notice,
)
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


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def usage_dashboard_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
    provider_key: str | None = None,
    model_id: str | None = None,
    group_by: str = "day",
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Usage Analytics",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Usage Analytics", href="/admin/usage"),
        ),
    )
    selected_tenant = tenant_id or shell.active_scope.tenant_id
    filters = UsageFilters(
        tenant_id=selected_tenant,
        provider_key=provider_key,
        model_id=model_id,
        group_by=group_by,  # type: ignore[arg-type]
    )
    scope = _access_scope(principal, selected_tenant)
    summary = await UsageAnalyticsService(UsageRepository(session)).summarize_usage(
        access_scope=scope,
        filters=filters,
    )
    page = UsageDashboardPage(
        filters=filters,
        totals=summary.totals,
        rollups=summary.rollups,
        events=summary.events,
        can_export=True,
    )
    shell.common_state = (
        build_common_state(
            CommonStateType.EMPTY,
            title="No usage events",
            summary="No token usage events match the current filters.",
            trace_id=principal.trace_id,
        )
        if not page.has_events
        else None
    )
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "usage/index.html",
            {
                "shell": shell,
                "principal": principal,
                "page": page,
                "redaction_notice": redaction_notice(),
            },
        ),
    )


@router.post("/exports", response_class=HTMLResponse, include_in_schema=False)
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
        f"/admin/usage/exports/{export.usage_export_request_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/exports/{usage_export_request_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def usage_export_detail_page(
    usage_export_request_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Usage Export",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Usage Analytics", href="/admin/usage"),
            BreadcrumbItem(label="Export", href=request.url.path),
        ),
    )
    scope = _access_scope(principal, shell.active_scope.tenant_id)
    try:
        export = await UsageRepository(session).get_export_request(
            usage_export_request_id,
            access_scope=scope,
        )
    except UsageAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if export is None:
        raise HTTPException(status_code=404, detail="usage export not found")
    page = UsageExportPage(
        status=export.status.value,
        row_count=export.row_count,
        artifact_uri=export.artifact_uri,
        denial_reason=export.denial_reason,
        failure_reason=export.failure_reason,
    )
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "usage/export_detail.html",
            {
                "shell": shell,
                "principal": principal,
                "page": page,
                "redaction_notice": redaction_notice(),
            },
        ),
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
