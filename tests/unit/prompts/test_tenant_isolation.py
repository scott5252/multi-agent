from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.prompts import PromptVersion
from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.service import PromptService


async def test_platform_prompt_visibility_requires_per_version_grant(session) -> None:
    service = PromptService.from_session(session)
    tenant_id = uuid4()
    created = await service.create_prompt_lineage(
        scope_type="platform",
        tenant_id=None,
        slug="platform-triage",
        display_name="Platform Triage",
        purpose="Summarize intake",
        principal_id="platform-admin",
    )
    revision = await service.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        prompt_title="Platform Triage",
        purpose="Summarize intake",
        usage_notes="",
        template_content="Hello {{name}}",
        variables=[PromptVariableDeclaration(name="name", purpose="Recipient")],
        fixture_values={"name": "Ada"},
        principal_id="platform-admin",
    )
    validation = await service.validate_revision(
        draft_revision=revision,
        principal_id="platform-admin",
    )
    version = await service.publish(
        lineage=created.lineage,
        draft=created.draft,
        draft_revision=revision,
        validation_result=validation,
        principal_id="platform-admin",
        reason="Initial publication",
    )

    assert not await service.repository.is_version_visible_to_tenant(
        prompt_version_id=version.prompt_version_id,
        tenant_id=tenant_id,
    )

    await service.grant_version_to_tenant(
        version=version,
        tenant_id=tenant_id,
        principal_id="platform-admin",
        reason="Allow tenant use",
    )

    assert await service.repository.is_version_visible_to_tenant(
        prompt_version_id=version.prompt_version_id,
        tenant_id=tenant_id,
    )


async def test_tenant_prompt_visibility_is_limited_to_owning_tenant(session) -> None:
    owner_tenant_id = uuid4()
    other_tenant_id = uuid4()
    version = PromptVersion(
        prompt_lineage_id=uuid4(),
        scope_type="tenant",
        tenant_id=owner_tenant_id,
        version_sequence=1,
        display_version="v1",
        published_from_draft_id=uuid4(),
        published_from_revision_id=uuid4(),
        validation_result_id=uuid4(),
        template_content="Hello {{name}}",
        template_content_sha256="a" * 64,
        variable_declarations_json=[],
        purpose="Summarize",
        usage_notes="",
        safe_summary_json={},
        published_by_principal_id="tenant-admin",
        publication_reason="Initial",
    )
    session.add(version)
    await session.flush()
    service = PromptService.from_session(session)

    assert await service.repository.is_version_visible_to_tenant(
        prompt_version_id=version.prompt_version_id,
        tenant_id=owner_tenant_id,
    )
    assert not await service.repository.is_version_visible_to_tenant(
        prompt_version_id=version.prompt_version_id,
        tenant_id=other_tenant_id,
    )
