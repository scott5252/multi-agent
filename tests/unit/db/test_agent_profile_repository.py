from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.agent_profiles import AgentProfileRepository


async def test_agent_profile_repository_creates_profile_and_active_pointer(
    session,
) -> None:
    repository = AgentProfileRepository(session)
    tenant_id = uuid4()

    created = await repository.create_profile_with_draft(
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
        display_name="Planner",
        purpose="Plan work",
        principal_id="tenant-admin",
    )
    revision = await repository.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        purpose="Plan work",
        prompt_references=[],
        model_routing_hints={},
        memory_scope_policy={},
        skill_requirements=[],
        tool_policy_expectations=[],
        output_contract_expectations={},
        test_suite_requirements=[],
        safe_summary={},
        principal_id="tenant-admin",
    )
    validation = await repository.record_validation_result(
        draft_revision=revision,
        status="passed",
        findings=[],
        principal_id="tenant-admin",
    )

    assert created.profile.latest_draft_id == created.draft.agent_profile_draft_id
    assert created.draft.current_revision_number == 1
    assert validation.blocking_issue_count == 0
