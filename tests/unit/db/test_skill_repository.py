from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.db.models.skill_registry import (
    SkillAuditRecord,
    SkillInstallation,
    SkillInstallationState,
    SkillPackage,
    SkillPackageTenantGrant,
    SkillPackageVersion,
    SkillVersionLifecycleState,
)
from multi_agent_platform.db.repositories.skill_registry import (
    SkillRegistryRepository,
    StaleSkillRegistryWriteError,
)


async def test_skill_repository_persists_package_version_grant_and_installation(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    package = await repository.add_package(
        SkillPackage(
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Safe skill.",
            owner_principal_id="platform-admin",
            created_by_principal_id="platform-admin",
        )
    )
    version = await repository.add_package_version(
        SkillPackageVersion(
            skill_package_id=package.skill_package_id,
            slug=package.slug,
            semantic_version="1.2.3",
            manifest_digest="sha256:manifest",
            manifest_snapshot={"slug": package.slug},
            safe_manifest_summary={"tools": ["calendar.list"]},
            artifact_digest="sha256:artifact",
            validation_status="passed",
            lifecycle_state=SkillVersionLifecycleState.PUBLISHED,
            availability_mode="selected_tenants",
        )
    )
    await repository.add_tenant_grant(
        SkillPackageTenantGrant(
            skill_package_version_id=version.skill_package_version_id,
            tenant_id=seeded_tenant.tenant_id,
            granted_by_principal_id="platform-admin",
        )
    )
    visible = await repository.list_available_versions(
        tenant_id=seeded_tenant.tenant_id
    )

    installation = await repository.add_installation(
        SkillInstallation(
            tenant_id=seeded_tenant.tenant_id,
            skill_package_version_id=version.skill_package_version_id,
            slug=package.slug,
            semantic_version="1.2.3",
            installation_version=1,
            manifest_digest="sha256:manifest",
            manifest_summary={"action_categories": ["read"]},
            artifact_digest="sha256:artifact",
            readiness_state=SkillInstallationState.READY,
            credential_status="ready",
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="passed",
            binding_eligibility_status="eligible",
            installed_by_principal_id="tenant-admin",
            revision_token="rev-1",
        )
    )

    assert await repository.get_package_by_slug(package.slug) == package
    assert visible == [version]
    assert (
        await repository.get_package_version(
            slug=package.slug,
            semantic_version="1.2.3",
        )
        == version
    )
    assert (
        await repository.get_installation(installation.skill_installation_id)
        == installation
    )
    assert await repository.list_installations_for_tenant(
        tenant_id=seeded_tenant.tenant_id
    ) == [installation]
    assert (
        await repository.require_revision(
            installation_id=installation.skill_installation_id,
            expected_revision_token="rev-1",
        )
        == installation
    )


async def test_skill_repository_rejects_stale_revision_and_lists_audit(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    package = await repository.add_package(
        SkillPackage(
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Safe skill.",
            owner_principal_id="platform-admin",
            created_by_principal_id="platform-admin",
        )
    )
    version = await repository.add_package_version(
        SkillPackageVersion(
            skill_package_id=package.skill_package_id,
            slug=package.slug,
            semantic_version="1.2.3",
            manifest_digest="sha256:manifest",
            manifest_snapshot={"slug": package.slug},
            safe_manifest_summary={},
            artifact_digest="sha256:artifact",
            validation_status="passed",
            lifecycle_state=SkillVersionLifecycleState.PUBLISHED,
            availability_mode="selected_tenants",
        )
    )
    installation = await repository.add_installation(
        SkillInstallation(
            tenant_id=seeded_tenant.tenant_id,
            skill_package_version_id=version.skill_package_version_id,
            slug=package.slug,
            semantic_version="1.2.3",
            installation_version=1,
            manifest_digest="sha256:manifest",
            manifest_summary={},
            artifact_digest="sha256:artifact",
            readiness_state=SkillInstallationState.BLOCKED,
            credential_status="blocked",
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="pending",
            binding_eligibility_status="denied",
            installed_by_principal_id="tenant-admin",
            revision_token="rev-1",
        )
    )
    audit = await repository.add_audit_record(
        SkillAuditRecord(
            event_type="skill_installation.created",
            actor_principal_id="tenant-admin",
            outcome="installed",
            tenant_id=seeded_tenant.tenant_id,
            package_slug=package.slug,
            package_version="1.2.3",
            skill_installation_id=installation.skill_installation_id,
            safe_summary={"installation_version": 1},
        )
    )

    with pytest.raises(StaleSkillRegistryWriteError):
        await repository.require_revision(
            installation_id=installation.skill_installation_id,
            expected_revision_token="stale",
        )

    assert await repository.list_audit_records(
        tenant_id=seeded_tenant.tenant_id,
        package_slug=package.slug,
    ) == [audit]

    with pytest.raises(LookupError):
        await repository.require_revision(
            installation_id=uuid4(),
            expected_revision_token="missing",
        )
