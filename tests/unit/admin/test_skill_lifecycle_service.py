from __future__ import annotations

import json

from multi_agent_platform.admin.skill_lifecycle import (
    build_binding_preview_result,
    build_candidate_result,
    build_candidate_validation_result,
    build_connector_diagnostic_result,
    build_credential_configuration_result,
    build_package_lifecycle_result,
    build_publish_result,
    build_readiness_refresh_result,
    build_skill_lifecycle_dashboard,
    build_tenant_grant_result,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_skill_lifecycle import (
    BindingEligibilityPreviewRequest,
    CredentialConfigurationRequest,
    ReadinessRefreshRequest,
    SkillPackageCandidateRequest,
    SkillPackagePublishRequest,
    TenantGrantMutationRequest,
)
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext
from multi_agent_platform.db.repositories.skill_registry import SkillRegistryRepository
from tests.fixtures.skill_registry import seed_live_skill_lifecycle_repository


def _tenant_scope(tenant_id: str) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=tenant_id,
        label="Acme",
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )


def _principal(*, platform: bool = False) -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform" if platform else "tenant",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",) if platform else ("tenant_user", "tenant_admin"),
        permission_codes=("skill-registry:publish",)
        if platform
        else ("tenant:admin", "skill-registry:install"),
        trace_id="trace-skill-lifecycle",
    )


async def test_skill_lifecycle_dashboard_scopes_empty_and_seeded(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    tenant_scope = _tenant_scope(str(seeded_tenant.tenant_id))

    empty = await build_skill_lifecycle_dashboard(
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    assert empty.empty_state is not None
    assert empty.installations == ()
    assert empty.tenant_discovery is not None
    assert empty.tenant_discovery.available_versions == ()

    await seed_live_skill_lifecycle_repository(
        repository,
        tenant_id=seeded_tenant.tenant_id,
    )
    platform = await build_skill_lifecycle_dashboard(
        scope=_platform_scope(),
        principal=_principal(platform=True),
        repository=repository,
    )
    tenant = await build_skill_lifecycle_dashboard(
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )

    assert platform.platform_publication is not None
    assert platform.platform_publication.package_versions[0].package_slug == (
        "calendar-assistant"
    )
    assert tenant.empty_state is None
    assert tenant.provenance is not None
    assert tenant.tenant_discovery is not None
    assert tenant.tenant_discovery.grants[0].tenant_label == "Acme"
    assert tenant.connector_diagnostics[0].connector_label == "Calendar"
    serialized = json.dumps(tenant.model_dump(mode="json")).lower()
    assert "qa032-secret-value" not in serialized
    assert "raw manifest" not in serialized
    assert "resolved credential" not in serialized


async def test_candidate_upload_precedence_and_publish_gates_are_safe(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    candidate = await build_candidate_result(
        request=SkillPackageCandidateRequest(
            idempotency_key="candidate",
            manifest_text="unsafe sample qa032-secret-value",
            uploaded_fixture_id="uploaded-manifest",
        ),
        principal=_principal(platform=True),
        repository=repository,
    )
    blocked = await build_candidate_validation_result(
        ready=False,
        principal=_principal(platform=True),
        repository=repository,
    )
    unavailable = await build_publish_result(
        request=SkillPackagePublishRequest(
            candidate_revision="candidate-unavailable",
            confirmed=True,
            idempotency_key="publish-unavailable",
        ),
        scope=_platform_scope(),
        principal=_principal(platform=True),
        repository=repository,
    )
    await seed_live_skill_lifecycle_repository(
        repository,
        tenant_id=seeded_tenant.tenant_id,
    )
    published = await build_publish_result(
        request=SkillPackagePublishRequest(
            candidate_revision="candidate-unavailable",
            confirmed=True,
            idempotency_key="publish",
        ),
        scope=_platform_scope(),
        principal=_principal(platform=True),
        repository=repository,
    )

    assert candidate.status == "accepted"
    assert "uploaded fixture metadata" in candidate.diagnostics[0].lower()
    assert "qa032-secret-value" not in candidate.model_dump_json()
    assert blocked.status == "validation_error"
    assert unavailable.status == "dependency_unavailable"
    assert published.publication is not None
    assert published.publication.lifecycle_status == "published"


async def test_install_credentials_grants_and_binding_preview_are_safe(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    ids = await seed_live_skill_lifecycle_repository(
        repository,
        tenant_id=seeded_tenant.tenant_id,
    )
    tenant_scope = _tenant_scope(str(seeded_tenant.tenant_id))
    dashboard = await build_skill_lifecycle_dashboard(
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    installation = dashboard.installations[0]
    reference_id = installation.credential_options[0].reference_id
    version_id = str(ids["version_id"])
    installation_id = str(ids["installation_id"])

    grant = await build_tenant_grant_result(
        request=TenantGrantMutationRequest(
            tenant_id=str(seeded_tenant.tenant_id),
            version_id=version_id,
            grant_enabled=True,
            revision=version_id,
            idempotency_key="grant",
        ),
        scope=_platform_scope(),
        principal=_principal(platform=True),
        repository=repository,
    )
    credential = await build_credential_configuration_result(
        installation_id=installation_id,
        request=CredentialConfigurationRequest(
            selected_reference_id=reference_id,
            revision=str(ids["revision"]),
            idempotency_key="credential",
        ),
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    denied_credential = await build_credential_configuration_result(
        installation_id=installation_id,
        request=CredentialConfigurationRequest(
            selected_reference_id="other-tenant-reference",
            revision=credential.revision or str(ids["revision"]),
            idempotency_key="credential-denied",
        ),
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    stale_credential = await build_credential_configuration_result(
        installation_id=installation_id,
        request=CredentialConfigurationRequest(
            selected_reference_id=reference_id,
            revision="stale-revision",
            idempotency_key="credential-stale",
        ),
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    readiness = await build_readiness_refresh_result(
        installation_id=installation_id,
        request=ReadinessRefreshRequest(
            revision=credential.revision or str(ids["revision"]),
            idempotency_key="readiness",
        ),
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    binding = await build_binding_preview_result(
        scope=tenant_scope,
        request=BindingEligibilityPreviewRequest(
            workflow_context="Calendar workflow",
            profile_id="profile-calendar-runtime",
            package_id=installation_id,
        ),
        principal=_principal(),
        repository=repository,
    )
    diagnostic = await build_connector_diagnostic_result(
        scope=tenant_scope,
        principal=_principal(),
        repository=repository,
    )
    quarantine = await build_package_lifecycle_result(
        package_id=version_id,
        action="quarantine",
        scope=_platform_scope(),
        principal=_principal(platform=True),
        repository=repository,
    )

    assert grant.status == "accepted"
    assert credential.credential is not None
    assert credential.credential.fingerprint is not None
    assert "resolved credential" not in credential.model_dump_json().lower()
    assert denied_credential.status == "validation_error"
    assert stale_credential.status == "stale_conflict"
    assert readiness.smoke_test is not None
    assert readiness.smoke_test.readiness == "queued"
    assert binding.binding_preview is not None
    assert "calendar.write" in binding.binding_preview.blocked_tools
    assert "No tools" in binding.diagnostics[0]
    assert diagnostic.diagnostic is not None
    assert diagnostic.diagnostic.gateway_decision == "queued"
    assert quarantine.publication is not None
    assert quarantine.publication.lifecycle_status == "quarantined"
