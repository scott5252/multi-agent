from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.field_help import (
    build_editor_metadata,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    PromptProfileReference,
    SkillInstallationReference,
    WorkflowDraftDocument,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    TestSuiteRequirement as BuilderTestSuiteRequirement,
)


def test_builder_document_round_trips_guided_sections(sample_workflow_document) -> None:
    document = sample_workflow_document.model_copy(
        update={
            "prompt_profile_references": [
                PromptProfileReference(
                    reference_key="triage-profile",
                    role_key="triage-role",
                    agent_key="triage",
                    agent_profile_version_id=uuid4(),
                    prompt_version_ids=[uuid4()],
                    readiness_status="ready",
                )
            ],
            "skill_installations": [
                SkillInstallationReference(
                    skill_installation_key="triage-skill-install",
                    skill_slug="triage-agent",
                    skill_version="2026.04.1",
                    credential_requirement_status="ready",
                )
            ],
            "test_requirements": [
                BuilderTestSuiteRequirement(
                    requirement_key="smoke",
                    suite_id="workflow-smoke",
                    latest_result_status="passed",
                )
            ],
        }
    )

    parsed = WorkflowDraftDocument.model_validate(document.model_dump(mode="json"))

    assert parsed.prompt_profile_references[0].readiness_status == "ready"
    assert parsed.skill_installations[0].skill_version == "2026.04.1"
    assert parsed.test_requirements[0].latest_result_status == "passed"


def test_editor_metadata_exposes_sections_fields_lookups_and_actions() -> None:
    metadata = build_editor_metadata()

    assert [section.section_key for section in metadata.sections[:3]] == [
        "overview",
        "roles",
        "prompt_profile_references",
    ]
    assert "skills" in metadata.lookup_sources
    assert metadata.action_urls.create_ui == "/admin/workflows/new"
    assert any(field.field_path == "nodes[].node_key" for field in metadata.fields)
    assert any(
        code.code == "graph.node.disconnected" for code in metadata.validation_codes
    )
