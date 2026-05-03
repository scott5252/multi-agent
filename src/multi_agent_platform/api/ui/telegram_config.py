from __future__ import annotations

from pydantic import BaseModel

from multi_agent_platform.api.schemas.telegram_config import (
    TelegramDiagnosticResponse,
    TelegramIdentitySummaryResponse,
    TelegramLinkTokenAuditResponse,
    TelegramReadinessResponse,
    TenantTelegramConfigResponse,
)


class TelegramConfigurationPage(BaseModel):
    title: str = "Telegram Configuration"
    readiness: TelegramReadinessResponse
    tenant_config: TenantTelegramConfigResponse | None
    token_audits: tuple[TelegramLinkTokenAuditResponse, ...]
    identities: tuple[TelegramIdentitySummaryResponse, ...]
    diagnostics: tuple[TelegramDiagnosticResponse, ...]
    issued_token: str | None = None
    conflict: bool = False
    can_mutate: bool = True

    @property
    def readiness_label(self) -> str:
        return "Ready" if self.readiness.ready else "Not ready"

    @property
    def command_ready(self) -> bool:
        return bool(
            self.tenant_config
            and self.tenant_config.enabled
            and self.readiness.ready
            and self.tenant_config.command_ready
        )

    @property
    def enabled_commands(self) -> str:
        if self.tenant_config is None:
            return "No tenant selected"
        return ", ".join(self.tenant_config.protected_commands)


def redaction_notice() -> str:
    return (
        "Telegram configuration shows safe references, fingerprints, masked "
        "identifiers, and diagnostic categories only. Bot tokens, webhook "
        "secrets, private messages, raw prompts, and run results are excluded."
    )
