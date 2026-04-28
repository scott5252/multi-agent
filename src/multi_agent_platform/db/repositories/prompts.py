from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from multi_agent_platform.db.base import utcnow
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


def _history_sort_key(event: dict[str, object]) -> datetime:
    created_at = cast(datetime, event["created_at"])
    if created_at.tzinfo is None:
        return created_at.replace(tzinfo=UTC)
    return created_at


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

    async def list_visible_lineages(
        self,
        *,
        principal_tenant_id: UUID | None,
        include_platform_admin: bool,
        scope_type: str | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> list[PromptLineage]:
        stmt = select(PromptLineage)
        if not include_platform_admin:
            visible_conditions: list[ColumnElement[bool]] = []
            if principal_tenant_id is not None:
                visible_conditions.append(
                    (PromptLineage.scope_type == "tenant")
                    & (PromptLineage.tenant_id == principal_tenant_id)
                )
                granted_platform_lineages = (
                    select(PromptVersion.prompt_lineage_id)
                    .join(
                        TenantPromptVersionGrant,
                        TenantPromptVersionGrant.prompt_version_id
                        == PromptVersion.prompt_version_id,
                    )
                    .where(
                        PromptVersion.scope_type == "platform",
                        PromptVersion.status == "active",
                        TenantPromptVersionGrant.grantee_tenant_id
                        == principal_tenant_id,
                        TenantPromptVersionGrant.status == "active",
                    )
                )
                visible_conditions.append(
                    PromptLineage.prompt_lineage_id.in_(granted_platform_lineages)
                )
            if not visible_conditions:
                return []
            stmt = stmt.where(or_(*visible_conditions))
        if scope_type is not None:
            stmt = stmt.where(PromptLineage.scope_type == scope_type)
        if status is not None:
            stmt = stmt.where(PromptLineage.status == status)
        if q:
            search = f"%{q}%"
            stmt = stmt.where(
                or_(
                    PromptLineage.display_name.ilike(search),
                    PromptLineage.slug.ilike(search),
                    PromptLineage.purpose.ilike(search),
                )
            )
        stmt = stmt.order_by(desc(PromptLineage.updated_at))
        return list((await self.session.execute(stmt)).scalars().all())

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

    async def list_versions_for_lineage(
        self,
        prompt_lineage_id: UUID,
    ) -> list[PromptVersion]:
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_lineage_id == prompt_lineage_id)
            .order_by(desc(PromptVersion.version_sequence))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_grants_for_version(
        self,
        prompt_version_id: UUID,
    ) -> list[TenantPromptVersionGrant]:
        stmt = (
            select(TenantPromptVersionGrant)
            .where(
                TenantPromptVersionGrant.prompt_version_id == prompt_version_id,
                TenantPromptVersionGrant.status == "active",
            )
            .order_by(desc(TenantPromptVersionGrant.created_at))
        )
        return list((await self.session.execute(stmt)).scalars().all())

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
        version.retired_at = utcnow()
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

    async def list_prompt_history(
        self,
        *,
        prompt_lineage_id: UUID | None = None,
        prompt_version_id: UUID | None = None,
        tenant_id: UUID | None = None,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        lineage_ids: set[UUID] = set()
        if prompt_lineage_id is not None:
            lineage_ids.add(prompt_lineage_id)
        if prompt_version_id is not None:
            version = await self.get_prompt_version(prompt_version_id)
            if version is None:
                return []
            lineage_ids.add(version.prompt_lineage_id)
        events: list[dict[str, object]] = []

        draft_stmt = select(PromptDraft)
        if lineage_ids:
            draft_stmt = draft_stmt.where(
                PromptDraft.prompt_lineage_id.in_(lineage_ids)
            )
        if tenant_id is not None:
            draft_stmt = draft_stmt.where(
                or_(PromptDraft.tenant_id == tenant_id, PromptDraft.tenant_id.is_(None))
            )
        drafts = list((await self.session.execute(draft_stmt)).scalars().all())
        draft_ids = [draft.prompt_draft_id for draft in drafts]

        if draft_ids:
            revision_stmt = (
                select(PromptDraftRevision)
                .where(PromptDraftRevision.prompt_draft_id.in_(draft_ids))
                .order_by(desc(PromptDraftRevision.created_at))
            )
            for revision in (await self.session.execute(revision_stmt)).scalars().all():
                events.append(
                    {
                        "action": "save_draft",
                        "actor_principal_id": revision.created_by_principal_id,
                        "created_at": revision.created_at,
                        "outcome": "recorded",
                        "reason": "",
                        "redacted_diff_summary": {
                            "revision_number": revision.revision_number,
                            "template_content_sha256": revision.template_content_sha256,
                            "variable_count": len(
                                revision.variable_declarations_json or []
                            ),
                        },
                    }
                )

            validation_stmt = (
                select(PromptValidationResult)
                .join(
                    PromptDraftRevision,
                    PromptDraftRevision.prompt_draft_revision_id
                    == PromptValidationResult.prompt_draft_revision_id,
                )
                .where(PromptDraftRevision.prompt_draft_id.in_(draft_ids))
                .order_by(desc(PromptValidationResult.executed_at))
            )
            for validation in (
                (await self.session.execute(validation_stmt)).scalars().all()
            ):
                events.append(
                    {
                        "action": "validate",
                        "actor_principal_id": validation.executed_by_principal_id,
                        "created_at": validation.executed_at,
                        "outcome": validation.status,
                        "reason": "",
                        "redacted_diff_summary": {
                            "blocking_issue_count": validation.blocking_issue_count,
                            "advisory_issue_count": validation.advisory_issue_count,
                            "finding_codes": [
                                str(finding.get("code", "validation"))
                                for finding in validation.findings_json or []
                            ],
                        },
                    }
                )

        version_stmt = select(PromptVersion)
        if lineage_ids:
            version_stmt = version_stmt.where(
                PromptVersion.prompt_lineage_id.in_(lineage_ids)
            )
        if prompt_version_id is not None:
            version_stmt = version_stmt.where(
                PromptVersion.prompt_version_id == prompt_version_id
            )
        if tenant_id is not None:
            version_stmt = version_stmt.where(
                or_(
                    PromptVersion.tenant_id == tenant_id,
                    PromptVersion.tenant_id.is_(None),
                )
            )
        versions = list((await self.session.execute(version_stmt)).scalars().all())
        version_ids = [version.prompt_version_id for version in versions]
        for version in versions:
            events.append(
                {
                    "action": "publish",
                    "actor_principal_id": version.published_by_principal_id,
                    "created_at": version.published_at,
                    "outcome": version.status,
                    "reason": version.publication_reason,
                    "redacted_diff_summary": {
                        "display_version": version.display_version,
                        "template_content_sha256": version.template_content_sha256,
                    },
                }
            )
            if version.retired_at is not None:
                events.append(
                    {
                        "action": "retire",
                        "actor_principal_id": version.retired_by_principal_id
                        or "system",
                        "created_at": version.retired_at,
                        "outcome": "retired",
                        "reason": version.retirement_reason or "",
                        "redacted_diff_summary": {
                            "display_version": version.display_version
                        },
                    }
                )

        if version_ids:
            grant_stmt = (
                select(TenantPromptVersionGrant)
                .where(TenantPromptVersionGrant.prompt_version_id.in_(version_ids))
                .order_by(desc(TenantPromptVersionGrant.created_at))
            )
            for grant in (await self.session.execute(grant_stmt)).scalars().all():
                events.append(
                    {
                        "action": "grant",
                        "actor_principal_id": grant.granted_by_principal_id,
                        "created_at": grant.created_at,
                        "outcome": grant.status,
                        "reason": grant.reason,
                        "redacted_diff_summary": {
                            "grantee_tenant_id": str(grant.grantee_tenant_id)
                        },
                    }
                )

        return sorted(
            events,
            key=_history_sort_key,
            reverse=True,
        )[:limit]
