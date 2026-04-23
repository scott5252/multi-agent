from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.admin.workflow_registry.service import (
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.ui.admin_workflows import (
    build_workflow_draft_editor_model,
    build_workflow_registry_page_model,
    build_workflow_version_detail_model,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)

router = APIRouter(tags=["workflow-registry-ui"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _build_admin_service(
    session: AsyncSession, container: ContainerDep
) -> AdminService:
    return AdminService(
        workflow_repository=WorkflowRegistryRepository(session),
        artifact_repository=ArtifactRepository(session),
        audit_service=AuditService(AuditRepository(session)),
        storage_provider=container.storage_provider,
        workflow_registry_artifact_prefix=container.settings.workflow_registry_artifact_prefix,
        logger=container.logger,
    )


@router.get("/admin/workflows/ui", response_class=HTMLResponse, include_in_schema=False)
async def workflow_registry_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    service = _build_admin_service(session, container)
    items = await service.list_workflows(principal=principal)
    page = build_workflow_registry_page_model(items)
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/index.html",
        {
            "page": page,
            "principal": principal,
        },
    )


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/editor",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def workflow_draft_editor_page(
    workflow_draft_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    service = _build_admin_service(session, container)
    try:
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    metadata = service.workflow_registry_service().get_editor_metadata()
    page = build_workflow_draft_editor_model(
        draft=draft,
        metadata=metadata,
        conflict_message=(
            "A newer draft revision already exists. Refresh before saving again."
            if request.query_params.get("conflict") == "stale-save"
            else None
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/draft_editor.html",
        {
            "page": page,
            "principal": principal,
        },
    )


@router.get(
    "/admin/workflows/versions/{workflow_version_bundle_id}/detail",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def workflow_version_detail_page(
    workflow_version_bundle_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    service = _build_admin_service(session, container)
    try:
        version = await service.get_workflow_version(
            principal=principal,
            workflow_version_bundle_id=workflow_version_bundle_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    page = build_workflow_version_detail_model(version=version)
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/version_detail.html",
        {
            "page": page,
            "principal": principal,
        },
    )
