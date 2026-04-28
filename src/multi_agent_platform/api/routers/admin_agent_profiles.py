from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.agents.resolution import AgentProfileResolutionError
from multi_agent_platform.agents.service import (
    AgentProfileActivationError,
    AgentProfileGrantError,
    AgentProfileService,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.agent_profiles import (
    ActivationRequest,
    AuditEventSummary,
    HistoryResponse,
    ProfileCreate,
    ProfileDraftDetail,
    ProfileDraftSave,
    ProfileResolveRequest,
    ProfileResolveResponse,
    ProfileSummary,
    ProfileVersionDetail,
    RetireRequest,
    TenantGrantRequest,
    TenantGrantResponse,
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
from multi_agent_platform.db.repositories.prompts import PromptRepository
from multi_agent_platform.tenancy.guards import (
    ScopeError,
    require_workflow_scope_access,
)

router = APIRouter(tags=["agent-runtime-profiles"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _attr(obj: object, name: str, default: object | None = None) -> Any:
    return getattr(obj, name, default)


def _profile_template_context(
    *,
    shell: object,
    principal: PrincipalContext,
    page: object,
    **extra: object,
) -> dict[str, object]:
    context = {"shell": shell, "principal": principal, "page": page}
    context.update(extra)
    return context


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


def _is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def _require_profile_scope_mutation(
    principal: PrincipalContext,
    *,
    scope_type: str,
    tenant_id: UUID | None,
) -> None:
    try:
        require_workflow_scope_access(
            principal,
            scope_type=scope_type,
            tenant_id=tenant_id,
        )
    except ScopeError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "profile_scope_denied", "message": str(exc)},
        ) from exc


def _assert_query_tenant_allowed(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> UUID | None:
    if tenant_id is None:
        return principal.tenant_id
    if _is_platform_admin(principal) or principal.tenant_id == tenant_id:
        return tenant_id
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": "tenant_scope_denied"},
    )


def _parse_optional_uuid(value: str | None) -> UUID | None:
    if value is None or not value.strip():
        return None
    return UUID(value)


def _load_json_array(raw: str, field_name: str) -> list[object]:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "invalid_json", "field": field_name},
        ) from exc
    if not isinstance(value, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "invalid_json_type", "field": field_name},
        )
    return value


def _load_json_object(raw: str, field_name: str) -> dict[str, object]:
    try:
        value = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "invalid_json", "field": field_name},
        ) from exc
    if not isinstance(value, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "invalid_json_type", "field": field_name},
        )
    return {str(key): value for key, value in value.items()}


def _parse_grant_tenant_ids(raw_value: str) -> list[UUID]:
    return [UUID(value.strip()) for value in raw_value.split(",") if value.strip()]


def _profile_validation_response(
    validation: object | None,
) -> ValidationResult | None:
    if validation is None:
        return None
    return ValidationResult(
        validation_result_id=_attr(
            validation,
            "agent_profile_validation_result_id",
            None,
        ),
        status="passed" if _attr(validation, "status") == "passed" else "failed",
        blocking_issue_count=int(_attr(validation, "blocking_issue_count", 0)),
        advisory_issue_count=int(_attr(validation, "advisory_issue_count", 0)),
        findings=[
            ValidationFinding(
                code=str(finding.get("code", "validation")),
                severity=(
                    "blocking" if finding.get("severity") == "blocking" else "advisory"
                ),
                message=str(finding.get("message", "Validation issue")),
                section=str(finding.get("section", "profile")),
            )
            for finding in _attr(validation, "findings_json", []) or []
        ],
    )


