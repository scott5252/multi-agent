from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from multi_agent_platform.api.deps import ContainerDep
from multi_agent_platform.api.routers.channel_runs import (
    ChannelServiceDep,
    get_authorized_scope,
)
from multi_agent_platform.api.ui.run_details import build_run_details_model
from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelType
from multi_agent_platform.channels.normalization import actor_from_scope
from multi_agent_platform.tenancy.context import ScopeContext

router = APIRouter(tags=["channels-ui"])
ScopeDep = Annotated[ScopeContext, Depends(get_authorized_scope)]


@router.get("/runs", response_class=HTMLResponse, include_in_schema=False)
async def runs_index(
    request: Request,
    scope: ScopeDep,
    container: ContainerDep,
    service: ChannelServiceDep,
) -> HTMLResponse:
    actor = actor_from_scope(scope, channel_type=ChannelType.WEB_UI)
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "runs/index.html",
        {
            "runs": service.list_runs(actor),
            "principal_id": scope.principal_id,
        },
    )


@router.get("/runs/new", response_class=HTMLResponse, include_in_schema=False)
async def runs_new(
    request: Request,
    scope: ScopeDep,
    container: ContainerDep,
    service: ChannelServiceDep,
) -> HTMLResponse:
    actor = actor_from_scope(scope, channel_type=ChannelType.WEB_UI)
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "runs/index.html",
        {
            "runs": service.list_runs(actor),
            "principal_id": scope.principal_id,
            "show_form": True,
        },
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse, include_in_schema=False)
async def run_detail(
    run_id: UUID,
    request: Request,
    scope: ScopeDep,
    container: ContainerDep,
    service: ChannelServiceDep,
) -> HTMLResponse:
    actor = actor_from_scope(scope, channel_type=ChannelType.WEB_UI)
    try:
        status = service.get_status(actor=actor, run_id=run_id)
        timeline, _cursor = service.list_timeline(
            actor=actor,
            run_id=run_id,
            cursor=None,
            limit=100,
        )
        result = service.get_result(actor=actor, run_id=run_id)
        artifacts = service.list_artifacts(actor=actor, run_id=run_id)
    except ChannelError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    page = build_run_details_model(
        status=status,
        timeline=timeline,
        result=result,
        artifacts=artifacts,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "runs/detail.html",
        {
            "page": page,
            "principal_id": scope.principal_id,
        },
    )
