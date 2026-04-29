from __future__ import annotations

import pytest
from fastapi import HTTPException

from multi_agent_platform.admin.skill_registry.service import SkillRegistryService
from multi_agent_platform.api.routers.admin_skill_registry import (
    configure_installation_credentials,
    create_skill_installation,
    create_skill_package,
    grant_skill_version_availability,
    list_available_skill_versions,
    preview_installation_eligibility,
    publish_skill_version,
    validate_skill_version,
)
from multi_agent_platform.api.schemas.skill_registry import (
    ConfigureCredentialsRequest,
    CredentialReferenceRequest,
    SkillInstallationCreateRequest,
    SkillPackageCreateRequest,
    SkillVersionPublishRequest,
    SkillVersionValidateRequest,
    TenantAvailabilityGrantRequest,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from tests.fixtures.skill_registry import valid_skill_manifest


def _principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        role_codes=("platform_admin", "tenant_admin"),
        permission_codes=("skill-registry:publish", "skill-registry:install"),
    )


@pytest.mark.asyncio
async def test_skill_registry_json_router_lifecycle() -> None:
    service = SkillRegistryService()
    principal = _principal()
    package = await create_skill_package(
        SkillPackageCreateRequest(
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Safe skill.",
            owner_principal_id="platform-admin",
        ),
        principal,
        service,
    )
    validation = await validate_skill_version(
        "calendar-assistant",
        SkillVersionValidateRequest(
            manifest=valid_skill_manifest(),
            approved_integration_refs={"tool:calendar:v1"},
        ),
        service,
        principal,
    )
    version = await publish_skill_version(
        "calendar-assistant",
        SkillVersionPublishRequest(
            manifest=valid_skill_manifest(),
            approved_integration_refs={"tool:calendar:v1"},
            artifact_digest="sha256:artifact",
        ),
        principal,
        service,
    )
    await grant_skill_version_availability(
        "calendar-assistant",
        "1.2.3",
        TenantAvailabilityGrantRequest(tenant_id="tenant-1"),
        principal,
        service,
    )
    available = await list_available_skill_versions("tenant-1", service, principal)
    installation = await create_skill_installation(
        SkillInstallationCreateRequest(
            tenant_id="tenant-1",
            slug="calendar-assistant",
            semantic_version="1.2.3",
        ),
        principal,
        service,
    )
    configured = await configure_installation_credentials(
        installation.installation_id,
        ConfigureCredentialsRequest(
            revision_token=installation.revision_token,
            credentials=[
                CredentialReferenceRequest(
                    requirement_key="calendar-oauth",
                    credential_kind="delegated_credential",
                    reference_id="delegated-1",
                    status="ready",
                )
            ],
        ),
        principal,
        service,
    )
    eligibility = await preview_installation_eligibility(
        installation.installation_id,
        service,
        principal,
    )

    assert package.slug == "calendar-assistant"
    assert validation.status == "passed"
    assert version.semantic_version == "1.2.3"
    assert available[0].slug == "calendar-assistant"
    assert configured.readiness_state == "ready"
    assert eligibility.allowed is True


@pytest.mark.asyncio
async def test_skill_registry_json_router_maps_errors() -> None:
    service = SkillRegistryService()
    principal = _principal()

    with pytest.raises(HTTPException) as exc_info:
        await publish_skill_version(
            "missing",
            SkillVersionPublishRequest(
                manifest=valid_skill_manifest(),
                approved_integration_refs={"tool:calendar:v1"},
                artifact_digest="sha256:artifact",
            ),
            principal,
            service,
        )

    assert exc_info.value.status_code == 404
