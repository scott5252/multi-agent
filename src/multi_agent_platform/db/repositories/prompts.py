from __future__ import annotations

import hashlib
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.prompts import (
    PromptDraft,
    PromptDraftRevision,
    PromptLineage,
    PromptValidationResult,
    PromptVersion,
    TenantPromptVersionGrant,
)


class StalePromptRevisionError(RuntimeError):
    pass


@dataclass(slots=True)
class PromptDraftRecord:
    lineage: PromptLineage
    draft: PromptDraft


def prompt_digest(template_content: str) -> str:
    return hashlib.sha256(template_content.encode("utf-8")).hexdigest()


class PromptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_lineage_with_draft(
        self,
        *,
        scope_type: str,
        tenant_id: UUID | None,
        slug: str,
        display_name: str,
        purpose: str,
        principal_id: str,
    ) -> PromptDraftRecord:
        lineage = PromptLineage(
            scope_type=scope_type,
            tenant_id=tenant_id,
            slug=slug,
            display_name=display_name,
            purpose=purpose,
            created_by_principal_id=principal_id,
        )
        self.session.add(lineage)
        await self.session.flush()
        draft = PromptDraft(
            prompt_lineage_id=lineage.prompt_lineage_id,
            scope_type=scope_type,
            tenant_id=tenant_id,
            created_by_principal_id=principal_id,
            last_edited_by_principal_id=principal_id,
        )
        self.session.add(draft)
        await self.session.flush()
        lineage.latest_draft_id = draft.prompt_draft_id
        await self.session.flush()
        return PromptDraftRecord(lineage=lineage, draft=draft)

    async def get_lineage(self, prompt_lineage_id: UUID) -> PromptLineage | None:
        return await self.session.get(PromptLineage, prompt_lineage_id)

    async def get_active_draft(self, prompt_lineage_id: UUID) -> PromptDraft | None:
        stmt = select(PromptDraft).where(
            PromptDraft.prompt_lineage_id == prompt_lineage_id,
            PromptDraft.status == "active",
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_latest_revision(
        self, draft: PromptDraft
    ) -> PromptDraftRevision | None:
        if draft.latest_revision_id is None:
            return None
        return await self.session.get(PromptDraftRevision, draft.latest_revision_id)

    async def get_validation_result(
        self,
        validation_result_id: UUID | None,
    ) -> PromptValidationResult | None:
        if validation_result_id is None:
            return None
        return await self.session.get(PromptValidationResult, validation_result_id)

    async def save_draft_revision(
        self,
        *,
        draft: PromptDraft,
        expected_revision_number: int,
        prompt_title: str,
        purpose: str,
        usage_notes: str,
        template_content: str,
        variable_declarations: list[dict[str, object]],
        fixture_value_sets: list[dict[str, object]],
        safe_summary: dict[str, object],
        principal_id: str,
    ) -> PromptDraftRevision:
        if draft.current_revision_number != expected_revision_number:
            raise StalePromptRevisionError("prompt draft revision is stale")
        revision = PromptDraftRevision(
            prompt_draft_id=draft.prompt_draft_id,
            revision_number=expected_revision_number + 1,
            prompt_title=prompt_title,
            purpose=purpose,
            usage_notes=usage_notes,
            template_content=template_content,
            template_content_sha256=prompt_digest(template_content),
            variable_declarations_json=variable_declarations,
            fixture_value_sets_json=fixture_value_sets,
            safe_summary_json=safe_summary,
            created_by_principal_id=principal_id,
        )
        self.session.add(revision)
        await self.session.flush()
        draft.current_revision_number = revision.revision_number
        draft.latest_revision_id = revision.prompt_draft_revision_id
        draft.last_edited_by_principal_id = principal_id
        draft.last_validation_result_id = None
        await self.session.flush()
        return revision

    async def record_validation_result(
        self,
        *,
        draft_revision: PromptDraftRevision,
        status: str,
        findings: list[dict[str, object]],
        principal_id: str,
    ) -> PromptValidationResult:
        blocking_count = sum(
            1 for finding in findings if finding.get("severity") == "blocking"
        )
        advisory_count = sum(
            1 for finding in findings if finding.get("severity") != "blocking"
        )
        result = PromptValidationResult(
            prompt_draft_revision_id=draft_revision.prompt_draft_revision_id,
            status=status,
            blocking_issue_count=blocking_count,
            advisory_issue_count=advisory_count,
            findings_json=findings,
            template_content_sha256=draft_revision.template_content_sha256,
            executed_by_principal_id=principal_id,
        )
        self.session.add(result)
        await self.session.flush()
        draft = await self.session.get(PromptDraft, draft_revision.prompt_draft_id)
        if draft is not None:
            draft.last_validation_result_id = result.prompt_validation_result_id
        await self.session.flush()
        return result

    async def next_version_sequence(self, prompt_lineage_id: UUID) -> int:
        max_sequence = await self.session.scalar(
            select(func.max(PromptVersion.version_sequence)).where(
                PromptVersion.prompt_lineage_id == prompt_lineage_id
            )
        )
        return int(max_sequence or 0) + 1

    async def get_prompt_version(
        self,
        prompt_version_id: UUID,
    ) -> PromptVersion | None:
        return await self.session.get(PromptVersion, prompt_version_id)

    async def list_new_use_versions(
        self,
        *,
        tenant_id: UUID | None,
        include_platform: bool,
    ) -> list[PromptVersion]:
        stmt = select(PromptVersion).where(PromptVersion.status == "active")
        if tenant_id is None:
            stmt = stmt.where(PromptVersion.scope_type == "platform")
        elif include_platform:
            stmt = stmt.where(
                or_(
                    PromptVersion.tenant_id == tenant_id,
                    PromptVersion.scope_type == "platform",
                )
            )
        else:
            stmt = stmt.where(
                PromptVersion.scope_type == "tenant",
                PromptVersion.tenant_id == tenant_id,
            )
        return list((await self.session.execute(stmt)).scalars().all())

    async def is_version_visible_to_tenant(
        self,
        *,
        prompt_version_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        version = await self.get_prompt_version(prompt_version_id)
        if version is None:
            return False
        if version.scope_type == "tenant":
            return version.tenant_id == tenant_id
        stmt = select(TenantPromptVersionGrant).where(
            TenantPromptVersionGrant.prompt_version_id == prompt_version_id,
            TenantPromptVersionGrant.grantee_tenant_id == tenant_id,
            TenantPromptVersionGrant.status == "active",
        )
        return (await self.session.execute(stmt)).scalar_one_or_none() is not None

    async def retire_prompt_version(
        self,
        *,
        version: PromptVersion,
        principal_id: str,
        reason: str,
    ) -> PromptVersion:
        version.status = "retired"
        version.retired_by_principal_id = principal_id
        version.retirement_reason = reason
        await self.session.flush()
        return version

    async def grant_prompt_version(
        self,
        *,
        prompt_version_id: UUID,
        grantee_tenant_id: UUID,
        principal_id: str,
        reason: str,
    ) -> TenantPromptVersionGrant:
        grant = TenantPromptVersionGrant(
            prompt_version_id=prompt_version_id,
            grantee_tenant_id=grantee_tenant_id,
            granted_by_principal_id=principal_id,
            reason=reason,
        )
        self.session.add(grant)
        await self.session.flush()
        return grant
