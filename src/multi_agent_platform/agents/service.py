from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.agents.resolution import (
    AgentProfileResolution,
    resolve_agent_profile,
)
from multi_agent_platform.agents.validation import (
    validate_profile_contract,
    validate_profile_prompt_references,
)
from multi_agent_platform.db.models.agent_profiles import (
    ActiveAgentProfilePointer,
    AgentProfileDraft,
    AgentProfileDraftRevision,
    AgentProfileValidationResult,
    AgentProfileVersion,
    AgentRuntimeProfile,
    TenantProfileVersionGrant,
)
from multi_agent_platform.db.repositories.agent_profiles import (
    AgentProfileDraftRecord,
    AgentProfileRepository,
)


class AgentProfileActivationError(RuntimeError):
    pass


class AgentProfileGrantError(RuntimeError):
    pass


class AgentProfileService:
    def __init__(self, repository: AgentProfileRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: AsyncSession) -> AgentProfileService:
        return cls(AgentProfileRepository(session))

    async def create_profile(
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
        return await self.repository.create_profile_with_draft(
            scope_type=scope_type,
            tenant_id=tenant_id,
            agent_key=agent_key,
            agent_kind=agent_kind,
            display_name=display_name,
            purpose=purpose,
            principal_id=principal_id,
        )

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
        principal_id: str,
    ) -> AgentProfileDraftRevision:
        return await self.repository.save_draft_revision(
            draft=draft,
            expected_revision_number=expected_revision_number,
            purpose=purpose,
            prompt_references=prompt_references,
            model_routing_hints=model_routing_hints,
            memory_scope_policy=memory_scope_policy,
            skill_requirements=skill_requirements,
            tool_policy_expectations=tool_policy_expectations,
            output_contract_expectations=output_contract_expectations,
            test_suite_requirements=test_suite_requirements,
            safe_summary={"prompt_reference_count": len(prompt_references)},
            principal_id=principal_id,
        )

    async def validate_revision(
        self,
        *,
        draft_revision: AgentProfileDraftRevision,
        principal_id: str,
    ) -> AgentProfileValidationResult:
        report = validate_profile_contract(
            prompt_references=draft_revision.prompt_references_json,
            model_routing_hints=draft_revision.model_routing_hints_json,
            memory_scope_policy=draft_revision.memory_scope_policy_json,
            skill_requirements=draft_revision.skill_requirements_json,
            tool_policy_expectations=draft_revision.tool_policy_expectations_json,
            output_contract_expectations=(
                draft_revision.output_contract_expectations_json
            ),
            test_suite_requirements=draft_revision.test_suite_requirements_json,
        )
        draft = await self.repository.session.get(
            AgentProfileDraft,
            draft_revision.agent_profile_draft_id,
        )
        prompt_reference_report = validate_profile_prompt_references(
            prompt_references=draft_revision.prompt_references_json,
            prompt_versions=await self.repository.prompt_versions_for_references(
                draft_revision.prompt_references_json
            ),
            tenant_id=str(draft.tenant_id) if draft and draft.tenant_id else None,
        )
        findings = [
            *report.to_json_findings(),
            *prompt_reference_report.to_json_findings(),
        ]
        return await self.repository.record_validation_result(
            draft_revision=draft_revision,
            status="failed" if findings else "passed",
            findings=findings,
            principal_id=principal_id,
        )

    async def activate(
        self,
        *,
        profile: AgentRuntimeProfile,
        draft: AgentProfileDraft,
        draft_revision: AgentProfileDraftRevision,
        validation_result: AgentProfileValidationResult,
        principal_id: str,
        reason: str,
    ) -> AgentProfileVersion:
        if validation_result.status != "passed":
            raise AgentProfileActivationError("profile validation must pass")
        sequence = await self.repository.next_profile_version_sequence(
            profile.agent_runtime_profile_id
        )
        version = AgentProfileVersion(
            agent_runtime_profile_id=profile.agent_runtime_profile_id,
            scope_type=profile.scope_type,
            tenant_id=profile.tenant_id,
            agent_key=profile.agent_key,
            agent_kind=profile.agent_kind,
            version_sequence=sequence,
            display_version=f"v{sequence}",
            activated_from_draft_id=draft.agent_profile_draft_id,
            activated_from_revision_id=draft_revision.agent_profile_draft_revision_id,
            validation_result_id=validation_result.agent_profile_validation_result_id,
            purpose=draft_revision.purpose,
            prompt_references_json=draft_revision.prompt_references_json,
            model_routing_hints_json=draft_revision.model_routing_hints_json,
            memory_scope_policy_json=draft_revision.memory_scope_policy_json,
            skill_requirements_json=draft_revision.skill_requirements_json,
            tool_policy_expectations_json=(
                draft_revision.tool_policy_expectations_json
            ),
            output_contract_expectations_json=(
                draft_revision.output_contract_expectations_json
            ),
            test_suite_requirements_json=draft_revision.test_suite_requirements_json,
            safe_summary_json=draft_revision.safe_summary_json,
            activated_by_principal_id=principal_id,
            activation_reason=reason,
        )
        self.repository.session.add(version)
        await self.repository.session.flush()
        profile.active_profile_version_id = version.agent_profile_version_id
        pointer = await self.repository.resolve_active_pointer(
            scope_type=profile.scope_type,
            tenant_id=profile.tenant_id,
            agent_kind=profile.agent_kind,
            agent_key=profile.agent_key,
        )
        if pointer is None:
            pointer = ActiveAgentProfilePointer(
                scope_type=profile.scope_type,
                tenant_id=profile.tenant_id,
                agent_kind=profile.agent_kind,
                agent_key=profile.agent_key,
                active_profile_version_id=version.agent_profile_version_id,
                activated_by_principal_id=principal_id,
                activation_reason=reason,
            )
            self.repository.session.add(pointer)
        else:
            pointer.expected_previous_version_id = pointer.active_profile_version_id
            pointer.active_profile_version_id = version.agent_profile_version_id
            pointer.activated_by_principal_id = principal_id
            pointer.activation_reason = reason
        await self.repository.session.flush()
        return version

    async def retire_version(
        self,
        *,
        version: AgentProfileVersion,
        principal_id: str,
        reason: str,
    ) -> AgentProfileVersion:
        return await self.repository.retire_profile_version(
            version=version,
            principal_id=principal_id,
            reason=reason,
        )

    async def grant_version_to_tenant(
        self,
        *,
        version: AgentProfileVersion,
        tenant_id: UUID,
        principal_id: str,
        reason: str,
    ) -> TenantProfileVersionGrant:
        if version.scope_type != "platform":
            raise AgentProfileGrantError(
                "only platform profile versions can be granted"
            )
        return await self.repository.grant_profile_version(
            agent_profile_version_id=version.agent_profile_version_id,
            grantee_tenant_id=tenant_id,
            principal_id=principal_id,
            reason=reason,
        )

    async def resolve_profile(
        self,
        *,
        tenant_id: UUID,
        agent_key: str,
        agent_kind: str,
    ) -> AgentProfileResolution:
        return resolve_agent_profile(
            tenant_id=tenant_id,
            agent_key=agent_key,
            agent_kind=agent_kind,
            candidates=await self.repository.list_resolution_candidates(
                tenant_id=tenant_id,
                agent_key=agent_key,
                agent_kind=agent_kind,
            ),
        )
