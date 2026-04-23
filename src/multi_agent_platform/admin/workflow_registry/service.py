from __future__ import annotations

import json
from enum import Enum
from hashlib import sha256
from logging import Logger
from uuid import UUID

from multi_agent_platform.admin.workflow_registry.compiler import (
    compile_workflow_blueprint,
)
from multi_agent_platform.admin.workflow_registry.field_help import (
    build_editor_metadata,
)
from multi_agent_platform.admin.workflow_registry.sharing import (
    can_grant_workflow_version_to_tenant,
)
from multi_agent_platform.admin.workflow_registry.validation import (
    validate_authoring_document,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    PublishDraftRequest,
    RegistrySharingGrantCreateRequest,
    RegistrySharingGrantResponse,
    ValidationFindingResponse,
    ValidationResultResponse,
    WorkflowDraftCreateRequest,
    WorkflowDraftDocument,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
    WorkflowDraftSaveRequest,
    WorkflowKind,
    WorkflowRegistryItem,
    WorkflowScopeType,
    WorkflowVersionResponse,
    WorkflowVisibilityStatus,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.artifact import ArtifactRecord
from multi_agent_platform.db.models.workflow_registry import (
    RegistrySharingGrant,
    ValidationResult,
    ValidationResultStatus,
    WorkflowDraft,
    WorkflowDraftStatus,
    WorkflowLineage,
    WorkflowLineageStatus,
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowDraftRecord,
    WorkflowRegistryRepository,
    WorkflowVersionRecord,
)
from multi_agent_platform.observability.logging import workflow_log_context
from multi_agent_platform.observability.metrics import (
    WORKFLOW_REGISTRY_ACTION_COUNTER,
)
from multi_agent_platform.runtime.versioning import (
    build_run_version_bundle,
    get_workflow_registry_compiler_version,
)
from multi_agent_platform.runtime.workflow_bundle import bundle_storage_key
from multi_agent_platform.storage.base import StorageProvider
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


class PublishConflictError(WorkflowRegistryError):
    pass


class ArtifactPersistenceError(WorkflowRegistryError):
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
        artifact_repository: ArtifactRepository,
        storage_provider: StorageProvider,
        artifact_prefix: str,
        audit_service: AuditService | None = None,
        logger: Logger | None = None,
    ) -> None:
        self.repository = repository
        self.artifact_repository = artifact_repository
        self.storage_provider = storage_provider
        self.artifact_prefix = artifact_prefix
        self.audit_service = audit_service
        self.logger = logger

    async def list_registry(
        self,
        *,
        principal: PrincipalContext,
        scope_filter: str = "all",
        status: str | None = None,
    ) -> list[WorkflowRegistryItem]:
        items: list[WorkflowRegistryItem] = []
        is_platform_admin = "platform_admin" in principal.role_codes

        if status in (None, "", "draft"):
            lineages = await self.repository.list_visible_lineages(
                tenant_id=principal.tenant_id,
                include_platform=is_platform_admin,
                scope_filter=scope_filter,
            )
            for lineage in lineages:
                draft = await self.repository.find_active_draft_for_lineage(
                    lineage.workflow_lineage_id
                )
                if draft is None:
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

        if status in (None, "", "published", "hidden", "retired"):
            versions = await self.repository.list_versions(scope_filter=scope_filter)
            for version in versions:
                record = await self.repository.get_version_record(
                    version.workflow_version_bundle_id
                )
                if record is None or not await self._can_view_version(
                    principal=principal,
                    record=record,
                ):
                    continue
                if status not in (None, "", _enum_value(record.version.status)):
                    continue
                items.append(self._to_registry_item_from_version(record))

        items.sort(key=lambda item: item.updated_at, reverse=True)
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="list",
            scope_type=principal.scope_type.value,
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

        _ = validate_authoring_document(payload.document)
        document_json, document_sha256 = _canonical_document_json(payload.document)
        lineage, created_from_version_id = await self._resolve_create_target(
            principal=principal,
            payload=payload,
            resolved_tenant_id=resolved_tenant_id,
            principal_id=principal_id,
        )
        if (
            await self.repository.find_active_draft_for_lineage(
                lineage.workflow_lineage_id
            )
            is not None
        ):
            raise WorkflowRegistryError(
                "an active draft already exists for this lineage"
            )

        draft = await self.repository.create_draft(
            WorkflowDraft(
                workflow_lineage_id=lineage.workflow_lineage_id,
                scope_type=lineage.scope_type,
                tenant_id=lineage.tenant_id,
                status=WorkflowDraftStatus.ACTIVE,
                current_revision_number=0,
                created_from_version_id=created_from_version_id,
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
        await self.repository.supersede_validation_results_for_draft(
            record.draft.workflow_draft_id
        )
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

    async def validate_draft(
        self,
        *,
        principal: PrincipalContext,
        workflow_draft_id: UUID,
    ) -> ValidationResultResponse:
        principal_id = self._principal_identity_id(principal)
        record = await self.repository.get_draft_record(workflow_draft_id)
        if record is None:
            raise WorkflowNotFoundError("workflow draft not found")
        self._ensure_editable(principal, record)
        latest_published_version = (
            await self.repository.get_latest_published_version_for_lineage(
                record.lineage.workflow_lineage_id
            )
        )
        available_subworkflow_ids = await self._visible_subworkflow_version_ids(
            principal=principal,
            document=WorkflowDraftDocument.model_validate(
                record.revision.authoring_document_json
            ),
        )
        previous_contract_schemas: dict[str, object] = {}
        if latest_published_version is not None:
            raw_contract_schemas = (
                latest_published_version.summary_json.get("contracts_by_key", {})
                if isinstance(latest_published_version.summary_json, dict)
                else {}
            )
            if isinstance(raw_contract_schemas, dict):
                previous_contract_schemas = {
                    str(key): value for key, value in raw_contract_schemas.items()
                }
        findings = validate_authoring_document(
            WorkflowDraftDocument.model_validate(
                record.revision.authoring_document_json
            ),
            available_subworkflow_version_ids=available_subworkflow_ids,
            previous_contract_schemas=previous_contract_schemas,
        )
        await self.repository.supersede_validation_results_for_revision(
            record.revision.workflow_draft_revision_id
        )
        blocking_issue_count = sum(
            1 for finding in findings if finding["severity"] == "blocking"
        )
        advisory_issue_count = sum(
            1 for finding in findings if finding["severity"] == "advisory"
        )
        validation_result = await self.repository.create_validation_result(
            ValidationResult(
                workflow_draft_revision_id=record.revision.workflow_draft_revision_id,
                rule_set_version="workflow-registry-rules-0.1",
                status=(
                    ValidationResultStatus.PASSED
                    if blocking_issue_count == 0
                    else ValidationResultStatus.FAILED
                ),
                blocking_issue_count=blocking_issue_count,
                advisory_issue_count=advisory_issue_count,
                findings_json={"findings": findings},
                executed_by_principal_id=principal_id,
            )
        )
        await self.repository.session.flush()
        response = self._to_validation_response(validation_result)
        await self._record_event(
            principal=principal,
            action="workflow_registry.validate_draft",
            record=record,
            payload={
                "validation_result_id": str(validation_result.validation_result_id),
                "blocking_issue_count": str(blocking_issue_count),
            },
        )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="validate_draft",
            scope_type=record.lineage.scope_type,
        ).inc()
        return response

    async def publish_draft(
        self,
        *,
        principal: PrincipalContext,
        workflow_draft_id: UUID,
        payload: PublishDraftRequest,
    ) -> WorkflowVersionResponse:
        principal_id = self._principal_identity_id(principal)
        record = await self.repository.get_draft_record(workflow_draft_id)
        if record is None:
            raise WorkflowNotFoundError("workflow draft not found")
        self._ensure_editable(principal, record)
        validation_result = await self.repository.get_validation_result(
            payload.validation_result_id
        )
        if validation_result is None:
            raise PublishConflictError("validation result not found")
        if (
            validation_result.workflow_draft_revision_id
            != record.revision.workflow_draft_revision_id
        ):
            raise PublishConflictError(
                "validation result does not match current draft revision"
            )
        latest_validation = await self.repository.get_latest_validation_for_revision(
            record.revision.workflow_draft_revision_id
        )
        if (
            latest_validation is None
            or latest_validation.validation_result_id
            != validation_result.validation_result_id
            or validation_result.status != ValidationResultStatus.PASSED
        ):
            raise PublishConflictError(
                "validation result is stale or failed publish readiness"
            )

        document = WorkflowDraftDocument.model_validate(
            record.revision.authoring_document_json
        )
        version_sequence = await self.repository.next_version_sequence(
            record.lineage.workflow_lineage_id
        )
        display_version = f"v{version_sequence}"
        compiler_version = get_workflow_registry_compiler_version()
        compiled_bundle = compile_workflow_blueprint(
            workflow_lineage_id=str(record.lineage.workflow_lineage_id),
            revision_sha256=record.revision.document_sha256,
            document=document,
            version_sequence=version_sequence,
            display_version=display_version,
            compiler_version=compiler_version,
        )
        compiled_bundle_digest = compiled_bundle.digest()
        artifact_key = bundle_storage_key(self.artifact_prefix, compiled_bundle_digest)
        compiled_payload = compiled_bundle.canonical_json()
        try:
            artifact_handle = await self.storage_provider.put(
                artifact_key, compiled_payload
            )
        except Exception as exc:  # pragma: no cover - exercised in integration test
            raise ArtifactPersistenceError(
                "compiled bundle artifact persistence failed"
            ) from exc
        artifact = await self.artifact_repository.create(
            ArtifactRecord(
                tenant_id=record.lineage.tenant_id,
                scope_type=record.lineage.scope_type,
                provider=artifact_handle.provider,
                storage_key=artifact_handle.key,
                media_type="application/json",
                size_bytes=artifact_handle.size_bytes,
                checksum=compiled_bundle_digest,
                retention_class="immutable",
            )
        )
        previous_version = (
            await self.repository.get_latest_published_version_for_lineage(
                record.lineage.workflow_lineage_id
            )
        )
        run_version_bundle = build_run_version_bundle(
            workflow_version_bundle_id="pending",
            compiled_bundle=compiled_bundle,
        )
        version_bundle = await self.repository.create_version_bundle(
            WorkflowVersionBundle(
                workflow_lineage_id=record.lineage.workflow_lineage_id,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
                version_sequence=version_sequence,
                display_version=display_version,
                status=WorkflowVersionStatus.PUBLISHED,
                published_from_draft_id=record.draft.workflow_draft_id,
                published_from_revision_id=record.revision.workflow_draft_revision_id,
                validation_result_id=validation_result.validation_result_id,
                previous_version_bundle_id=(
                    previous_version.workflow_version_bundle_id
                    if previous_version is not None
                    else None
                ),
                compiled_bundle_artifact_id=artifact.artifact_id,
                compiled_bundle_digest=compiled_bundle_digest,
                compiler_version=compiler_version,
                summary_json={
                    "workflow_key": document.workflow_key,
                    "entry_node_key": document.entry_node_key,
                    "contracts_by_key": {
                        contract.contract_key: contract.json_schema
                        for contract in document.contracts
                    },
                    "skill_versions": run_version_bundle.pinned_skill_versions,
                    "subworkflow_refs": run_version_bundle.subworkflow_version_refs,
                    "run_version_blueprint": compiled_bundle.run_version_blueprint,
                },
                published_by_principal_id=principal_id,
            )
        )
        version_bundle.summary_json["run_version_bundle"] = (
            run_version_bundle.model_dump(mode="json")
        )
        record.draft.status = WorkflowDraftStatus.PUBLISHED_SOURCE
        record.lineage.status = WorkflowLineageStatus.PUBLISHED
        record.lineage.latest_published_version_id = (
            version_bundle.workflow_version_bundle_id
        )
        await self.repository.session.flush()
        version_record = await self.repository.get_version_record(
            version_bundle.workflow_version_bundle_id
        )
        if version_record is None:
            raise WorkflowRegistryError("published workflow version is unavailable")
        await self._record_event(
            principal=principal,
            action="workflow_registry.publish_draft",
            record=record,
            payload={
                "workflow_version_bundle_id": str(
                    version_bundle.workflow_version_bundle_id
                ),
                "compiled_bundle_digest": compiled_bundle_digest,
            },
        )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="publish_draft",
            scope_type=record.lineage.scope_type,
        ).inc()
        return self._to_version_response(version_record)

    async def get_version(
        self,
        *,
        principal: PrincipalContext,
        workflow_version_bundle_id: UUID,
    ) -> WorkflowVersionResponse:
        record = await self.repository.get_version_record(workflow_version_bundle_id)
        if record is None:
            raise WorkflowNotFoundError("workflow version not found")
        if not await self._can_view_version(principal=principal, record=record):
            raise WorkflowAccessError("workflow version is outside the current scope")
        return self._to_version_response(record)

    async def create_sharing_grant(
        self,
        *,
        principal: PrincipalContext,
        workflow_version_bundle_id: UUID,
        payload: RegistrySharingGrantCreateRequest,
    ) -> RegistrySharingGrantResponse:
        principal_id = self._principal_identity_id(principal)
        if "platform_admin" not in principal.role_codes:
            raise WorkflowAccessError("sharing grants require platform_admin")
        record = await self.repository.get_version_record(workflow_version_bundle_id)
        if record is None:
            raise WorkflowNotFoundError("workflow version not found")
        if not can_grant_workflow_version_to_tenant(
            scope_type=record.version.scope_type
        ):
            raise WorkflowAccessError("only platform-scoped versions can be shared")
        existing = await self.repository.get_active_sharing_grant(
            workflow_version_bundle_id=workflow_version_bundle_id,
            grantee_tenant_id=payload.grantee_tenant_id,
        )
        if existing is not None:
            return self._to_sharing_grant_response(existing)
        sharing_grant = await self.repository.create_sharing_grant(
            RegistrySharingGrant(
                workflow_version_bundle_id=workflow_version_bundle_id,
                grantee_tenant_id=payload.grantee_tenant_id,
                granted_by_principal_id=principal_id,
            )
        )
        await self.repository.session.flush()
        if self.audit_service is not None:
            await self.audit_service.record_workflow_event(
                principal=principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
                action="workflow_registry.create_sharing_grant",
                entity_type="workflow_version_bundle",
                entity_id=str(record.version.workflow_version_bundle_id),
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted={"grantee_tenant_id": str(payload.grantee_tenant_id)},
            )
        WORKFLOW_REGISTRY_ACTION_COUNTER.labels(
            action="create_sharing_grant",
            scope_type=record.lineage.scope_type,
        ).inc()
        return self._to_sharing_grant_response(sharing_grant)

    def get_editor_metadata(self) -> WorkflowEditorMetadataResponse:
        return build_editor_metadata()

    async def _resolve_create_target(
        self,
        *,
        principal: PrincipalContext,
        payload: WorkflowDraftCreateRequest,
        resolved_tenant_id: UUID | None,
        principal_id: UUID,
    ) -> tuple[WorkflowLineage, UUID | None]:
        if payload.created_from_version_id is not None:
            version_record = await self.repository.get_version_record(
                payload.created_from_version_id
            )
            if version_record is None:
                raise WorkflowNotFoundError("source workflow version not found")
            if not await self._can_view_version(
                principal=principal, record=version_record
            ):
                raise WorkflowAccessError(
                    "source workflow version is outside the current scope"
                )
            if (
                version_record.lineage.scope_type == payload.scope_type.value
                and version_record.lineage.tenant_id == resolved_tenant_id
                and version_record.lineage.slug == payload.slug
            ):
                return (
                    version_record.lineage,
                    version_record.version.workflow_version_bundle_id,
                )

        existing = await self.repository.get_lineage_by_slug(
            scope_type=payload.scope_type.value,
            tenant_id=resolved_tenant_id,
            slug=payload.slug,
        )
        if existing is not None:
            raise WorkflowRegistryError("workflow slug already exists in this scope")
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
        return lineage, payload.created_from_version_id

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
        if record.draft.status != WorkflowDraftStatus.ACTIVE:
            raise DraftConflictError("published workflow drafts are immutable")
        try:
            require_workflow_scope_access(
                principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
            )
        except ScopeError as exc:
            raise WorkflowAccessError(str(exc)) from exc

    async def _can_view_version(
        self,
        *,
        principal: PrincipalContext,
        record: WorkflowVersionRecord,
    ) -> bool:
        if record.lineage.scope_type == WorkflowScopeType.TENANT.value:
            return can_view_workflow_scope(
                principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
            )
        if "platform_admin" in principal.role_codes:
            return True
        if principal.tenant_id is None or "tenant_admin" not in principal.role_codes:
            return False
        return any(
            grant.grantee_tenant_id == principal.tenant_id
            for grant in record.sharing_grants
        )

    async def _visible_subworkflow_version_ids(
        self,
        *,
        principal: PrincipalContext,
        document: WorkflowDraftDocument,
    ) -> set[str]:
        visible: set[str] = set()
        for reference in document.subworkflow_refs:
            try:
                version_id = UUID(reference.workflow_version_ref)
            except ValueError:
                continue
            version_record = await self.repository.get_version_record(version_id)
            if version_record is None:
                continue
            if await self._can_view_version(principal=principal, record=version_record):
                visible.add(reference.workflow_version_ref)
        return visible

    def _principal_identity_id(self, principal: PrincipalContext) -> UUID:
        if principal.principal_identity_id is None:
            raise WorkflowAccessError("workflow actions require a persisted identity")
        return principal.principal_identity_id

    def _to_response(self, record: WorkflowDraftRecord) -> WorkflowDraftResponse:
        latest_validation = record.latest_validation
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
            created_from_version_id=record.draft.created_from_version_id,
            latest_revision=WorkflowDraftRevisionResponse(
                workflow_draft_revision_id=record.revision.workflow_draft_revision_id,
                revision_number=record.revision.revision_number,
                document_sha256=record.revision.document_sha256,
                change_summary=record.revision.change_summary,
                created_at=record.revision.created_at,
            ),
            latest_validation=(
                self._to_validation_response(latest_validation)
                if latest_validation is not None
                else None
            ),
            document=WorkflowDraftDocument.model_validate(
                record.revision.authoring_document_json
            ),
            updated_at=record.draft.updated_at,
        )

    def _to_validation_response(
        self,
        validation_result: ValidationResult,
    ) -> ValidationResultResponse:
        raw_findings = validation_result.findings_json.get("findings", [])
        findings = raw_findings if isinstance(raw_findings, list) else []
        return ValidationResultResponse(
            validation_result_id=validation_result.validation_result_id,
            status=_enum_value(validation_result.status),
            blocking_issue_count=validation_result.blocking_issue_count,
            advisory_issue_count=validation_result.advisory_issue_count,
            findings=[
                ValidationFindingResponse.model_validate(finding)
                for finding in findings
                if isinstance(finding, dict)
            ],
        )

    def _to_version_response(
        self,
        record: WorkflowVersionRecord,
    ) -> WorkflowVersionResponse:
        return WorkflowVersionResponse(
            workflow_version_bundle_id=record.version.workflow_version_bundle_id,
            workflow_lineage_id=record.lineage.workflow_lineage_id,
            slug=record.lineage.slug,
            display_name=record.lineage.display_name,
            display_version=record.version.display_version,
            scope_type=WorkflowScopeType(record.version.scope_type),
            tenant_id=record.version.tenant_id,
            status=_enum_value(record.version.status),
            compiled_bundle_digest=record.version.compiled_bundle_digest,
            compiler_version=record.version.compiler_version,
            published_from_draft_id=record.version.published_from_draft_id,
            published_from_revision_id=record.version.published_from_revision_id,
            previous_version_bundle_id=record.version.previous_version_bundle_id,
            compiled_bundle_artifact_id=record.version.compiled_bundle_artifact_id,
            summary_json=record.version.summary_json,
            sharing_grants=[
                self._to_sharing_grant_response(grant)
                for grant in record.sharing_grants
            ],
            published_at=record.version.published_at,
        )

    def _to_sharing_grant_response(
        self,
        sharing_grant: RegistrySharingGrant,
    ) -> RegistrySharingGrantResponse:
        return RegistrySharingGrantResponse(
            registry_sharing_grant_id=sharing_grant.registry_sharing_grant_id,
            workflow_version_bundle_id=sharing_grant.workflow_version_bundle_id,
            grantee_tenant_id=sharing_grant.grantee_tenant_id,
            status=_enum_value(sharing_grant.status),
            created_at=sharing_grant.created_at,
        )

    def _to_registry_item_from_version(
        self,
        record: WorkflowVersionRecord,
    ) -> WorkflowRegistryItem:
        return WorkflowRegistryItem(
            workflow_lineage_id=record.lineage.workflow_lineage_id,
            workflow_version_bundle_id=record.version.workflow_version_bundle_id,
            slug=record.lineage.slug,
            display_name=record.lineage.display_name,
            workflow_kind=WorkflowKind(_enum_value(record.lineage.workflow_kind)),
            scope_type=WorkflowScopeType(record.lineage.scope_type),
            tenant_id=record.lineage.tenant_id,
            visibility_status=WorkflowVisibilityStatus(
                _enum_value(record.version.status)
            ),
            display_version=record.version.display_version,
            updated_at=record.version.published_at,
        )

    async def _record_event(
        self,
        *,
        principal: PrincipalContext,
        action: str,
        record: WorkflowDraftRecord,
        payload: dict[str, str] | None = None,
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
            audit_payload = {
                "slug": record.lineage.slug,
                "revision_number": str(record.draft.current_revision_number),
            }
            if payload is not None:
                audit_payload.update(payload)
            await self.audit_service.record_workflow_event(
                principal=principal,
                scope_type=record.lineage.scope_type,
                tenant_id=record.lineage.tenant_id,
                action=action,
                entity_type="workflow_draft",
                entity_id=str(record.draft.workflow_draft_id),
                trace_id=principal.trace_id,
                request_id=principal.request_id,
                payload_redacted=audit_payload,
            )
