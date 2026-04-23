from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowLineage,
)


@dataclass(slots=True)
class WorkflowDraftRecord:
    lineage: WorkflowLineage
    draft: WorkflowDraft
    revision: WorkflowDraftRevision


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

    async def create_revision(
        self, revision: WorkflowDraftRevision
    ) -> WorkflowDraftRevision:
        self.session.add(revision)
        await self.session.flush()
        return revision

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
        return WorkflowDraftRecord(lineage=lineage, draft=draft, revision=revision)

    async def save_revision(
        self,
        *,
        draft: WorkflowDraft,
        document_json: dict[str, object],
        document_sha256: str,
        change_summary: str | None,
        principal_identity_id: UUID,
    ) -> WorkflowDraftRecord:
        next_revision_number = draft.current_revision_number + 1
        revision = WorkflowDraftRevision(
            workflow_draft_id=draft.workflow_draft_id,
            revision_number=next_revision_number,
            authoring_document_json=document_json,
            document_sha256=document_sha256,
            change_summary=change_summary,
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
