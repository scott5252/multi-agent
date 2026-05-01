from __future__ import annotations

import json
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.skill_registry.readiness import (
    CredentialReferenceSummary,
)
from multi_agent_platform.admin.skill_registry.service import (
    SkillInstallationRecord,
    SkillPackageVersionRecord,
    SkillRegistryService,
    SkillRegistryServiceError,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.skill_registry import (
    BindingEligibilityResponse,
    ConfigureCredentialsRequest,
    SkillInstallationCreateRequest,
    SkillInstallationResponse,
    SkillPackageCreateRequest,
    SkillPackageResponse,
    SkillPackageVersionResponse,
    SkillRegistryFindingResponse,
    SkillVersionPublishRequest,
    SkillVersionValidateRequest,
    SkillVersionValidationResponse,
    TenantAvailabilityGrantRequest,
)
from multi_agent_platform.api.ui.admin_console import BreadcrumbItem
from multi_agent_platform.api.ui.skill_registry import (
    BindingEligibilityPreviewForm,
    BrowserFormError,
    CredentialReferenceConfigForm,
    InstallSkillForm,
    ManifestCandidateForm,
    SkillPackageCreateForm,
    SmokeTestActionForm,
    TenantGrantForm,
    build_installation_detail_page,
    build_installation_list_page,
    build_package_detail_page,
    build_package_list_page,
    build_revision_conflict_view,
    build_version_detail_page,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext

router = APIRouter(prefix="/admin/skill-registry", tags=["skill-registry"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
_SERVICE = SkillRegistryService()
SEE_OTHER = status.HTTP_303_SEE_OTHER


def get_skill_registry_service() -> SkillRegistryService:
    return _SERVICE


def reset_skill_registry_service() -> None:
    global _SERVICE
    _SERVICE = SkillRegistryService()


@router.post("/packages", response_model=SkillPackageResponse)
async def create_skill_package(
    request: SkillPackageCreateRequest,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> SkillPackageResponse:
    try:
        package = service.create_package(
            slug=request.slug,
            display_name=request.display_name,
            description=request.description,
            owner_principal_id=request.owner_principal_id,
            actor_principal_id=principal.principal_id,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return SkillPackageResponse(
        slug=package.slug,
        display_name=package.display_name,
        description=package.description,
        lifecycle_state=package.lifecycle_state,
        latest_published_version=max(package.versions, default=None),
    )


@router.post(
    "/packages/{slug}/versions/validate",
    response_model=SkillVersionValidationResponse,
)
async def validate_skill_version(
    slug: str,
    request: SkillVersionValidateRequest,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
    principal: PrincipalDep,
) -> SkillVersionValidationResponse:
    _ = slug, principal
    result = service.validate_candidate(
        manifest_payload=request.manifest,
        approved_integration_refs=request.approved_integration_refs or None,
    )
    return SkillVersionValidationResponse(
        status=result.status,
        manifest_digest=result.manifest_digest,
        safe_summary=result.safe_summary,
        findings=[
            SkillRegistryFindingResponse(
                code=finding.code,
                message=finding.message,
                severity=finding.severity,
                field_path=finding.field_path,
                blocking=finding.blocking,
                remediation=finding.remediation,
            )
            for finding in result.findings
        ],
    )


@router.post(
    "/packages/{slug}/versions",
    response_model=SkillPackageVersionResponse,
)
async def publish_skill_version(
    slug: str,
    request: SkillVersionPublishRequest,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> SkillPackageVersionResponse:
    try:
        version = service.publish_version(
            slug=slug,
            manifest_payload=request.manifest,
            artifact_digest=request.artifact_digest,
            actor_principal_id=principal.principal_id,
            approved_integration_refs=request.approved_integration_refs or None,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return _version_response(version)


@router.post(
    "/packages/{slug}/versions/{semantic_version}/availability",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def grant_skill_version_availability(
    slug: str,
    semantic_version: str,
    request: TenantAvailabilityGrantRequest,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> None:
    try:
        service.grant_tenant_availability(
            slug=slug,
            semantic_version=semantic_version,
            tenant_id=request.tenant_id,
            actor_principal_id=principal.principal_id,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc


@router.get(
    "/tenants/{tenant_id}/available-versions",
    response_model=list[SkillPackageVersionResponse],
)
async def list_available_skill_versions(
    tenant_id: str,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
    principal: PrincipalDep,
) -> list[SkillPackageVersionResponse]:
    _ensure_tenant_access(principal, tenant_id)
    return [
        _version_response(version)
        for version in service.list_available_versions(tenant_id=tenant_id)
    ]


@router.post("/installations", response_model=SkillInstallationResponse)
async def create_skill_installation(
    request: SkillInstallationCreateRequest,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> SkillInstallationResponse:
    _ensure_tenant_access(principal, request.tenant_id)
    try:
        installation = service.install_version(
            tenant_id=request.tenant_id,
            slug=request.slug,
            semantic_version=request.semantic_version,
            actor_principal_id=principal.principal_id,
            previous_installation_id=request.previous_installation_id,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return _installation_response(installation)


@router.post(
    "/installations/{installation_id}/credentials",
    response_model=SkillInstallationResponse,
)
async def configure_installation_credentials(
    installation_id: str,
    request: ConfigureCredentialsRequest,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> SkillInstallationResponse:
    _installation_for_principal(service, installation_id, principal)
    try:
        installation = service.configure_credentials(
            installation_id=installation_id,
            revision_token=request.revision_token,
            credentials=[
                CredentialReferenceSummary(
                    requirement_key=item.requirement_key,
                    credential_kind=item.credential_kind,
                    reference_id=item.reference_id,
                    status=item.status,
                    safe_summary=item.safe_summary,
                )
                for item in request.credentials
            ],
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return _installation_response(installation)


@router.get(
    "/installations/{installation_id}/eligibility",
    response_model=BindingEligibilityResponse,
)
async def preview_installation_eligibility(
    installation_id: str,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
    principal: PrincipalDep,
) -> BindingEligibilityResponse:
    _installation_for_principal(service, installation_id, principal)
    try:
        decision = service.binding_eligibility(installation_id=installation_id)
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return BindingEligibilityResponse(
        allowed=decision.allowed,
        reason_codes=list(decision.reason_codes),
        evidence=decision.evidence,
    )


@router.get("/ui/packages", response_class=HTMLResponse, include_in_schema=False)
async def skill_registry_package_list_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    page = build_package_list_page(
        list(service.packages.values()),
        platform_admin="platform_admin" in principal.role_codes,
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Skill Registry", href="/admin/skill-registry/ui/packages"
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/package_list.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get("/ui/packages/new", response_class=HTMLResponse, include_in_schema=False)
async def skill_registry_package_create_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    page: dict[str, Any] = {
        "title": "Create Skill Package",
        "redaction_notice": _redaction_notice(),
        "errors": (),
    }
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/package_create.html",
        {"page": page, "principal": principal, "shell": shell},
    )


async def _render_package_create_form(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    container: Any,
    errors: tuple[object, ...],
    values: object | None = None,
) -> HTMLResponse:
    page: dict[str, Any] = {
        "title": "Create Skill Package",
        "redaction_notice": _redaction_notice(),
        "errors": errors,
        "values": values,
    }
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
    )
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "skill_registry/package_create.html",
            {"page": page, "principal": principal, "shell": shell},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    )


@router.post("/ui/packages", response_class=HTMLResponse, include_in_schema=False)
async def skill_registry_package_create_submit(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> Response:
    form = await request.form()
    browser_form = SkillPackageCreateForm.from_mapping(
        form, default_owner=principal.principal_id
    )
    if browser_form.errors:
        return await _render_package_create_form(
            request=request,
            principal=principal,
            session=session,
            container=container,
            errors=browser_form.errors,
            values=browser_form,
        )
    try:
        package = service.create_package(
            slug=browser_form.slug,
            display_name=browser_form.display_name,
            description=browser_form.description,
            owner_principal_id=browser_form.steward_principal_id,
            actor_principal_id=principal.principal_id,
        )
    except SkillRegistryServiceError as exc:
        if exc.category == "duplicate_package":
            return await _render_package_create_form(
                request=request,
                principal=principal,
                session=session,
                container=container,
                errors=(
                    BrowserFormError(
                        "slug",
                        "A package with this slug already exists.",
                    ),
                ),
                values=browser_form,
            )
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/packages/{package.slug}", status_code=SEE_OTHER
    )


@router.get(
    "/ui/packages/{slug}/candidate",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_candidate_page(
    slug: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    _ = principal
    page = _candidate_page(slug, service)
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
        package_slug=slug,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/package_candidate_form.html",
        {"page": page, "principal": principal, "shell": shell},
    )


async def _render_candidate_form(
    *,
    slug: str,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    container: Any,
    service: SkillRegistryService,
    errors: tuple[BrowserFormError, ...],
) -> HTMLResponse:
    page = _candidate_page(slug, service)
    page["errors"] = errors
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
        package_slug=slug,
    )
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "skill_registry/package_candidate_form.html",
            {"page": page, "principal": principal, "shell": shell},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    )


@router.post(
    "/ui/packages/{slug}/candidate",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_candidate_submit(
    slug: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> Response:
    form = await request.form()
    browser_form = ManifestCandidateForm.from_mapping(
        form,
        uploaded_manifest_text=await _uploaded_manifest_text(form.get("manifest_file")),
    )
    if browser_form.errors:
        return await _render_candidate_form(
            slug=slug,
            request=request,
            principal=principal,
            session=session,
            container=container,
            service=service,
            errors=browser_form.errors,
        )
    try:
        service.save_candidate(
            slug=slug,
            manifest_payload=browser_form.manifest_payload,
            artifact_digest=browser_form.artifact_digest,
            approved_integration_refs=browser_form.approved_integration_refs,
            actor_principal_id=principal.principal_id,
            expected_revision_token=browser_form.candidate_revision,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/packages/{slug}/candidate", status_code=SEE_OTHER
    )


@router.post(
    "/ui/packages/{slug}/candidate/validate",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_candidate_validate_submit(
    slug: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    form = await request.form()
    revision_token = str(form.get("revision_token", "")).strip()
    try:
        service.validate_saved_candidate(
            slug=slug,
            revision_token=revision_token,
            actor_principal_id=principal.principal_id,
        )
    except SkillRegistryServiceError as exc:
        if exc.category == "stale_revision":
            candidate = service.candidates.get(slug)
            _ = build_revision_conflict_view(
                resource_type="manifest_candidate",
                resource_id=slug,
                submitted_revision=revision_token,
                current_revision=candidate.revision_token if candidate else None,
                reload_url=f"/admin/skill-registry/ui/packages/{slug}/candidate",
            )
            return RedirectResponse(
                f"/admin/skill-registry/ui/packages/{slug}/candidate?conflict=stale",
                status_code=SEE_OTHER,
            )
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/packages/{slug}/candidate", status_code=SEE_OTHER
    )


@router.post(
    "/ui/packages/{slug}/candidate/publish",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_candidate_publish_submit(
    slug: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    form = await request.form()
    revision_token = str(form.get("revision_token", "")).strip()
    try:
        version = service.publish_saved_candidate(
            slug=slug,
            revision_token=revision_token,
            actor_principal_id=principal.principal_id,
        )
    except SkillRegistryServiceError as exc:
        if exc.category == "stale_revision":
            return RedirectResponse(
                f"/admin/skill-registry/ui/packages/{slug}/candidate?conflict=stale",
                status_code=SEE_OTHER,
            )
        raise _http_error(exc) from exc
    return RedirectResponse(
        (
            f"/admin/skill-registry/ui/packages/{slug}/versions/"
            f"{version.semantic_version}"
        ),
        status_code=SEE_OTHER,
    )


@router.get(
    "/ui/packages/{slug}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_detail_page(
    slug: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    package = service.packages.get(slug)
    if package is None:
        raise HTTPException(status_code=404, detail="skill package not found")
    page = build_package_detail_page(package)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Skill Registry", href="/admin/skill-registry/ui/packages"
            ),
            BreadcrumbItem(
                label=slug, href=f"/admin/skill-registry/ui/packages/{slug}"
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/package_detail.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get(
    "/ui/packages/{slug}/versions/{semantic_version}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_package_version_page(
    slug: str,
    semantic_version: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    _ = principal
    package = service.packages.get(slug)
    if package is None or semantic_version not in package.versions:
        raise HTTPException(status_code=404, detail="skill package version not found")
    version = package.versions[semantic_version]
    page = build_version_detail_page(version)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Skill Registry", href="/admin/skill-registry/ui/packages"
            ),
            BreadcrumbItem(
                label=slug, href=f"/admin/skill-registry/ui/packages/{slug}"
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/package_version_detail.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get(
    "/ui/packages/{slug}/versions/{semantic_version}/grants",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_tenant_grant_page(
    slug: str,
    semantic_version: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    _ = principal
    package = service.packages.get(slug)
    if package is None or semantic_version not in package.versions:
        raise HTTPException(status_code=404, detail="skill package version not found")
    version = package.versions[semantic_version]
    page: dict[str, Any] = {
        "title": f"Tenant Grants: {slug} {semantic_version}",
        "redaction_notice": _redaction_notice(),
        "version": _version_response(version).model_dump(),
    }
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
        package_slug=slug,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/tenant_grant_form.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.post(
    "/ui/packages/{slug}/versions/{semantic_version}/grants",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_tenant_grant_submit(
    slug: str,
    semantic_version: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    form = await request.form()
    browser_form = TenantGrantForm.from_mapping(form)
    if browser_form.errors:
        raise HTTPException(status_code=422, detail="tenant_ids required")
    try:
        for tenant_id in browser_form.selected_tenant_ids:
            service.grant_tenant_availability(
                slug=slug,
                semantic_version=semantic_version,
                tenant_id=tenant_id,
                actor_principal_id=principal.principal_id,
            )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/packages/{slug}", status_code=SEE_OTHER
    )


@router.get(
    "/ui/available-versions",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_available_versions_page(
    request: Request,
    tenant_id: str,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    _ensure_tenant_access(principal, tenant_id)
    page: dict[str, Any] = {
        "title": "Available Skills",
        "tenant_id": tenant_id,
        "versions": [
            _version_response(version).model_dump()
            for version in service.list_available_versions(tenant_id=tenant_id)
        ],
        "redaction_notice": _redaction_notice(),
    }
    shell = await _skill_registry_shell(
        request=request,
        principal=principal,
        session=session,
        title=page["title"],
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/available_versions.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.post(
    "/ui/installations",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_submit(
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    form = await request.form()
    browser_form = InstallSkillForm.from_mapping(form)
    if browser_form.errors:
        raise HTTPException(status_code=422, detail="install form is incomplete")
    _ensure_tenant_access(principal, browser_form.tenant_id)
    try:
        installation = service.install_version(
            tenant_id=browser_form.tenant_id,
            slug=browser_form.slug,
            semantic_version=browser_form.semantic_version,
            actor_principal_id=principal.principal_id,
            previous_installation_id=browser_form.previous_installation_id,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/installations/{installation.installation_id}",
        status_code=SEE_OTHER,
    )


@router.get(
    "/ui/installations",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_list_page(
    request: Request,
    tenant_id: str,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    _ensure_tenant_access(principal, tenant_id)
    installations = [
        installation
        for installation in service.installations.values()
        if installation.tenant_id == tenant_id
    ]
    page = build_installation_list_page(installations, tenant_id=tenant_id)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Installed Skills",
                href="/admin/skill-registry/ui/installations",
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/installation_list.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get(
    "/ui/installations/{installation_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_detail_page(
    installation_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    installation = _installation_for_principal(service, installation_id, principal)
    page = build_installation_detail_page(installation)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Installed Skills",
                href="/admin/skill-registry/ui/installations",
            ),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/installation_detail.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get(
    "/ui/installations/{installation_id}/credentials",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_credentials_page(
    installation_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> HTMLResponse:
    installation = _installation_for_principal(service, installation_id, principal)
    page = build_installation_detail_page(installation)
    context = {
        "page": page,
        "principal": principal,
        "shell": await _skill_registry_shell(
            request=request,
            principal=principal,
            session=session,
            title="Configure Installed Skill",
        ),
        "conflict": request.query_params.get("conflict") == "stale",
    }
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "skill_registry/installation_configure.html",
        context,
    )


@router.post(
    "/ui/installations/{installation_id}/credentials",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_credentials_submit(
    installation_id: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    _installation_for_principal(service, installation_id, principal)
    form = await request.form()
    browser_form = CredentialReferenceConfigForm.from_mapping(form)
    if browser_form.errors:
        raise HTTPException(status_code=422, detail="credential form is incomplete")
    reference_id = browser_form.selected_reference_id or ""
    status_value = "ready" if reference_id else "missing"
    try:
        installation = service.configure_credentials(
            installation_id=installation_id,
            revision_token=browser_form.revision_token,
            credentials=[
                CredentialReferenceSummary(
                    requirement_key=browser_form.requirement_key,
                    credential_kind=browser_form.credential_kind,
                    reference_id=reference_id or None,
                    status=status_value,
                    safe_summary=browser_form.delegated_metadata_fields,
                )
            ],
        )
    except SkillRegistryServiceError as exc:
        if exc.category == "stale_revision":
            return RedirectResponse(
                (
                    "/admin/skill-registry/ui/installations/"
                    f"{installation_id}/credentials?conflict=stale"
                ),
                status_code=SEE_OTHER,
            )
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/installations/{installation.installation_id}",
        status_code=SEE_OTHER,
    )


@router.post(
    "/ui/installations/{installation_id}/smoke-tests",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_smoke_submit(
    installation_id: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    _installation_for_principal(service, installation_id, principal)
    form = await request.form()
    browser_form = SmokeTestActionForm.from_mapping(form)
    try:
        installation = service.refresh_smoke_tests(
            installation_id=installation_id,
            revision_token=browser_form.revision_token,
        )
    except SkillRegistryServiceError as exc:
        if exc.category == "stale_revision":
            return RedirectResponse(
                f"/admin/skill-registry/ui/installations/{installation_id}?conflict=stale",
                status_code=SEE_OTHER,
            )
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/installations/{installation.installation_id}",
        status_code=SEE_OTHER,
    )


@router.post(
    "/ui/installations/{installation_id}/eligibility-preview",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def skill_registry_installation_eligibility_submit(
    installation_id: str,
    request: Request,
    principal: PrincipalDep,
    service: Annotated[SkillRegistryService, Depends(get_skill_registry_service)],
) -> RedirectResponse:
    _installation_for_principal(service, installation_id, principal)
    form = BindingEligibilityPreviewForm.from_mapping(await request.form())
    try:
        service.binding_eligibility(
            installation_id=installation_id,
            required_action_categories={form.selected_context_type}
            if form.selected_context_type == "unsupported_action"
            else None,
        )
    except SkillRegistryServiceError as exc:
        raise _http_error(exc) from exc
    return RedirectResponse(
        f"/admin/skill-registry/ui/installations/{installation_id}",
        status_code=SEE_OTHER,
    )


def _version_response(
    version: SkillPackageVersionRecord,
) -> SkillPackageVersionResponse:
    return SkillPackageVersionResponse(
        package_version_id=version.package_version_id,
        slug=version.slug,
        semantic_version=version.semantic_version,
        manifest_digest=version.manifest_digest,
        artifact_digest=version.artifact_digest,
        validation_status=version.validation_status,
        lifecycle_state=version.lifecycle_state,
        tenant_grants=sorted(version.tenant_grants),
        quarantined=version.quarantined,
        runtime_blocked=version.runtime_blocked,
    )


def _installation_response(
    installation: SkillInstallationRecord,
) -> SkillInstallationResponse:
    readiness = installation.readiness
    return SkillInstallationResponse(
        installation_id=installation.installation_id,
        tenant_id=installation.tenant_id,
        slug=installation.slug,
        semantic_version=installation.semantic_version,
        installation_version=installation.installation_version,
        manifest_digest=installation.manifest_digest,
        artifact_digest=installation.artifact_digest,
        revision_token=installation.revision_token,
        readiness_state=readiness.readiness_state if readiness else "blocked",
        credential_status=readiness.credential_status if readiness else "blocked",
        compatibility_status=readiness.compatibility_status if readiness else "blocked",
        permission_status=readiness.permission_status if readiness else "blocked",
        smoke_test_status=readiness.smoke_test_status if readiness else "blocked",
        binding_eligibility_status=(
            readiness.binding_eligibility_status if readiness else "denied"
        ),
        findings=[
            {
                "code": finding.code,
                "message": finding.message,
                "blocking": finding.blocking,
            }
            for finding in (readiness.findings if readiness else ())
        ],
        runtime_blocked=installation.runtime_blocked,
        quarantined=installation.quarantined,
    )


def _installation_for_principal(
    service: SkillRegistryService,
    installation_id: str,
    principal: PrincipalContext,
) -> SkillInstallationRecord:
    installation = service.installations.get(installation_id)
    if installation is None:
        raise HTTPException(status_code=404, detail="skill installation not found")
    _ensure_tenant_access(principal, installation.tenant_id)
    return installation


def _ensure_tenant_access(principal: PrincipalContext, tenant_id: str) -> None:
    if "platform_admin" in principal.role_codes:
        return
    if principal.tenant_id is not None and str(principal.tenant_id) == tenant_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cross_tenant")


def _candidate_page(slug: str, service: SkillRegistryService) -> dict[str, Any]:
    package = service.packages.get(slug)
    if package is None:
        raise HTTPException(status_code=404, detail="skill package not found")
    candidate = service.candidates.get(slug)
    validation = candidate.validation if candidate else None
    safe_summary = validation.safe_summary if validation else {}
    findings = validation.findings if validation else ()
    return {
        "title": f"Package Candidate: {slug}",
        "slug": slug,
        "redaction_notice": _redaction_notice(),
        "errors": (),
        "candidate": candidate,
        "validation_status": validation.status if validation else "not_validated",
        "manifest_digest": validation.manifest_digest if validation else None,
        "safe_summary": safe_summary,
        "findings": findings,
    }


async def _uploaded_manifest_text(value: object) -> str | None:
    filename = getattr(value, "filename", None)
    if not filename:
        return None
    read = getattr(value, "read", None)
    if read is None:
        return None
    data = await read()
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return str(data)


def _parse_manifest_payload(raw_manifest: str) -> dict[str, object]:
    raw_manifest = raw_manifest.strip()
    if not raw_manifest:
        raise HTTPException(status_code=422, detail="manifest is required")
    try:
        parsed = json.loads(raw_manifest)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise HTTPException(
                status_code=422, detail="manifest must be JSON"
            ) from exc
        parsed = yaml.safe_load(raw_manifest)
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="manifest must be an object")
    return dict(parsed)


def _split_form_values(raw_value: str) -> set[str]:
    return {
        item.strip()
        for chunk in raw_value.splitlines()
        for item in chunk.split(",")
        if item.strip()
    }


def _redaction_notice() -> str:
    return (
        "Raw package payloads, secrets, credential values, provider tokens, "
        "unsafe docs, and cross-tenant data are omitted."
    )


async def _skill_registry_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    title: str,
    package_slug: str | None = None,
) -> object:
    breadcrumbs = [
        BreadcrumbItem(label="Admin", href="/admin"),
        BreadcrumbItem(
            label="Skill Registry", href="/admin/skill-registry/ui/packages"
        ),
    ]
    if package_slug:
        breadcrumbs.append(
            BreadcrumbItem(
                label=package_slug,
                href=f"/admin/skill-registry/ui/packages/{package_slug}",
            )
        )
    return await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=title,
        breadcrumbs=tuple(breadcrumbs),
    )


def _http_error(exc: SkillRegistryServiceError) -> HTTPException:
    status_code = {
        "duplicate_package": status.HTTP_409_CONFLICT,
        "duplicate_version": status.HTTP_409_CONFLICT,
        "stale_revision": status.HTTP_409_CONFLICT,
        "unauthorized": status.HTTP_403_FORBIDDEN,
        "not_found": status.HTTP_404_NOT_FOUND,
        "validation_blocked": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }.get(exc.category, status.HTTP_400_BAD_REQUEST)
    return HTTPException(
        status_code=status_code,
        detail={"category": exc.category, "message": str(exc)},
    )
