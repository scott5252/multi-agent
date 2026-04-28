from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.agent_profiles import (
    ActiveAgentProfilePointer,
    AgentProfileDraft,
    AgentProfileDraftRevision,
    AgentProfileValidationResult,
    AgentRuntimeProfile,
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