def _profile_draft_detail(
    *,
    draft: object,
    revision: object | None,
    validation: object | None,
) -> ProfileDraftDetail:
    return ProfileDraftDetail(
        agent_runtime_profile_id=_attr(draft, "agent_runtime_profile_id"),
        agent_profile_draft_id=_attr(draft, "agent_profile_draft_id"),
        current_revision_number=_attr(draft, "current_revision_number"),
        purpose=_attr(revision, "purpose", None),
        prompt_references=_attr(revision, "prompt_references_json", []) or [],
        model_routing_hints=_attr(revision, "model_routing_hints_json", {}) or {},
        memory_scope_policy=_attr(revision, "memory_scope_policy_json", {}) or {},
        skill_requirements=_attr(revision, "skill_requirements_json", []) or [],
        tool_policy_expectations=_attr(
            revision,
            "tool_policy_expectations_json",
            [],
        )
        or [],
        output_contract_expectations=_attr(
            revision,
            "output_contract_expectations_json",
            {},
        )
        or {},
        test_suite_requirements=_attr(
            revision,
            "test_suite_requirements_json",
            [],
        )
        or [],
        latest_validation=_profile_validation_response(validation),
    )


def _profile_summary(
    profile: object,
    validation: object | None,
) -> ProfileSummary:
    return ProfileSummary(
        agent_runtime_profile_id=_attr(profile, "agent_runtime_profile_id"),
        scope_type=_attr(profile, "scope_type"),
        tenant_id=_attr(profile, "tenant_id"),
        agent_key=_attr(profile, "agent_key"),
        agent_kind=_attr(profile, "agent_kind"),
        display_name=_attr(profile, "display_name"),
        purpose=_attr(profile, "purpose"),
        status=_attr(profile, "status"),
        active_profile_version_id=_attr(profile, "active_profile_version_id", None),
        validation_status=_attr(validation, "status", None),
    )


def _profile_version_detail(version: object) -> ProfileVersionDetail:
    return ProfileVersionDetail(
        agent_profile_version_id=_attr(version, "agent_profile_version_id"),
        agent_runtime_profile_id=_attr(version, "agent_runtime_profile_id"),
        agent_key=_attr(version, "agent_key"),
        agent_kind=_attr(version, "agent_kind"),
        display_version=_attr(version, "display_version"),
        status=_attr(version, "status"),
        safe_summary=_attr(version, "safe_summary_json", {}) or {},
    )


def _profile_submitted_fields(
    *,
    shell: object,
    profile: object | None = None,
    revision: object | None = None,
) -> dict[str, object]:
    active_scope = shell.active_scope  # type: ignore[attr-defined]
    return {
        "scope_type": _attr(profile, "scope_type", active_scope.scope_type),
        "tenant_id": str(_attr(profile, "tenant_id", active_scope.tenant_id) or ""),
        "agent_key": _attr(profile, "agent_key", ""),
        "agent_kind": _attr(profile, "agent_kind", "agent"),
        "display_name": _attr(profile, "display_name", ""),
        "purpose": _attr(revision, "purpose", _attr(profile, "purpose", "")),
        "prompt_references_json": json.dumps(
            _attr(revision, "prompt_references_json", []) or [],
            indent=2,
        ),
        "model_routing_hints_json": json.dumps(
            _attr(revision, "model_routing_hints_json", {}) or {},
            indent=2,
        ),
        "memory_scope_policy_json": json.dumps(
            _attr(revision, "memory_scope_policy_json", {}) or {},
            indent=2,
        ),
        "skill_requirements_json": json.dumps(
            _attr(revision, "skill_requirements_json", []) or [],
            indent=2,
        ),
        "tool_policy_expectations_json": json.dumps(
            _attr(revision, "tool_policy_expectations_json", []) or [],
            indent=2,
        ),
        "output_contract_expectations_json": json.dumps(
            _attr(revision, "output_contract_expectations_json", {}) or {},
            indent=2,
        ),
        "test_suite_requirements_json": json.dumps(
            _attr(revision, "test_suite_requirements_json", []) or [],
            indent=2,
        ),
    }


