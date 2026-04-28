from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.service import PromptPublishError, PromptService


async def test_prompt_service_publishes_validated_immutable_version(session) -> None:
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

    assert version.version_sequence == 1
    assert version.template_content == "Hello {{name}}"
    assert (
        created.lineage.latest_published_prompt_version_id == version.prompt_version_id
    )


async def test_prompt_service_rejects_publish_without_passing_validation(
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
        template_content="Hello {{name}} {{missing}}",
        variables=[PromptVariableDeclaration(name="name", purpose="Recipient")],
        fixture_values={"name": "Ada"},
        principal_id="tenant-admin",
    )
    validation = await service.validate_revision(
        draft_revision=revision,
        principal_id="tenant-admin",
    )

    with pytest.raises(PromptPublishError):
        await service.publish(
            lineage=created.lineage,
            draft=created.draft,
            draft_revision=revision,
            validation_result=validation,
            principal_id="tenant-admin",
            reason="Initial publication",
        )
