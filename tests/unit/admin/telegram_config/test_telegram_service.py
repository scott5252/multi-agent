from __future__ import annotations

from multi_agent_platform.admin.telegram_config.models import (
    TelegramAccessScope,
    TelegramConfigScopeType,
    TelegramDiagnosticStatus,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
)
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)


def _settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "telegram_provider_token_ref": "env:TELEGRAM_PROVIDER_TOKEN",
            "telegram_webhook_secret": "local:telegram-webhook-secret",
        }
    )


def _service(session, settings: Settings) -> TelegramConfigurationService:
    resolved = _settings(settings)
    return TelegramConfigurationService(
        repository=TelegramConfigRepository(session),
        settings=resolved,
        channel_service=ChannelService(settings=resolved),
    )


async def test_telegram_service_readiness_and_webhook_diagnostic(
    session,
    seeded_tenant,
    settings,
) -> None:
    service = _service(session, settings)
    scope = TelegramAccessScope(
        scope_type=TelegramConfigScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin",
    )

    readiness = service.provider_readiness()
    diagnostic = await service.validate_webhook(scope)

    assert readiness.ready is True
    assert readiness.token_reference_label == "env:***"
    assert diagnostic.status == TelegramDiagnosticStatus.READY.value
    assert diagnostic.redacted_metadata["external_call_performed"] is False


async def test_telegram_service_link_token_and_identity_are_redacted(
    session,
    seeded_tenant,
    settings,
) -> None:
    service = _service(session, settings)
    scope = TelegramAccessScope(
        scope_type=TelegramConfigScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin",
    )

    issued = await service.issue_link_token(scope)
    identity = service.channel_service.consume_telegram_link_token(
        token=issued.raw_token,
        telegram_user_id=123456789,
        telegram_chat_id=987654321,
    )
    identities = await service.list_identities(scope)
    revoked = await service.revoke_link_token(
        access_scope=scope,
        token_audit_id=issued.audit.telegram_link_token_audit_id,
    )

    assert identity.platform_identity_id == "tenant-admin"
    assert issued.raw_token not in issued.audit.token_fingerprint
    assert identities[0].telegram_user_display == "123***789"
    assert revoked is not None


def test_telegram_service_production_requires_safe_webhook_reference() -> None:
    settings = Settings(
        _env_file=None,
        app_env="production",
        auth_mode="auth0",
        auth0_domain="auth.example.com",
        auth0_issuer="https://auth.example.com/",
        auth0_audience="api://test",
        telegram_provider_token_ref="env:TELEGRAM_PROVIDER_TOKEN",
        telegram_webhook_secret="raw-webhook-value",
    )
    service = TelegramConfigurationService(
        repository=TelegramConfigRepository(None),  # type: ignore[arg-type]
        settings=settings,
        channel_service=ChannelService(settings=settings),
    )

    readiness = service.provider_readiness()

    assert readiness.ready is False
    assert readiness.production_guardrails_ready is False