def _profile_payloads_from_form(
    *,
    scope_type: str,
    tenant_id: UUID | None,
    agent_key: str,
    agent_kind: str,
    display_name: str,
    purpose: str,
    expected_revision_number: int,
    prompt_references_json: str,
    model_routing_hints_json: str,
    memory_scope_policy_json: str,
    skill_requirements_json: str,
    tool_policy_expectations_json: str,
    output_contract_expectations_json: str,
    test_suite_requirements_json: str,
) -> tuple[ProfileCreate, ProfileDraftSave]:
    create_payload = ProfileCreate(
        scope_type=scope_type,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        agent_key=agent_key,
        agent_kind=agent_kind,  # type: ignore[arg-type]
        display_name=display_name,
        purpose=purpose,
    )
    draft_payload = ProfileDraftSave(
        expected_revision_number=expected_revision_number,
        purpose=purpose,
        prompt_references=[
            dict(item)
            for item in _load_json_array(
                prompt_references_json,
                "prompt_references_json",
            )
            if isinstance(item, dict)
        ],
        model_routing_hints=_load_json_object(
            model_routing_hints_json,
            "model_routing_hints_json",
        ),
        memory_scope_policy=_load_json_object(
            memory_scope_policy_json,
            "memory_scope_policy_json",
        ),
        skill_requirements=[
            dict(item)
            for item in _load_json_array(
                skill_requirements_json,
                "skill_requirements_json",
            )
            if isinstance(item, dict)
        ],
        tool_policy_expectations=[
            dict(item)
            for item in _load_json_array(
                tool_policy_expectations_json,
                "tool_policy_expectations_json",
            )
            if isinstance(item, dict)
        ],
        output_contract_expectations=_load_json_object(
            output_contract_expectations_json,
            "output_contract_expectations_json",
        ),
        test_suite_requirements=[
            dict(item)
            for item in _load_json_array(
                test_suite_requirements_json,
                "test_suite_requirements_json",
            )
            if isinstance(item, dict)
        ],
    )
    return create_payload, draft_payload


@router.get("/admin/prompt-runtime/profiles", response_class=HTMLResponse)
async def agent_profiles_index(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = AgentProfileRepository(session)
    profiles = await repository.list_visible_profiles(
        principal_tenant_id=principal.tenant_id,
        include_platform_admin=_is_platform_admin(principal),
    )
    items: list[ProfileSummary] = []
    for profile in profiles:
        draft = await repository.get_active_draft(profile.agent_runtime_profile_id)
        validation = None
        if draft is not None:
            validation = await repository.get_validation_result(
                draft.last_validation_result_id
            )
        items.append(_profile_summary(profile, validation))
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
            items=items,
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
            page=build_agent_profile_ui_model(
                title="New Agent Profile",
                scope_type=shell.active_scope.scope_type,
                tenant_id=shell.active_scope.tenant_id,
                submitted_fields=_profile_submitted_fields(shell=shell),
            ),
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
    repository = AgentProfileRepository(session)
    profile = await repository.get_profile(agent_runtime_profile_id)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if profile is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=profile.scope_type,
        tenant_id=profile.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    validation = await repository.get_validation_result(draft.last_validation_result_id)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Edit Agent Profile",
    )
    submitted_fields = _profile_submitted_fields(
        shell=shell,
        profile=profile,
        revision=revision,
    )
    submitted_fields["current_revision_number"] = draft.current_revision_number
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "agent_profiles/edit.html",
        _profile_template_context(
            shell=shell,
            principal=principal,
            page=build_agent_profile_ui_model(
                title="Edit Agent Profile",
                scope_type=profile.scope_type,
                tenant_id=profile.tenant_id,
                agent_runtime_profile_id=agent_runtime_profile_id,
                agent_key=profile.agent_key,
                agent_kind=profile.agent_kind,
                validation_status=_attr(validation, "status", None),
                findings=_attr(validation, "findings_json", None),
                submitted_fields=submitted_fields,
            ),
            draft=revision,
            validation=_profile_validation_response(validation),
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
    repository = AgentProfileRepository(session)
    version = await repository.get_profile_version(agent_profile_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    grants = await repository.list_grants_for_version(agent_profile_version_id)
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
            page=build_agent_profile_ui_model(
                title="Agent Profile Version",
                scope_type=version.scope_type,
                tenant_id=version.tenant_id,
                agent_key=version.agent_key,
                agent_kind=version.agent_kind,
                agent_profile_version_id=agent_profile_version_id,
                status=version.status,
            ),
            version=_profile_version_detail(version),
            grants=grants,
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
    repository = AgentProfileRepository(session)
    profile = await repository.get_profile(agent_runtime_profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=profile.scope_type,
        tenant_id=profile.tenant_id,
    )
    history = HistoryResponse(
        items=[
            AuditEventSummary.model_validate(event)
            for event in await repository.list_profile_history(
                agent_runtime_profile_id=agent_runtime_profile_id,
                tenant_id=(
                    None if _is_platform_admin(principal) else principal.tenant_id
                ),
            )
        ]
    )
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
            history=history,
        ),
    )


