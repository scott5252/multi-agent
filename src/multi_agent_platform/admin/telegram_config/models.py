from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

PROTECTED_TELEGRAM_COMMANDS = (
    "/run",
    "/status",
    "/approve",
    "/reject",
    "/resume",
    "/cancel",
    "/result",
    "/artifacts",
)


class TelegramConfigScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class TelegramLinkTokenStatus(StrEnum):
    ISSUED = "issued"
    CONSUMED = "consumed"
    REVOKED = "revoked"
    EXPIRED = "expired"


class TelegramIdentityStatus(StrEnum):
    LINKED = "linked"
    REVOKED = "revoked"


class TelegramDiagnosticCategory(StrEnum):
    READINESS = "readiness"
    WEBHOOK_VALIDATION = "webhook_validation"
    LINK_TOKEN = "link_token"
    IDENTITY = "identity"
    DELIVERY = "delivery"
    WRONG_SECRET = "wrong_secret"
    DUPLICATE_UPDATE = "duplicate_update"
    ACCESS_DENIED = "access_denied"


class TelegramDiagnosticStatus(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"
    OK = "ok"
    WARNING = "warning"
    FAILED = "failed"
    DENIED = "denied"
    REVOKED = "revoked"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class TelegramAccessScope:
    scope_type: TelegramConfigScopeType
    principal_id: str
    tenant_id: UUID | None = None
    platform_admin: bool = False

    def require_tenant(self) -> UUID:
        if self.tenant_id is None:
            raise PermissionError("tenant Telegram scope required")
        return self.tenant_id


@dataclass(frozen=True, slots=True)
class TelegramProviderReadiness:
    token_reference_configured: bool
    webhook_secret_configured: bool
    token_reference_safe: bool
    webhook_secret_safe: bool
    production_guardrails_ready: bool
    local_validation_only: bool
    ready: bool
    token_reference_label: str
    webhook_secret_label: str
    protected_commands: tuple[str, ...] = PROTECTED_TELEGRAM_COMMANDS


class TelegramConfigStaleRevisionError(ValueError):
    """Raised when a mutable Telegram config form uses an old revision token."""


def normalize_alias_text(value: str) -> str:
    return " ".join(value.strip().casefold().split())
