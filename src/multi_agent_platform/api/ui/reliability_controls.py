from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext

router = APIRouter(prefix="/admin/reliability/ui", tags=["reliability-ui"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SEE_OTHER = status.HTTP_303_SEE_OTHER
RELIABILITY_QUERY_KEYS = frozenset(
    {"tenant_id", "state", "status", "failure_category", "saved_filter_id"}
)


def reliability_breakers_filter_profile() -> FilterProfile:
    return filter_profiles()["reliability_breakers"]


def reliability_dead_letters_filter_profile() -> FilterProfile:
    return filter_profiles()["reliability_dead_letters"]


@router.get("/", response_model=None)
async def reliability_dashboard_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = (principal, session)
    return _react_redirect(request, panel="reliability")


@router.get("/breakers", response_model=None)
async def reliability_breakers_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = (principal, session)
    return _react_redirect(request, panel="breakers")


@router.get("/dead-letters", response_model=None)
async def reliability_dead_letters_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = (principal, session)
    return _react_redirect(request, panel="dead-letters")


def _react_redirect(request: Request, *, panel: str) -> RedirectResponse:
    query = {
        key: value
        for key, value in request.query_params.items()
        if key in RELIABILITY_QUERY_KEYS and value
    }
    query["panel"] = panel
    return RedirectResponse(
        f"/admin/app/operations?{urlencode(query)}",
        status_code=SEE_OTHER,
    )
