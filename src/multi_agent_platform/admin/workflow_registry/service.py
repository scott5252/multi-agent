from __future__ import annotations

import json
from enum import Enum
from hashlib import sha256
from logging import Logger
from uuid import UUID

from multi_agent_platform.admin.workflow_registry.field_help import (
    build_editor_metadata,
)
from multi_agent_platform.admin.workflow_registry.validation import (
    validate_authoring_document,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftCreateRequest,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowDraftSaveRequest,
    WorkflowKind,
    WorkflowRegistryItem,
    WorkflowScopeType,
    WorkflowVisibilityStatus,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftStatus,
    WorkflowLineage,
    WorkflowLineageStatus,
)
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowDraftRecord,
    WorkflowRegistryRepository,
)
from multi_agent_platform.observability.logging import workflow_log_context
from multi_agent_platform.observability.metrics import (
    WORKFLOW_REGISTRY_ACTION_COUNTER,
)
from multi_agent_platform.tenancy.guards import (
    ScopeError,
    can_view_workflow_scope,
    require_workflow_scope_access,
)


class WorkflowRegistryError(RuntimeError):
    pass


class WorkflowNotFoundError(WorkflowRegistryError):
    pass


class WorkflowAccessError(WorkflowRegistryError):
    pass


class DraftConflictError(WorkflowRegistryError):
    pass


