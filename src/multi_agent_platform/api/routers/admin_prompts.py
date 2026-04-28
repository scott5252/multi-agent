from __future__ import annotations

import json
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.prompts import (
    AuditEventSummary,
    FixtureValueSet,
    HistoryResponse,
    PromptDraftDetail,
    PromptDraftSave,
    PromptLineageCreate,
    PromptLineageSummary,
    PromptPreviewRequest,
    PromptPreviewResponse,
    PromptVersionDetail,
    PublishRequest,
    RetireRequest,
    TenantGrantRequest,
    TenantGrantResponse,
    ValidationFinding,
    ValidationResult,
)
from multi_agent_platform.api.schemas.prompts import (
    PromptVariableDeclaration as PromptVariableSchema,
)
from multi_agent_platform.api.ui.prompts import build_prompt_ui_model
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.prompts import (
    PromptRepository,
    StalePromptRevisionError,
)
from multi_agent_platform.prompts.models import (
    PromptVariableDeclaration as DomainPromptVariableDeclaration,
)
from multi_agent_platform.prompts.preview import PromptPreviewError, render_safe_preview
from multi_agent_platform.prompts.service import PromptPublishError, PromptService
from multi_agent_platform.tenancy.guards import (
    ScopeError,
    require_workflow_scope_access,
)

