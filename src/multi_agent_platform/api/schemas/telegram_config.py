from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from multi_agent_platform.admin.telegram_config.models import (
    PROTECTED_TELEGRAM_COMMANDS,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramIdentityStatus,
    TelegramLinkTokenStatus,
)


class TelegramReadinessResponse(BaseModel):
    token_reference_configured: bool
    webhook_secret_configured: bool
    token_reference_safe: bool
    webhook_secret_safe: bool
    production_guardrails_ready: bool
    local_validation_only: bool
    ready: bool
    token_reference_label: str
    webhook_secret_label: str
    protected_commands: tuple[str, ...]


class TenantTelegramConfigResponse(BaseModel):
    telegram_tenant_config_id: UUID
    tenant_id: UUID
    enabled: bool
    protected_commands: tuple[str, ...]
    status_note: str | None = None
    revision_token: str
    updated_by_principal_id: str
    created_at: datetime
    updated_at: datetime
    command_ready: bool


class TenantTelegramConfigUpdateRequest(BaseModel):
    tenant_id: UUID | None = None
    enabled: bool
    protected_commands: tuple[str, ...] = PROTECTED_TELEGRAM_COMMANDS
    status_note: str | None = Field(default=None, max_length=500)
    revision_token: str | None = None

    @field_validator("protected_commands")
    @classmethod
    def validate_commands(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        allowed = set(PROTECTED_TELEGRAM_COMMANDS)
        if any(value not in allowed for value in values):
            raise ValueError("unsupported Telegram protected command")
        return values


class TelegramCommandAliasResponse(BaseModel):
    telegram_command_alias_id: UUID
    tenant_id: UUID
    alias_text: str
    alias_normalized: str
    published_workflow_version_id: UUID
    description: str | None = None
    protected: bool
    enabled: bool
    revision_token: str
    updated_by_principal_id: str
    created_at: datetime
    updated_at: datetime


class TelegramCommandAliasUpsertRequest(BaseModel):
    tenant_id: UUID | None = None
    alias_text: str = Field(min_length=1, max_length=120)
    published_workflow_version_id: UUID
    description: str | None = Field(default=None, max_length=500)
    protected: bool = True
    enabled: bool = True
    revision_token: str | None = None


class TelegramCommandAliasListResponse(BaseModel):
    items: tuple[TelegramCommandAliasResponse, ...]


class TelegramDiagnosticResponse(BaseModel):
    telegram_diagnostic_event_id: UUID
    tenant_id: UUID | None
    principal_id: str | None
    category: TelegramDiagnosticCategory
    status: TelegramDiagnosticStatus
    summary: str
    trace_id: str
    redacted_metadata: dict[str, object]
    created_at: datetime


class TelegramDiagnosticsResponse(BaseModel):
    items: tuple[TelegramDiagnosticResponse, ...]


class TelegramLinkTokenAuditResponse(BaseModel):
    telegram_link_token_audit_id: UUID
    tenant_id: UUID
    issued_by_principal_id: str
    token_fingerprint: str
    status: TelegramLinkTokenStatus
    expires_at: datetime
    issued_at: datetime
    consumed_at: datetime | None = None
    revoked_at: datetime | None = None
    trace_id: str


class TelegramLinkTokenIssueResponse(BaseModel):
    link_token: str
    token_audit: TelegramLinkTokenAuditResponse


class TelegramLinkTokenListResponse(BaseModel):
    items: tuple[TelegramLinkTokenAuditResponse, ...]


class TelegramIdentitySummaryResponse(BaseModel):
    telegram_linked_identity_summary_id: UUID
    tenant_id: UUID
    platform_identity_id: str
    telegram_user_display: str
    telegram_chat_display: str
    status: TelegramIdentityStatus
    linked_at: datetime
    revoked_at: datetime | None = None
    command_ready: bool
    trace_id: str


class TelegramIdentityListResponse(BaseModel):
    items: tuple[TelegramIdentitySummaryResponse, ...]


class TelegramConsoleSnapshotResponse(BaseModel):
    readiness: TelegramReadinessResponse
    tenant_config: TenantTelegramConfigResponse | None
    aliases: tuple[TelegramCommandAliasResponse, ...] = ()
    token_audits: tuple[TelegramLinkTokenAuditResponse, ...]
    identities: tuple[TelegramIdentitySummaryResponse, ...]
    diagnostics: tuple[TelegramDiagnosticResponse, ...]
