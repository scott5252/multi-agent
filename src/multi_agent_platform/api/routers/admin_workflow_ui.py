from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.admin.workflow_registry.service import (
    ArtifactPersistenceError,
    DraftConflictError,
    PublishConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import (
    build_shell_for_request,
    resolve_scope_for_request,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupResponse,
    GraphPreviewResponse,
    PublishGateRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    CopyDraftRequest,
    PublishDraftRequest,
    RestoreRevisionRequest,
    WorkflowDraftCreateRequest,
    WorkflowDraftDocument,
    WorkflowDraftSaveRequest,
    WorkflowKind,
    WorkflowScopeType,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    build_common_state,
    build_saved_filter_summary,
)
from multi_agent_platform.api.ui.admin_workflows import (
    build_workflow_draft_create_page_model,
    build_workflow_draft_editor_model,
    build_workflow_publish_gate_model,
    build_workflow_registry_page_model,
    build_workflow_revision_history_model,
    build_workflow_version_detail_model,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.admin_console import (
    AdminSavedFilterRepository,
)
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)

router = APIRouter(tags=["workflow-registry-ui"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")


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


def _redirect(path: str) -> RedirectResponse:
    return RedirectResponse(url=path, status_code=status.HTTP_303_SEE_OTHER)


def _tenant_id_for_ui_create(
    principal: PrincipalContext, scope_type: WorkflowScopeType
) -> UUID | None:
    if scope_type == WorkflowScopeType.PLATFORM:
        return None
    return principal.tenant_id or ACME_TENANT_ID


def _minimal_ready_document(
    *,
    slug: str,
    display_name: str,
    description: str | None,
    workflow_kind: WorkflowKind,
) -> WorkflowDraftDocument:
    return WorkflowDraftDocument.model_validate(
        {
            "workflow_key": slug,
            "display_name": display_name,
            "description": description or "Minimal ready draft.",
            "workflow_kind": workflow_kind.value,
            "entry_node_key": "done",
            "roles": [],
            "prompt_profile_references": [],
            "skill_installations": [],
            "contracts": [],
            "nodes": [
                {
                    "node_key": "done",
                    "node_type": "terminal",
                    "display_name": "Done",
                }
            ],
            "edges": [],
            "join_policies": [],
            "approval_gates": [],
            "subworkflow_refs": [],
            "test_requirements": [],
        }
    )


def _blocked_readiness_document(
    *,
    slug: str,
    display_name: str,
    description: str | None,
    workflow_kind: WorkflowKind,
) -> WorkflowDraftDocument:
    return WorkflowDraftDocument.model_validate(
        {
            "workflow_key": slug,
            "display_name": display_name,
            "description": description or "Draft with deliberate readiness gaps.",
            "workflow_kind": workflow_kind.value,
            "entry_node_key": "intake",
            "roles": [
                {
                    "role_key": "triage",
                    "display_name": "Triage",
                    "purpose": "Classify the request.",
                    "input_contract_key": "intake-request",
                    "output_contract_key": "triage-result",
                    "skill_bindings": [],
                }
            ],
            "prompt_profile_references": [
                {
                    "reference_key": "triage-profile",
                    "role_key": "triage",
                    "agent_key": "triage-agent",
                    "readiness_status": "retired",
                    "model_routing_preview": {
                        "preview_key": "triage-route",
                        "model_id": "example-model",
                        "health_state": "degraded",
                        "policy_status": "blocked",
                    },
                }
            ],
            "skill_installations": [
                {
                    "skill_installation_key": "triage-skill",
                    "skill_slug": "triage-agent",
                    "skill_version": "latest",
                    "credential_requirement_status": "missing",
                }
            ],
            "contracts": [
                {
                    "contract_key": "intake-request",
                    "display_name": "Intake Request",
                    "json_schema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    },
                },
                {
                    "contract_key": "triage-result",
                    "display_name": "Triage Result",
                    "json_schema": {
                        "type": "object",
                        "properties": {"decision": {"type": "string"}},
                    },
                },
            ],
            "nodes": [
                {
                    "node_key": "intake",
                    "node_type": "role",
                    "display_name": "Intake",
                    "role_key": "triage",
                },
                {
                    "node_key": "terminal",
                    "node_type": "terminal",
                    "display_name": "Done",
                },
            ],
            "edges": [
                {
                    "edge_key": "unbounded-loop",
                    "source_node_key": "intake",
                    "target_node_key": "intake",
                    "contract_key": "triage-result",
                }
            ],
            "join_policies": [],
            "approval_gates": [],
            "subworkflow_refs": [
                {
                    "alias": "qa-child",
                    "workflow_version_ref": "missing-bundle",
                }
            ],
            "test_requirements": [
                {
                    "requirement_key": "smoke",
                    "suite_id": "qa013-smoke",
                    "latest_result_status": "missing",
                }
            ],
        }
    )


def _document_for_template(
    *,
    starter_template: str,
    slug: str,
    display_name: str,
    description: str | None,
    workflow_kind: WorkflowKind,
) -> WorkflowDraftDocument:
    if starter_template == "qa013_blocked_readiness":
        return _blocked_readiness_document(
            slug=slug,
            display_name=display_name,
            description=description,
            workflow_kind=workflow_kind,
        )
    return _minimal_ready_document(
        slug=slug,
        display_name=display_name,
        description=description,
        workflow_kind=workflow_kind,
    )


@router.get("/admin/workflows/ui", response_class=HTMLResponse, include_in_schema=False)
async def workflow_registry_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    scope_filter: Annotated[str, Query()] = "all",
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search_query: Annotated[str | None, Query(alias="q")] = None,
) -> HTMLResponse:
    service = _build_admin_service(session, container)
    items = await service.list_workflows(
        principal=principal,
        scope_filter=scope_filter,
        status=status_filter,
        search_query=search_query,
    )
    page = build_workflow_registry_page_model(
        items,
        scope_filter=scope_filter,
        status_filter=status_filter,
        search_query=search_query,
    )
    active_scope = await resolve_scope_for_request(
        request=request,
        principal=principal,
        session=session,
    )
    saved_filter_records = await AdminSavedFilterRepository(session).list_filters(
        principal=principal,
        admin_area="workflows",
        scope=active_scope,
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Workflow Registry",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
        ),
        common_state=build_common_state(
            CommonStateType.EMPTY,
            title="No workflow records",
            summary="No workflow drafts or versions are visible in this scope.",
            trace_id=principal.trace_id,
        )
        if not items
        else None,
        saved_filters=tuple(
            build_saved_filter_summary(record, active_scope=active_scope)
            for record in saved_filter_records
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/index.html",
        {
            "page": page,
            "principal": principal,
            "shell": shell,
        },
    )


@router.get(
    "/admin/workflows/new", response_class=HTMLResponse, include_in_schema=False
)
async def workflow_draft_create_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    service = _build_admin_service(session, container)
    metadata = service.workflow_registry_service().get_editor_metadata()
    page = build_workflow_draft_create_page_model(metadata)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Create Workflow Draft",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
            BreadcrumbItem(label="Create", href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/create.html",
        {
            "page": page,
            "principal": principal,
            "shell": shell,
        },
    )


@router.post("/admin/workflows/new", include_in_schema=False)
async def workflow_draft_create_submit(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    scope_type: Annotated[str, Form()],
    workflow_kind: Annotated[str, Form()],
    slug: Annotated[str, Form()],
    display_name: Annotated[str, Form()],
    starter_template: Annotated[str, Form()] = "minimal_ready",
    description: Annotated[str, Form()] = "",
) -> RedirectResponse:
    _ = request
    service = _build_admin_service(session, container)
    scope = WorkflowScopeType(scope_type)
    kind = WorkflowKind(workflow_kind)
    document = _document_for_template(
        starter_template=starter_template,
        slug=slug,
        display_name=display_name,
        description=description or None,
        workflow_kind=kind,
    )
    try:
        draft = await service.create_workflow_draft(
            principal=principal,
            payload=WorkflowDraftCreateRequest(
                scope_type=scope,
                tenant_id=_tenant_id_for_ui_create(principal, scope),
                workflow_kind=kind,
                slug=slug,
                display_name=display_name,
                description=description or None,
                document=document,
            ),
        )
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _redirect(f"/admin/workflows/drafts/{draft.workflow_draft_id}/editor")


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
    graph_preview = (
        await service.get_workflow_graph_preview(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
        if hasattr(service, "get_workflow_graph_preview")
        else GraphPreviewResponse()
    )
    lookups = (
        await service.get_workflow_editor_lookups(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
        if hasattr(service, "get_workflow_editor_lookups")
        else EditorLookupResponse()
    )
    page = build_workflow_draft_editor_model(
        draft=draft,
        metadata=metadata,
        graph_preview=graph_preview,
        lookups=lookups,
        conflict_message=(
            "A newer draft revision already exists. Refresh before saving again."
            if request.query_params.get("conflict") == "stale-save"
            else None
        ),
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.draft.display_name,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
            BreadcrumbItem(label=page.draft.display_name, href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/draft_editor.html",
        {
            "page": page,
            "principal": principal,
            "shell": shell,
        },
    )


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/save-ui",
    include_in_schema=False,
)
async def workflow_draft_save_ui(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    base_revision_number: Annotated[int, Form()],
    description: Annotated[str, Form()] = "",
    change_summary: Annotated[str, Form()] = "UI save",
) -> RedirectResponse:
    service = _build_admin_service(session, container)
    try:
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
        document = draft.document.model_copy(update={"description": description})
        updated = await service.save_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=WorkflowDraftSaveRequest(
                base_revision_number=base_revision_number,
                display_name=draft.display_name,
                description=description,
                document=document,
                change_summary=change_summary,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError:
        return _redirect(
            f"/admin/workflows/drafts/{workflow_draft_id}/editor?conflict=stale-save"
        )
    return _redirect(f"/admin/workflows/drafts/{updated.workflow_draft_id}/editor")


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/validate/ui",
    include_in_schema=False,
)
async def workflow_draft_validate_ui(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> RedirectResponse:
    service = _build_admin_service(session, container)
    try:
        await service.validate_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _redirect(f"/admin/workflows/drafts/{workflow_draft_id}/editor")


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/revisions/ui",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def workflow_draft_revision_history_page(
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
        revisions = await service.list_workflow_draft_revisions(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    page = build_workflow_revision_history_model(draft=draft, revisions=revisions)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=f"{draft.display_name} Revisions",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
            BreadcrumbItem(
                label=draft.display_name,
                href=f"/admin/workflows/drafts/{workflow_draft_id}/editor",
            ),
            BreadcrumbItem(label="Revisions", href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/revision_history.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/restore/ui",
    include_in_schema=False,
)
async def workflow_draft_restore_ui(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    revision_number: Annotated[int, Form()],
    base_revision_number: Annotated[int, Form()],
    change_summary: Annotated[str, Form()] = "Restore from browser UI",
) -> RedirectResponse:
    service = _build_admin_service(session, container)
    try:
        await service.restore_workflow_revision(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=RestoreRevisionRequest(
                revision_number=revision_number,
                base_revision_number=base_revision_number,
                change_summary=change_summary,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _redirect(f"/admin/workflows/drafts/{workflow_draft_id}/revisions/ui")


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/copy/ui",
    include_in_schema=False,
)
async def workflow_draft_copy_ui(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    source_revision_number: Annotated[int, Form()],
    new_slug: Annotated[str, Form()],
    display_name: Annotated[str, Form()],
    change_summary: Annotated[str, Form()] = "Copied from browser UI",
) -> RedirectResponse:
    service = _build_admin_service(session, container)
    try:
        draft = await service.copy_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=CopyDraftRequest(
                source_revision_number=source_revision_number,
                new_slug=new_slug,
                display_name=display_name,
                change_summary=change_summary,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _redirect(f"/admin/workflows/drafts/{draft.workflow_draft_id}/editor")


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def workflow_publish_gate_page(
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
        gate = await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=PublishGateRequest(),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    page = build_workflow_publish_gate_model(draft=draft, gate=gate)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=f"{draft.display_name} Publish Gate",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
            BreadcrumbItem(
                label=draft.display_name,
                href=f"/admin/workflows/drafts/{workflow_draft_id}/editor",
            ),
            BreadcrumbItem(label="Publish Gate", href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/publish_gate.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/publish/ui",
    include_in_schema=False,
)
async def workflow_draft_publish_ui(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    validation_result_id: Annotated[UUID, Form()],
    publish_gate_id: Annotated[str, Form()],
    reason: Annotated[str, Form()] = "Publish from browser UI",
) -> RedirectResponse:
    service = _build_admin_service(session, container)
    try:
        version = await service.publish_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=PublishDraftRequest(
                validation_result_id=validation_result_id,
                publish_gate_id=publish_gate_id or None,
                reason=reason,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (DraftConflictError, PublishConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ArtifactPersistenceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _redirect(
        f"/admin/workflows/versions/{version.workflow_version_bundle_id}/detail"
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
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=f"{page.version.display_name} {page.version.display_version}",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Workflow Registry", href="/admin/workflows/ui"),
            BreadcrumbItem(label=page.version.display_name, href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "workflows/version_detail.html",
        {
            "page": page,
            "principal": principal,
            "shell": shell,
        },
    )
