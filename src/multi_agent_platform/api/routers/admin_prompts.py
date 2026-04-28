from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.prompts import (
    PromptDraftDetail,
    PromptDraftSave,
    PromptLineageCreate,
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
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.prompts import (
    PromptRepository,
    StalePromptRevisionError,
)
from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.preview import PromptPreviewError, render_safe_preview
from multi_agent_platform.prompts.service import PromptPublishError, PromptService

router = APIRouter(tags=["prompt-library"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/admin/prompt-runtime/prompts", response_class=HTMLResponse)
async def prompt_library_index(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Prompt Library",
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "prompts/index.html",
        {"shell": shell, "principal": principal},
    )


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
    repository = PromptRepository(session)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
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
                PromptVariableDeclaration(
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
    draft = await repository.get_active_draft(prompt_lineage_id)
    if draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    validation = await PromptService(repository).validate_revision(
        draft_revision=revision,
        principal_id=principal.principal_id,
    )
    return ValidationResult(
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
    session: SessionDep,
) -> PromptPreviewResponse:
    repository = PromptRepository(session)
    draft = await repository.get_active_draft(prompt_lineage_id)
    if draft is None:
        raise HTTPException(status_code=404, detail={"code": "prompt_not_found"})
    revision = await repository.get_latest_revision(draft)
    if revision is None:
        raise HTTPException(status_code=422, detail={"code": "missing_revision"})
    fixture = next(
        (
            item
            for item in revision.fixture_value_sets_json
            if item.get("fixture_set_id") == payload.fixture_set_id
        ),
        None,
    )
    if fixture is None:
        raise HTTPException(status_code=422, detail={"code": "missing_fixture_set"})
    raw_values = fixture.get("values_by_variable", {})
    values = raw_values if isinstance(raw_values, dict) else {}
    required = tuple(
        str(variable["name"])
        for variable in revision.variable_declarations_json
        if variable.get("required", True)
    )
    try:
        preview = render_safe_preview(
            revision.template_content,
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
    return PromptVersionDetail.model_validate(version)


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
    retired = await PromptService(repository).retire_version(
        version=version,
        principal_id=principal.principal_id,
        reason=payload.reason,
    )
    return PromptVersionDetail.model_validate(retired)


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
    service = PromptService(repository)
    granted = []
    for tenant_id in payload.tenant_ids:
        grant = await service.grant_version_to_tenant(
            version=version,
            tenant_id=tenant_id,
            principal_id=principal.principal_id,
            reason=payload.reason,
        )
        granted.append(grant.grantee_tenant_id)
    return TenantGrantResponse(granted_tenant_ids=granted)