def _enum_value(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _canonical_document_json(
    document: WorkflowDraftDocument,
) -> tuple[dict[str, object], str]:
    payload = document.model_dump(mode="json")
    digest = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return payload, digest


class WorkflowRegistryService:
    def __init__(
        self,
        *,
        repository: WorkflowRegistryRepository,
        audit_service: AuditService | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.repository = repository
        self.audit_service = audit_service
        self.logger = logger

    async def list_registry(
        self,
        *,
        principal: PrincipalContext,
        scope_filter: str = "all",
        status: str | None = None,
    ) -> list[WorkflowRegistryItem]:
        include_platform = (
            "platform_admin" in principal.role_codes and principal.tenant_id is not None
        )
        lineages = await self.repository.list_visible_lineages(
            tenant_id=principal.tenant_id,
            include_platform=include_platform,
            scope_filter=scope_filter,
        )
        items: list[WorkflowRegistryItem] = []
        for lineage in lineages:
            draft = await self.repository.find_active_draft_for_lineage(
                lineage.workflow_lineage_id
            )
            if draft is None:
                continue
            if status not in (None, "", "draft"):
                continue
            if not can_view_workflow_scope(
                principal,
                scope_type=lineage.scope_type,
                tenant_id=lineage.tenant_id,
            ):
                continue
            items.append(
                WorkflowRegistryItem(
                    workflow_lineage_id=lineage.workflow_lineage_id,
                    workflow_draft_id=draft.workflow_draft_id,
                    slug=lineage.slug,
                    display_name=lineage.display_name,
                    workflow_kind=WorkflowKind(_enum_value(lineage.workflow_kind)),
                    scope_type=WorkflowScopeType(lineage.scope_type),
                    tenant_id=lineage.tenant_id,
                    visibility_status=WorkflowVisibilityStatus.DRAFT,
                    current_revision_number=draft.current_revision_number,
                    updated_at=draft.updated_at,
                )
            )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="list", scope_type=principal.scope_type.value
        ).inc()
        return items

    async def create_draft(
        self,
        *,
        principal: PrincipalContext,
        payload: WorkflowDraftCreateRequest,
    ) -> WorkflowDraftResponse:
        principal_id = self._principal_identity_id(principal)
        try:
            resolved_tenant_id = require_workflow_scope_access(
                principal,
                scope_type=payload.scope_type.value,
                tenant_id=payload.tenant_id,
            )
        except ScopeError as exc:
            raise WorkflowAccessError(str(exc)) from exc

        existing = await self.repository.get_lineage_by_slug(
            scope_type=payload.scope_type.value,
            tenant_id=resolved_tenant_id,
            slug=payload.slug,
        )
        if existing is not None:
            raise WorkflowRegistryError("workflow slug already exists in this scope")

        _ = validate_authoring_document(payload.document)
        document_json, document_sha256 = _canonical_document_json(payload.document)
        lineage = await self.repository.create_lineage(
            WorkflowLineage(
                scope_type=payload.scope_type.value,
                tenant_id=resolved_tenant_id,
                slug=payload.slug,
                display_name=payload.display_name,
                description=payload.description,
                workflow_kind=payload.workflow_kind,
                status=WorkflowLineageStatus.DRAFTING,
                created_by_principal_id=principal_id,
            )
        )
        draft = await self.repository.create_draft(
            WorkflowDraft(
                workflow_lineage_id=lineage.workflow_lineage_id,
                scope_type=lineage.scope_type,
                tenant_id=lineage.tenant_id,
                status=WorkflowDraftStatus.ACTIVE,
                current_revision_number=0,
                created_by_principal_id=principal_id,
                last_edited_by_principal_id=principal_id,
            )
        )
        record = await self.repository.save_revision(
            draft=draft,
            document_json=document_json,
            document_sha256=document_sha256,
            change_summary="Initial draft",
            principal_identity_id=principal_id,
        )
        record.lineage.display_name = payload.display_name
        record.lineage.description = payload.description
        await self.repository.session.flush()
        await self._record_event(
            principal=principal,
            action="workflow_registry.create_draft",
            record=record,
        )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="create_draft",
            scope_type=payload.scope_type.value,
        ).inc()
        return self._to_response(record)

    async def get_draft(
        self,
        *,
        principal: PrincipalContext,
        workflow_draft_id: UUID,
    ) -> WorkflowDraftResponse:
        record = await self.repository.get_draft_record(workflow_draft_id)
        if record is None:
            raise WorkflowNotFoundError("workflow draft not found")
        self._ensure_visible(principal, record)
        return self._to_response(record)

    async def save_draft(
        self,
        *,
        principal: PrincipalContext,
        workflow_draft_id: UUID,
        payload: WorkflowDraftSaveRequest,
    ) -> WorkflowDraftResponse:
        principal_id = self._principal_identity_id(principal)
        record = await self.repository.get_draft_record(workflow_draft_id)
        if record is None:
            raise WorkflowNotFoundError("workflow draft not found")
        self._ensure_editable(principal, record)
        if record.draft.current_revision_number != payload.base_revision_number:
            raise DraftConflictError("workflow draft revision is stale")
        _ = validate_authoring_document(payload.document)
        document_json, document_sha256 = _canonical_document_json(payload.document)
        record.lineage.display_name = payload.display_name
        record.lineage.description = payload.description
        updated = await self.repository.save_revision(
            draft=record.draft,
            document_json=document_json,
            document_sha256=document_sha256,
            change_summary=payload.change_summary,
            principal_identity_id=principal_id,
        )
        updated.lineage.display_name = payload.display_name
        updated.lineage.description = payload.description
        await self.repository.session.flush()
        await self._record_event(
            principal=principal,
            action="workflow_registry.save_draft",
            record=updated,
        )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="save_draft",
            scope_type=updated.lineage.scope_type,
        ).inc()
        return self._to_response(updated)

    def get_editor_metadata(self) -> WorkflowEditorMetadataResponse:
        return build_editor_metadata()

    def _ensure_visible(
        self,
        principal: PrincipalContext,
        record: WorkflowDraftRecord,
    ) -> None:
        if not can_view_workflow_scope(
            principal,
            scope_type=record.lineage.scope_type,
            tenant_id=record.lineage.tenant_id,
        ):
            raise WorkflowAccessError("workflow draft is outside the current scope")

    def _ensure_editable(
        self,
        principal: PrincipalContext,
        record: WorkflowDraftRecord,
    ) -> None:
        self._ensure_visible(principal, record)
        try:
            require_workflow_scope_access(
                principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
            )
        except ScopeError as exc:
            raise WorkflowAccessError(str(exc)) from exc

    def _principal_identity_id(self, principal: PrincipalContext) -> UUID:
        if principal.principal_identity_id is None:
            raise WorkflowAccessError("workflow actions require a persisted identity")
        return principal.principal_identity_id

    def _to_response(self, record: WorkflowDraftRecord) -> WorkflowDraftResponse:
        return WorkflowDraftResponse(
            workflow_draft_id=record.draft.workflow_draft_id,
            workflow_lineage_id=record.lineage.workflow_lineage_id,
            slug=record.lineage.slug,
            display_name=record.lineage.display_name,
            description=record.lineage.description,
            scope_type=WorkflowScopeType(record.lineage.scope_type),
            tenant_id=record.lineage.tenant_id,
            workflow_kind=WorkflowKind(_enum_value(record.lineage.workflow_kind)),
            status=_enum_value(record.draft.status),
            current_revision_number=record.draft.current_revision_number,
            latest_revision=WorkflowDraftRevisionResponse(
                workflow_draft_revision_id=record.revision.workflow_draft_revision_id,
                revision_number=record.revision.revision_number,
                document_sha256=record.revision.document_sha256,
                change_summary=record.revision.change_summary,
                created_at=record.revision.created_at,
            ),
            document=WorkflowDraftDocument.model_validate(
                record.revision.authoring_document_json
            ),
            updated_at=record.draft.updated_at,
        )

    async def _record_event(
        self,
        *,
        principal: PrincipalContext,
        action: str,
        record: WorkflowDraftRecord,
    ) -> None:
        if self.logger is not None:
            self.logger.info(
                action,
                extra=workflow_log_context(
                    action=action,
                    scope_type=record.lineage.scope_type,
                    trace_id=principal.trace_id,
                    workflow_lineage_id=str(record.lineage.workflow_lineage_id),
                    workflow_draft_id=str(record.draft.workflow_draft_id),
                    principal_id=principal.principal_id,
                ),
            )
        if self.audit_service is not None:
            await self.audit_service.record_workflow_event(
                principal=principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
                action=action,
                entity_type="workflow_draft",
                entity_id=str(record.draft.workflow_draft_id),
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted={
                    "slug": record.lineage.slug,
                    "revision_number": str(record.draft.current_revision_number),
                },
            )
