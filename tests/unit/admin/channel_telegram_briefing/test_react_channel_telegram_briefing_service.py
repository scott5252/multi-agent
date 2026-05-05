from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.channel_telegram_briefing import (
    ACME_TENANT_ID,
    GLOBEX_TENANT_ID,
    SAFE_RUN_ID,
    build_alias_save_result,
    build_channel_telegram_briefing_dashboard,
    build_link_token_result,
    build_preference_export_result,
    build_preference_save_result,
    build_run_status_summary,
    build_webhook_validation_result,
)
from multi_agent_platform.api.schemas.admin_channel_telegram_briefing_react import (
    BriefingOutputStyle,
    BriefingPreferenceExportRequest,
    BriefingPreferenceSaveRequest,
    ChannelMutationStatus,
    CommuteMode,
    LinkTokenCreateRequest,
    TelegramAliasSaveRequest,
    WebhookValidationRequest,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def test_platform_dashboard_contains_authorized_tenant_summaries() -> None:
    dashboard = build_channel_telegram_briefing_dashboard(
        scope=_platform_scope(),
        principal=_platform_principal(),
        allowed_scope_options=_scope_options(),
    )

    labels = {item.tenant_label for item in dashboard.readiness}
    assert labels == {"Acme", "Globex"}
    assert dashboard.aliases
    assert "pair-code" not in dashboard.model_dump_json()
    assert "qa036-secret-value" not in dashboard.model_dump_json()


def test_tenant_dashboard_filters_other_tenants_and_hides_token_follow_up() -> None:
    dashboard = build_channel_telegram_briefing_dashboard(
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_admin_principal(),
        allowed_scope_options=_scope_options(),
    )

    assert {item.tenant_label for item in dashboard.readiness} == {"Acme"}
    assert "Globex" not in dashboard.model_dump_json()
    assert dashboard.link_token_result is not None
    assert dashboard.link_token_result.token_value is None


def test_link_token_creation_returns_immediate_visible_value() -> None:
    result = build_link_token_result(
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_admin_principal(),
        request=LinkTokenCreateRequest(
            principal_label="Acme briefing user",
            expires_in_minutes=10,
            idempotency_key="link-token-qa036",
        ),
    )

    assert result.display_mode == "immediate"
    assert result.token_value == "pair-code-10-qa036"


def test_alias_and_webhook_mutations_include_idempotency_and_audit() -> None:
    scope = _tenant_scope(ACME_TENANT_ID, "Acme")
    principal = _tenant_admin_principal()
    alias = build_alias_save_result(
        scope=scope,
        principal=principal,
        request=TelegramAliasSaveRequest(
            alias_text="Morning briefing",
            target_summary="Daily briefing workflow",
            idempotency_key="alias-qa036",
        ),
    )
    webhook = build_webhook_validation_result(
        scope=scope,
        principal=principal,
        request=WebhookValidationRequest(
            revision="telegram-config-rev-qa036",
            idempotency_key="webhook-qa036-replay",
        ),
    )

    assert alias.status is ChannelMutationStatus.ACCEPTED
    assert alias.audit_reference
    assert webhook.status is ChannelMutationStatus.REPLAYED
    assert webhook.replayed is True


def test_tenant_user_gets_preference_profile_and_safe_run_status() -> None:
    dashboard = build_channel_telegram_briefing_dashboard(
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_user_principal(),
        allowed_scope_options=_scope_options(),
    )
    run_status = build_run_status_summary(
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_user_principal(),
        workflow_run_id=SAFE_RUN_ID,
    )

    assert dashboard.preference_profiles.current_user_profile is not None
    assert dashboard.aliases == ()
    assert run_status.status == "running"
    assert "run result" not in run_status.model_dump_json().lower()


def test_preference_save_and_export_are_redaction_safe() -> None:
    scope = _tenant_scope(ACME_TENANT_ID, "Acme")
    principal = _tenant_user_principal()
    save = build_preference_save_result(
        scope=scope,
        principal=principal,
        request=BriefingPreferenceSaveRequest(
            timezone="America/New_York",
            location_summary="Metro area summary",
            news_topics_summary="4 topic categories",
            vip_sender_summary="3 masked sender hints",
            workday_hours="08:30-17:30",
            commute_mode=CommuteMode.TRANSIT,
            default_account_summary="2 masked account refs",
            output_style=BriefingOutputStyle.EXECUTIVE,
            scheduled_time_summary="Profile preference 07:45",
        ),
    )
    export = build_preference_export_result(
        scope=scope,
        principal=principal,
        request=BriefingPreferenceExportRequest(format="json"),
    )

    assert save.status is ChannelMutationStatus.ACCEPTED
    assert export.artifact_reference == "preference-export-artifact-qa036"
    assert "raw preference" not in export.model_dump_json().lower()


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(scope_type=ReactAdminScopeType.PLATFORM, label="Platform")


def _tenant_scope(tenant_id: UUID, label: str) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=tenant_id,
        label=label,
    )


def _scope_options() -> tuple[ReactAdminScopeOption, ...]:
    return (
        ReactAdminScopeOption(
            scope=_platform_scope(),
            label="Platform",
            href="/admin/app/channels",
            selected=False,
        ),
        ReactAdminScopeOption(
            scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
            label="Acme",
            href=f"/admin/app/channels?tenant_id={ACME_TENANT_ID}",
            selected=True,
        ),
        ReactAdminScopeOption(
            scope=_tenant_scope(GLOBEX_TENANT_ID, "Globex"),
            label="Globex",
            href=f"/admin/app/channels?tenant_id={GLOBEX_TENANT_ID}",
            selected=False,
        ),
    )


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-platform",
    )


def _tenant_admin_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=ACME_TENANT_ID,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-tenant-admin",
    )


def _tenant_user_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-user-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=ACME_TENANT_ID,
        role_codes=("tenant_user",),
        permission_codes=("tenant:read",),
        trace_id="trace-tenant-user",
    )
