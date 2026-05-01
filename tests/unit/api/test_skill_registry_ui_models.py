from __future__ import annotations

import json

from multi_agent_platform.admin.skill_registry.service import SkillRegistryService
from multi_agent_platform.api.ui.skill_registry import (
    BindingEligibilityPreviewForm,
    CredentialReferenceConfigForm,
    InstallSkillForm,
    ManifestCandidateForm,
    RedactionSafePageContext,
    SkillPackageCreateForm,
    SmokeTestActionForm,
    TenantGrantForm,
    build_package_list_page,
    build_revision_conflict_view,
)
from tests.fixtures.skill_registry import valid_skill_manifest


def test_skill_registry_ui_model_omits_raw_content() -> None:
    service = SkillRegistryService()
    package = service.create_package(
        slug="calendar-assistant",
        display_name="Calendar Assistant",
        description="Safe calendar skill.",
        owner_principal_id="platform-admin",
        actor_principal_id="platform-admin",
    )

    page = build_package_list_page([package], platform_admin=True)

    assert page.packages[0]["slug"] == "calendar-assistant"
    assert "Raw package payloads" in page.redaction_notice


def test_browser_form_models_parse_primary_skill_registry_forms() -> None:
    package = SkillPackageCreateForm.from_mapping(
        {
            "slug": "Calendar-Assistant",
            "display_name": "Calendar Assistant",
            "description": "Safe calendar skill.",
            "safe_documentation_summary": "Operator-safe docs only.",
        },
        default_owner="platform-admin",
    )
    manifest = ManifestCandidateForm.from_mapping(
        {
            "manifest": json.dumps(valid_skill_manifest()),
            "artifact_digest": "sha256:artifact",
            "approved_integration_refs": "tool:calendar:v1",
            "revision_token": "candidate-1",
        }
    )
    grant = TenantGrantForm.from_mapping(
        {"tenant_ids": "tenant-a, tenant-b", "grant_reason": "QA"}
    )
    install = InstallSkillForm.from_mapping(
        {
            "tenant_id": "tenant-a",
            "slug": "calendar-assistant",
            "semantic_version": "1.2.3",
        }
    )
    credential = CredentialReferenceConfigForm.from_mapping(
        {
            "revision_token": "install-1",
            "requirement_key": "calendar-oauth",
            "credential_kind": "delegated_credential",
            "reference_id": "delegated-calendar-acme",
            "delegated_scope": "calendar.readonly",
        }
    )
    smoke = SmokeTestActionForm.from_mapping(
        {"revision_token": "install-1", "fixture_keys": "list-calendars"}
    )
    eligibility = BindingEligibilityPreviewForm.from_mapping(
        {
            "revision_token": "install-1",
            "context_type": "profile",
            "context_id": "qa-profile",
        }
    )

    assert package.slug == "calendar-assistant"
    assert package.errors == ()
    assert manifest.input_source == "paste"
    assert manifest.manifest_payload["slug"] == "calendar-assistant"
    assert manifest.candidate_revision == "candidate-1"
    assert grant.selected_tenant_ids == {"tenant-a", "tenant-b"}
    assert install.previous_installation_id is None
    assert credential.selected_reference_id == "delegated-calendar-acme"
    assert credential.delegated_metadata_fields == {"scope": "calendar.readonly"}
    assert smoke.fixture_keys == {"list-calendars"}
    assert eligibility.selected_context_id == "qa-profile"


def test_browser_form_models_report_safe_errors_and_conflicts() -> None:
    package = SkillPackageCreateForm.from_mapping({}, default_owner="platform-admin")
    manifest = ManifestCandidateForm.from_mapping({"manifest": "not: [valid"})
    grant = TenantGrantForm.from_mapping({})
    context = RedactionSafePageContext(tenant_scope_label="tenant-a")
    conflict = build_revision_conflict_view(
        resource_type="credential_configuration",
        resource_id="installation-1",
        submitted_revision="old",
        current_revision="new",
        reload_url="/admin/skill-registry/ui/installations/installation-1/credentials",
    )

    assert {error.field for error in package.errors} == {"slug", "display_name"}
    assert manifest.errors[0].field == "manifest"
    assert grant.errors[0].field == "tenant_ids"
    assert "raw_credential_value" in context.redacted_fields
    assert conflict.current_revision == "new"
    assert "No stale browser action" in conflict.safe_message
