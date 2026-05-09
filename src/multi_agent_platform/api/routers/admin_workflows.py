from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
from multi_agent_platform.api.schemas.admin_agent_graph import AgentCommunicationGraph
from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupResponse,
    GraphPreviewResponse,
    PublishGateRequest,
    PublishGateResponse,
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    CopyDraftRequest,
    DraftRevisionListResponse,
    PublishDraftRequest,
    RegistrySharingGrantCreateRequest,
    RegistrySharingGrantResponse,
    RestoreRevisionRequest,
    ValidationResultResponse,
    WorkflowDraftCreateRequest,
    WorkflowDraftResponse,
    WorkflowDraftSaveRequest,
    WorkflowRegistryListResponse,
    WorkflowVersionResponse,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)

router = APIRouter(prefix="/admin/workflows", tags=["workflow-registry"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
MAX_BUILDER_PAYLOAD_BYTES = 1_000_000


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


def _ensure_payload_size(payload: object) -> None:
    if not hasattr(payload, "model_dump_json"):
        return
    size_bytes = len(payload.model_dump_json().encode("utf-8"))
    if size_bytes > MAX_BUILDER_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="workflow builder payload exceeds the bounded request limit",
        )


@router.get("", response_model=WorkflowRegistryListResponse)
async def list_workflows(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    scope_filter: Annotated[str, Query()] = "all",
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search_query: Annotated[str | None, Query(alias="q")] = None,
) -> WorkflowRegistryListResponse:
    service = _build_admin_service(session, container)
    try:
        items = await service.list_workflows(
            principal=principal,
            scope_filter=scope_filter,
            status=status_filter,
            search_query=search_query,
        )
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return WorkflowRegistryListResponse(items=items)


@router.post(
    "", response_model=WorkflowDraftResponse, status_code=status.HTTP_201_CREATED
)
async def create_workflow_draft(
    payload: WorkflowDraftCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowDraftResponse:
    _ensure_payload_size(payload)
    service = _build_admin_service(session, container)
    try:
        return await service.create_workflow_draft(principal=principal, payload=payload)
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/editor-metadata", response_model=WorkflowEditorMetadataResponse)
async def get_editor_metadata(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowEditorMetadataResponse:
    _ = principal, session
    service = _build_admin_service(session, container)
    return service.workflow_registry_service().get_editor_metadata()


@router.get("/editor-lookups", response_model=EditorLookupResponse)
async def get_editor_lookups(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    workflow_draft_id: Annotated[UUID | None, Query()] = None,
    lookup_kind: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> EditorLookupResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.get_workflow_editor_lookups(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            lookup_kind=lookup_kind,
            search=search,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get("/drafts/{workflow_draft_id}", response_model=WorkflowDraftResponse)
async def get_workflow_draft(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowDraftResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.put("/drafts/{workflow_draft_id}", response_model=WorkflowDraftResponse)
async def save_workflow_draft(
    workflow_draft_id: UUID,
    payload: WorkflowDraftSaveRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowDraftResponse:
    _ensure_payload_size(payload)
    service = _build_admin_service(session, container)
    try:
        return await service.save_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=payload,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get(
    "/drafts/{workflow_draft_id}/graph-preview",
    response_model=GraphPreviewResponse,
)
async def get_workflow_graph_preview(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> GraphPreviewResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.get_workflow_graph_preview(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get(
    "/drafts/{workflow_draft_id}/agent-graph",
    response_model=AgentCommunicationGraph,
)
async def get_workflow_agent_graph(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> AgentCommunicationGraph:
    service = _build_admin_service(session, container)
    try:
        registry_service = service.workflow_registry_service()
        return await registry_service.get_agent_communication_graph_for_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get(
    "/drafts/{workflow_draft_id}/revisions",
    response_model=DraftRevisionListResponse,
)
async def list_workflow_draft_revisions(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> DraftRevisionListResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.list_workflow_draft_revisions(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post(
    "/drafts/{workflow_draft_id}/restore", response_model=WorkflowDraftResponse
)
async def restore_workflow_revision(
    workflow_draft_id: UUID,
    payload: RestoreRevisionRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowDraftResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.restore_workflow_revision(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=payload,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/drafts/{workflow_draft_id}/copy",
    response_model=WorkflowDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
async def copy_workflow_draft(
    workflow_draft_id: UUID,
    payload: CopyDraftRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowDraftResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.copy_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=payload,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/drafts/{workflow_draft_id}/validate",
    response_model=ValidationResultResponse,
)
async def validate_workflow_draft(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> ValidationResultResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.validate_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/drafts/{workflow_draft_id}/publish-gate",
    response_model=PublishGateResponse,
)
async def evaluate_workflow_publish_gate(
    workflow_draft_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    payload: PublishGateRequest | None = None,
) -> PublishGateResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=payload or PublishGateRequest(),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/drafts/{workflow_draft_id}/publish",
    response_model=WorkflowVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def publish_workflow_draft(
    workflow_draft_id: UUID,
    payload: PublishDraftRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowVersionResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.publish_workflow_draft(
            principal=principal,
            workflow_draft_id=workflow_draft_id,
            payload=payload,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (DraftConflictError, PublishConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ArtifactPersistenceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/versions/{workflow_version_bundle_id}",
    response_model=WorkflowVersionResponse,
)
async def get_workflow_version(
    workflow_version_bundle_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> WorkflowVersionResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.get_workflow_version(
            principal=principal,
            workflow_version_bundle_id=workflow_version_bundle_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get(
    "/versions/{workflow_version_bundle_id}/agent-graph",
    response_model=AgentCommunicationGraph,
)
async def get_workflow_version_agent_graph(
    workflow_version_bundle_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> AgentCommunicationGraph:
    service = _build_admin_service(session, container)
    try:
        registry_service = service.workflow_registry_service()
        return await registry_service.get_agent_communication_graph_for_version(
            principal=principal,
            workflow_version_bundle_id=workflow_version_bundle_id,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post(
    "/versions/{workflow_version_bundle_id}/sharing-grants",
    response_model=RegistrySharingGrantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow_sharing_grant(
    workflow_version_bundle_id: UUID,
    payload: RegistrySharingGrantCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> RegistrySharingGrantResponse:
    service = _build_admin_service(session, container)
    try:
        return await service.create_workflow_sharing_grant(
            principal=principal,
            workflow_version_bundle_id=workflow_version_bundle_id,
            payload=payload,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
