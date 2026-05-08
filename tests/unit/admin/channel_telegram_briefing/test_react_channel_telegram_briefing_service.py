from __future__ import annotations

from uuid import UUID

from tests.fixtures.channel_telegram_briefing import (
    ACME_TENANT_ID,
    GLOBEX_TENANT_ID,
    seed_channel_telegram_briefing_live_data,
)

from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
)
from multi_agent_platform.admin.channel_telegram_briefing import (
    build_alias_save_result,
    build_briefing_preferences,
    build_channel_telegram_briefing_dashboard,
    build_delivery_diagnostics,
    build_link_token_result,
    build_preference_export_result,
    build_preference_save_result,
    build_run_status_summary,
    build_webhook_validation_result,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
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
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)


async def test_empty_tenant_dashboard_returns_truthful_empty_state(
    session,
    settings,
) -> None:
    services = _services(session, settings)
    dashboard = await build_channel_telegram_briefing_dashboard(
        **services,
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_admin_principal(),
        allowed_scope_options=_scope_options(),
    )

    serialized = dashboard.model_dump_json()
    assert dashboard.aliases == ()
    assert dashboard.delivery_attempts == ()
    assert dashboard.states[-1].reason == "empty"
    assert "qa036" not in serialized.lower()
    assert "Globex" not in serialized


async def test_seeded_tenant_dashboard_uses_live_rows(session, settings) -> None:
    seed = await seed_channel_telegram_briefing_live_data(session)
    services = _services(session, settings)
    dashboard = await build_channel_telegram_briefing_dashboard(
        **services,
        scope=_tenant_scope(seed.tenant_id, "Acme"),
        principal=_tenant_admin_principal(),
        allowed_scope_options=_scope_options(),
    )

    serialized = dashboard.model_dump_json()
    assert {item.alias_text for item in dashboard.aliases} == {"Morning briefing"}
    assert dashboard.link_token_result is not None
    assert dashboard.link_token_result.token_value is None
    assert dashboard.delivery_attempts[0].status == "delivered"
    assert dashboard.run_status_links[0].run_id == str(seed.run_id)
    assert "Globex" not in serialized
    assert "qa036" not in serialized.lower()


async def test_platform_dashboard_uses_allowed_scope_tenants(
    session,
    settings,
) -> None:
    await seed_channel_telegram_briefing_live_data(session)
    services = _services(session, settings)
    dashboard = await build_channel_telegram_briefing_dashboard(
        **services,
        scope=_platform_scope(),
        principal=_platform_principal(),
        allowed_scope_options=_scope_options(),
    )

    assert {item.tenant_label for item in dashboard.readiness} == {"Acme", "Globex"}
    assert any(config.tenant_label == "Globex" for config in dashboard.tenant_configs)
    assert "qa036" not in dashboard.model_dump_json().lower()


async def test_link_token_creation_returns_immediate_value(
    session,
    settings,
) -> None:
    services = _services(session, settings)
    result = await build_link_token_result(
        telegram_service=services["telegram_service"],
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_admin_principal(),
        request=LinkTokenCreateRequest(
            principal_label="Acme briefing user",
            expires_in_minutes=10,
            idempotency_key="link-token-live",
        ),
    )

    assert result.display_mode == "immediate"
    assert result.token_value is not None
    assert len(result.token_value) == 32


async def test_alias_and_webhook_mutations_use_services(session, settings) -> None:
    services = _services(session, settings)
    scope = _tenant_scope(ACME_TENANT_ID, "Acme")
    principal = _tenant_admin_principal()
    alias = await build_alias_save_result(
        telegram_service=services["telegram_service"],
        scope=scope,
        principal=principal,
        request=TelegramAliasSaveRequest(
            alias_text="Morning briefing",
            target_summary="Configured workflow",
            idempotency_key="alias-live",
        ),
    )
    webhook = await build_webhook_validation_result(
        telegram_service=services["telegram_service"],
        scope=scope,
        principal=principal,
        request=WebhookValidationRequest(
            revision="telegram-config-not-configured",
            idempotency_key="webhook-live",
        ),
    )

    assert alias.status is ChannelMutationStatus.ACCEPTED
    assert alias.audit_reference
    assert webhook.status is ChannelMutationStatus.ACCEPTED
    assert webhook.audit_reference


async def test_tenant_user_gets_preference_profile_and_safe_run_status(
    session,
    settings,
) -> None:
    seed = await seed_channel_telegram_briefing_live_data(session)
    services = _services(session, settings)
    dashboard = await build_channel_telegram_briefing_dashboard(
        **services,
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_user_principal(),
        allowed_scope_options=_scope_options(),
    )
    run_status = await build_run_status_summary(
        runtime_repository=services["runtime_repository"],
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_user_principal(),
        workflow_run_id=str(seed.run_id),
    )

    assert dashboard.preference_profiles.current_user_profile is not None
    assert dashboard.aliases == ()
    assert run_status.status == "running"
    assert "run result" not in run_status.model_dump_json().lower()


async def test_preference_save_and_export_are_redaction_safe(session, settings) -> None:
    await seed_channel_telegram_briefing_live_data(session)
    services = _services(session, settings)
    scope = _tenant_scope(ACME_TENANT_ID, "Acme")
    principal = _tenant_user_principal()
    profiles = await build_briefing_preferences(
        briefing_service=services["briefing_service"],
        briefing_repository=services["briefing_repository"],
        scope=scope,
        principal=principal,
        allowed_scope_options=_scope_options(),
    )
    save = await build_preference_save_result(
        briefing_service=services["briefing_service"],
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
            revision=profiles.current_user_profile.revision
            if profiles.current_user_profile
            else None,
        ),
    )
    export = await build_preference_export_result(
        briefing_service=services["briefing_service"],
        scope=scope,
        principal=principal,
        request=BriefingPreferenceExportRequest(format="json"),
    )

    assert save.status is ChannelMutationStatus.ACCEPTED
    assert export.artifact_reference is not None
    assert "raw preference" not in export.model_dump_json().lower()


async def test_delivery_diagnostics_are_bounded(session, settings) -> None:
    await seed_channel_telegram_briefing_live_data(session)
    services = _services(session, settings)
    diagnostics = await build_delivery_diagnostics(
        telegram_repository=services["telegram_repository"],
        channel_repository=services["channel_repository"],
        scope=_tenant_scope(ACME_TENANT_ID, "Acme"),
        principal=_tenant_admin_principal(),
        allowed_scope_options=_scope_options(),
    )

    assert len(diagnostics.attempts) <= 25
    assert diagnostics.limit == 25
    assert diagnostics.webhook_receipts


def _services(session, settings):
    telegram_repository = TelegramConfigRepository(session)
    briefing_repository = BriefingPreferenceRepository(session)
    channel_service = ChannelService(settings=settings)
    return {
        "telegram_repository": telegram_repository,
        "telegram_service": TelegramConfigurationService(
            repository=telegram_repository,
            settings=settings,
            channel_service=channel_service,
        ),
        "briefing_repository": briefing_repository,
        "briefing_service": BriefingPreferenceService(briefing_repository),
        "channel_repository": ChannelRepository(session),
        "runtime_repository": RuntimeOrchestrationRepository(session),
    }


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
