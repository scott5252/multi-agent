from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminMutationStatus,
    ConfirmationRequirement,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
    safe_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminEmptyStateMetadata,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminShellState,
)

MEMBERSHIP_UNSAFE_MARKERS = (
    "qa034-secret-value",
    "raw email",
    "full subject",
    "authorization header",
    "bearer ",
    "provider token",
    "credential value",
    "private message",
    "raw prompt",
    "raw completion",
    "raw transcript",
    "password",
    "stack trace",
    "/users/",
    "unauthorized tenant label",
)


def safe_membership_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in MEMBERSHIP_UNSAFE_MARKERS):
        raise ValueError("unsafe membership text cannot be rendered")
    if normalized.startswith("/"):
        raise ValueError("local paths cannot be rendered")
    return normalized


class MembershipLifecycleStatus(StrEnum):
    READY = "ready"
    ACTIVE = "active"
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    REMOVED = "removed"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    PARTIAL = "partial"
    REPLAYED = "replayed"


class MembershipScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class MembershipSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    label: str
    status: MembershipLifecycleStatus
    summary: str

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=180)


class MembershipSummaryCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    label: str
    value: str
    status: MembershipLifecycleStatus
    summary: str

    @field_validator("label", "value", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=180)


class MembershipFilterOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str
    label: str
    value: str
    selected: bool = False

    @field_validator("option_id", "label", "value")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=160)


class MembershipDirectoryFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str | None = None
    tenant_options: tuple[MembershipFilterOption, ...] = Field(default_factory=tuple)
    role_options: tuple[MembershipFilterOption, ...] = Field(default_factory=tuple)
    status_options: tuple[MembershipFilterOption, ...] = Field(default_factory=tuple)
    invitation_state_options: tuple[MembershipFilterOption, ...] = Field(
        default_factory=tuple
    )
    access_decision_options: tuple[MembershipFilterOption, ...] = Field(
        default_factory=tuple
    )

    @field_validator("query")
    @classmethod
    def optional_query_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=120)


class RoleChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_code: str
    role_label: str
    scope_type: MembershipScopeType
    tenant_id: str | None = None
    tenant_label: str | None = None
    eligible: bool = True
    disabled_reason: str | None = None

    @field_validator(
        "role_code", "role_label", "tenant_id", "tenant_label", "disabled_reason"
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=180)


class RawIdentifierDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authorized: bool
    principal_identity_id: str | None = None
    external_subject: str | None = None
    invitation_id: str | None = None
    copy_label: str
    reason: str

    @field_validator(
        "principal_identity_id",
        "external_subject",
        "invitation_id",
        "copy_label",
        "reason",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=220)


class TenantMembershipSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_membership_id: str
    tenant_id: str
    tenant_label: str
    membership_status: MembershipLifecycleStatus
    revision: str
    membership_source: str
    status_reason: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "tenant_membership_id",
        "tenant_id",
        "tenant_label",
        "revision",
        "membership_source",
        "status_reason",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=200)


class RoleGrantSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_grant_id: str
    principal_identity_id: str
    principal_label: str
    scope_type: MembershipScopeType
    tenant_id: str | None = None
    tenant_label: str | None = None
    role_code: str
    role_label: str
    grant_status: MembershipLifecycleStatus
    effective_label: str
    revoked_label: str | None = None
    next_request_effect: str
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "role_grant_id",
        "principal_identity_id",
        "principal_label",
        "tenant_id",
        "tenant_label",
        "role_code",
        "role_label",
        "effective_label",
        "revoked_label",
        "next_request_effect",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=220)


class UserDirectoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_identity_id: str
    display_name: str
    masked_email: str
    safe_subject_suffix: str
    principal_status: MembershipLifecycleStatus
    tenant_memberships: tuple[TenantMembershipSummary, ...] = Field(
        default_factory=tuple
    )
    role_summaries: tuple[RoleGrantSummary, ...] = Field(default_factory=tuple)
    last_access_summary: str
    raw_identifier_detail: RawIdentifierDetail | None = None
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "principal_identity_id",
        "display_name",
        "masked_email",
        "safe_subject_suffix",
        "last_access_summary",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class InvitationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invitation_id: str
    tenant_id: str | None = None
    tenant_label: str | None = None
    masked_email: str
    email_hash_label: str
    requested_roles: tuple[str, ...] = Field(default_factory=tuple)
    status: MembershipLifecycleStatus
    expires_label: str
    replayed: bool
    next_request_effect: str
    audit_reference_id: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "invitation_id",
        "tenant_id",
        "tenant_label",
        "masked_email",
        "email_hash_label",
        "expires_label",
        "next_request_effect",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=220)

    @field_validator("requested_roles")
    @classmethod
    def roles_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_membership_text(item, max_length=120) for item in value)


class PrincipalLinkSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_identity_id: str
    display_name: str
    masked_email: str | None = None
    safe_subject_suffix: str
    link_status: MembershipLifecycleStatus
    conflict_summary: str | None = None
    audit_reference_id: str

    @field_validator(
        "principal_identity_id",
        "display_name",
        "masked_email",
        "safe_subject_suffix",
        "conflict_summary",
        "audit_reference_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=220)


class MembershipStatusSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_membership_id: str
    principal_identity_id: str
    tenant_id: str
    tenant_label: str
    membership_status: MembershipLifecycleStatus
    revision: str
    membership_source: str
    status_reason: str
    authorized_actions: tuple[AdminAction, ...] = Field(default_factory=tuple)

    @field_validator(
        "tenant_membership_id",
        "principal_identity_id",
        "tenant_id",
        "tenant_label",
        "revision",
        "membership_source",
        "status_reason",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class AccessHistoryRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_history_id: str
    principal_label: str
    tenant_label: str
    surface_key: str
    requested_action: str
    decision: str
    reason_category: str
    role_source_summary: str
    timestamp_label: str
    trace_id: str
    audit_reference_id: str

    @field_validator(
        "access_history_id",
        "principal_label",
        "tenant_label",
        "surface_key",
        "requested_action",
        "decision",
        "reason_category",
        "role_source_summary",
        "timestamp_label",
        "trace_id",
        "audit_reference_id",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class MembershipAuditRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_reference_id: str
    domain: str
    actor_label: str
    target_label: str
    tenant_scope_label: str
    action: str
    outcome: str
    safe_diff_summary: str
    timestamp_label: str
    redaction_class: str

    @field_validator(
        "audit_reference_id",
        "domain",
        "actor_label",
        "target_label",
        "tenant_scope_label",
        "action",
        "outcome",
        "safe_diff_summary",
        "timestamp_label",
        "redaction_class",
    )
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=240)


class SupportOverrideSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    support_override_id: str
    tenant_id: str | None = None
    tenant_label: str
    requester_label: str
    approver_label: str | None = None
    status: MembershipLifecycleStatus
    expires_label: str
    audit_reference_id: str
    safe_summary: str

    @field_validator(
        "support_override_id",
        "tenant_id",
        "tenant_label",
        "requester_label",
        "approver_label",
        "expires_label",
        "audit_reference_id",
        "safe_summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=220)


class InvitationFormMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_tenant_id: str | None = None
    tenant_options: tuple[MembershipFilterOption, ...] = Field(default_factory=tuple)
    role_choices: tuple[RoleChoice, ...] = Field(default_factory=tuple)
    default_expiry_label: str
    idempotency_hint: str

    @field_validator("default_tenant_id", "default_expiry_label", "idempotency_hint")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=180)


class RoleGrantFormMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_choices: tuple[RoleChoice, ...] = Field(default_factory=tuple)
    confirmation_copy: str
    stale_recovery_copy: str

    @field_validator("confirmation_copy", "stale_recovery_copy")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class MembershipDashboard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    summary_cards: tuple[MembershipSummaryCard, ...] = Field(default_factory=tuple)
    sections: tuple[MembershipSection, ...] = Field(default_factory=tuple)
    directory: tuple[UserDirectoryEntry, ...] = Field(default_factory=tuple)
    filters: MembershipDirectoryFilters
    allowed_scope_options: tuple[ReactAdminScopeOption, ...] = Field(
        default_factory=tuple
    )
    invite_form: InvitationFormMetadata
    role_grant_form: RoleGrantFormMetadata
    invitations: tuple[InvitationSummary, ...] = Field(default_factory=tuple)
    role_grants: tuple[RoleGrantSummary, ...] = Field(default_factory=tuple)
    status_actions: tuple[MembershipStatusSummary, ...] = Field(default_factory=tuple)
    access_history: tuple[AccessHistoryRecord, ...] = Field(default_factory=tuple)
    audit_timeline: tuple[MembershipAuditRecord, ...] = Field(default_factory=tuple)
    support_overrides: tuple[SupportOverrideSummary, ...] = Field(default_factory=tuple)
    provenance: ReactAdminPageProvenance
    empty_state: ReactAdminEmptyStateMetadata | None = None
    common_states: tuple[ReactAdminShellState, ...] = Field(default_factory=tuple)

    @field_validator("page_id", "title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class MembershipAccessHistoryList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    records: tuple[AccessHistoryRecord, ...] = Field(default_factory=tuple)
    partial: bool = False
    safe_summary: str

    @field_validator("safe_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class MembershipAuditList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: ReactAdminScope
    records: tuple[MembershipAuditRecord, ...] = Field(default_factory=tuple)
    unavailable: bool = False
    safe_summary: str

    @field_validator("safe_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=220)


class MembershipMutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdminMutationStatus
    summary: str
    toast: ToastHint | None = None
    directory_entry: UserDirectoryEntry | None = None
    invitation: InvitationSummary | None = None
    principal_link: PrincipalLinkSummary | None = None
    role_grant: RoleGrantSummary | None = None
    membership_status: MembershipStatusSummary | None = None
    access_history: tuple[AccessHistoryRecord, ...] = Field(default_factory=tuple)
    audit_reference_id: str
    field_errors: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)
    stale_conflict: RevisionConflict | None = None
    idempotency_replay: bool = False
    confirmation: ConfirmationRequirement | None = None
    next_request_effect: str

    @field_validator("summary", "audit_reference_id", "next_request_effect")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_membership_text(value, max_length=240)


class MembershipInvitationSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: str | None = None
    email: str = Field(min_length=3, max_length=180)
    requested_roles: tuple[str, ...] = Field(default_factory=tuple)
    idempotency_key: str = Field(min_length=8, max_length=120)

    @field_validator("email")
    @classmethod
    def email_shape_is_safe(cls, value: str) -> str:
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("email address is required")
        return normalized


class PrincipalLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_identity_id: str | None = None
    display_name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, min_length=3, max_length=180)
    external_subject: str = Field(min_length=4, max_length=180)
    overwrite_confirmed: bool = False
    idempotency_key: str = Field(min_length=8, max_length=120)

    @field_validator("email")
    @classmethod
    def optional_email_shape_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("email address is required")
        return normalized


class RoleGrantSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_identity_id: str
    scope_type: MembershipScopeType
    tenant_id: str | None = None
    role_code: str
    confirmed: bool = False
    idempotency_key: str = Field(min_length=8, max_length=120)


class MembershipConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmed: bool = False
    revision: str | None = None
    reason: str | None = None
    idempotency_key: str = Field(min_length=8, max_length=120)

    @field_validator("revision", "reason")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_membership_text(value, max_length=180)
