from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
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
    build_installation_detail_page,
    build_installation_list_page,
    build_package_detail_page,
    build_package_list_page,
    build_version_detail_page,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext

router = APIRouter(prefix="/admin/skill-registry", tags=["skill-registry"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
_SERVICE = SkillRegistryService()


def get_skill_registry_service() -> SkillRegistryService:
    return _SERVICE


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
    _ = principal
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
    _ = principal
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
    _ = principal
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
    installation = service.installations.get(installation_id)
    if installation is None:
        raise HTTPException(status_code=404, detail="skill installation not found")
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
