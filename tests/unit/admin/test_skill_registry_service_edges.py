from __future__ import annotations

import pytest

from multi_agent_platform.admin.skill_registry.readiness import (
    CredentialReferenceSummary,
)
from multi_agent_platform.admin.skill_registry.service import (
    SkillRegistryService,
    SkillRegistryServiceError,
)
from tests.fixtures.skill_registry import valid_skill_manifest


def _published_service() -> SkillRegistryService:
    service = SkillRegistryService()
    service.create_package(
        slug="calendar-assistant",
        display_name="Calendar Assistant",
        description="Safe calendar skill.",
        owner_principal_id="platform-admin",
        actor_principal_id="platform-admin",
    )
    service.publish_version(
        slug="calendar-assistant",
        manifest_payload=valid_skill_manifest(),
        artifact_digest="sha256:artifact",
        actor_principal_id="platform-admin",
        approved_integration_refs={"tool:calendar:v1"},
    )
    return service


def test_skill_registry_service_duplicate_and_validation_errors() -> None:
    service = _published_service()

    with pytest.raises(SkillRegistryServiceError) as duplicate_package:
        service.create_package(
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Safe calendar skill.",
            owner_principal_id="platform-admin",
            actor_principal_id="platform-admin",
        )
    with pytest.raises(SkillRegistryServiceError) as duplicate_version:
        service.publish_version(
            slug="calendar-assistant",
            manifest_payload=valid_skill_manifest(),
            artifact_digest="sha256:artifact",
            actor_principal_id="platform-admin",
            approved_integration_refs={"tool:calendar:v1"},
        )
    with pytest.raises(SkillRegistryServiceError) as blocked:
        service.publish_version(
            slug="calendar-assistant",
            manifest_payload={**valid_skill_manifest(), "semantic_version": "2"},
            artifact_digest="sha256:artifact",
            actor_principal_id="platform-admin",
            approved_integration_refs={"tool:calendar:v1"},
        )

    assert duplicate_package.value.category == "duplicate_package"
    assert duplicate_version.value.category == "duplicate_version"
    assert blocked.value.category == "validation_blocked"


def test_skill_registry_service_visibility_quarantine_and_stale_edges() -> None:
    service = _published_service()

    assert service.list_available_versions(tenant_id="tenant-1") == []
    service.grant_tenant_availability(
        slug="calendar-assistant",
        semantic_version="1.2.3",
        tenant_id="tenant-1",
        actor_principal_id="platform-admin",
    )
    installation = service.install_version(
        tenant_id="tenant-1",
        slug="calendar-assistant",
        semantic_version="1.2.3",
        actor_principal_id="tenant-admin",
    )
    with pytest.raises(SkillRegistryServiceError) as stale:
        service.configure_credentials(
            installation_id=installation.installation_id,
            revision_token="stale",
            credentials=[],
        )
    configured = service.configure_credentials(
        installation_id=installation.installation_id,
        revision_token=installation.revision_token,
        credentials=[
            CredentialReferenceSummary(
                requirement_key="calendar-oauth",
                credential_kind="delegated_credential",
                reference_id="delegated-1",
                status="ready",
            )
        ],
    )
    denied = service.binding_eligibility(
        installation_id=installation.installation_id,
        required_action_categories={"write"},
    )
    service.quarantine_installation(installation_id=installation.installation_id)
    blocked = service.binding_eligibility(installation_id=installation.installation_id)

    assert stale.value.category == "stale_revision"
    assert configured.readiness is not None
    assert denied.allowed is False
    assert "policy.action_category_mismatch" in denied.reason_codes
    assert blocked.allowed is False
    assert "quarantine.runtime_blocked" in blocked.reason_codes
