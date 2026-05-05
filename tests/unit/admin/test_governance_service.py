from __future__ import annotations

from multi_agent_platform.admin.governance import (
    build_credential_reference_result,
    build_governance_dashboard,
    build_profile_resolution,
    build_profile_save_result,
    build_prompt_preview,
    build_prompt_save_result,
    build_provider_list,
    build_provider_probe_result,
    build_routing_preview_mutation,
)
from multi_agent_platform.api.schemas.admin_governance import (
    ProfileSaveRequest,
    PromptPreviewRequest,
    PromptSaveRequest,
    ProviderCredentialReferenceRequest,
    RoutingPreviewRequest,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("tenant:read", "admin:model-providers:write"),
        trace_id="trace-governance-platform-test",
    )


def _tenant_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-governance-tenant-test",
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type="tenant",
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )


def test_governance_dashboard_contains_safe_domain_summaries() -> None:
    dashboard = build_governance_dashboard(
        scope=_platform_scope(),
        principal=_platform_principal(),
    )

    assert dashboard.page_id == "react-governance"
    assert {section.section_id for section in dashboard.sections} >= {
        "providers",
        "prompts",
        "profiles",
        "routing",
        "provenance",
    }
    assert dashboard.providers[0].authorized_actions
    assert dashboard.prompt_preview.status == "ready"
    assert dashboard.routing_preview.direct_call_guardrail
    assert "qa031-secret-value" not in dashboard.model_dump_json()


def test_provider_list_limits_tenant_actions_and_catalog() -> None:
    platform = build_provider_list(
        scope=_platform_scope(),
        principal=_platform_principal(),
    )
    tenant = build_provider_list(scope=_tenant_scope(), principal=_tenant_principal())

    assert len(platform.providers) == 2
    assert platform.providers[0].authorized_actions
    assert len(tenant.providers) == 1
    assert tenant.providers[0].authorized_actions == ()


def test_provider_probe_and_prompt_preview_are_safe() -> None:
    probe = build_provider_probe_result("openai-primary")
    credential = build_credential_reference_result(
        provider_id="openai-primary",
        request=ProviderCredentialReferenceRequest(
            credential_reference_id="secret-ref-openai-primary",
            revision="provider-rev-qa031-current",
        ),
    )
    safe_preview = build_prompt_preview(
        prompt_lineage_id="daily-briefing",
        request=PromptPreviewRequest(fixture_id="qa031-safe-preview"),
    )
    unsafe_preview = build_prompt_preview(
        prompt_lineage_id="daily-briefing",
        request=PromptPreviewRequest(fixture_id="qa031-unsafe-preview"),
    )

    assert probe.status == "accepted"
    assert probe.probe is not None
    assert probe.probe.credential_resolution_status == "safe reference selected"
    assert credential.status == "accepted"
    assert credential.audit_reference_id == (
        "audit-governance-credential-qa031-openai-primary"
    )
    assert "resolved credential" not in credential.model_dump_json().lower()
    assert safe_preview.status == "ready"
    assert unsafe_preview.status == "summarized"
    assert "raw prompt" not in unsafe_preview.model_dump_json().lower()


def test_prompt_profile_and_routing_mutations_return_safe_evidence() -> None:
    prompt = build_prompt_save_result(
        prompt_lineage_id="daily-briefing",
        request=PromptSaveRequest(
            idempotency_key="prompt-save",
            revision="prompt-rev-qa031-current",
            safe_summary="Review fixture-safe prompt summary.",
        ),
    )
    profile = build_profile_save_result(
        profile_id="briefing-runtime",
        request=ProfileSaveRequest(
            idempotency_key="profile-save",
            model_binding="gpt-qa031-safe-route",
            provider_binding="openai-primary",
            revision="profile-rev-qa031-current",
        ),
    )
    routing = build_routing_preview_mutation(
        scope=_tenant_scope(),
        request=RoutingPreviewRequest(
            workflow_context="Daily briefing workflow",
            profile_id="briefing-runtime",
            skill_id="weather-readonly",
        ),
    )

    assert prompt.status == "accepted"
    assert prompt.revision == "daily-briefing-rev-qa031-next"
    assert profile.profile_resolution is not None
    assert build_profile_resolution("briefing-runtime").status == "ready"
    assert routing.routing_preview is not None
    assert "No live providers were invoked." in routing.diagnostics