@router.get("/admin/prompt-runtime/profiles/resolve", response_class=HTMLResponse)
async def agent_profiles_resolve(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Query()] = None,
    agent_key: Annotated[str | None, Query(max_length=128)] = None,
    agent_kind: Annotated[str, Query()] = "agent",
) -> HTMLResponse:
    resolved_tenant_id = _assert_query_tenant_allowed(principal, tenant_id)
    resolution: ProfileResolveResponse | None = None
    if resolved_tenant_id is not None and agent_key:
        try:
            result = await AgentProfileService(
                AgentProfileRepository(session)
            ).resolve_profile(
                tenant_id=resolved_tenant_id,
                agent_key=agent_key,
                agent_kind=agent_kind,
            )
            resolution = ProfileResolveResponse(
                resolved=True,
                selected_profile_version_id=result.selected_profile_version_id,
                source_scope=result.source_scope,  # type: ignore[arg-type]
                considered_profile_version_ids=list(
                    result.considered_profile_version_ids
                ),
            )
        except AgentProfileResolutionError as exc:
            resolution = ProfileResolveResponse(
                resolved=False,
                blocking_issues=[
                    ValidationFinding(
                        code="profile_resolution_failed",
                        severity="blocking",
                        message=str(exc),
                        section="resolution",
                    )
                ],
            )
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
            page=build_agent_profile_ui_model(
                title="Profile Resolution",
                scope_type=shell.active_scope.scope_type,
                tenant_id=shell.active_scope.tenant_id,
                agent_key=agent_key or "",
                agent_kind=agent_kind,
            ),
            resolution=resolution,
            resolve_tenant_id=resolved_tenant_id,
        ),
    )


