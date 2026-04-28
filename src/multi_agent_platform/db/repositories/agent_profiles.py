from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from multi_agent_platform.agents.resolution import AgentProfileCandidate
from multi_agent_platform.db.models.agent_profiles import (
    ActiveAgentProfilePointer,
    AgentProfileDraft,
    AgentProfileDraftRevision,
    AgentProfileValidationResult,
    AgentProfileVersion,
    AgentRuntimeProfile,
    TenantProfileVersionGrant,
)
from multi_agent_platform.db.models.prompts import (
    PromptVersion,
    TenantPromptVersionGrant,
)


class StaleAgentProfileRevisionError(RuntimeError):
    pass


@dataclass(slots=True)
class AgentProfileDraftRecord:
    profile: AgentRuntimeProfile
    draft: AgentProfileDraft


class AgentProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_profile_with_draft(
        self,
        *,
        scope_type: str,
        tenant_id: UUID | None,
        agent_key: str,
        agent_kind: str,
        display_name: str,
        purpose: str,
        principal_id: str,
    ) -> AgentProfileDraftRecord:
        profile = AgentRuntimeProfile(
            scope_type=scope_type,
            tenant_id=tenant_id,
            agent_key=agent_key,
            agent_kind=agent_kind,
            display_name=display_name,
            purpose=purpose,
            created_by_principal_id=principal_id,
        )
        self.session.add(profile)
        await self.session.flush()
        draft = AgentProfileDraft(
            agent_runtime_profile_id=profile.agent_runtime_profile_id,
            scope_type=scope_type,
            tenant_id=tenant_id,
            created_by_principal_id=principal_id,
            last_edited_by_principal_id=principal_id,
        )
        self.session.add(draft)
        await self.session.flush()
        profile.latest_draft_id = draft.agent_profile_draft_id
        await self.session.flush()
        return AgentProfileDraftRecord(profile=profile, draft=draft)

    async def save_draft_revision(
        self,
        *,
        draft: AgentProfileDraft,
        expected_revision_number: int,
        purpose: str,
        prompt_references: list[dict[str, object]],
        model_routing_hints: dict[str, object],
        memory_scope_policy: dict[str, object],
        skill_requirements: list[dict[str, object]],
        tool_policy_expectations: list[dict[str, object]],
        output_contract_expectations: dict[str, object],
        test_suite_requirements: list[dict[str, object]],
        safe_summary: dict[str, object],
        principal_id: str,
    ) -> AgentProfileDraftRevision:
        if draft.current_revision_number != expected_revision_number:
            raise StaleAgentProfileRevisionError(
                "agent profile draft revision is stale"
            )
        profile = await self.session.get(
            AgentRuntimeProfile,
            draft.agent_runtime_profile_id,
        )
        if profile is None:
            raise KeyError(str(draft.agent_runtime_profile_id))
        revision = AgentProfileDraftRevision(
            agent_profile_draft_id=draft.agent_profile_draft_id,
            revision_number=expected_revision_number + 1,
            agent_key=profile.agent_key,
            agent_kind=profile.agent_kind,
            purpose=purpose,
            prompt_references_json=prompt_references,
            model_routing_hints_json=model_routing_hints,
            memory_scope_policy_json=memory_scope_policy,
            skill_requirements_json=skill_requirements,
            tool_policy_expectations_json=tool_policy_expectations,
            output_contract_expectations_json=output_contract_expectations,
            test_suite_requirements_json=test_suite_requirements,
            safe_summary_json=safe_summary,
            created_by_principal_id=principal_id,
        )
        self.session.add(revision)
        await self.session.flush()
        draft.current_revision_number = revision.revision_number
        draft.latest_revision_id = revision.agent_profile_draft_revision_id
        draft.last_edited_by_principal_id = principal_id
        draft.last_validation_result_id = None
        await self.session.flush()
        return revision

    async def record_validation_result(
        self,
        *,
        draft_revision: AgentProfileDraftRevision,
        status: str,
        findings: list[dict[str, object]],
        principal_id: str,
    ) -> AgentProfileValidationResult:
        blocking_count = sum(
            1 for finding in findings if finding.get("severity") == "blocking"
        )
        advisory_count = sum(
            1 for finding in findings if finding.get("severity") != "blocking"
        )
        result = AgentProfileValidationResult(
            agent_profile_draft_revision_id=draft_revision.agent_profile_draft_revision_id,
            status=status,
            blocking_issue_count=blocking_count,
            advisory_issue_count=advisory_count,
            findings_json=findings,
            referenced_prompt_version_ids=[
                str(reference["prompt_version_id"])
                for reference in draft_revision.prompt_references_json
                if "prompt_version_id" in reference
            ],
            executed_by_principal_id=principal_id,
        )
        self.session.add(result)
        await self.session.flush()
        draft = await self.session.get(
            AgentProfileDraft,
            draft_revision.agent_profile_draft_id,
        )
        if draft is not None:
            draft.last_validation_result_id = result.agent_profile_validation_result_id
        await self.session.flush()
        return result

    async def next_profile_version_sequence(
        self,
        agent_runtime_profile_id: UUID,
    ) -> int:
        from multi_agent_platform.db.models.agent_profiles import AgentProfileVersion

        max_sequence = await self.session.scalar(
            select(func.max(AgentProfileVersion.version_sequence)).where(
                AgentProfileVersion.agent_runtime_profile_id == agent_runtime_profile_id
            )
        )
        return int(max_sequence or 0) + 1

    async def get_profile(
        self,
        agent_runtime_profile_id: UUID,
    ) -> AgentRuntimeProfile | None:
        return await self.session.get(AgentRuntimeProfile, agent_runtime_profile_id)

    async def list_visible_profiles(
        self,
        *,
        principal_tenant_id: UUID | None,
        include_platform_admin: bool,
        agent_key: str | None = None,
        agent_kind: str | None = None,
    ) -> list[AgentRuntimeProfile]:
        stmt = select(AgentRuntimeProfile)
        if not include_platform_admin:
            visible_conditions: list[ColumnElement[bool]] = []
            if principal_tenant_id is not None:
                visible_conditions.append(
                    (AgentRuntimeProfile.scope_type == "tenant")
                    & (AgentRuntimeProfile.tenant_id == principal_tenant_id)
                )
                granted_platform_profiles = (
                    select(AgentProfileVersion.agent_runtime_profile_id)
                    .join(
                        TenantProfileVersionGrant,
                        TenantProfileVersionGrant.agent_profile_version_id
                        == AgentProfileVersion.agent_profile_version_id,
                    )
                    .where(
                        AgentProfileVersion.scope_type == "platform",
                        AgentProfileVersion.status == "active",
                        TenantProfileVersionGrant.grantee_tenant_id
                        == principal_tenant_id,
                        TenantProfileVersionGrant.status == "active",
                    )
                )
                visible_conditions.append(
                    AgentRuntimeProfile.agent_runtime_profile_id.in_(
                        granted_platform_profiles
                    )
                )
            if not visible_conditions:
                return []
            stmt = stmt.where(or_(*visible_conditions))
        if agent_key is not None:
            stmt = stmt.where(AgentRuntimeProfile.agent_key == agent_key)
        if agent_kind is not None:
            stmt = stmt.where(AgentRuntimeProfile.agent_kind == agent_kind)
        stmt = stmt.order_by(desc(AgentRuntimeProfile.updated_at))
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_active_draft(
        self,
        agent_runtime_profile_id: UUID,
    ) -> AgentProfileDraft | None:
        stmt = select(AgentProfileDraft).where(
            AgentProfileDraft.agent_runtime_profile_id == agent_runtime_profile_id,
            AgentProfileDraft.status == "active",
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_latest_revision(
        self,
        draft: AgentProfileDraft,
    ) -> AgentProfileDraftRevision | None:
        if draft.latest_revision_id is None:
            return None
        return await self.session.get(
            AgentProfileDraftRevision,
            draft.latest_revision_id,
        )

    async def get_validation_result(
        self,
        validation_result_id: UUID | None,
    ) -> AgentProfileValidationResult | None:
        if validation_result_id is None:
            return None
        return await self.session.get(
            AgentProfileValidationResult,
            validation_result_id,
        )

    async def get_profile_version(
        self,
        agent_profile_version_id: UUID,
    ) -> AgentProfileVersion | None:
        return await self.session.get(AgentProfileVersion, agent_profile_version_id)

    async def list_versions_for_profile(
        self,
        agent_runtime_profile_id: UUID,
    ) -> list[AgentProfileVersion]:
        stmt = (
            select(AgentProfileVersion)
            .where(
                AgentProfileVersion.agent_runtime_profile_id == agent_runtime_profile_id
            )
            .order_by(desc(AgentProfileVersion.version_sequence))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def resolve_active_pointer(
        self,
        *,
        scope_type: str,
        tenant_id: UUID | None,
        agent_kind: str,
        agent_key: str,
    ) -> ActiveAgentProfilePointer | None:
        stmt = select(ActiveAgentProfilePointer).where(
            ActiveAgentProfilePointer.scope_type == scope_type,
            ActiveAgentProfilePointer.tenant_id == tenant_id,
            ActiveAgentProfilePointer.agent_kind == agent_kind,
            ActiveAgentProfilePointer.agent_key == agent_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def retire_profile_version(
        self,
        *,
        version: AgentProfileVersion,
        principal_id: str,
        reason: str,
    ) -> AgentProfileVersion:
        version.status = "retired"
        version.retired_by_principal_id = principal_id
        version.retirement_reason = reason
        profile = await self.get_profile(version.agent_runtime_profile_id)
        if profile is not None and profile.active_profile_version_id == (
            version.agent_profile_version_id
        ):
            profile.active_profile_version_id = None
        pointer = await self.resolve_active_pointer(
            scope_type=version.scope_type,
            tenant_id=version.tenant_id,
            agent_kind=version.agent_kind,
            agent_key=version.agent_key,
        )
        if (
            pointer is not None
            and pointer.active_profile_version_id == version.agent_profile_version_id
        ):
            await self.session.delete(pointer)
        await self.session.flush()
        return version

    async def grant_profile_version(
        self,
        *,
        agent_profile_version_id: UUID,
        grantee_tenant_id: UUID,
        principal_id: str,
        reason: str,
    ) -> TenantProfileVersionGrant:
        grant = TenantProfileVersionGrant(
            agent_profile_version_id=agent_profile_version_id,
            grantee_tenant_id=grantee_tenant_id,
            granted_by_principal_id=principal_id,
            reason=reason,
        )
        self.session.add(grant)
        await self.session.flush()
        return grant

    async def list_grants_for_version(
        self,
        agent_profile_version_id: UUID,
    ) -> list[TenantProfileVersionGrant]:
        stmt = (
            select(TenantProfileVersionGrant)
            .where(
                TenantProfileVersionGrant.agent_profile_version_id
                == agent_profile_version_id,
                TenantProfileVersionGrant.status == "active",
            )
            .order_by(desc(TenantProfileVersionGrant.created_at))
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_resolution_candidates(
        self,
        *,
        tenant_id: UUID,
        agent_key: str,
        agent_kind: str,
    ) -> tuple[AgentProfileCandidate, ...]:
        stmt = select(AgentProfileVersion).where(
            AgentProfileVersion.status == "active",
            AgentProfileVersion.agent_key == agent_key,
            AgentProfileVersion.agent_kind == agent_kind,
            or_(
                (AgentProfileVersion.scope_type == "tenant")
                & (AgentProfileVersion.tenant_id == tenant_id),
                AgentProfileVersion.scope_type == "platform",
            ),
        )
        versions = list((await self.session.execute(stmt)).scalars().all())
        version_ids = [version.agent_profile_version_id for version in versions]
        grants_by_version: dict[UUID, list[UUID]] = {
            version_id: [] for version_id in version_ids
        }
        if version_ids:
            grant_stmt = select(TenantProfileVersionGrant).where(
                TenantProfileVersionGrant.agent_profile_version_id.in_(version_ids),
                TenantProfileVersionGrant.status == "active",
            )
            for grant in (await self.session.execute(grant_stmt)).scalars().all():
                grants_by_version.setdefault(grant.agent_profile_version_id, []).append(
                    grant.grantee_tenant_id
                )
        return tuple(
            AgentProfileCandidate(
                agent_profile_version_id=version.agent_profile_version_id,
                scope_type=version.scope_type,
                tenant_id=version.tenant_id,
                agent_key=version.agent_key,
                agent_kind=version.agent_kind,
                status=version.status,
                granted_tenant_ids=tuple(
                    grants_by_version.get(version.agent_profile_version_id, [])
                ),
            )
            for version in versions
        )

    async def prompt_versions_for_references(
        self,
        prompt_references: list[dict[str, object]],
    ) -> dict[str, dict[str, object]]:
        version_ids: list[UUID] = []
        for reference in prompt_references:
            raw_version_id = str(reference.get("prompt_version_id", "")).strip()
            if not raw_version_id:
                continue
            try:
                version_ids.append(UUID(raw_version_id))
            except ValueError:
                continue
        if not version_ids:
            return {}
        stmt = select(PromptVersion).where(
            PromptVersion.prompt_version_id.in_(version_ids)
        )
        versions = list((await self.session.execute(stmt)).scalars().all())
        grant_stmt = select(TenantPromptVersionGrant).where(
            TenantPromptVersionGrant.prompt_version_id.in_(version_ids),
            TenantPromptVersionGrant.status == "active",
        )
        grants_by_version: dict[UUID, list[str]] = {
            version_id: [] for version_id in version_ids
        }
        for grant in (await self.session.execute(grant_stmt)).scalars().all():
            grants_by_version.setdefault(grant.prompt_version_id, []).append(
                str(grant.grantee_tenant_id)
            )
        return {
            str(version.prompt_version_id): {
                "status": version.status,
                "scope_type": version.scope_type,
                "tenant_id": str(version.tenant_id) if version.tenant_id else None,
                "grants": grants_by_version.get(version.prompt_version_id, []),
            }
            for version in versions
        }

    async def list_profile_history(
        self,
        *,
        agent_runtime_profile_id: UUID | None = None,
        agent_profile_version_id: UUID | None = None,
        tenant_id: UUID | None = None,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        profile_ids: set[UUID] = set()
        if agent_runtime_profile_id is not None:
            profile_ids.add(agent_runtime_profile_id)
        if agent_profile_version_id is not None:
            version = await self.get_profile_version(agent_profile_version_id)
            if version is not None:
                profile_ids.add(version.agent_runtime_profile_id)
        events: list[dict[str, object]] = []

        draft_stmt = select(AgentProfileDraft)
        if profile_ids:
            draft_stmt = draft_stmt.where(
                AgentProfileDraft.agent_runtime_profile_id.in_(profile_ids)
            )
        if tenant_id is not None:
            draft_stmt = draft_stmt.where(
                or_(
                    AgentProfileDraft.tenant_id == tenant_id,
                    AgentProfileDraft.tenant_id.is_(None),
                )
            )
        drafts = list((await self.session.execute(draft_stmt)).scalars().all())
        draft_ids = [draft.agent_profile_draft_id for draft in drafts]

        if draft_ids:
            revision_stmt = (
                select(AgentProfileDraftRevision)
                .where(AgentProfileDraftRevision.agent_profile_draft_id.in_(draft_ids))
                .order_by(desc(AgentProfileDraftRevision.created_at))
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
                            "prompt_reference_count": len(
                                revision.prompt_references_json or []
                            ),
                        },
                    }
                )

            validation_stmt = (
                select(AgentProfileValidationResult)
                .join(
                    AgentProfileDraftRevision,
                    AgentProfileDraftRevision.agent_profile_draft_revision_id
                    == AgentProfileValidationResult.agent_profile_draft_revision_id,
                )
                .where(AgentProfileDraftRevision.agent_profile_draft_id.in_(draft_ids))
                .order_by(desc(AgentProfileValidationResult.executed_at))
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

        version_stmt = select(AgentProfileVersion)
        if profile_ids:
            version_stmt = version_stmt.where(
                AgentProfileVersion.agent_runtime_profile_id.in_(profile_ids)
            )
        if agent_profile_version_id is not None:
            version_stmt = version_stmt.where(
                AgentProfileVersion.agent_profile_version_id == agent_profile_version_id
            )
        if tenant_id is not None:
            version_stmt = version_stmt.where(
                or_(
                    AgentProfileVersion.tenant_id == tenant_id,
                    AgentProfileVersion.tenant_id.is_(None),
                )
            )
        versions = list((await self.session.execute(version_stmt)).scalars().all())
        version_ids = [version.agent_profile_version_id for version in versions]
        for version in versions:
            events.append(
                {
                    "action": "activate",
                    "actor_principal_id": version.activated_by_principal_id,
                    "created_at": version.activated_at,
                    "outcome": version.status,
                    "reason": version.activation_reason,
                    "redacted_diff_summary": {
                        "display_version": version.display_version,
                        "prompt_reference_count": len(
                            version.prompt_references_json or []
                        ),
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
                select(TenantProfileVersionGrant)
                .where(
                    TenantProfileVersionGrant.agent_profile_version_id.in_(version_ids)
                )
                .order_by(desc(TenantProfileVersionGrant.created_at))
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
            key=lambda event: cast(datetime, event["created_at"]),
            reverse=True,
        )[:limit]
