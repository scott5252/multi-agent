from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.agents.service import (
    AgentProfileActivationError,
    AgentProfileService,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.agent_profiles import (
    ActivationRequest,
    ProfileCreate,
    ProfileDraftDetail,
    ProfileDraftSave,
    ProfileSummary,
    ProfileVersionDetail,
    ValidationFinding,
    ValidationResult,
)
from multi_agent_platform.api.ui.agent_profiles import build_agent_profile_ui_model
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.agent_profiles import (
    AgentProfileRepository,
    StaleAgentProfileRevisionError,
)

router = APIRouter(tags=["agent-runtime-profiles"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _profile_template_context(
    *,
    shell: object,
    principal: PrincipalContext,
    page: object,
) -> dict[str, object]:
    return {"shell": shell, "principal": principal, "page": page}


def _profile_ui_page(
    *,
    title: str,
    shell: object,
    agent_runtime_profile_id: UUID | None = None,
    agent_profile_version_id: UUID | None = None,
    status_value: str = "draft",
) -> object:
    active_scope = shell.active_scope  # type: ignore[attr-defined]
    return build_agent_profile_ui_model(
        title=title,
        scope_type=active_scope.scope_type,
        tenant_id=active_scope.tenant_id,
        agent_runtime_profile_id=agent_runtime_profile_id,
        agent_profile_version_id=agent_profile_version_id,
        status=status_value,
    )


@router.get("/admin/prompt-runtime/profiles", response_class=HTMLResponse)
async def agent_profiles_index(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Agent Profiles",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/index.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(title="Agent Profiles", shell=shell),
        ),
    )


@router.get("/admin/prompt-runtime/profiles/new", response_class=HTMLResponse)
async def agent_profiles_new(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="New Agent Profile",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/edit.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(title="New Agent Profile", shell=shell),
        ),
    )


@router.get(
    "/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/edit",
    response_class=HTMLResponse,
)
async def agent_profiles_edit(
    agent_runtime_profile_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Edit Agent Profile",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/edit.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(
                title="Edit Agent Profile",
                shell=shell,
                agent_runtime_profile_id=agent_runtime_profile_id,
            ),
        ),
    )


@router.get(
    "/admin/prompt-runtime/profiles/versions/{agent_profile_version_id}",
    response_class=HTMLResponse,
)
async def agent_profiles_detail(
    agent_profile_version_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Agent Profile Version",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/detail.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(
                title="Agent Profile Version",
                shell=shell,
                agent_profile_version_id=agent_profile_version_id,
                status_value="active",
            ),
        ),
    )


@router.get(
    "/admin/prompt-runtime/profiles/{agent_runtime_profile_id}/history",
    response_class=HTMLResponse,
)
async def agent_profiles_history(
    agent_runtime_profile_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Agent Profile History",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/history.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(
                title="Agent Profile History",
                shell=shell,
                agent_runtime_profile_id=agent_runtime_profile_id,
            ),
        ),
    )


@router.get("/admin/prompt-runtime/profiles/resolve", response_class=HTMLResponse)
async def agent_profiles_resolve(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Profile Resolution",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/resolve.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=_profile_ui_page(title="Profile Resolution", shell=shell),
        ),
    )


@router.post("/admin/prompt-runtime/profiles/form", response_class=HTMLResponse)
async def agent_profile_form() -> RedirectResponse:
    return RedirectResponse(
        "/admin/prompt-runtime/profiles?flash=profile-saved",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/admin/prompt-runtime/api/profiles",
    response_model=dict[str, list[ProfileSummary]],
)
async def list_agent_profiles() -> dict[str, list[ProfileSummary]]:
    return {"items": []}


@router.post(
    "/admin/prompt-runtime/api/profiles",
    response_model=ProfileDraftDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_profile(
    payload: ProfileCreate,
    principal: PrincipalDep,
    session: SessionDep,
) -> ProfileDraftDetail:
    created = await AgentProfileRepository(session).create_profile_with_draft(
        scope_type=payload.scope_type,
        tenant_id=payload.tenant_id,
        agent_key=payload.agent_key,
        agent_kind=payload.agent_kind,
        display_name=payload.display_name,
        purpose=payload.purpose,
        principal_id=principal.principal_id,
    )
    return ProfileDraftDetail(
        agent_runtime_profile_id=created.profile.agent_runtime_profile_id,
        agent_profile_draft_id=created.draft.agent_profile_draft_id,
        current_revision_number=created.draft.current_revision_number,
    )


@router.put(
    "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft",
    response_model=ProfileDraftDetail,
)
async def save_agent_profile_draft(
    agent_runtime_profile_id: UUID,
    payload: ProfileDraftSave,
    principal: PrincipalDep,
    session: SessionDep,
) -> ProfileDraftDetail:
    repository = AgentProfileRepository(session)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    try:
        await AgentProfileService(repository).save_draft_revision(
            draft=draft,
            expected_revision_number=payload.expected_revision_number,
            purpose=payload.purpose,
            prompt_references=payload.prompt_references,
            model_routing_hints=payload.model_routing_hints,
            memory_scope_policy=payload.memory_scope_policy,
            skill_requirements=payload.skill_requirements,
            tool_policy_expectations=payload.tool_policy_expectations,
            output_contract_expectations=payload.output_contract_expectations,
            test_suite_requirements=payload.test_suite_requirements,
            principal_id=principal.principal_id,
        )
    except StaleAgentProfileRevisionError as exc:
        raise HTTPException(status_code=409, detail={"code": "stale_revision"}) from exc
    return ProfileDraftDetail(
        agent_runtime_profile_id=draft.agent_runtime_profile_id,
        agent_profile_draft_id=draft.agent_profile_draft_id,
        current_revision_number=draft.current_revision_number,
    )


@router.post(
    "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/validate",
    response_model=ValidationResult,
)
async def validate_agent_profile_draft(
    agent_runtime_profile_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> ValidationResult:
    repository = AgentProfileRepository(session)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    validation = await AgentProfileService(repository).validate_revision(
        draft_revision=revision,
        principal_id=principal.principal_id,
    )
    return ValidationResult(
        status="passed" if validation.status == "passed" else "failed",
        blocking_issue_count=validation.blocking_issue_count,
        findings=[
            ValidationFinding(
                code=str(finding["code"]),
                severity=(
                    "blocking" if finding.get("severity") == "blocking" else "advisory"
                ),
                message=str(finding["message"]),
                section=str(finding.get("section", "")),
            )
            for finding in validation.findings_json
        ],
    )


@router.post(
    "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/activate",
    response_model=ProfileVersionDetail,
    status_code=status.HTTP_201_CREATED,
)
async def activate_agent_profile(
    agent_runtime_profile_id: UUID,
    payload: ActivationRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ProfileVersionDetail:
    repository = AgentProfileRepository(session)
    profile = await repository.get_profile(agent_runtime_profile_id)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if profile is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    revision = await repository.get_latest_revision(draft)
    validation = await repository.get_validation_result(draft.last_validation_result_id)
    if revision is None or validation is None:
        raise HTTPException(status_code=409, detail={"code": "missing_validation"})
    try:
        version = await AgentProfileService(repository).activate(
            profile=profile,
            draft=draft,
            draft_revision=revision,
            validation_result=validation,
            principal_id=principal.principal_id,
            reason=payload.reason,
        )
    except AgentProfileActivationError as exc:
        raise HTTPException(
            status_code=409, detail={"code": "stale_validation"}
        ) from exc
    return ProfileVersionDetail.model_validate(version)
