from __future__ import annotations

import pytest
from tests.fixtures.skill_registry import valid_skill_manifest

from multi_agent_platform.admin.skill_registry.readiness import (
    CredentialReferenceSummary,
)
from multi_agent_platform.admin.skill_registry.service import (
    SkillRegistryService,
    SkillRegistryServiceError,
)


def test_tenant_installation_lifecycle_and_upgrade_lineage() -> None:
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

    assert installation.installation_version == 1
    assert installation.readiness is not None
    assert installation.readiness.readiness_state == "blocked"

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

    assert configured.readiness is not None
    assert configured.readiness.readiness_state == "ready"


def test_cross_tenant_install_is_denied_and_audited() -> None:
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

    with pytest.raises(SkillRegistryServiceError):
        service.install_version(
            tenant_id="tenant-2",
            slug="calendar-assistant",
            semantic_version="1.2.3",
            actor_principal_id="tenant-admin",
        )

    assert service.audit_events[-1].event_type == "skill_installation.denied"
