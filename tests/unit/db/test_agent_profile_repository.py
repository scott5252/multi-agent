from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.agents.service import AgentProfileService
from multi_agent_platform.db.repositories.agent_profiles import AgentProfileRepository
from multi_agent_platform.db.repositories.prompts import PromptRepository
from multi_agent_platform.prompts.service import PromptService


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


async def _publish_prompt_version(
    session,
    *,
    scope_type: str,
    tenant_id,
    slug: str,
) -> object:
    repository = PromptRepository(session)
    service = PromptService(repository)
    created = await repository.create_lineage_with_draft(
        scope_type=scope_type,
        tenant_id=tenant_id,
        slug=slug,
        display_name=slug.title(),
        purpose="planner",
        principal_id="prompt-admin",
    )
    revision = await repository.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        prompt_title=slug.title(),
        purpose="planner",
        usage_notes="",
        template_content="Hello {{name}}",
        variable_declarations=[{"name": "name", "purpose": "Recipient"}],
        fixture_value_sets=[],
        safe_summary={},
        principal_id="prompt-admin",
    )
    validation = await repository.record_validation_result(
        draft_revision=revision,
        status="passed",
        findings=[],
        principal_id="prompt-admin",
    )
    return await service.publish(
        lineage=created.lineage,
        draft=created.draft,
        draft_revision=revision,
        validation_result=validation,
        principal_id="prompt-admin",
        reason="Prompt release",
    )


async def _activate_profile_version(
    repository: AgentProfileRepository,
    *,
    scope_type: str,
    tenant_id,
    agent_key: str,
    principal_id: str,
) -> object:
    service = AgentProfileService(repository)
    created = await repository.create_profile_with_draft(
        scope_type=scope_type,
        tenant_id=tenant_id,
        agent_key=agent_key,
        agent_kind="agent",
        display_name=agent_key.title(),
        purpose="Plan work",
        principal_id=principal_id,
    )
    revision = await repository.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        purpose="Plan work",
        prompt_references=[{"purpose": "planner"}],
        model_routing_hints={"provider": "openai"},
        memory_scope_policy={"scope_mode": "read_only", "retention_mode": "run"},
        skill_requirements=[{"skill": "planning"}],
        tool_policy_expectations=[{"category": "read"}],
        output_contract_expectations={"type": "object"},
        test_suite_requirements=[{"suite": "smoke"}],
        safe_summary={},
        principal_id=principal_id,
    )
    validation = await repository.record_validation_result(
        draft_revision=revision,
        status="passed",
        findings=[],
        principal_id=principal_id,
    )
    return created, await service.activate(
        profile=created.profile,
        draft=created.draft,
        draft_revision=revision,
        validation_result=validation,
        principal_id=principal_id,
        reason="Activate profile",
    )


async def test_agent_profile_repository_visibility_resolution_and_history_helpers(
    session,
) -> None:
    repository = AgentProfileRepository(session)
    tenant_id = uuid4()
    other_tenant_id = uuid4()

    assert (
        await repository.list_visible_profiles(
            principal_tenant_id=None,
            include_platform_admin=False,
        )
        == []
    )
    assert (
        await repository.list_resolution_candidates(
            tenant_id=tenant_id,
            agent_key="missing",
            agent_kind="agent",
        )
        == ()
    )
    assert await repository.prompt_versions_for_references([]) == {}
    assert (
        await repository.prompt_versions_for_references(
            [{"prompt_version_id": "not-a-uuid"}]
        )
        == {}
    )

    tenant_prompt = await _publish_prompt_version(
        session,
        scope_type="tenant",
        tenant_id=tenant_id,
        slug="tenant-profile-prompt",
    )
    platform_prompt = await _publish_prompt_version(
        session,
        scope_type="platform",
        tenant_id=None,
        slug="platform-profile-prompt",
    )
    prompt_repository = PromptRepository(session)
    await prompt_repository.grant_prompt_version(
        prompt_version_id=platform_prompt.prompt_version_id,
        grantee_tenant_id=tenant_id,
        principal_id="platform-admin",
        reason="Prompt fallback",
    )
    prompt_reference_map = await repository.prompt_versions_for_references(
        [
            {"prompt_version_id": str(tenant_prompt.prompt_version_id)},
            {"prompt_version_id": str(platform_prompt.prompt_version_id)},
        ]
    )
    assert prompt_reference_map[str(tenant_prompt.prompt_version_id)]["tenant_id"] == (
        str(tenant_id)
    )
    assert prompt_reference_map[str(platform_prompt.prompt_version_id)]["grants"] == [
        str(tenant_id)
    ]

    tenant_created, tenant_version = await _activate_profile_version(
        repository,
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_key="planner",
        principal_id="tenant-admin",
    )
    platform_created, platform_version = await _activate_profile_version(
        repository,
        scope_type="platform",
        tenant_id=None,
        agent_key="planner",
        principal_id="platform-admin",
    )
    assert await repository.list_versions_for_profile(
        tenant_created.profile.agent_runtime_profile_id
    ) == [tenant_version]
    assert await repository.resolve_active_pointer(
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_kind="agent",
        agent_key="planner",
    )

    profile_grant = await repository.grant_profile_version(
        agent_profile_version_id=platform_version.agent_profile_version_id,
        grantee_tenant_id=tenant_id,
        principal_id="platform-admin",
        reason="Profile fallback",
    )
    assert profile_grant in await repository.list_grants_for_version(
        platform_version.agent_profile_version_id
    )
    assert {
        profile.agent_runtime_profile_id
        for profile in await repository.list_visible_profiles(
            principal_tenant_id=tenant_id,
            include_platform_admin=False,
            agent_key="planner",
            agent_kind="agent",
        )
    } == {
        tenant_created.profile.agent_runtime_profile_id,
        platform_created.profile.agent_runtime_profile_id,
    }
    assert await repository.list_visible_profiles(
        principal_tenant_id=tenant_id,
        include_platform_admin=True,
        agent_key="planner",
        agent_kind="agent",
    )

    candidates = await repository.list_resolution_candidates(
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
    )
    assert {candidate.scope_type for candidate in candidates} == {"tenant", "platform"}
    assert any(
        candidate.granted_tenant_ids == (tenant_id,)
        for candidate in candidates
        if candidate.scope_type == "platform"
    )

    await repository.retire_profile_version(
        version=tenant_version,
        principal_id="tenant-admin",
        reason="Retire tenant profile",
    )
    assert tenant_version.retired_at is not None
    assert tenant_created.profile.active_profile_version_id is None
    assert (
        await repository.resolve_active_pointer(
            scope_type="tenant",
            tenant_id=tenant_id,
            agent_kind="agent",
            agent_key="planner",
        )
        is None
    )

    history_by_version = await repository.list_profile_history(
        agent_profile_version_id=tenant_version.agent_profile_version_id,
        tenant_id=tenant_id,
    )
    assert {"save_draft", "validate", "activate", "retire"}.issubset(
        {event["action"] for event in history_by_version}
    )
    assert (
        await repository.list_profile_history(
            agent_profile_version_id=uuid4(),
        )
        == []
    )
    combined_history = await repository.list_profile_history(tenant_id=tenant_id)
    assert any(event["action"] == "grant" for event in combined_history)

    other_visible = await repository.list_visible_profiles(
        principal_tenant_id=other_tenant_id,
        include_platform_admin=False,
        agent_key="planner",
    )
    assert other_visible == []
