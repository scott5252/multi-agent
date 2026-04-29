from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.reference_validation import (
    build_editor_lookup_response,
    pin_summary_from_snapshots,
    validate_reference_readiness,
)
from multi_agent_platform.api.schemas.workflow_editor import ReferenceReadinessSnapshot
from multi_agent_platform.api.schemas.workflow_registry import (
    ModelRoutingPreviewReference,
    PromptProfileReference,
    SkillInstallationReference,
    SubworkflowReference,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    TestSuiteRequirement as BuilderTestSuiteRequirement,
)


def test_reference_readiness_blocks_missing_skill_subworkflow_and_tests(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(
        update={
            "skill_installations": [
                SkillInstallationReference(
                    skill_installation_key="floating",
                    skill_slug="triage-agent",
                    skill_version="latest",
                    credential_requirement_status="ready",
                )
            ],
            "subworkflow_refs": [
                SubworkflowReference(alias="child", workflow_version_ref="missing")
            ],
            "test_requirements": [
                BuilderTestSuiteRequirement(requirement_key="smoke", suite_id="smoke")
            ],
        }
    )

    snapshots, findings, tests = validate_reference_readiness(document)

    assert tests.missing_count == 1
    assert any(snapshot.reference_type == "skill" for snapshot in snapshots)
    assert any(finding["code"] == "reference.skill.not_ready" for finding in findings)
    assert any(
        finding["code"] == "reference.subworkflow.not_visible" for finding in findings
    )


def test_editor_lookups_are_tenant_filtered_and_searchable(
    sample_workflow_document,
) -> None:
    response = build_editor_lookup_response(
        sample_workflow_document,
        lookup_kind="contracts",
        scope_type="tenant",
        tenant_id="tenant-1",
        search="intake",
    )

    assert response.groups[0].lookup_kind == "contracts"
    assert response.groups[0].options[0].tenant_id == "tenant-1"
    assert response.groups[0].options[0].value == "intake-request"


def test_reference_readiness_pins_prompt_profiles_and_ready_refs(
    sample_workflow_document,
) -> None:
    provider_catalog_entry_id = uuid4()
    document = sample_workflow_document.model_copy(
        update={
            "prompt_profile_references": [
                PromptProfileReference(
                    reference_key="triage-profile",
                    role_key="triage-role",
                    agent_key="triage-agent",
                    agent_profile_version_id=uuid4(),
                    prompt_reference_version_ids=[uuid4()],
                    prompt_version_ids=[uuid4()],
                    model_routing_preview=ModelRoutingPreviewReference(
                        preview_key="triage-route",
                        provider_catalog_entry_id=provider_catalog_entry_id,
                        model_id="example-model",
                        health_state="ready",
                        policy_status="allowed",
                    ),
                    readiness_status="retired",
                )
            ],
            "skill_installations": [
                SkillInstallationReference(
                    skill_installation_key="triage-skill",
                    skill_slug="triage-agent",
                    skill_version="2026.04.1",
                    credential_requirement_status="ready",
                )
            ],
            "subworkflow_refs": [
                SubworkflowReference(alias="child", workflow_version_ref="bundle-1")
            ],
            "test_requirements": [
                BuilderTestSuiteRequirement(
                    requirement_key="smoke",
                    suite_id="smoke",
                    latest_result_status="passed",
                )
            ],
        }
    )

    snapshots, findings, tests = validate_reference_readiness(
        document,
        visible_subworkflow_version_ids={"bundle-1"},
    )
    pin_summary = pin_summary_from_snapshots(
        [
            *snapshots,
            ReferenceReadinessSnapshot(
                reference_type="test_suite",
                reference_key="smoke",
                status="passed",
                pin_payload={"suite_id": "smoke"},
            ),
        ]
    )

    assert tests.passing_count == 1
    assert any(
        finding["code"] == "reference.prompt_profile.not_ready" for finding in findings
    )
    assert not any(
        finding["code"] == "reference.skill.not_ready" for finding in findings
    )
    assert pin_summary["prompt_profile_pins"]
    assert pin_summary["skill_installation_pins"]
    assert pin_summary["subworkflow_bundle_pins"]
    assert pin_summary["required_test_evidence"] == [{"suite_id": "smoke"}]
    assert pin_summary["provider_catalog_pins"][0]["provider_catalog_entry_id"] == str(
        provider_catalog_entry_id
    )


def test_editor_lookup_response_handles_empty_documents_and_search() -> None:
    response = build_editor_lookup_response(
        document=None,
        lookup_kind="profiles",
        search="missing",
    )

    assert response.groups[0].lookup_kind == "profiles"
    assert response.groups[0].options == []