router = APIRouter(tags=["prompt-library"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
MAX_PROMPT_TEMPLATE_BYTES = 64 * 1024
MAX_FIXTURE_SET_COUNT = 20


def _attr(obj: object, name: str, default: object | None = None) -> Any:
    return getattr(obj, name, default)


def _prompt_template_context(
    *,
    shell: object,
    principal: PrincipalContext,
    page: object,
    **extra: object,
) -> dict[str, object]:
    context = {"shell": shell, "principal": principal, "page": page}
    context.update(extra)
    return context


def _prompt_ui_page(
    *,
    title: str,
    shell: object,
    prompt_lineage_id: UUID | None = None,
    prompt_version_id: UUID | None = None,
    status_value: str = "draft",
) -> object:
    active_scope = shell.active_scope  # type: ignore[attr-defined]
    return build_prompt_ui_model(
        title=title,
        scope_type=active_scope.scope_type,
        tenant_id=active_scope.tenant_id,
        prompt_lineage_id=prompt_lineage_id,
        prompt_version_id=prompt_version_id,
        status=status_value,
    )


def _is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def _require_prompt_scope_mutation(
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
            detail={"code": "prompt_scope_denied", "message": str(exc)},
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


def _prompt_validation_response(
    validation: object | None,
) -> ValidationResult | None:
    if validation is None:
        return None
    return ValidationResult(
        validation_result_id=_attr(validation, "prompt_validation_result_id", None),
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
                field=str(finding["field"]) if finding.get("field") else None,
            )
            for finding in _attr(validation, "findings_json", []) or []
        ],
    )


def _prompt_draft_detail(
    *,
    lineage: object,
    draft: object,
    revision: object | None,
    validation: object | None,
) -> PromptDraftDetail:
    variables = []
    fixture_sets = []
    if revision is not None:
        variables = [
            PromptVariableSchema.model_validate(variable)
            for variable in _attr(revision, "variable_declarations_json", []) or []
        ]
        fixture_sets = [
            FixtureValueSet.model_validate(fixture)
            for fixture in _attr(revision, "fixture_value_sets_json", []) or []
        ]
    return PromptDraftDetail(
        prompt_lineage_id=_attr(draft, "prompt_lineage_id"),
        prompt_draft_id=_attr(draft, "prompt_draft_id"),
        current_revision_number=_attr(draft, "current_revision_number"),
        prompt_title=_attr(revision, "prompt_title", None),
        purpose=_attr(revision, "purpose", _attr(lineage, "purpose", None)),
        usage_notes=_attr(revision, "usage_notes", ""),
        template_content=_attr(revision, "template_content", ""),
        variables=variables,
        fixture_sets=fixture_sets,
        latest_validation=_prompt_validation_response(validation),
    )


def _prompt_lineage_summary(
    lineage: object,
    validation: object | None,
) -> PromptLineageSummary:
    return PromptLineageSummary(
        prompt_lineage_id=_attr(lineage, "prompt_lineage_id"),
        scope_type=_attr(lineage, "scope_type"),
        tenant_id=_attr(lineage, "tenant_id"),
        slug=_attr(lineage, "slug"),
        display_name=_attr(lineage, "display_name"),
        purpose=_attr(lineage, "purpose"),
        status=_attr(lineage, "status"),
        latest_published_prompt_version_id=_attr(
            lineage,
            "latest_published_prompt_version_id",
            None,
        ),
        validation_status=_attr(validation, "status", None),
    )


def _prompt_version_detail(version: object) -> PromptVersionDetail:
    return PromptVersionDetail(
        prompt_version_id=_attr(version, "prompt_version_id"),
        prompt_lineage_id=_attr(version, "prompt_lineage_id"),
        display_version=_attr(version, "display_version"),
        status=_attr(version, "status"),
        template_content_sha256=_attr(version, "template_content_sha256"),
        safe_summary=_attr(version, "safe_summary_json", {}) or {},
    )


def _prompt_submitted_fields(
    *,
    shell: object,
    lineage: object | None = None,
    revision: object | None = None,
) -> dict[str, object]:
    active_scope = shell.active_scope  # type: ignore[attr-defined]
    variables = _attr(revision, "variable_declarations_json", None) or [
        {
            "name": "name",
            "purpose": "Recipient or subject used by the prompt",
            "required": True,
            "allowed_value_category": "synthetic",
            "safety_classification": "safe_fixture",
            "sample_guidance": "Use safe synthetic fixture text.",
            "display_order": 0,
        }
    ]
    fixture_values: dict[str, object] = {"name": "Ada"}
    fixture_sets = _attr(revision, "fixture_value_sets_json", None) or []
    if fixture_sets:
        raw_values = fixture_sets[0].get("values_by_variable", {})
        if isinstance(raw_values, dict):
            fixture_values = {str(key): value for key, value in raw_values.items()}
    return {
        "scope_type": _attr(lineage, "scope_type", active_scope.scope_type),
        "tenant_id": str(_attr(lineage, "tenant_id", active_scope.tenant_id) or ""),
        "display_name": _attr(lineage, "display_name", ""),
        "slug": _attr(lineage, "slug", ""),
        "purpose": _attr(revision, "purpose", _attr(lineage, "purpose", "")),
        "usage_notes": _attr(revision, "usage_notes", ""),
        "template_content": _attr(revision, "template_content", "Hello {{name}}"),
        "variables_json": json.dumps(variables, indent=2),
        "fixture_values_json": json.dumps(fixture_values, indent=2),
    }


def _prompt_payloads_from_form(
    *,
    scope_type: str,
    tenant_id: UUID | None,
    slug: str,
    display_name: str,
    purpose: str,
    usage_notes: str,
    template_content: str,
    variables_json: str,
    fixture_values_json: str,
    expected_revision_number: int,
) -> tuple[PromptLineageCreate, PromptDraftSave]:
    variables = [
        PromptVariableSchema.model_validate(variable)
        for variable in _load_json_array(variables_json, "variables_json")
    ]
    fixture_values = _load_json_object(fixture_values_json, "fixture_values_json")
    fixture_set = FixtureValueSet(
        fixture_set_id="default",
        label="Default",
        values_by_variable={
            str(key): str(value) for key, value in fixture_values.items()
        },
    )
    create_payload = PromptLineageCreate(
        scope_type=scope_type,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        slug=slug,
        display_name=display_name,
        purpose=purpose,
    )
    draft_payload = PromptDraftSave(
        expected_revision_number=expected_revision_number,
        prompt_title=display_name,
        purpose=purpose,
        usage_notes=usage_notes,
        template_content=template_content,
        variables=variables,
        fixture_sets=[fixture_set],
    )
    _assert_prompt_payload_bounds(draft_payload)
    return create_payload, draft_payload


def _parse_grant_tenant_ids(raw_value: str) -> list[UUID]:
    return [UUID(value.strip()) for value in raw_value.split(",") if value.strip()]


@router.get("/admin/prompt-runtime/prompts", response_class=HTMLResponse)
async def prompt_library_index(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = PromptRepository(session)
    lineages = await repository.list_visible_lineages(
        principal_tenant_id=principal.tenant_id,
        include_platform_admin=_is_platform_admin(principal),
    )
    items: list[PromptLineageSummary] = []
    for lineage in lineages:
        draft = await repository.get_active_draft(lineage.prompt_lineage_id)
        validation = None
        if draft is not None:
            validation = await repository.get_validation_result(
                draft.last_validation_result_id
            )
        items.append(_prompt_lineage_summary(lineage, validation))
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Prompt Library",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/index.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=_prompt_ui_page(title="Prompt Library", shell=shell),
            items=items,
        ),
    )