@router.post("/admin/prompt-runtime/profiles/form", response_class=HTMLResponse)
async def agent_profile_form(
    principal: PrincipalDep,
    session: SessionDep,
    action: Annotated[str, Form(alias="_action")] = "save",
    agent_runtime_profile_id_value: Annotated[
        str,
        Form(alias="agent_runtime_profile_id"),
    ] = "",
    agent_profile_version_id_value: Annotated[
        str,
        Form(alias="agent_profile_version_id"),
    ] = "",
    scope_type: Annotated[str, Form()] = "tenant",
    tenant_id_value: Annotated[str, Form(alias="tenant_id")] = "",
    agent_key: Annotated[str, Form()] = "",
    agent_kind: Annotated[str, Form()] = "agent",
    display_name: Annotated[str, Form()] = "",
    purpose: Annotated[str, Form()] = "",
    prompt_references_json: Annotated[str, Form()] = "[]",
    model_routing_hints_json: Annotated[str, Form()] = "{}",
    memory_scope_policy_json: Annotated[str, Form()] = "{}",
    skill_requirements_json: Annotated[str, Form()] = "[]",
    tool_policy_expectations_json: Annotated[str, Form()] = "[]",
    output_contract_expectations_json: Annotated[str, Form()] = "{}",
    test_suite_requirements_json: Annotated[str, Form()] = "[]",
    expected_revision_number: Annotated[int, Form()] = 0,
    reason: Annotated[str, Form()] = "Updated from admin UI",
    grant_tenant_ids: Annotated[str, Form()] = "",
) -> RedirectResponse:
    repository = AgentProfileRepository(session)
    service = AgentProfileService(repository)
    agent_runtime_profile_id = _parse_optional_uuid(agent_runtime_profile_id_value)
    agent_profile_version_id = _parse_optional_uuid(agent_profile_version_id_value)

    if action == "activate":
        if agent_runtime_profile_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "missing_agent_runtime_profile_id"},
            )
        profile = await repository.get_profile(agent_runtime_profile_id)
        draft = await repository.get_active_draft(agent_runtime_profile_id)
        if profile is None or draft is None:
            raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
        _require_profile_scope_mutation(
            principal,
            scope_type=profile.scope_type,
            tenant_id=profile.tenant_id,
        )
        revision = await repository.get_latest_revision(draft)
        validation = await repository.get_validation_result(
            draft.last_validation_result_id
        )
        if revision is None or validation is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "missing_validation"},
            )
        try:
            activated_version = await service.activate(
                profile=profile,
                draft=draft,
                draft_revision=revision,
                validation_result=validation,
                principal_id=principal.principal_id,
                reason=reason,
            )
        except AgentProfileActivationError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "stale_validation"},
            ) from exc
        return RedirectResponse(
            "/admin/prompt-runtime/profiles/versions/"
            f"{activated_version.agent_profile_version_id}?flash=profile-activated",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if action in {"retire", "grant"}:
        if agent_profile_version_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "missing_agent_profile_version_id"},
            )
        target_version = await repository.get_profile_version(agent_profile_version_id)
        if target_version is None:
            raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
        _require_profile_scope_mutation(
            principal,
            scope_type=target_version.scope_type,
            tenant_id=target_version.tenant_id,
        )
        if action == "retire":
            await service.retire_version(
                version=target_version,
                principal_id=principal.principal_id,
                reason=reason,
            )
            flash = "profile-retired"
        else:
            for grant_tenant_id in _parse_grant_tenant_ids(grant_tenant_ids):
                try:
                    await service.grant_version_to_tenant(
                        version=target_version,
                        tenant_id=grant_tenant_id,
                        principal_id=principal.principal_id,
                        reason=reason,
                    )
                except AgentProfileGrantError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={"code": "grant_not_allowed"},
                    ) from exc
            flash = "profile-granted"
        return RedirectResponse(
            "/admin/prompt-runtime/profiles/versions/"
            f"{agent_profile_version_id}?flash={flash}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    form_tenant_id = _parse_optional_uuid(tenant_id_value)
    create_payload, draft_payload = _profile_payloads_from_form(
        scope_type=scope_type,
        tenant_id=form_tenant_id,
        agent_key=agent_key,
        agent_kind=agent_kind,
        display_name=display_name,
        purpose=purpose,
        expected_revision_number=expected_revision_number,
        prompt_references_json=prompt_references_json,
        model_routing_hints_json=model_routing_hints_json,
        memory_scope_policy_json=memory_scope_policy_json,
        skill_requirements_json=skill_requirements_json,
        tool_policy_expectations_json=tool_policy_expectations_json,
        output_contract_expectations_json=output_contract_expectations_json,
        test_suite_requirements_json=test_suite_requirements_json,
    )
    if agent_runtime_profile_id is None:
        _require_profile_scope_mutation(
            principal,
            scope_type=create_payload.scope_type,
            tenant_id=create_payload.tenant_id,
        )
        created = await service.create_profile(
            scope_type=create_payload.scope_type,
            tenant_id=create_payload.tenant_id,
            agent_key=create_payload.agent_key,
            agent_kind=create_payload.agent_kind,
            display_name=create_payload.display_name,
            purpose=create_payload.purpose,
            principal_id=principal.principal_id,
        )
        profile = created.profile
        draft = created.draft
    else:
        profile = await repository.get_profile(agent_runtime_profile_id)
        draft = await repository.get_active_draft(agent_runtime_profile_id)
        if profile is None or draft is None:
            raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
        _require_profile_scope_mutation(
            principal,
            scope_type=profile.scope_type,
            tenant_id=profile.tenant_id,
        )
    try:
        revision = await service.save_draft_revision(
            draft=draft,
            expected_revision_number=draft_payload.expected_revision_number,
            purpose=draft_payload.purpose,
            prompt_references=draft_payload.prompt_references,
            model_routing_hints=draft_payload.model_routing_hints,
            memory_scope_policy=draft_payload.memory_scope_policy,
            skill_requirements=draft_payload.skill_requirements,
            tool_policy_expectations=draft_payload.tool_policy_expectations,
            output_contract_expectations=draft_payload.output_contract_expectations,
            test_suite_requirements=draft_payload.test_suite_requirements,
            principal_id=principal.principal_id,
        )
    except StaleAgentProfileRevisionError as exc:
        raise HTTPException(status_code=409, detail={"code": "stale_revision"}) from exc

    if action == "validate":
        await service.validate_revision(
            draft_revision=revision,
            principal_id=principal.principal_id,
        )
        flash = "profile-validated"
    else:
        flash = "profile-saved"
    return RedirectResponse(
        "/admin/prompt-runtime/profiles/"
        f"{profile.agent_runtime_profile_id}/edit?flash={flash}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/admin/prompt-runtime/api/profiles",
    response_model=dict[str, list[ProfileSummary]],
)
async def list_agent_profiles(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Query()] = None,
    agent_key: Annotated[str | None, Query(max_length=128)] = None,
    agent_kind: Annotated[str | None, Query()] = None,
) -> dict[str, list[ProfileSummary]]:
    visible_tenant_id = _assert_query_tenant_allowed(principal, tenant_id)
    repository = AgentProfileRepository(session)
    profiles = await repository.list_visible_profiles(
        principal_tenant_id=visible_tenant_id,
        include_platform_admin=_is_platform_admin(principal),
        agent_key=agent_key,
        agent_kind=agent_kind,
    )
    items: list[ProfileSummary] = []
    for profile in profiles:
        draft = await repository.get_active_draft(profile.agent_runtime_profile_id)
        validation = None
        if draft is not None:
            validation = await repository.get_validation_result(
                draft.last_validation_result_id
            )
        items.append(_profile_summary(profile, validation))
    return {"items": items}


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
    _require_profile_scope_mutation(
        principal,
        scope_type=payload.scope_type,
        tenant_id=payload.tenant_id,
    )
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
    profile = await repository.get_profile(agent_runtime_profile_id)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if profile is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=profile.scope_type,
        tenant_id=profile.tenant_id,
    )
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
    profile = await repository.get_profile(agent_runtime_profile_id)
    draft = await repository.get_active_draft(agent_runtime_profile_id)
    if profile is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=profile.scope_type,
        tenant_id=profile.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    validation = await AgentProfileService(repository).validate_revision(
        draft_revision=revision,
        principal_id=principal.principal_id,
    )
    return ValidationResult(
        validation_result_id=validation.agent_profile_validation_result_id,
        status="passed" if validation.status == "passed" else "failed",
        blocking_issue_count=validation.blocking_issue_count,
        advisory_issue_count=validation.advisory_issue_count,
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
    _require_profile_scope_mutation(
        principal,
        scope_type=profile.scope_type,
        tenant_id=profile.tenant_id,
    )
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
    return _profile_version_detail(version)


@router.post(
    "/admin/prompt-runtime/api/profiles/versions/{agent_profile_version_id}/retire",
    response_model=ProfileVersionDetail,
)
async def retire_agent_profile_version(
    agent_profile_version_id: UUID,
    payload: RetireRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ProfileVersionDetail:
    repository = AgentProfileRepository(session)
    version = await repository.get_profile_version(agent_profile_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    retired = await AgentProfileService(repository).retire_version(
        version=version,
        principal_id=principal.principal_id,
        reason=payload.reason,
    )
    return _profile_version_detail(retired)


@router.post(
    "/admin/prompt-runtime/api/profiles/versions/{agent_profile_version_id}/grants",
    response_model=TenantGrantResponse,
)
async def grant_agent_profile_version(
    agent_profile_version_id: UUID,
    payload: TenantGrantRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> TenantGrantResponse:
    repository = AgentProfileRepository(session)
    version = await repository.get_profile_version(agent_profile_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "profile_not_found"})
    _require_profile_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    service = AgentProfileService(repository)
    granted = []
    for tenant_id in payload.tenant_ids:
        try:
            grant = await service.grant_version_to_tenant(
                version=version,
                tenant_id=tenant_id,
                principal_id=principal.principal_id,
                reason=payload.reason,
            )
        except AgentProfileGrantError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "grant_not_allowed"},
            ) from exc
        granted.append(grant.grantee_tenant_id)
    return TenantGrantResponse(granted_tenant_ids=granted)


@router.post(
    "/admin/prompt-runtime/api/resolve-profile",
    response_model=ProfileResolveResponse,
)
async def resolve_agent_profile(
    payload: ProfileResolveRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ProfileResolveResponse:
    _assert_query_tenant_allowed(principal, payload.tenant_id)
    try:
        resolution = await AgentProfileService(
            AgentProfileRepository(session)
        ).resolve_profile(
            tenant_id=payload.tenant_id,
            agent_key=payload.agent_key,
            agent_kind=payload.agent_kind,
        )
    except AgentProfileResolutionError as exc:
        return ProfileResolveResponse(
            resolved=False,
            blocking_issues=[
                ValidationFinding(
                    code="profile_resolution_failed",
                    severity="blocking",
                    message=str(exc),
                    section="resolution",
                )
            ],
        )
    return ProfileResolveResponse(
        resolved=True,
        selected_profile_version_id=resolution.selected_profile_version_id,
        source_scope=resolution.source_scope,  # type: ignore[arg-type]
        considered_profile_version_ids=list(resolution.considered_profile_version_ids),
    )


@router.get(
    "/admin/prompt-runtime/api/history",
    response_model=HistoryResponse,
    tags=["prompt-runtime-audit"],
)
async def list_prompt_runtime_history(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Query()] = None,
    resource_kind: Annotated[str | None, Query()] = None,
    resource_id: Annotated[UUID | None, Query()] = None,
) -> HistoryResponse:
    visible_tenant_id = _assert_query_tenant_allowed(principal, tenant_id)
    if _is_platform_admin(principal) and tenant_id is None:
        visible_tenant_id = None
    events: list[dict[str, object]] = []
    if resource_kind in (None, "prompt"):
        events.extend(
            await PromptRepository(session).list_prompt_history(
                prompt_lineage_id=resource_id if resource_kind == "prompt" else None,
                tenant_id=visible_tenant_id,
            )
        )
    if resource_kind in (None, "profile"):
        events.extend(
            await AgentProfileRepository(session).list_profile_history(
                agent_runtime_profile_id=resource_id
                if resource_kind == "profile"
                else None,
                tenant_id=visible_tenant_id,
            )
        )
    return HistoryResponse(
        items=[
            AuditEventSummary.model_validate(event)
            for event in sorted(
                events,
                key=lambda item: cast(datetime, item["created_at"]),
                reverse=True,
            )[:100]
        ]
    )
