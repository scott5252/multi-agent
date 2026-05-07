from __future__ import annotations

from datetime import datetime
from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.schemas.operations import (
    OperationsDashboardResponse,
    OperationsExportCreateRequest,
    OperationsExportResponse,
    OperationsLogResponse,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.operations.models import (
    OperationsAccessScope,
    OperationsAuthorizationError,
    OperationsLogFilters,
    OperationsRole,
)
from multi_agent_platform.operations.service import OperationsConsoleService

router = APIRouter(prefix="/admin/operations", tags=["operations-console"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
OptionalStringForm = Form(default=None)
OptionalTenantForm = Form(default=None)
LimitForm = Form(default=100)
SEE_OTHER = status.HTTP_303_SEE_OTHER
OPERATIONS_QUERY_KEYS = frozenset(
    {
        "trace_id",
        "tenant_id",
        "run_id",
        "component",
        "severity",
        "status",
        "dependency",
        "start",
        "end",
        "limit",
        "panel",
        "saved_filter_id",
    }
)


@router.get("/api/dashboard", response_model=OperationsDashboardResponse)
async def operations_dashboard_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    trace_id: str | None = None,
    tenant_id: UUID | None = None,
    run_id: UUID | None = None,
    component: str | None = None,
    severity: str | None = None,
    status_value: Annotated[str | None, Query(alias="status")] = None,
    dependency: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> OperationsDashboardResponse:
    access_scope = _access_scope(principal)
    filters = _filters_from_params(
        trace_id=trace_id,
        tenant_id=tenant_id,
        run_id=run_id,
        component=component,
        severity=severity,
        status=status_value,
        dependency=dependency,
        start=start,
        end=end,
        limit=limit,
    )
    dashboard = await OperationsConsoleService(
        session=session,
        container=container,
    ).dashboard(access_scope=access_scope, filters=filters)
    return OperationsDashboardResponse.model_validate(dashboard.model_dump())


@router.get("/api/logs", response_model=OperationsLogResponse)
async def operations_logs_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    trace_id: str | None = None,
    tenant_id: UUID | None = None,
    run_id: UUID | None = None,
    component: str | None = None,
    severity: str | None = None,
    status_value: Annotated[str | None, Query(alias="status")] = None,
    dependency: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> OperationsLogResponse:
    access_scope = _access_scope(principal)
    filters = _filters_from_params(
        trace_id=trace_id,
        tenant_id=tenant_id,
        run_id=run_id,
        component=component,
        severity=severity,
        status=status_value,
        dependency=dependency,
        start=start,
        end=end,
        limit=limit,
    )
    items = await OperationsConsoleService(
        session=session,
        container=container,
    ).query_logs(access_scope=access_scope, filters=filters)
    return OperationsLogResponse(items=items, filters=filters.safe_snapshot())


@router.post(
    "/api/logs/export",
    response_model=OperationsExportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def operations_export_api(
    payload: OperationsExportCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> OperationsExportResponse:
    return await _export_logs(
        principal=principal,
        session=session,
        container=container,
        filters=payload.filters,
    )


@router.get("", response_model=None, include_in_schema=False)
async def operations_console_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    trace_id: str | None = None,
    tenant_id: UUID | None = None,
    run_id: UUID | None = None,
    component: str | None = None,
    severity: str | None = None,
    status_value: Annotated[str | None, Query(alias="status")] = None,
    dependency: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> RedirectResponse:
    _ = (
        principal,
        session,
        trace_id,
        tenant_id,
        run_id,
        component,
        severity,
        status_value,
        dependency,
        start,
        end,
        limit,
    )
    return _react_redirect(request, "/admin/app/operations")


@router.post(
    "/logs/export",
    response_model=OperationsExportResponse,
    include_in_schema=False,
)
async def operations_export_page(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    trace_id: str | None = OptionalStringForm,
    tenant_id: UUID | None = OptionalTenantForm,
    run_id: UUID | None = OptionalTenantForm,
    component: str | None = OptionalStringForm,
    severity: str | None = OptionalStringForm,
    status_value: str | None = Form(default=None, alias="status"),
    dependency: str | None = OptionalStringForm,
    limit: int = LimitForm,
) -> OperationsExportResponse:
    filters = _filters_from_params(
        trace_id=trace_id,
        tenant_id=tenant_id,
        run_id=run_id,
        component=component,
        severity=severity,
        status=status_value,
        dependency=dependency,
        limit=limit,
    )
    return await _export_logs(
        principal=principal,
        session=session,
        container=container,
        filters=filters,
    )


async def _export_logs(
    *,
    principal: PrincipalContext,
    session: AsyncSession,
    container: ContainerDep,
    filters: OperationsLogFilters,
) -> OperationsExportResponse:
    access_scope = _access_scope(principal)
    try:
        export = await OperationsConsoleService(
            session=session,
            container=container,
        ).export_logs(
            access_scope=access_scope,
            filters=filters,
            storage_provider=container.storage_provider,
        )
    except OperationsAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return OperationsExportResponse.model_validate(export.model_dump())


def _access_scope(principal: PrincipalContext) -> OperationsAccessScope:
    permissions = set(principal.permission_codes)
    if "platform_admin" in principal.role_codes:
        return OperationsAccessScope(
            principal_id=principal.principal_id,
            role=OperationsRole.PLATFORM_ADMIN,
            can_export="operations:export" in permissions,
            trace_id=principal.trace_id,
        )
    if "auditor" in principal.role_codes:
        return OperationsAccessScope(
            principal_id=principal.principal_id,
            role=OperationsRole.AUDITOR,
            can_export="operations:export" in permissions,
            trace_id=principal.trace_id,
        )
    raise HTTPException(status_code=403, detail="platform operations access required")


def _filters_from_params(**kwargs: object) -> OperationsLogFilters:
    return OperationsLogFilters.model_validate(
        {key: value for key, value in kwargs.items() if value is not None}
    )


def _react_redirect(
    request: Request,
    destination: str,
    *,
    extra: dict[str, object] | None = None,
) -> RedirectResponse:
    query: dict[str, str] = {
        key: value
        for key, value in request.query_params.items()
        if key in OPERATIONS_QUERY_KEYS and value
    }
    if extra:
        for key, value in extra.items():
            if value is not None:
                query[key] = str(value)
    suffix = f"?{urlencode(query)}" if query else ""
    return RedirectResponse(f"{destination}{suffix}", status_code=SEE_OTHER)
