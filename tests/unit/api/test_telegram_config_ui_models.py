from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.api.schemas.telegram_config import (
    TelegramReadinessResponse,
    TenantTelegramConfigResponse,
)
from multi_agent_platform.api.ui.telegram_config import (
    TelegramConfigurationPage,
    redaction_notice,
)


def _readiness(*, ready: bool) -> TelegramReadinessResponse:
    return TelegramReadinessResponse(
        token_reference_configured=True,
        webhook_secret_configured=True,
        token_reference_safe=True,
        webhook_secret_safe=True,
        production_guardrails_ready=ready,
        local_validation_only=True,
        ready=ready,
        token_reference_label="static:qa017/telegram-provider-token",
        webhook_secret_label="sha256:abcdef123456",
        protected_commands=("/run", "/status"),
    )


def _tenant_config(
    *,
    enabled: bool,
    command_ready: bool,
) -> TenantTelegramConfigResponse:
    now = datetime.now(UTC)
    tenant_id = uuid4()
    return TenantTelegramConfigResponse(
        telegram_tenant_config_id=uuid4(),
        tenant_id=tenant_id,
        enabled=enabled,
        protected_commands=("/run", "/status"),
        status_note="Enabled for QA",
        revision_token="rev-1",
        updated_by_principal_id="local-platform-admin",
        created_at=now,
        updated_at=now,
        command_ready=command_ready,
    )


def test_telegram_configuration_page_reports_command_readiness() -> None:
    page = TelegramConfigurationPage(
        readiness=_readiness(ready=True),
        tenant_config=_tenant_config(enabled=True, command_ready=True),
        token_audits=(),
        identities=(),
        diagnostics=(),
    )

    assert page.readiness_label == "Ready"
    assert page.command_ready is True
    assert page.enabled_commands == "/run, /status"


def test_telegram_configuration_page_handles_missing_tenant() -> None:
    page = TelegramConfigurationPage(
        readiness=_readiness(ready=False),
        tenant_config=None,
        token_audits=(),
        identities=(),
        diagnostics=(),
    )

    assert page.readiness_label == "Not ready"
    assert page.command_ready is False
    assert page.enabled_commands == "No tenant selected"


def test_telegram_redaction_notice_excludes_raw_secret_language() -> None:
    notice = redaction_notice()

    assert "Bot tokens" in notice
    assert "raw prompts" in notice
    assert "fingerprints" in notice
