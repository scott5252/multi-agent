from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from multi_agent_platform.api.schemas.admin_patterns import safe_text
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminShellState,
)

CHANNEL_TELEGRAM_BRIEFING_UNSAFE_MARKERS = (
    "qa036-secret-value",
    "bot token",
    "webhook secret",
    "full telegram",
    "telegram user id",
    "telegram chat id",
    "private message",
    "raw preference",
    "raw prompt",
    "raw completion",
    "run result",
    "raw run",
    "raw tool payload",
    "authorization header",
    "bearer ",
    "credential value",
    "provider token",
    "unauthorized tenant label",
    "/users/",
    "/Users/",
)


def safe_channel_text(value: str, *, max_length: int = 320) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(
        marker.lower() in lowered for marker in CHANNEL_TELEGRAM_BRIEFING_UNSAFE_MARKERS
    ):
        raise ValueError(
            "unsafe channel, Telegram, or briefing text cannot be rendered"
        )
    return normalized


def _validate_strings(value: object) -> None:
    if isinstance(value, str):
        safe_channel_text(value)
        return
    if isinstance(value, dict):
        for item in value.values():
            _validate_strings(item)
        return
    if isinstance(value, list | tuple):
        for item in value:
            _validate_strings(item)


class SafeChannelTelegramBriefingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def safe_string_payload(self) -> SafeChannelTelegramBriefingModel:
        _validate_strings(self.model_dump(mode="python"))
        return self


class ChannelReadinessStatus(StrEnum):
    READY = "ready"
    PARTIAL = "partial"
    DISABLED = "disabled"
    STALE = "stale"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class ChannelActionMethod(StrEnum):
    GET = "get"
    POST = "post"


class ChannelMutationStatus(StrEnum):
    ACCEPTED = "accepted"
    REPLAYED = "replayed"
    VALIDATION_ERROR = "validation_error"
    CONFLICT = "conflict"
    DENIED = "denied"
    AUDIT_UNAVAILABLE = "audit_unavailable"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"


class AliasLifecycleStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING_VALIDATION = "pending_validation"
    DELETED = "deleted"


