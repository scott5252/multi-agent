from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ProviderType(StrEnum):
    OPENAI = "openai"
    LOCAL_OPENAI_COMPATIBLE = "local_openai_compatible"


class VisibilityMode(StrEnum):
    PLATFORM_DEFAULT = "platform_default"
    TENANT_ALLOWLIST = "tenant_allowlist"


class HealthState(StrEnum):
    DISABLED = "disabled"
    UNTESTED = "untested"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    UNAVAILABLE = "unavailable"


class TestOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"


TestOutcome.__test__ = False  # type: ignore[attr-defined]


class ErrorCategory(StrEnum):
    NONE = "none"
    AUTHORIZATION_FAILURE = "authorization_failure"
    INVALID_MODEL = "invalid_model"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    MALFORMED_PROVIDER_RESPONSE = "malformed_provider_response"
    POLICY_OR_VISIBILITY_DENIAL = "policy_or_visibility_denial"
    SECRET_REFERENCE_INVALID = "secret_reference_invalid"
    CATALOG_INACTIVE = "catalog_inactive"
    UNKNOWN_PROVIDER_FAILURE = "unknown_provider_failure"


class UsageAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MALFORMED = "malformed"


class SyncAction(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    MARKED_UNAVAILABLE = "marked_unavailable"
    BLOCKED = "blocked"


class OperationStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"
    RECOVERED = "recovered"
    DENIED = "denied"
    THROTTLED = "throttled"
    PARTIAL = "partial"


class RetryDecisionCategory(StrEnum):
    RETRYABLE = "retryable"
    NON_RETRYABLE = "non-retryable"
    EXHAUSTED = "exhausted"
    SKIPPED = "skipped"
    RECOVERED = "recovered"


class TimeoutPolicy(BaseModel):
    connect_seconds: float = Field(default=5.0, ge=0.1, le=60.0)
    read_seconds: float = Field(default=30.0, ge=0.1, le=300.0)
    total_seconds: float = Field(default=45.0, ge=0.1, le=300.0)

    @model_validator(mode="after")
    def validate_total(self) -> TimeoutPolicy:
        if self.total_seconds < max(self.connect_seconds, self.read_seconds):
            raise ValueError("total timeout must cover connect and read timeouts")
        return self


class ProviderModel(BaseModel):
    model_id: str = Field(min_length=1, max_length=128)
    display_name: str | None = Field(default=None, max_length=255)
    capability_metadata: dict[str, object] = Field(default_factory=dict)
    cost_metadata: dict[str, object] = Field(default_factory=dict)
    default_parameters: dict[str, object] = Field(default_factory=dict)
    available: bool = True


class TenantVisibility(BaseModel):
    mode: VisibilityMode = VisibilityMode.PLATFORM_DEFAULT
    tenant_ids: tuple[UUID, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_tenants(self) -> TenantVisibility:
        if self.mode is VisibilityMode.TENANT_ALLOWLIST and not self.tenant_ids:
            raise ValueError("tenant allowlist visibility requires tenant ids")
        if self.mode is VisibilityMode.PLATFORM_DEFAULT and self.tenant_ids:
            raise ValueError("platform-default visibility cannot include tenant ids")
        return self


class ProviderConnectionSummary(BaseModel):
    provider_connection_id: UUID
    provider_type: ProviderType
    display_name: str
    base_url_safe: str | None = None
    timeout_policy: TimeoutPolicy
    visibility: TenantVisibility
    active: bool
    health_state: HealthState
    model_count: int
    last_test_outcome: TestOutcome | None = None
    last_test_reason: ErrorCategory | None = None
    catalog_sync_status: str = "not_synced"
    updated_at: datetime | None = None


class ProviderTestSummary(BaseModel):
    outcome: TestOutcome
    normalized_reason: ErrorCategory
    latency_ms: int
    tested_model_id: str | None = None
    safe_diagnostic_summary: str
    safe_provider_request_id: str | None = None
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CatalogEntrySummary(BaseModel):
    tenant_id: UUID | None = None
    provider_type: ProviderType
    provider_connection_id: UUID
    provider_model_definition_id: UUID
    model_id: str
    display_name: str
    health_state: HealthState
    availability_status: str
    selectable: bool
    visibility_mode: VisibilityMode
    safe_summary: str = "Gateway-governed model catalog entry"


class GatewayUsage(BaseModel):
    availability: UsageAvailability = UsageAvailability.UNAVAILABLE
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    provider_model_id: str | None = None


class GatewayResult(BaseModel):
    outcome: TestOutcome
    content: str | None = None
    normalized_error_category: ErrorCategory = ErrorCategory.NONE
    latency_ms: int = 0
    usage: GatewayUsage = Field(default_factory=GatewayUsage)
    safe_audit_summary: dict[str, object] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GatewayInvocationContext:
    tenant_id: UUID | None
    trace_id: str | None = None
    workflow_run_id: UUID | None = None
    workflow_run_step_id: UUID | None = None
    test_bench_run_id: UUID | None = None
    workflow_validation_id: UUID | None = None
    idempotency_key: str | None = None
    operation_identity: str | None = None
    agent_key: str | None = None
    agent_kind: str | None = None
    agent_profile_version_id: UUID | None = None
    prompt_version_ids: tuple[UUID, ...] = ()
    prompt_reference_version_ids: tuple[UUID, ...] = ()
    model_routing_provenance: dict[str, object] = field(default_factory=dict)
    profile_provenance: dict[str, object] = field(default_factory=dict)
    memory_policy_context: dict[str, object] = field(default_factory=dict)
    tool_policy_expectations: dict[str, object] = field(default_factory=dict)
    output_contract_metadata: dict[str, object] = field(default_factory=dict)
    side_effect_boundary: str = "before_provider_invocation"

    def safe_summary(self) -> dict[str, object]:
        return {
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "workflow_run_id": str(self.workflow_run_id)
            if self.workflow_run_id
            else None,
            "workflow_run_step_id": str(self.workflow_run_step_id)
            if self.workflow_run_step_id
            else None,
            "test_bench_run_id": str(self.test_bench_run_id)
            if self.test_bench_run_id
            else None,
            "workflow_validation_id": str(self.workflow_validation_id)
            if self.workflow_validation_id
            else None,
            "trace_id": self.trace_id,
            "idempotency_key": self.idempotency_key,
            "operation_identity": self.operation_identity,
            "agent_key": self.agent_key,
            "agent_kind": self.agent_kind,
            "agent_profile_version_id": str(self.agent_profile_version_id)
            if self.agent_profile_version_id
            else None,
            "prompt_version_ids": [str(value) for value in self.prompt_version_ids],
            "prompt_reference_version_ids": [
                str(value) for value in self.prompt_reference_version_ids
            ],
            "model_routing_provenance": dict(self.model_routing_provenance),
            "profile_provenance": dict(self.profile_provenance),
            "memory_policy_context_keys": sorted(self.memory_policy_context),
            "tool_policy_expectation_keys": sorted(self.tool_policy_expectations),
            "output_contract_metadata_keys": sorted(self.output_contract_metadata),
            "side_effect_boundary": self.side_effect_boundary,
        }


@dataclass(frozen=True, slots=True)
class AdapterRequest:
    model_id: str
    messages: tuple[dict[str, str], ...]
    timeout_policy: TimeoutPolicy
    base_url: str | None = None
    credential: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AdapterResponse:
    outcome: TestOutcome
    content: str | None = None
    normalized_error_category: ErrorCategory = ErrorCategory.NONE
    latency_ms: int = 0
    provider_request_id: str | None = None
    usage: GatewayUsage = field(default_factory=GatewayUsage)
    safe_diagnostic_summary: str = "Provider call completed"
