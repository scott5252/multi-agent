from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.prompts import (
    PromptDraftRevision,
    PromptLineage,
    PromptVersion,
)


def test_prompt_tables_are_registered() -> None:
    import_models()

    assert "prompt_lineages" in Base.metadata.tables
    assert "prompt_draft_revisions" in Base.metadata.tables
    assert "prompt_versions" in Base.metadata.tables


def test_prompt_models_track_immutable_revision_and_version_digests() -> None:
    lineage = PromptLineage(
        scope_type="tenant",
        tenant_id=uuid4(),
        slug="triage-summary",
        display_name="Triage Summary",
        purpose="Summarize intake details",
        created_by_principal_id="tenant-admin",
    )
    revision = PromptDraftRevision(
        prompt_draft_id=uuid4(),
        revision_number=1,
        prompt_title="Triage",
        purpose="Summarize",
        usage_notes="Use with synthetic fixtures",
        template_content="Hello {{name}}",
        template_content_sha256="a" * 64,
        variable_declarations_json=[{"name": "name"}],
        fixture_value_sets_json=[],
        safe_summary_json={"variables": 1},
        created_by_principal_id="tenant-admin",
    )
    version = PromptVersion(
        prompt_lineage_id=uuid4(),
        scope_type="tenant",
        tenant_id=lineage.tenant_id,
        version_sequence=1,
        display_version="v1",
        published_from_draft_id=uuid4(),
        published_from_revision_id=uuid4(),
        validation_result_id=uuid4(),
        template_content=revision.template_content,
        template_content_sha256=revision.template_content_sha256,
        variable_declarations_json=revision.variable_declarations_json,
        purpose=revision.purpose,
        usage_notes=revision.usage_notes,
        safe_summary_json=revision.safe_summary_json,
        published_by_principal_id="tenant-admin",
        publication_reason="Initial publication",
    )

    assert lineage.slug == "triage-summary"
    assert revision.template_content_sha256 == "a" * 64
    assert version.template_content == "Hello {{name}}"
