from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.ui.admin_console import BreadcrumbItem
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.skill_execution.adapters import DAILY_BRIEFING_TOOL_NAMES
from multi_agent_platform.skill_execution.gateway import SkillExecutionGateway
from multi_agent_platform.skill_execution.policies import SkillExecutionPolicyBundle
from multi_agent_platform.skill_execution.schemas import (
    SkillToolDiagnosticRecord,
    SkillToolExecutionResult,
)

router = APIRouter(prefix="/admin/skill-execution", tags=["skill-execution"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
DEFAULT_QA_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")


class SkillToolDiagnosticsResponse(BaseModel):
    items: tuple[SkillToolDiagnosticRecord, ...]


class RunSkillToolDiagnosticsRequest(BaseModel):
    tenant_id: UUID | None = None
    tool_names: tuple[str, ...] = Field(default_factory=tuple)


class RunSkillToolDiagnosticsResponse(BaseModel):
    items: tuple[SkillToolExecutionResult, ...]


@router.get(
    "/api/diagnostics",
    response_model=SkillToolDiagnosticsResponse,
)
async def list_skill_tool_diagnostics(
    request: Request,
    principal: PrincipalDep,
) -> SkillToolDiagnosticsResponse:
    tenant_id = _tenant_id_for_request(request, principal)
    gateway = _gateway_for_tenant(tenant_id)
    await gateway.run_mock_diagnostics(
        tenant_id=tenant_id, actor_id=principal.principal_id
    )
    return SkillToolDiagnosticsResponse(items=gateway.diagnostic_records())


@router.post(
    "/api/diagnostics/run",
    response_model=RunSkillToolDiagnosticsResponse,
)
async def run_skill_tool_diagnostics(
    payload: RunSkillToolDiagnosticsRequest,
    principal: PrincipalDep,
) -> RunSkillToolDiagnosticsResponse:
    tenant_id = payload.tenant_id or principal.tenant_id or DEFAULT_QA_TENANT_ID
    tool_names = payload.tool_names or DAILY_BRIEFING_TOOL_NAMES
    unknown = sorted(set(tool_names) - set(DAILY_BRIEFING_TOOL_NAMES))
    if unknown:
        raise HTTPException(status_code=422, detail={"unknown_tools": unknown})
    gateway = _gateway_for_tenant(tenant_id)
    results = await gateway.run_mock_diagnostics(
        tenant_id=tenant_id,
        actor_id=principal.principal_id,
        tool_names=tool_names,
    )
    return RunSkillToolDiagnosticsResponse(items=results)


@router.get(
    "/ui/diagnostics",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_tool_diagnostics_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    tenant_id = _tenant_id_for_request(request, principal)
    gateway = _gateway_for_tenant(tenant_id)
    results = await gateway.run_mock_diagnostics(
        tenant_id=tenant_id,
        actor_id=principal.principal_id,
    )
    records = gateway.diagnostic_records()
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Skill Tool Diagnostics",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Skill Tool Diagnostics",
                href="/admin/skill-execution/ui/diagnostics",
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_execution/diagnostics.html",
        {
            "principal": principal,
            "shell": shell,
            "tenant_id": tenant_id,
            "records": records,
            "results": results,
        },
    )


def _tenant_id_for_request(request: Request, principal: PrincipalContext) -> UUID:
    query_tenant_id = request.query_params.get("tenant_id")
    if query_tenant_id:
        return UUID(query_tenant_id)
    return principal.tenant_id or DEFAULT_QA_TENANT_ID


def _gateway_for_tenant(tenant_id: UUID) -> SkillExecutionGateway:
    return SkillExecutionGateway(
        policy_bundle=SkillExecutionPolicyBundle.local_qa_default(tenant_id=tenant_id)
    )
