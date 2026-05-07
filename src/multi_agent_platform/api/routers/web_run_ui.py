from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from multi_agent_platform.api.routers.channel_runs import (
    ChannelServiceDep,
    get_authorized_scope,
)
from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelType
from multi_agent_platform.channels.normalization import actor_from_scope
from multi_agent_platform.tenancy.context import ScopeContext

router = APIRouter(tags=["channels-ui"])
ScopeDep = Annotated[ScopeContext, Depends(get_authorized_scope)]


@router.get("/runs", response_model=None, include_in_schema=False)
async def runs_index(
    request: Request,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> RedirectResponse:
    _ = (scope, service)
    return _react_redirect(request, "/admin/app/channels/runs")


@router.get("/runs/new", response_model=None, include_in_schema=False)
async def runs_new(
    request: Request,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> RedirectResponse:
    _ = (scope, service)
    return _react_redirect(request, "/admin/app/channels/runs")


@router.get("/runs/{run_id}", response_model=None, include_in_schema=False)
async def run_detail(
    run_id: UUID,
    request: Request,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> RedirectResponse:
    actor = actor_from_scope(scope, channel_type=ChannelType.WEB_UI)
    try:
        service.get_status(actor=actor, run_id=run_id)
    except ChannelError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _react_redirect(request, f"/admin/app/channels/runs/{run_id}")


def _react_redirect(request: Request, destination: str) -> RedirectResponse:
    query = {
        key: value
        for key, value in request.query_params.items()
        if key in {"tenant_id", "cursor", "limit"} and value
    }
    suffix = f"?{urlencode(query)}" if query else ""
    return RedirectResponse(f"{destination}{suffix}", status_code=303)
