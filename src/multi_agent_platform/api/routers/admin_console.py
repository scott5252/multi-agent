from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.ui.admin_console import (
    AdminConsoleAccessError,
    AdminScope,
    AdminShellContext,
    BreadcrumbItem,
    CommonState,
    CommonStateType,
    SavedFilterSummary,
    build_admin_shell_context,
    build_common_state,
    build_saved_filter_summary,
    filter_profiles,
    normalize_filter_criteria,
    resolve_admin_scope,
    safe_redirect_target,
    sanitize_text,
    with_scope_query,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.repositories.admin_console import (
    AdminSavedFilterRepository,
)
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.observability.logging import admin_shell_log_context
from multi_agent_platform.observability.metrics import (
    record_admin_shell_audit_failure,
    record_admin_shell_fail_closed,
)

router = APIRouter(tags=["admin-console-shell"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def resolve_scope_for_request(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
) -> AdminScope:
    active_scope = resolve_admin_scope(principal, request.query_params.get("tenant_id"))
    if active_scope.scope_type == "tenant" and active_scope.tenant_id is not None:
        tenant = await session.get(Tenant, active_scope.tenant_id)
        if tenant is not None:
            if tenant.status is not TenantStatus.ACTIVE:
                raise AdminConsoleAccessError(
                    "tenant scope is unavailable",
                    reason_category="tenant_unavailable",
                )
            active_scope = AdminScope.tenant(
                tenant.tenant_id,
                label=tenant.display_name,
            )
    return active_scope


async def build_shell_for_request(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    title: str,
    breadcrumbs: tuple[BreadcrumbItem, ...] = (),
    common_state: CommonState | None = None,
    saved_filters: Sequence[SavedFilterSummary] = (),
) -> AdminShellContext:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    shell = build_admin_shell_context(
        principal=principal,
        active_scope=active_scope,
        current_path=request.url.path,
        title=title,
        breadcrumbs=breadcrumbs,
        common_state=common_state,
        saved_filters=saved_filters,
    )
    try:
        await AuditService(AuditRepository(session)).record_admin_navigation_visibility(
            principal=principal,
            active_scope=shell.active_scope,
            request_path=request.url.path,
            outcomes=shell.navigation_outcomes,
        )
    except Exception as exc:
        record_admin_shell_audit_failure(
            action="navigation_visibility",
            reason=exc.__class__.__name__,
        )
        raise AdminConsoleAccessError(
            "admin shell audit persistence is unavailable",
            status_code=503,
            reason_category="audit_unavailable",
        ) from exc
    return shell


async def render_admin_error(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    status_code: int,
    title: str,
    summary: str,
    reason: str,
) -> HTMLResponse:
    record_admin_shell_fail_closed(surface=request.url.path, reason=reason)
    state = build_common_state(
        CommonStateType.UNAVAILABLE if status_code == 503 else CommonStateType.DENIED,
        title=title,
        summary=summary,
        trace_id=principal.trace_id,
    )
    shell = None
    try:
        fallback_scope = resolve_admin_scope(principal, None)
        shell = build_admin_shell_context(
            principal=principal,
            active_scope=fallback_scope,
            current_path="/admin",
            title=title,
            common_state=state,
        )
    except AdminConsoleAccessError:
        shell = None
    tenant_id_for_log = None
    if shell is not None and shell.active_scope.tenant_id is not None:
        tenant_id_for_log = str(shell.active_scope.tenant_id)
    container = request.app.state.container
    container.logger.warning(
        "admin shell fail closed",
        **admin_shell_log_context(
            action="render",
            outcome="blocked",
            reason=reason,
            trace_id=principal.trace_id,
            tenant_id=tenant_id_for_log,
            principal_id=principal.principal_id,
            request_path=request.url.path,
        ),
    )
    response = container.workflow_ui_templates.TemplateResponse(
        request,
        "admin_shell/unavailable.html",
        {"shell": shell, "state": state, "principal": principal},
        status_code=status_code,
    )
    return cast(HTMLResponse, response)


@router.get("/admin", response_class=HTMLResponse)
async def admin_console_landing(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    try:
        shell = await build_shell_for_request(
            request=request,
            principal=principal,
            session=session,
            title="Admin Console",
            breadcrumbs=(BreadcrumbItem(label="Admin", href="/admin"),),
        )
    except AdminConsoleAccessError as exc:
        return await render_admin_error(
            request=request,
            principal=principal,
            session=session,
            status_code=exc.status_code,
            title="Admin console unavailable",
            summary="The admin console could not be opened for this scope.",
            reason=exc.reason_category,
        )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "admin_shell/index.html",
        {"shell": shell, "principal": principal},
    )


@router.get("/admin/scope", response_class=HTMLResponse, response_model=None)
async def admin_console_scope(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
    next: Annotated[str | None, Query()] = None,  # noqa: A002
) -> RedirectResponse | HTMLResponse:
    current_scope = resolve_admin_scope(principal, None)
    try:
        selected_scope = resolve_admin_scope(principal, tenant_id)
        if (
            selected_scope.scope_type == "tenant"
            and selected_scope.tenant_id is not None
        ):
            tenant = await session.get(Tenant, selected_scope.tenant_id)
            if tenant is not None and tenant.status is not TenantStatus.ACTIVE:
                raise AdminConsoleAccessError(
                    "tenant scope is unavailable",
                    reason_category="tenant_unavailable",
                )
        await AuditService(AuditRepository(session)).record_admin_scope_selection(
            principal=principal,
            active_scope=current_scope,
            selected_scope=selected_scope,
            outcome="allowed",
            reason_category="validated",
        )
    except AdminConsoleAccessError as exc:
        return await render_admin_error(
            request=request,
            principal=principal,
            session=session,
            status_code=exc.status_code,
            title="Scope unavailable",
            summary="The requested admin scope is not available.",
            reason=exc.reason_category,
        )
    except Exception as exc:
        record_admin_shell_audit_failure(
            action="scope_selection",
            reason=exc.__class__.__name__,
        )
        return await render_admin_error(
            request=request,
            principal=principal,
            session=session,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            title="Scope unavailable",
            summary="Scope selection could not be safely audited.",
            reason="audit_unavailable",
        )
    redirect_to = with_scope_query(
        safe_redirect_target(next, fallback="/admin"),
        selected_scope,
    )
    return RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/admin/filters/{admin_area}", response_class=HTMLResponse)
async def list_saved_filters(
    admin_area: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    if admin_area not in filter_profiles():
        raise HTTPException(status_code=404, detail="unsupported admin area")
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    records = await AdminSavedFilterRepository(session).list_filters(
        principal=principal,
        admin_area=admin_area,
        scope=active_scope,
    )
    saved_filters = tuple(
        build_saved_filter_summary(record, active_scope=active_scope)
        for record in records
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Saved Filters",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Saved Filters", href=request.url.path),
        ),
        saved_filters=saved_filters,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "admin_shell/saved_filters_page.html",
        {"shell": shell, "principal": principal, "admin_area": admin_area},
    )


@router.post("/admin/filters/{admin_area}", response_class=HTMLResponse)
async def save_saved_filter(
    admin_area: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    filter_key: Annotated[str, Form()],
    display_name: Annotated[str, Form()],
    criteria: Annotated[str, Form()] = "{}",
    return_to: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    try:
        normalized = normalize_filter_criteria(
            admin_area,
            criteria,
            active_scope=active_scope,
            filter_key=filter_key,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="invalid filter criteria") from exc
    await AdminSavedFilterRepository(session).save_filter(
        principal=principal,
        admin_area=admin_area,
        filter_key=normalized.filter_key,
        scope=active_scope,
        display_name=sanitize_text(
            display_name,
            fallback="Saved filter",
            max_length=120,
        ),
        criteria=dict(normalized.criteria),
        safe_summary=normalized.safe_summary,
    )
    redirect_to = with_scope_query(
        safe_redirect_target(
            return_to,
            fallback=filter_profiles()[admin_area].destination_href,
        ),
        active_scope,
    )
    return RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/admin/filters/{admin_area}/{filter_id}/restore")
async def restore_saved_filter(
    admin_area: str,
    filter_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    repo = AdminSavedFilterRepository(session)
    record = await repo.mark_restored(
        principal=principal,
        admin_area=admin_area,
        scope=active_scope,
        filter_id=filter_id,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="saved filter not found")
    try:
        normalized = normalize_filter_criteria(
            admin_area,
            record.criteria,
            active_scope=active_scope,
            filter_key=record.filter_key,
        )
        await AuditService(AuditRepository(session)).record_admin_filter_restore(
            principal=principal,
            active_scope=active_scope,
            admin_area=admin_area,
            filter_id=str(filter_id),
            outcome="allowed",
            reason_category="validated",
        )
    except Exception as exc:
        record_admin_shell_audit_failure(
            action="saved_filter_restore",
            reason=exc.__class__.__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="saved filter restore could not be audited",
        ) from exc
    profile = filter_profiles()[admin_area]
    redirect_to = with_scope_query(profile.destination_href, active_scope)
    for key, value in normalized.criteria.items():
        redirect_to = with_scope_query(
            f"{redirect_to}&{key}={value}"
            if "?" in redirect_to
            else f"{redirect_to}?{key}={value}",
            active_scope,
        )
    return RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/admin/filters/{admin_area}/{filter_id}", response_class=HTMLResponse)
@router.delete("/admin/filters/{admin_area}/{filter_id}", response_class=HTMLResponse)
async def delete_saved_filter(
    admin_area: str,
    filter_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    return_to: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    await AdminSavedFilterRepository(session).delete_filter(
        principal=principal,
        admin_area=admin_area,
        scope=active_scope,
        filter_id=filter_id,
    )
    redirect_to = with_scope_query(
        safe_redirect_target(return_to, fallback=f"/admin/filters/{admin_area}"),
        active_scope,
    )
    return RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)
