from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.prompts import PromptRepository


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
