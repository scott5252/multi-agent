from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminShellState,
)

UNSAFE_TEXT_MARKERS = (
    "sk-",
    "authorization:",
    "bearer ",
    "begin private key",
    "traceback",
    "raw prompt",
    "raw completion",
    "memory contents",
    "provider payload",
    "tool payload",
    "/users/",
    "qa028-secret-value",
)


def safe_text(value: str, *, max_length: int = 220) -> str:
    normalized = " ".join(value.strip().split())
    if not normalized:
        raise ValueError("safe text is required")
    lowered = normalized.lower()
    if any(marker in lowered for marker in UNSAFE_TEXT_MARKERS):
        raise ValueError("unsafe text cannot be rendered in React admin contracts")
    return normalized[:max_length]


class AdminActionMethod(StrEnum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class AdminProblemReason(StrEnum):
    AUTH_REQUIRED = "auth_required"
    INSUFFICIENT_ROLE = "insufficient_role"
    TENANT_SCOPE_DENIED = "tenant_scope_denied"
    VALIDATION_ERROR = "validation_error"
    STALE_CONFLICT = "stale_conflict"
    CONFIRMATION_REQUIRED = "confirmation_required"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    UNEXPECTED_ERROR = "unexpected_error"


class AdminMutationStatus(StrEnum):
    ACCEPTED = "accepted"
    VALIDATION_ERROR = "validation_error"
    STALE_CONFLICT = "stale_conflict"
    REPLAYED = "replayed"
    CONFIRMATION_REQUIRED = "confirmation_required"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    UNEXPECTED_ERROR = "unexpected_error"


class AdminSortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class AdminExportStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    EXPIRED = "expired"


class EvidenceReferenceType(StrEnum):
    AUDIT = "audit"
    EXPORT = "export"
    DELIVERY = "delivery"
    RUNTIME = "runtime"
    GATEWAY = "gateway"
    VALIDATION = "validation"


class ValidationFieldError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    label: str
    message: str
    code: str

    @field_validator("label", "message")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=140)


class SafeProblemDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    reason_category: AdminProblemReason
    field_errors: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)
    retry_after_seconds: int | None = None
    audit_reference_id: str | None = None

    @field_validator("title", "detail")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=180)


class ConfirmationRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    confirm_label: str = "Confirm"

    @field_validator("title", "summary", "confirm_label")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=160)


class AdminAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: str
    label: str
    method: AdminActionMethod
    href: str
    variant: ReactAdminPageActionVariant = ReactAdminPageActionVariant.SECONDARY
    requires_confirmation: bool = False
    confirmation: ConfirmationRequirement | None = None
    requires_idempotency_key: bool = False
    action_token: str | None = None
    enabled: bool = True
    disabled_reason: str | None = None

    @field_validator("label", "disabled_reason")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_text(value, max_length=120)


class ToastHint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tone: ReactAdminNotificationTone
    title: str
    summary: str

    @field_validator("title", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=160)


class RevisionConflict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    submitted_revision: str
    current_revision: str
    message: str
    reload_href: str

    @field_validator("message")
    @classmethod
    def message_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=180)


class IdempotencyReplay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: str
    replayed: bool
    original_result_reference: str | None = None
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=160)


class MutationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AdminMutationStatus
    summary: str
    toast: ToastHint | None = None
    field_errors: tuple[ValidationFieldError, ...] = Field(default_factory=tuple)
    stale_conflict: RevisionConflict | None = None
    idempotency: IdempotencyReplay | None = None
    confirmation: ConfirmationRequirement | None = None
    audit_reference_id: str | None = None
    next_action: AdminAction | None = None

    @field_validator("summary")
    @classmethod
    def summary_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=220)


class FilterOperator(StrEnum):
    EQUALS = "equals"
    IN = "in"


class FilterOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str
    label: str

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=90)


class FilterCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    operator: FilterOperator = FilterOperator.EQUALS
    options: tuple[FilterOption, ...] = Field(default_factory=tuple)

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=90)


class FilterChip(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    value: str
    href: str

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=120)


class SavedFilterSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filter_id: str
    label: str
    href: str

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=90)


class FilterProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    criteria: tuple[FilterCriterion, ...] = Field(default_factory=tuple)
    active_chips: tuple[FilterChip, ...] = Field(default_factory=tuple)
    saved_filters: tuple[SavedFilterSummary, ...] = Field(default_factory=tuple)


class PaginationState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_size: int = Field(ge=1, le=50)
    page_size_options: tuple[int, ...] = (10, 25, 50)
    next_cursor: str | None = None
    previous_cursor: str | None = None
    total_known: bool = True
    total_items: int | None = Field(default=None, ge=0)


class SortField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    direction: AdminSortDirection = AdminSortDirection.ASC

    @field_validator("label")
    @classmethod
    def label_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=90)


class SortingState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    active: SortField
    allowed: tuple[SortField, ...] = Field(default_factory=tuple)


class ExportSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_id: str
    status: AdminExportStatus
    summary: str
    artifact_reference_id: str | None = None
    progress_label: str | None = None
    expires_at: datetime | None = None
    audit_reference_id: str | None = None

    @field_validator("summary", "progress_label")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_text(value, max_length=160)

    @field_validator("artifact_reference_id")
    @classmethod
    def artifact_reference_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith(("/", "file:")) or ".." in value:
            raise ValueError("artifact reference must not expose a filesystem path")
        return value


class EvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    label: str
    summary: str
    reference_type: EvidenceReferenceType
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=160)


class RefreshHint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str = "manual"
    interval_seconds: int | None = Field(default=None, ge=5, le=300)


class SampleRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    name: str
    status: str
    owner_scope: str
    updated_label: str
    revision: str

    @field_validator("name", "status", "owner_scope", "updated_label")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=120)


class FormFieldDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    label: str
    input_type: str = "text"
    required: bool = False
    help_text: str | None = None

    @field_validator("label", "help_text")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_text(value, max_length=160)


class SampleFormDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: tuple[FormFieldDescriptor, ...] = Field(default_factory=tuple)
    default_values: dict[str, str | bool] = Field(default_factory=dict)
    revision: str
    idempotency_key: str


class PatternsSampleData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    records: tuple[SampleRecord, ...] = Field(default_factory=tuple)
    form: SampleFormDescriptor
    export_snapshot: ExportSnapshot
    details: tuple[EvidenceSummary, ...] = Field(default_factory=tuple)


class AdminPageEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    state: ReactAdminShellState | None = None
    data: PatternsSampleData
    filters: FilterProfile
    pagination: PaginationState
    sorting: SortingState
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    evidence: tuple[EvidenceSummary, ...] = Field(default_factory=tuple)
    refresh: RefreshHint | None = None

    @field_validator("title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_text(value, max_length=180)


class SampleActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_name: str = ""
    revision: str = ""
    idempotency_key: str = ""
    confirmed: bool = False
    outcome: str = "accepted"


def redacted_dict(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only safe scalar values for tests and future summaries."""
    return {
        key: value
        for key, value in payload.items()
        if isinstance(value, (str, int, float, bool))
        and not str(value).startswith("sk-")
    }
