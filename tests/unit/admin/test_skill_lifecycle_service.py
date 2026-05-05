from __future__ import annotations

import json

from multi_agent_platform.admin.skill_lifecycle import (
    build_binding_preview_result,
    build_candidate_result,
    build_candidate_validation_result,
    build_credential_configuration_result,
    build_install_result,
    build_publish_result,
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
    SkillPackageCandidateRequest,
    SkillPackagePublishRequest,
    TenantGrantMutationRequest,
    TenantSkillInstallRequest,
)
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id="11111111-1111-1111-1111-111111111111",
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


def test_skill_lifecycle_dashboard_scopes_platform_and_tenant() -> None:
    platform = build_skill_lifecycle_dashboard(
        scope=_platform_scope(),
        principal=_principal(platform=True),
    )
    tenant = build_skill_lifecycle_dashboard(
        scope=_tenant_scope(),
        principal=_principal(),
    )

    assert platform.platform_publication is not None
    assert platform.platform_publication.candidate.manifest_source == "upload"
    assert tenant.platform_publication is None
    assert tenant.tenant_discovery is not None
    assert tenant.tenant_discovery.grants[0].tenant_label == "Acme"
    assert tenant.connector_diagnostics[0].connector_label == "Calendar"
    serialized = json.dumps(tenant.model_dump(mode="json")).lower()
    assert "qa032-secret-value" not in serialized
    assert "raw manifest" not in serialized
    assert "resolved credential" not in serialized


def test_candidate_upload_precedence_and_publish_gates_are_safe() -> None:
    candidate = build_candidate_result(
        request=SkillPackageCandidateRequest(
            idempotency_key="candidate",
            manifest_text="unsafe sample qa032-secret-value",
            uploaded_fixture_id="qa032-uploaded-manifest",
        )
    )
    blocked = build_candidate_validation_result(ready=False)
    stale = build_publish_result(
        request=SkillPackagePublishRequest(
            candidate_revision="stale-revision",
            confirmed=True,
            idempotency_key="publish-stale",
        ),
        scope=_platform_scope(),
    )
    published = build_publish_result(
        request=SkillPackagePublishRequest(
            candidate_revision="candidate-rev-qa032-current",
            confirmed=True,
            idempotency_key="publish",
        ),
        scope=_platform_scope(),
    )

    assert candidate.status == "accepted"
    assert "uploaded manifest fixture" in candidate.diagnostics[0].lower()
    assert "qa032-secret-value" not in candidate.model_dump_json()
    assert blocked.status == "validation_error"
    assert stale.status == "stale_conflict"
    assert published.publication is not None
    assert published.publication.lifecycle_status == "published"


def test_install_credentials_grants_and_binding_preview_are_safe() -> None:
    grant = build_tenant_grant_result(
        request=TenantGrantMutationRequest(
            tenant_id="11111111-1111-1111-1111-111111111111",
            version_id="package-version-daily-briefing-1-4-0",
            grant_enabled=True,
            revision="grant-rev-qa032-current",
            idempotency_key="grant",
        ),
        scope=_platform_scope(),
    )
    install = build_install_result(
        request=TenantSkillInstallRequest(
            package_id="package-daily-briefing-connectors",
            version_id="package-version-daily-briefing-1-4-0",
            revision="installation-rev-qa032-current",
            idempotency_key="install",
        ),
        scope=_tenant_scope(),
    )
    credential = build_credential_configuration_result(
        request=CredentialConfigurationRequest(
            selected_reference_id="cred-ref-acme-briefing",
            revision="installation-rev-qa032-current",
            idempotency_key="credential",
        )
    )
    denied_credential = build_credential_configuration_result(
        request=CredentialConfigurationRequest(
            selected_reference_id="other-tenant-reference",
            revision="installation-rev-qa032-current",
            idempotency_key="credential-denied",
        )
    )
    binding = build_binding_preview_result(
        scope=_tenant_scope(),
        request=BindingEligibilityPreviewRequest(
            workflow_context="Daily briefing workflow",
            profile_id="profile-briefing-runtime",
            package_id="package-daily-briefing-connectors",
        ),
    )

    assert grant.status == "accepted"
    assert install.installation is not None
    assert install.installation.credential_readiness == "ready"
    assert credential.credential is not None
    assert credential.credential.fingerprint == "fp_qa032_acme_briefing"
    assert denied_credential.status == "validation_error"
    assert binding.binding_preview is not None
    assert "email.send" in binding.binding_preview.blocked_tools
    assert "No live tools" in binding.diagnostics[0]
