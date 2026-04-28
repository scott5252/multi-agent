from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.routers.admin_console import (
    build_shell_for_request,
    resolve_scope_for_request,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    FilterProfile,
    build_common_state,
    build_saved_filter_summary,
    filter_profiles,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.repositories.admin_console import (
    AdminSavedFilterRepository,
)

router = APIRouter(prefix="/admin/reliability/ui", tags=["reliability-ui"])
templates = Jinja2Templates(directory=str(Settings().web_admin_templates_dir))
SessionDep = Annotated[AsyncSession, Depends(get_session)]
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]


def reliability_template(name: str) -> Path:
    return Settings().web_admin_templates_dir / "reliability" / name


def reliability_breakers_filter_profile() -> FilterProfile:
    return filter_profiles()["reliability_breakers"]


def reliability_dead_letters_filter_profile() -> FilterProfile:
    return filter_profiles()["reliability_dead_letters"]


@router.get("/", response_class=HTMLResponse)
async def reliability_dashboard_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Reliability",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Reliability", href="/admin/reliability/ui/"),
        ),
    )
    return templates.TemplateResponse(
        request,
        "reliability/index.html",
        {"title": "Reliability", "principal": principal, "shell": shell},
    )


@router.get("/breakers", response_class=HTMLResponse)
async def reliability_breakers_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> HTMLResponse:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    records = await AdminSavedFilterRepository(session).list_filters(
        principal=principal,
        admin_area="reliability_breakers",
        scope=active_scope,
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Circuit Breakers",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Reliability", href="/admin/reliability/ui/"),
            BreadcrumbItem(label="Circuit Breakers", href=request.url.path),
        ),
        common_state=build_common_state(
            CommonStateType.EMPTY,
            title="No breaker records",
            summary="No circuit breaker records are visible in this scope.",
            trace_id=principal.trace_id,
        ),
        saved_filters=tuple(
            build_saved_filter_summary(record, active_scope=active_scope)
            for record in records
        ),
    )
    return templates.TemplateResponse(
        request,
        "reliability/breakers.html",
        {"title": "Circuit Breakers", "principal": principal, "shell": shell},
    )


@router.get("/dead-letters", response_class=HTMLResponse)
async def reliability_dead_letters_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> HTMLResponse:
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    records = await AdminSavedFilterRepository(session).list_filters(
        principal=principal,
        admin_area="reliability_dead_letters",
        scope=active_scope,
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Dead Letters",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Reliability", href="/admin/reliability/ui/"),
            BreadcrumbItem(label="Dead Letters", href=request.url.path),
        ),
        common_state=build_common_state(
            CommonStateType.EMPTY,
            title="No dead-letter records",
            summary="No dead-letter records are visible in this scope.",
            trace_id=principal.trace_id,
        ),
        saved_filters=tuple(
            build_saved_filter_summary(record, active_scope=active_scope)
            for record in records
        ),
    )
    return templates.TemplateResponse(
        request,
        "reliability/dead_letters.html",
        {"title": "Dead Letters", "principal": principal, "shell": shell},
    )
