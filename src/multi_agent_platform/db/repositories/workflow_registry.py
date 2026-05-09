from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.workflow_registry import (
    RegistrySharingGrant,
    RegistrySharingGrantStatus,
    ValidationResult,
    ValidationResultStatus,
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowLineage,
    WorkflowVersionBundle,
)


@dataclass(slots=True)
class WorkflowDraftRecord:
    lineage: WorkflowLineage
    draft: WorkflowDraft
    revision: WorkflowDraftRevision
    latest_validation: ValidationResult | None = None


@dataclass(slots=True)
class WorkflowVersionRecord:
    lineage: WorkflowLineage
    version: WorkflowVersionBundle
    sharing_grants: list[RegistrySharingGrant] = field(default_factory=list)


class WorkflowRegistryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_lineage_by_slug(
        self,
        *,
        scope_type: str,
        tenant_id: UUID | None,
        slug: str,
    ) -> WorkflowLineage | None:
        stmt = select(WorkflowLineage).where(
            WorkflowLineage.scope_type == scope_type,
            WorkflowLineage.tenant_id == tenant_id,
            WorkflowLineage.slug == slug,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_lineage(self, workflow_lineage_id: UUID) -> WorkflowLineage | None:
        return await self.session.get(WorkflowLineage, workflow_lineage_id)

    async def create_lineage(self, lineage: WorkflowLineage) -> WorkflowLineage:
        self.session.add(lineage)
        await self.session.flush()
        return lineage

    async def list_visible_lineages(
        self,
        *,
        tenant_id: UUID | None,
        include_platform: bool,
        scope_filter: str,
    ) -> list[WorkflowLineage]:
        stmt = select(WorkflowLineage)
        if scope_filter == "tenant":
            stmt = stmt.where(
                WorkflowLineage.scope_type == "tenant",
                WorkflowLineage.tenant_id == tenant_id,
            )
        elif scope_filter == "platform":
            stmt = stmt.where(WorkflowLineage.scope_type == "platform")
        elif tenant_id is None:
            stmt = stmt.where(WorkflowLineage.scope_type == "platform")
        elif include_platform:
            stmt = stmt.where(
                (WorkflowLineage.scope_type == "platform")
                | (
                    (WorkflowLineage.scope_type == "tenant")
                    & (WorkflowLineage.tenant_id == tenant_id)
                )
            )
        else:
            stmt = stmt.where(
                WorkflowLineage.scope_type == "tenant",
                WorkflowLineage.tenant_id == tenant_id,
            )
        stmt = stmt.order_by(WorkflowLineage.updated_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def find_active_draft_for_lineage(
        self, workflow_lineage_id: UUID
    ) -> WorkflowDraft | None:
        stmt = select(WorkflowDraft).where(
            WorkflowDraft.workflow_lineage_id == workflow_lineage_id,
            WorkflowDraft.status == WorkflowDraftStatus.ACTIVE,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_draft(self, draft: WorkflowDraft) -> WorkflowDraft:
        self.session.add(draft)
        await self.session.flush()
        return draft

    async def get_draft_record(
        self, workflow_draft_id: UUID
    ) -> WorkflowDraftRecord | None:
        draft = await self.session.get(WorkflowDraft, workflow_draft_id)
        if draft is None or draft.latest_revision_id is None:
            return None
        lineage = await self.session.get(WorkflowLineage, draft.workflow_lineage_id)
        revision = await self.session.get(
            WorkflowDraftRevision,
            draft.latest_revision_id,
        )
        if lineage is None or revision is None:
            return None
        latest_validation = await self.get_latest_validation_for_revision(
            revision.workflow_draft_revision_id
        )
        return WorkflowDraftRecord(
            lineage=lineage,
            draft=draft,
            revision=revision,
            latest_validation=latest_validation,
        )

    async def save_revision(
        self,
        *,
        draft: WorkflowDraft,
        document_json: dict[str, object],
        document_sha256: str,
        change_summary: str | None,
        principal_identity_id: UUID,
        react_save_idempotency_key: str | None = None,
        react_save_scope_hash: str | None = None,
        react_save_payload_hash: str | None = None,
    ) -> WorkflowDraftRecord:
        next_revision_number = draft.current_revision_number + 1
        revision = WorkflowDraftRevision(
            workflow_draft_id=draft.workflow_draft_id,
            revision_number=next_revision_number,
            authoring_document_json=document_json,
            document_sha256=document_sha256,
            change_summary=change_summary,
            react_save_idempotency_key=react_save_idempotency_key,
            react_save_scope_hash=react_save_scope_hash,
            react_save_payload_hash=react_save_payload_hash,
            created_by_principal_id=principal_identity_id,
        )
        self.session.add(revision)
        await self.session.flush()
        draft.current_revision_number = next_revision_number
        draft.latest_revision_id = revision.workflow_draft_revision_id
        draft.last_edited_by_principal_id = principal_identity_id
        await self.session.flush()
        lineage = await self.session.get(WorkflowLineage, draft.workflow_lineage_id)
        if lineage is None:
            raise RuntimeError("workflow lineage missing")
        return WorkflowDraftRecord(lineage=lineage, draft=draft, revision=revision)

    async def get_revision_by_react_save_idempotency_key(
        self,
        *,
        workflow_draft_id: UUID,
        idempotency_key: str,
    ) -> WorkflowDraftRevision | None:
        stmt = select(WorkflowDraftRevision).where(
            WorkflowDraftRevision.workflow_draft_id == workflow_draft_id,
            WorkflowDraftRevision.react_save_idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def list_draft_revisions(
        self,
        workflow_draft_id: UUID,
    ) -> list[WorkflowDraftRevision]:
        stmt = (
            select(WorkflowDraftRevision)
            .where(WorkflowDraftRevision.workflow_draft_id == workflow_draft_id)
            .order_by(WorkflowDraftRevision.revision_number.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_draft_revision_by_number(
        self,
        *,
        workflow_draft_id: UUID,
        revision_number: int,
    ) -> WorkflowDraftRevision | None:
        stmt = select(WorkflowDraftRevision).where(
            WorkflowDraftRevision.workflow_draft_id == workflow_draft_id,
            WorkflowDraftRevision.revision_number == revision_number,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_validation_result(
        self, validation_result: ValidationResult
    ) -> ValidationResult:
        self.session.add(validation_result)
        await self.session.flush()
        return validation_result

    async def get_validation_result(
        self, validation_result_id: UUID
    ) -> ValidationResult | None:
        return await self.session.get(ValidationResult, validation_result_id)

    async def get_latest_validation_for_revision(
        self,
        workflow_draft_revision_id: UUID,
    ) -> ValidationResult | None:
        stmt = (
            select(ValidationResult)
            .where(
                ValidationResult.workflow_draft_revision_id
                == workflow_draft_revision_id,
                ValidationResult.status != ValidationResultStatus.SUPERSEDED,
            )
            .order_by(ValidationResult.executed_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def supersede_validation_results_for_revision(
        self,
        workflow_draft_revision_id: UUID,
    ) -> None:
        stmt = select(ValidationResult).where(
            ValidationResult.workflow_draft_revision_id == workflow_draft_revision_id,
            ValidationResult.status != ValidationResultStatus.SUPERSEDED,
        )
        results = list((await self.session.execute(stmt)).scalars().all())
        for result in results:
            result.status = ValidationResultStatus.SUPERSEDED
        await self.session.flush()

    async def supersede_validation_results_for_draft(
        self,
        workflow_draft_id: UUID,
    ) -> None:
        stmt = (
            select(ValidationResult)
            .join(
                WorkflowDraftRevision,
                ValidationResult.workflow_draft_revision_id
                == WorkflowDraftRevision.workflow_draft_revision_id,
            )
            .where(
                WorkflowDraftRevision.workflow_draft_id == workflow_draft_id,
                ValidationResult.status != ValidationResultStatus.SUPERSEDED,
            )
        )
        results = list((await self.session.execute(stmt)).scalars().all())
        for result in results:
            result.status = ValidationResultStatus.SUPERSEDED
        await self.session.flush()

    async def create_version_bundle(
        self, workflow_version_bundle: WorkflowVersionBundle
    ) -> WorkflowVersionBundle:
        self.session.add(workflow_version_bundle)
        await self.session.flush()
        return workflow_version_bundle

    async def get_version_bundle(
        self,
        workflow_version_bundle_id: UUID,
    ) -> WorkflowVersionBundle | None:
        return await self.session.get(WorkflowVersionBundle, workflow_version_bundle_id)

    async def get_version_record(
        self,
        workflow_version_bundle_id: UUID,
    ) -> WorkflowVersionRecord | None:
        version = await self.get_version_bundle(workflow_version_bundle_id)
        if version is None:
            return None
        lineage = await self.session.get(WorkflowLineage, version.workflow_lineage_id)
        if lineage is None:
            return None
        sharing_grants = await self.list_active_sharing_grants(
            workflow_version_bundle_id=workflow_version_bundle_id
        )
        return WorkflowVersionRecord(
            lineage=lineage,
            version=version,
            sharing_grants=sharing_grants,
        )

    async def list_versions(self, *, scope_filter: str) -> list[WorkflowVersionBundle]:
        stmt = select(WorkflowVersionBundle)
        if scope_filter == "tenant":
            stmt = stmt.where(WorkflowVersionBundle.scope_type == "tenant")
        elif scope_filter == "platform":
            stmt = stmt.where(WorkflowVersionBundle.scope_type == "platform")
        stmt = stmt.order_by(WorkflowVersionBundle.published_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_latest_published_version_for_lineage(
        self,
        workflow_lineage_id: UUID,
    ) -> WorkflowVersionBundle | None:
        stmt = (
            select(WorkflowVersionBundle)
            .where(WorkflowVersionBundle.workflow_lineage_id == workflow_lineage_id)
            .order_by(WorkflowVersionBundle.version_sequence.desc())
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def next_version_sequence(self, workflow_lineage_id: UUID) -> int:
        latest = await self.get_latest_published_version_for_lineage(
            workflow_lineage_id
        )
        if latest is None:
            return 1
        return latest.version_sequence + 1

    async def create_sharing_grant(
        self, sharing_grant: RegistrySharingGrant
    ) -> RegistrySharingGrant:
        self.session.add(sharing_grant)
        await self.session.flush()
        return sharing_grant

    async def get_active_sharing_grant(
        self,
        *,
        workflow_version_bundle_id: UUID,
        grantee_tenant_id: UUID,
    ) -> RegistrySharingGrant | None:
        stmt = select(RegistrySharingGrant).where(
            RegistrySharingGrant.workflow_version_bundle_id
            == workflow_version_bundle_id,
            RegistrySharingGrant.grantee_tenant_id == grantee_tenant_id,
            RegistrySharingGrant.status == RegistrySharingGrantStatus.ACTIVE,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_active_sharing_grants(
        self,
        *,
        workflow_version_bundle_id: UUID,
    ) -> list[RegistrySharingGrant]:
        stmt = (
            select(RegistrySharingGrant)
            .where(
                RegistrySharingGrant.workflow_version_bundle_id
                == workflow_version_bundle_id,
                RegistrySharingGrant.status == RegistrySharingGrantStatus.ACTIVE,
            )
            .order_by(RegistrySharingGrant.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())
