from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.service import PromptService


async def test_retired_prompt_version_keeps_content_but_is_not_new_use_eligible(
    session,
) -> None:
    service = PromptService.from_session(session)
    created = await service.create_prompt_lineage(
        scope_type="tenant",
        tenant_id=uuid4(),
        slug="triage-summary",
        display_name="Triage Summary",
        purpose="Summarize intake",
        principal_id="tenant-admin",
    )
    revision = await service.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        prompt_title="Triage Summary",
        purpose="Summarize intake",
        usage_notes="",
        template_content="Hello {{name}}",
        variables=[PromptVariableDeclaration(name="name", purpose="Recipient")],
        fixture_values={"name": "Ada"},
        principal_id="tenant-admin",
    )
    validation = await service.validate_revision(
        draft_revision=revision,
        principal_id="tenant-admin",
    )
    version = await service.publish(
        lineage=created.lineage,
        draft=created.draft,
        draft_revision=revision,
        validation_result=validation,
        principal_id="tenant-admin",
        reason="Initial publication",
    )

    retired = await service.retire_version(
        version=version,
        principal_id="tenant-admin",
        reason="Replace with a safer version",
    )
    eligible = await service.repository.list_new_use_versions(
        tenant_id=version.tenant_id,
        include_platform=False,
    )

    assert retired.status == "retired"
    assert retired.template_content == "Hello {{name}}"
    assert retired.prompt_version_id not in {
        item.prompt_version_id for item in eligible
    }