class AliasProtectedReadiness(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"
    MISSING_IDENTITY = "missing_identity"
    MISSING_CONFIG = "missing_config"
    VALIDATION_ERROR = "validation_error"


class LinkedIdentityStatus(StrEnum):
    LINKED = "linked"
    PENDING = "pending"
    REVOKED = "revoked"
    STALE = "stale"


class DeliveryAttemptStatus(StrEnum):
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"


class DeliveryRetryCategory(StrEnum):
    NONE = "none"
    RETRYABLE = "retryable"
    PERMANENT = "permanent"
    THROTTLED = "throttled"
    POLICY_DENIED = "policy_denied"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"


class BotBoundaryStatus(StrEnum):
    MOCKED = "mocked"
    SKIPPED = "skipped"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class WebhookDiagnosticStatus(StrEnum):
    VALID = "valid"
    STALE = "stale"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    PENDING = "pending"


class RunStatusCategory(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNAVAILABLE = "unavailable"


class CommuteMode(StrEnum):
    NONE = "none"
    CAR = "car"
    TRANSIT = "transit"
    WALK = "walk"
    BIKE = "bike"
    REMOTE = "remote"


class BriefingOutputStyle(StrEnum):
    CONCISE = "concise"
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    ACTION_FIRST = "action_first"


class ChannelAction(SafeChannelTelegramBriefingModel):
    action_id: str
    label: str
    href: str | None = None
    method: ChannelActionMethod = ChannelActionMethod.POST
    enabled: bool = True
    disabled_reason: str | None = None


class ChannelProblem(SafeChannelTelegramBriefingModel):
    reason: str
    title: str
    detail: str
    next_action: str
    audit_reference: str | None = None


class ChannelTelegramReadiness(SafeChannelTelegramBriefingModel):
    readiness_id: str
    status: ChannelReadinessStatus
    channel_label: str
    tenant_label: str
    telegram_enabled: bool
    webhook_status: WebhookDiagnosticStatus
    secret_reference_status: ChannelReadinessStatus
    linked_identity_count: int = Field(ge=0)
    alias_count: int = Field(ge=0)
    delivery_health_label: str
    preference_resolver_label: str
    audit_reference: str
    next_step: str


class TelegramTenantConfiguration(SafeChannelTelegramBriefingModel):
    tenant_id: UUID | None
    tenant_label: str
    enabled: bool
    bot_token_reference_label: str
    webhook_signing_reference_label: str
    webhook_url_status: ChannelReadinessStatus
    revision: str
    last_validated_at: datetime | None = None
    audit_reference: str
    actions: tuple[ChannelAction, ...] = Field(default_factory=tuple, max_length=8)


class TelegramAliasRecord(SafeChannelTelegramBriefingModel):
    alias_id: str
    tenant_label: str
    alias_text: str
    target_summary: str
    protected_readiness: AliasProtectedReadiness
    status: AliasLifecycleStatus
    revision: str
    last_used_at: datetime | None = None
    audit_reference: str
    actions: tuple[ChannelAction, ...] = Field(default_factory=tuple, max_length=8)


class LinkTokenResult(SafeChannelTelegramBriefingModel):
    link_token_request_id: str
    token_value: str | None = None
    masked_status: str
    expires_at: datetime
    consumed_at: datetime | None = None
    next_step: str
    audit_reference: str
    display_mode: str = Field(default="masked", pattern="^(immediate|masked)$")

    @model_validator(mode="after")
    def hidden_token_is_not_recoverable(self) -> LinkTokenResult:
        if self.display_mode == "masked" and self.token_value is not None:
            raise ValueError("masked link token result cannot include token value")
        if self.display_mode == "immediate" and not self.token_value:
            raise ValueError("immediate link token result requires token value")
        return self


class LinkedTelegramIdentitySummary(SafeChannelTelegramBriefingModel):
    identity_id: str
    principal_label: str
    telegram_label: str
    chat_label: str
    linked_at: datetime
    status: LinkedIdentityStatus
    audit_reference: str


class WebhookDiagnosticSummary(SafeChannelTelegramBriefingModel):
    diagnostic_id: str
    status: WebhookDiagnosticStatus
    last_checked_at: datetime
    safe_update_summary: str
    receipt_count: int = Field(ge=0, le=50)
    next_step: str
    audit_reference: str


class DeliveryAttemptSummary(SafeChannelTelegramBriefingModel):
    attempt_id: str
    tenant_label: str
    alias_label: str
    status: DeliveryAttemptStatus
    retry_category: DeliveryRetryCategory
    bot_api_boundary_status: BotBoundaryStatus
    run_status_href: str | None = None
    safe_error_summary: str
    attempted_at: datetime
    trace_reference: str
    audit_reference: str


class DeliveryDiagnosticList(SafeChannelTelegramBriefingModel):
    attempts: tuple[DeliveryAttemptSummary, ...] = Field(
        default_factory=tuple, max_length=25
    )
    limit: int = Field(default=25, ge=1, le=25)
    total_rows: int = Field(ge=0)
    webhook_receipts: tuple[WebhookDiagnosticSummary, ...] = Field(
        default_factory=tuple, max_length=10
    )


class RunStatusSummary(SafeChannelTelegramBriefingModel):
    run_id: str
    status: RunStatusCategory
    workflow_label: str
    requested_by_label: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    next_step: str
    href: str
    artifact_references: tuple[str, ...] = Field(default_factory=tuple, max_length=5)
    audit_reference: str


class BriefingPreferenceProfile(SafeChannelTelegramBriefingModel):
    profile_id: str
    tenant_label: str
    principal_label: str
    timezone: str
    location_summary: str
    news_topics_summary: str
    vip_sender_summary: str
    workday_hours: str
    commute_mode: CommuteMode
    default_account_summary: str
    output_style: BriefingOutputStyle
    scheduled_time_summary: str | None = None
    revision: str
    runtime_ready: bool
    audit_reference: str


class BriefingPreferenceList(SafeChannelTelegramBriefingModel):
    current_user_profile: BriefingPreferenceProfile | None = None
    admin_summaries: tuple[BriefingPreferenceProfile, ...] = Field(
        default_factory=tuple, max_length=20
    )
    import_export_evidence: tuple[str, ...] = Field(default_factory=tuple, max_length=8)


class BriefingPreferenceMutationResult(SafeChannelTelegramBriefingModel):
    status: ChannelMutationStatus
    profile_summary: str
    revision: str | None = None
    field_errors: dict[str, str] = Field(default_factory=dict)
    artifact_reference: str | None = None
    row_count: int | None = Field(default=None, ge=0)
    audit_reference: str
    next_step: str


class ChannelMutationResult(SafeChannelTelegramBriefingModel):
    status: ChannelMutationStatus
    summary: str
    revision: str | None = None
    idempotency_key: str | None = None
    replayed: bool = False
    field_errors: dict[str, str] = Field(default_factory=dict)
    audit_reference: str
    next_step: str


class ChannelTelegramBriefingDashboard(SafeChannelTelegramBriefingModel):
    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = Field(
        default_factory=tuple
    )
    readiness: tuple[ChannelTelegramReadiness, ...] = Field(
        default_factory=tuple, max_length=12
    )
    tenant_configs: tuple[TelegramTenantConfiguration, ...] = Field(
        default_factory=tuple, max_length=12
    )
    aliases: tuple[TelegramAliasRecord, ...] = Field(
        default_factory=tuple, max_length=25
    )
    link_token_result: LinkTokenResult | None = None
    linked_identities: tuple[LinkedTelegramIdentitySummary, ...] = Field(
        default_factory=tuple, max_length=25
    )
    webhook_diagnostics: tuple[WebhookDiagnosticSummary, ...] = Field(
        default_factory=tuple, max_length=10
    )
    delivery_attempts: tuple[DeliveryAttemptSummary, ...] = Field(
        default_factory=tuple, max_length=25
    )
    run_status_links: tuple[RunStatusSummary, ...] = Field(
        default_factory=tuple, max_length=12
    )
    preference_profiles: BriefingPreferenceList
    states: tuple[ChannelProblem, ...] = Field(default_factory=tuple, max_length=12)
    common_states: tuple[ReactAdminShellState, ...] = Field(default_factory=tuple)
    updated_at: datetime


class ChannelTelegramDashboardQuery(SafeChannelTelegramBriefingModel):
    tenant_id: str | None = None

    @field_validator("tenant_id")
    @classmethod
    def optional_tenant_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_channel_text(value, max_length=80)


class TelegramConfigSaveRequest(SafeChannelTelegramBriefingModel):
    enabled: bool
    bot_token_reference_label: str = Field(max_length=160)
    webhook_signing_reference_label: str = Field(max_length=160)
    revision: str = Field(max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)


class WebhookValidationRequest(SafeChannelTelegramBriefingModel):
    tenant_id: str | None = None
    revision: str = Field(max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)


class TelegramAliasSaveRequest(SafeChannelTelegramBriefingModel):
    alias_id: str | None = Field(default=None, max_length=128)
    alias_text: str = Field(max_length=120)
    target_summary: str = Field(max_length=220)
    revision: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)


class TelegramAliasActionRequest(SafeChannelTelegramBriefingModel):
    revision: str = Field(max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)


class LinkTokenCreateRequest(SafeChannelTelegramBriefingModel):
    principal_label: str = Field(max_length=160)
    expires_in_minutes: int = Field(default=10, ge=1, le=60)
    idempotency_key: str | None = Field(default=None, max_length=128)


class BriefingPreferenceSaveRequest(SafeChannelTelegramBriefingModel):
    timezone: str = Field(max_length=80)
    location_summary: str = Field(max_length=160)
    news_topics_summary: str = Field(max_length=160)
    vip_sender_summary: str = Field(max_length=160)
    workday_hours: str = Field(max_length=80)
    commute_mode: CommuteMode
    default_account_summary: str = Field(max_length=160)
    output_style: BriefingOutputStyle
    scheduled_time_summary: str | None = Field(default=None, max_length=80)
    revision: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=128)


class BriefingPreferenceImportRequest(SafeChannelTelegramBriefingModel):
    artifact_reference: str = Field(max_length=160)
    field_count: int = Field(ge=1, le=50)
    idempotency_key: str | None = Field(default=None, max_length=128)


class BriefingPreferenceExportRequest(SafeChannelTelegramBriefingModel):
    format: str = Field(default="json", pattern="^(json|csv)$")
    idempotency_key: str | None = Field(default=None, max_length=128)