@router.get("/admin/prompt-runtime/prompts/new", response_class=HTMLResponse)
async def prompt_library_new(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="New Prompt",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/edit.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=build_prompt_ui_model(
                title="New Prompt",
                scope_type=shell.active_scope.scope_type,
                tenant_id=shell.active_scope.tenant_id,
                submitted_fields=_prompt_submitted_fields(shell=shell),
            ),
        ),
    )


@router.get(
    "/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit",
    response_class=HTMLResponse,
)
async def prompt_library_edit(
    prompt_lineage_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    validation = await repository.get_validation_result(draft.last_validation_result_id)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Edit Prompt",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/edit.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=build_prompt_ui_model(
                title="Edit Prompt",
                scope_type=lineage.scope_type,
                tenant_id=lineage.tenant_id,
                prompt_lineage_id=prompt_lineage_id,
                current_revision_number=draft.current_revision_number,
                validation_status=_attr(validation, "status", None),
                findings=_attr(validation, "findings_json", None),
                submitted_fields=_prompt_submitted_fields(
                    shell=shell,
                    lineage=lineage,
                    revision=revision,
                ),
            ),
            draft=revision,
            validation=_prompt_validation_response(validation),
        ),
    )


@router.post("/admin/prompt-runtime/prompts/form", response_class=HTMLResponse)
async def prompt_library_form(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    action: Annotated[str, Form(alias="_action")] = "save",
    prompt_lineage_id_value: Annotated[str, Form(alias="prompt_lineage_id")] = "",
    prompt_version_id_value: Annotated[str, Form(alias="prompt_version_id")] = "",
    scope_type: Annotated[str, Form()] = "tenant",
    tenant_id_value: Annotated[str, Form(alias="tenant_id")] = "",
    display_name: Annotated[str, Form()] = "",
    slug: Annotated[str, Form()] = "",
    purpose: Annotated[str, Form()] = "",
    usage_notes: Annotated[str, Form()] = "",
    template_content: Annotated[str, Form()] = "",
    variables_json: Annotated[str, Form()] = "[]",
    fixture_values_json: Annotated[str, Form()] = "{}",
    expected_revision_number: Annotated[int, Form()] = 0,
    reason: Annotated[str, Form()] = "Updated from admin UI",
    grant_tenant_ids: Annotated[str, Form()] = "",
) -> RedirectResponse:
    _ = request, container
    repository = PromptRepository(session)
    service = PromptService(repository)
    prompt_lineage_id = _parse_optional_uuid(prompt_lineage_id_value)
    prompt_version_id = _parse_optional_uuid(prompt_version_id_value)

    if action == "publish":
        if prompt_lineage_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "missing_prompt_lineage_id"},
            )
        lineage = await repository.get_lineage(prompt_lineage_id)
        draft = await repository.get_active_draft(prompt_lineage_id)
        if lineage is None or draft is None:
            raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
        _require_prompt_scope_mutation(
            principal,
            scope_type=lineage.scope_type,
            tenant_id=lineage.tenant_id,
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
            published_version = await service.publish(
                lineage=lineage,
                draft=draft,
                draft_revision=revision,
                validation_result=validation,
                principal_id=principal.principal_id,
                reason=reason,
            )
        except PromptPublishError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "stale_validation"},
            ) from exc
        return RedirectResponse(
            "/admin/prompt-runtime/prompts/versions/"
            f"{published_version.prompt_version_id}"
            "?flash=prompt-published",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if action in {"retire", "grant"}:
        if prompt_version_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "missing_prompt_version_id"},
            )
        target_version = await repository.get_prompt_version(prompt_version_id)
        if target_version is None:
            raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
        _require_prompt_scope_mutation(
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
            flash = "prompt-retired"
        else:
            for grant_tenant_id in _parse_grant_tenant_ids(grant_tenant_ids):
                try:
                    await service.grant_version_to_tenant(
                        version=target_version,
                        tenant_id=grant_tenant_id,
                        principal_id=principal.principal_id,
                        reason=reason,
                    )
                except PromptPublishError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={"code": "grant_not_allowed"},
                    ) from exc
            flash = "prompt-granted"
        return RedirectResponse(
            f"/admin/prompt-runtime/prompts/versions/{prompt_version_id}?flash={flash}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    form_tenant_id = _parse_optional_uuid(tenant_id_value)
    create_payload, draft_payload = _prompt_payloads_from_form(
        scope_type=scope_type,
        tenant_id=form_tenant_id,
        slug=slug,
        display_name=display_name,
        purpose=purpose,
        usage_notes=usage_notes,
        template_content=template_content,
        variables_json=variables_json,
        fixture_values_json=fixture_values_json,
        expected_revision_number=expected_revision_number,
    )
    if prompt_lineage_id is None:
        _require_prompt_scope_mutation(
            principal,
            scope_type=create_payload.scope_type,
            tenant_id=create_payload.tenant_id,
        )
        created = await service.create_prompt_lineage(
            scope_type=create_payload.scope_type,
            tenant_id=create_payload.tenant_id,
            slug=create_payload.slug,
            display_name=create_payload.display_name,
            purpose=create_payload.purpose,
            principal_id=principal.principal_id,
        )
        lineage = created.lineage
        draft = created.draft
    else:
        lineage = await repository.get_lineage(prompt_lineage_id)
        draft = await repository.get_active_draft(prompt_lineage_id)
        if lineage is None or draft is None:
            raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
        _require_prompt_scope_mutation(
            principal,
            scope_type=lineage.scope_type,
            tenant_id=lineage.tenant_id,
        )

    try:
        revision = await service.save_draft_revision(
            draft=draft,
            expected_revision_number=draft_payload.expected_revision_number,
            prompt_title=draft_payload.prompt_title,
            purpose=draft_payload.purpose,
            usage_notes=draft_payload.usage_notes,
            template_content=draft_payload.template_content,
            variables=[
                DomainPromptVariableDeclaration(
                    name=variable.name,
                    purpose=variable.purpose,
                    required=variable.required,
                    allowed_value_category=variable.allowed_value_category,
                    safety_classification=variable.safety_classification,
                    sample_guidance=variable.sample_guidance,
                    display_order=variable.display_order,
                )
                for variable in draft_payload.variables
            ],
            fixture_values=(
                draft_payload.fixture_sets[0].values_by_variable
                if draft_payload.fixture_sets
                else {}
            ),
            principal_id=principal.principal_id,
        )
    except StalePromptRevisionError as exc:
        raise HTTPException(status_code=409, detail={"code": "stale_revision"}) from exc

    if action == "validate":
        await service.validate_revision(
            draft_revision=revision,
            principal_id=principal.principal_id,
        )
        flash = "prompt-validated"
    elif action == "preview":
        return RedirectResponse(
            f"/admin/prompt-runtime/prompts/{lineage.prompt_lineage_id}/preview"
            "?fixture_set_id=default",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        flash = "prompt-saved"
    return RedirectResponse(
        f"/admin/prompt-runtime/prompts/{lineage.prompt_lineage_id}/edit?flash={flash}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/admin/prompt-runtime/prompts/versions/{prompt_version_id}",
    response_class=HTMLResponse,
)
async def prompt_library_detail(
    prompt_version_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = PromptRepository(session)
    version = await repository.get_prompt_version(prompt_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    grants = await repository.list_grants_for_version(prompt_version_id)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Prompt Version",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/detail.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=build_prompt_ui_model(
                title="Prompt Version",
                scope_type=version.scope_type,
                tenant_id=version.tenant_id,
                prompt_version_id=prompt_version_id,
                status=version.status,
            ),
            version=_prompt_version_detail(version),
            grants=grants,
        ),
    )


@router.get(
    "/admin/prompt-runtime/prompts/{prompt_lineage_id}/history",
    response_class=HTMLResponse,
)
async def prompt_library_history(
    prompt_lineage_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    if lineage is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    history = HistoryResponse(
        items=[
            AuditEventSummary.model_validate(event)
            for event in await repository.list_prompt_history(
                prompt_lineage_id=prompt_lineage_id,
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
        title="Prompt History",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/history.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=_prompt_ui_page(
                title="Prompt History",
                shell=shell,
                prompt_lineage_id=prompt_lineage_id,
            ),
            history=history,
        ),
    )


@router.get(
    "/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview",
    response_class=HTMLResponse,
)
async def prompt_library_preview_page(
    prompt_lineage_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    fixture_set_id: Annotated[str, Query()] = "default",
) -> HTMLResponse:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    preview_response = await _render_preview_from_revision(
        revision=revision,
        fixture_set_id=fixture_set_id,
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Prompt Preview",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/preview.html",
        _prompt_template_context(
            shell=shell,
            principal=principal,
            page=_prompt_ui_page(
                title="Prompt Preview",
                shell=shell,
                prompt_lineage_id=prompt_lineage_id,
            ),
            preview=preview_response,
        ),
    )


def _assert_prompt_payload_bounds(payload: PromptDraftSave) -> None:
    if len(payload.template_content.encode("utf-8")) > MAX_PROMPT_TEMPLATE_BYTES:
        raise HTTPException(status_code=413, detail={"code": "prompt_too_large"})
    if len(payload.fixture_sets) > MAX_FIXTURE_SET_COUNT:
        raise HTTPException(status_code=413, detail={"code": "too_many_fixture_sets"})


async def _render_preview_from_revision(
    *,
    revision: object,
    fixture_set_id: str,
) -> PromptPreviewResponse:
    fixture = next(
        (
            item
            for item in _attr(revision, "fixture_value_sets_json", []) or []
            if item.get("fixture_set_id") == fixture_set_id
        ),
        None,
    )
    if fixture is None:
        raise HTTPException(status_code=422, detail={"code": "missing_fixture_set"})
    raw_values = fixture.get("values_by_variable", {})
    values = raw_values if isinstance(raw_values, dict) else {}
    required = tuple(
        str(variable["name"])
        for variable in _attr(revision, "variable_declarations_json", []) or []
        if variable.get("required", True)
    )
    try:
        preview = render_safe_preview(
            _attr(revision, "template_content"),
            {str(key): str(value) for key, value in values.items()},
            required_variables=required,
        )
    except PromptPreviewError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "missing_fixture_value",
                "missing_variables": list(exc.missing_variables),
            },
        ) from exc
    return PromptPreviewResponse(
        rendered_preview=preview.rendered_preview,
        redaction_categories=list(preview.redaction_categories),
        missing_variables=list(preview.missing_variables),
    )


@router.get(
    "/admin/prompt-runtime/api/prompts",
    response_model=dict[str, list[PromptLineageSummary]],
)
async def list_prompt_lineages(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Query()] = None,
    scope_type: Annotated[str | None, Query()] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> dict[str, list[PromptLineageSummary]]:
    visible_tenant_id = _assert_query_tenant_allowed(principal, tenant_id)
    repository = PromptRepository(session)
    lineages = await repository.list_visible_lineages(
        principal_tenant_id=visible_tenant_id,
        include_platform_admin=_is_platform_admin(principal),
        scope_type=scope_type,
        status=status_filter,
        q=q,
    )
    items: list[PromptLineageSummary] = []
    for lineage in lineages:
        draft = await repository.get_active_draft(lineage.prompt_lineage_id)
        validation = None
        if draft is not None:
            validation = await repository.get_validation_result(
                draft.last_validation_result_id
            )
        items.append(_prompt_lineage_summary(lineage, validation))
    return {"items": items}


@router.post(
    "/admin/prompt-runtime/api/prompts",
    response_model=PromptDraftDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt_lineage(
    payload: PromptLineageCreate,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptDraftDetail:
    _require_prompt_scope_mutation(
        principal,
        scope_type=payload.scope_type,
        tenant_id=payload.tenant_id,
    )
    created = await PromptRepository(session).create_lineage_with_draft(
        scope_type=payload.scope_type,
        tenant_id=payload.tenant_id,
        slug=payload.slug,
        display_name=payload.display_name,
        purpose=payload.purpose,
        principal_id=principal.principal_id,
    )
    return PromptDraftDetail(
        prompt_lineage_id=created.lineage.prompt_lineage_id,
        prompt_draft_id=created.draft.prompt_draft_id,
        current_revision_number=created.draft.current_revision_number,
    )


@router.get(
    "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft",
    response_model=PromptDraftDetail,
)
async def get_prompt_draft(
    prompt_lineage_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptDraftDetail:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    validation = await repository.get_validation_result(draft.last_validation_result_id)
    return _prompt_draft_detail(
        lineage=lineage,
        draft=draft,
        revision=revision,
        validation=validation,
    )


@router.put(
    "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft",
    response_model=PromptDraftDetail,
)
async def save_prompt_draft(
    prompt_lineage_id: UUID,
    payload: PromptDraftSave,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptDraftDetail:
    _assert_prompt_payload_bounds(payload)
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    fixture_values: dict[str, str] = {}
    if payload.fixture_sets:
        fixture_values = payload.fixture_sets[0].values_by_variable
    try:
        await PromptService(repository).save_draft_revision(
            draft=draft,
            expected_revision_number=payload.expected_revision_number,
            prompt_title=payload.prompt_title,
            purpose=payload.purpose,
            usage_notes=payload.usage_notes,
            template_content=payload.template_content,
            variables=[
                DomainPromptVariableDeclaration(
                    name=variable.name,
                    purpose=variable.purpose,
                    required=variable.required,
                    allowed_value_category=variable.allowed_value_category,
                    safety_classification=variable.safety_classification,
                    sample_guidance=variable.sample_guidance,
                    display_order=variable.display_order,
                )
                for variable in payload.variables
            ],
            fixture_values=fixture_values,
            principal_id=principal.principal_id,
        )
    except StalePromptRevisionError as exc:
        raise HTTPException(status_code=409, detail={"code": "stale_revision"}) from exc
    return PromptDraftDetail(
        prompt_lineage_id=draft.prompt_lineage_id,
        prompt_draft_id=draft.prompt_draft_id,
        current_revision_number=draft.current_revision_number,
    )


@router.post(
    "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate",
    response_model=ValidationResult,
)
async def validate_prompt_draft(
    prompt_lineage_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> ValidationResult:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    validation = await PromptService(repository).validate_revision(
        draft_revision=revision,
        principal_id=principal.principal_id,
    )
    return ValidationResult(
        validation_result_id=validation.prompt_validation_result_id,
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
                field=str(finding["field"]) if "field" in finding else None,
            )
            for finding in validation.findings_json
        ],
    )


@router.post(
    "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview",
    response_model=PromptPreviewResponse,
)
async def preview_prompt_draft(
    prompt_lineage_id: UUID,
    payload: PromptPreviewRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptPreviewResponse:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    return await _render_preview_from_revision(
        revision=revision,
        fixture_set_id=payload.fixture_set_id,
    )


@router.post(
    "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish",
    response_model=PromptVersionDetail,
    status_code=status.HTTP_201_CREATED,
)
async def publish_prompt_draft(
    prompt_lineage_id: UUID,
    payload: PublishRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptVersionDetail:
    repository = PromptRepository(session)
    lineage = await repository.get_lineage(prompt_lineage_id)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if lineage is None or draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=lineage.scope_type,
        tenant_id=lineage.tenant_id,
    )
    revision = await repository.get_latest_revision(draft)
    validation = await repository.get_validation_result(draft.last_validation_result_id)
    if revision is None or validation is None:
        raise HTTPException(status_code=409, detail={"code": "missing_validation"})
    try:
        version = await PromptService(repository).publish(
            lineage=lineage,
            draft=draft,
            draft_revision=revision,
            validation_result=validation,
            principal_id=principal.principal_id,
            reason=payload.reason,
        )
    except PromptPublishError as exc:
        raise HTTPException(
            status_code=409, detail={"code": "stale_validation"}
        ) from exc
    return _prompt_version_detail(version)


@router.post(
    "/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/retire",
    response_model=PromptVersionDetail,
)
async def retire_prompt_version(
    prompt_version_id: UUID,
    payload: RetireRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> PromptVersionDetail:
    repository = PromptRepository(session)
    version = await repository.get_prompt_version(prompt_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    retired = await PromptService(repository).retire_version(
        version=version,
        principal_id=principal.principal_id,
        reason=payload.reason,
    )
    return _prompt_version_detail(retired)


@router.post(
    "/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants",
    response_model=TenantGrantResponse,
)
async def grant_prompt_version(
    prompt_version_id: UUID,
    payload: TenantGrantRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> TenantGrantResponse:
    repository = PromptRepository(session)
    version = await repository.get_prompt_version(prompt_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    _require_prompt_scope_mutation(
        principal,
        scope_type=version.scope_type,
        tenant_id=version.tenant_id,
    )
    service = PromptService(repository)
    granted = []
    for tenant_id in payload.tenant_ids:
        try:
            grant = await service.grant_version_to_tenant(
                version=version,
                tenant_id=tenant_id,
                principal_id=principal.principal_id,
                reason=payload.reason,
            )
        except PromptPublishError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "grant_not_allowed"},
            ) from exc
        granted.append(grant.grantee_tenant_id)
    return TenantGrantResponse(granted_tenant_ids=granted)
