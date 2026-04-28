from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.repositories.prompts import StalePromptRevisionError
from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.service import PromptService


async def test_prompt_service_creates_draft_and_rejects_stale_saves(session) -> None:
    service = PromptService.from_session(session)
    tenant_id = uuid4()
    created = await service.create_prompt_lineage(
        scope_type="tenant",
        tenant_id=tenant_id,
        slug="triage-summary",
        display_name="Triage Summary",
        purpose="Summarize intake",
        principal_id="tenant-admin",
    )

    await service.save_draft_revision(
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

    with pytest.raises(StalePromptRevisionError):
        await service.save_draft_revision(
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
