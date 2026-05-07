from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
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
ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
REACT_WORKFLOWS_PATH = "/admin/app/workflows"
LEGACY_QUERY_PRESERVE_KEYS = frozenset(
    {
        "tenant_id",
        "scope_filter",
        "status",
        "q",
        "saved_filter",
        "revision",
        "conflict",
    }
)


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


def _react_workflow_redirect(
    request: Request,
    suffix: str = "",
    *,
    extra_query: dict[str, str] | None = None,
) -> RedirectResponse:
    clean_suffix = suffix if not suffix or suffix.startswith("/") else f"/{suffix}"
    query: dict[str, str] = {
        key: value
        for key, value in request.query_params.items()
        if key in LEGACY_QUERY_PRESERVE_KEYS and len(value) <= 240
    }
    if extra_query:
        query.update(extra_query)
    target = f"{REACT_WORKFLOWS_PATH}{clean_suffix}"
    if query:
        target = f"{target}?{urlencode(query)}"
    return _redirect(target)


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


@router.get("/admin/workflows/ui", include_in_schema=False)
async def workflow_registry_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(request)


@router.get("/admin/workflows/new", include_in_schema=False)
async def workflow_draft_create_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(request, "/new")


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
    return _react_workflow_redirect(request, f"/drafts/{draft.workflow_draft_id}")


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/editor",
    include_in_schema=False,
)
async def workflow_draft_editor_page(
    workflow_draft_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(request, f"/drafts/{workflow_draft_id}")


@router.post(
    "/admin/workflows/drafts/{workflow_draft_id}/save-ui",
    include_in_schema=False,
)
async def workflow_draft_save_ui(
    workflow_draft_id: UUID,
    request: Request,
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
        return _react_workflow_redirect(
            request,
            f"/drafts/{workflow_draft_id}",
            extra_query={"conflict": "stale-save"},
        )
    return _redirect(f"{REACT_WORKFLOWS_PATH}/drafts/{updated.workflow_draft_id}")


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
    return _redirect(f"{REACT_WORKFLOWS_PATH}/drafts/{workflow_draft_id}")


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/revisions/ui",
    include_in_schema=False,
)
async def workflow_draft_revision_history_page(
    workflow_draft_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(request, f"/drafts/{workflow_draft_id}/revisions")


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
    return _redirect(f"{REACT_WORKFLOWS_PATH}/drafts/{workflow_draft_id}/revisions")


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
    return _redirect(f"{REACT_WORKFLOWS_PATH}/drafts/{draft.workflow_draft_id}")


@router.get(
    "/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui",
    include_in_schema=False,
)
async def workflow_publish_gate_page(
    workflow_draft_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(
        request,
        f"/drafts/{workflow_draft_id}/publish-gate",
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
        f"{REACT_WORKFLOWS_PATH}/versions/{version.workflow_version_bundle_id}"
    )


@router.get(
    "/admin/workflows/versions/{workflow_version_bundle_id}/detail",
    include_in_schema=False,
)
async def workflow_version_detail_page(
    workflow_version_bundle_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> RedirectResponse:
    _ = principal, session
    return _react_workflow_redirect(
        request,
        f"/versions/{workflow_version_bundle_id}",
    )
