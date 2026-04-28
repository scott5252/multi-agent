from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.prompts import PromptRepository
from multi_agent_platform.prompts.service import PromptService


async def test_prompt_repository_creates_lineage_draft_revision_and_validation(
    session,
) -> None:
    repository = PromptRepository(session)
    tenant_id = uuid4()

    created = await repository.create_lineage_with_draft(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug="triage-summary",
        display_name="Triage Summary",
        purpose="Summarize intake",
        principal_id="tenant-admin",
    )
    revision = await repository.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        prompt_title="Triage Summary",
        purpose="Summarize intake",
        usage_notes="Use fixture values",
        template_content="Hello {{name}}",
        variable_declarations=[{"name": "name"}],
        fixture_value_sets=[],
        safe_summary={"variables": 1},
        principal_id="tenant-admin",
    )
    validation = await repository.record_validation_result(
        draft_revision=revision,
        status="passed",
        findings=[],
        principal_id="tenant-admin",
    )

    assert created.lineage.latest_draft_id == created.draft.prompt_draft_id
    assert created.draft.current_revision_number == 1
    assert validation.blocking_issue_count == 0


async def test_prompt_repository_visibility_versions_and_history_helpers(
    session,
) -> None:
    repository = PromptRepository(session)
    service = PromptService(repository)
    tenant_id = uuid4()
    other_tenant_id = uuid4()

    assert (
        await repository.list_visible_lineages(
            principal_tenant_id=None,
            include_platform_admin=False,
        )
        == []
    )
    assert (
        await repository.is_version_visible_to_tenant(
            prompt_version_id=uuid4(),
            tenant_id=tenant_id,
        )
        is False
    )

    tenant_created = await repository.create_lineage_with_draft(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug="tenant-planner",
        display_name="Tenant Planner",
        purpose="planner",
        principal_id="tenant-admin",
    )
    tenant_revision = await repository.save_draft_revision(
        draft=tenant_created.draft,
        expected_revision_number=0,
        prompt_title="Tenant Planner",
        purpose="planner",
        usage_notes="",
        template_content="Hello {{name}}",
        variable_declarations=[{"name": "name", "purpose": "Recipient"}],
        fixture_value_sets=[
            {
                "fixture_set_id": "default",
                "label": "Default",
                "values_by_variable": {"name": "Ada"},
            }
        ],
        safe_summary={"variables": 1},
        principal_id="tenant-admin",
    )
    tenant_validation = await repository.record_validation_result(
        draft_revision=tenant_revision,
        status="passed",
        findings=[],
        principal_id="tenant-admin",
    )
    tenant_version = await service.publish(
        lineage=tenant_created.lineage,
        draft=tenant_created.draft,
        draft_revision=tenant_revision,
        validation_result=tenant_validation,
        principal_id="tenant-admin",
        reason="Tenant release",
    )

    platform_created = await repository.create_lineage_with_draft(
        scope_type="platform",
        tenant_id=None,
        slug="platform-planner",
        display_name="Platform Planner",
        purpose="planner",
        principal_id="platform-admin",
    )
    platform_revision = await repository.save_draft_revision(
        draft=platform_created.draft,
        expected_revision_number=0,
        prompt_title="Platform Planner",
        purpose="planner",
        usage_notes="",
        template_content="Plan for {{name}}",
        variable_declarations=[{"name": "name", "purpose": "Recipient"}],
        fixture_value_sets=[],
        safe_summary={"variables": 1},
        principal_id="platform-admin",
    )
    platform_validation = await repository.record_validation_result(
        draft_revision=platform_revision,
        status="passed",
        findings=[],
        principal_id="platform-admin",
    )
    platform_version = await service.publish(
        lineage=platform_created.lineage,
        draft=platform_created.draft,
        draft_revision=platform_revision,
        validation_result=platform_validation,
        principal_id="platform-admin",
        reason="Platform release",
    )

    assert await repository.list_versions_for_lineage(
        tenant_created.lineage.prompt_lineage_id
    ) == [tenant_version]
    assert await repository.list_new_use_versions(
        tenant_id=None,
        include_platform=True,
    ) == [platform_version]
    assert {
        version.prompt_version_id
        for version in await repository.list_new_use_versions(
            tenant_id=tenant_id,
            include_platform=True,
        )
    } == {tenant_version.prompt_version_id, platform_version.prompt_version_id}
    assert await repository.list_new_use_versions(
        tenant_id=tenant_id,
        include_platform=False,
    ) == [tenant_version]

    assert (
        await repository.is_version_visible_to_tenant(
            prompt_version_id=tenant_version.prompt_version_id,
            tenant_id=tenant_id,
        )
        is True
    )
    assert (
        await repository.is_version_visible_to_tenant(
            prompt_version_id=tenant_version.prompt_version_id,
            tenant_id=other_tenant_id,
        )
        is False
    )
    assert (
        await repository.is_version_visible_to_tenant(
            prompt_version_id=platform_version.prompt_version_id,
            tenant_id=tenant_id,
        )
        is False
    )

    grant = await repository.grant_prompt_version(
        prompt_version_id=platform_version.prompt_version_id,
        grantee_tenant_id=tenant_id,
        principal_id="platform-admin",
        reason="Tenant fallback",
    )
    assert grant in await repository.list_grants_for_version(
        platform_version.prompt_version_id
    )
    assert (
        await repository.is_version_visible_to_tenant(
            prompt_version_id=platform_version.prompt_version_id,
            tenant_id=tenant_id,
        )
        is True
    )
    assert {
        lineage.prompt_lineage_id
        for lineage in await repository.list_visible_lineages(
            principal_tenant_id=tenant_id,
            include_platform_admin=False,
            q="planner",
        )
    } == {
        tenant_created.lineage.prompt_lineage_id,
        platform_created.lineage.prompt_lineage_id,
    }
    assert await repository.list_visible_lineages(
        principal_tenant_id=tenant_id,
        include_platform_admin=True,
        scope_type="tenant",
        status="active",
        q="tenant",
    ) == [tenant_created.lineage]

    await repository.retire_prompt_version(
        version=tenant_version,
        principal_id="tenant-admin",
        reason="Retire tenant version",
    )
    assert tenant_version.retired_at is not None

    history_by_version = await repository.list_prompt_history(
        prompt_version_id=tenant_version.prompt_version_id,
        tenant_id=tenant_id,
    )
    assert {"save_draft", "validate", "publish", "retire"}.issubset(
        {event["action"] for event in history_by_version}
    )
    history_by_missing_version = await repository.list_prompt_history(
        prompt_version_id=uuid4(),
    )
    assert history_by_missing_version == []
    combined_history = await repository.list_prompt_history(tenant_id=tenant_id)
    assert any(event["action"] == "grant" for event in combined_history)
