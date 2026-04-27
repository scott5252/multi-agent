from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4


def now_utc() -> datetime:
    return datetime.now(UTC)


class ReliabilityScopeType(StrEnum):
    GLOBAL = "global"
    TENANT = "tenant"
    WORKFLOW = "workflow"
    DEPENDENCY = "dependency"
    ARTIFACT_STORE = "artifact_store"


class PolicyStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class AdmissionDecisionKind(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    DELAYED = "delayed"
    THROTTLED = "throttled"
    REJECTED = "rejected"
    RETRY_ELIGIBLE = "retry_eligible"


class QuotaResourceKind(StrEnum):
    SUBMITTED_WORK = "submitted_work"
    ACTIVE_WORK = "active_work"
    WORKER_LEASE = "worker_lease"
    RECOVERY_WORK = "recovery_work"
    RETRY_ATTEMPT = "retry_attempt"
    COMPENSATION_WORK = "compensation_work"
    ARTIFACT_IO = "artifact_io"
    OPERATIONAL_ACTION = "operational_action"


class ScalingDecisionKind(StrEnum):
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    HOLD = "hold"
    BLOCK_SCALE_OUT = "block_scale_out"


class RetryScheduleStatus(StrEnum):
    SCHEDULED = "scheduled"
    LEASED = "leased"
    STOPPED = "stopped"
    COMPLETED = "completed"


class FailureCategory(StrEnum):
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    AUTHORIZATION = "authorization"
    QUOTA_EXHAUSTED = "quota_exhausted"
    CONTRACT_INVALID = "contract_invalid"
    CHECKPOINT_INVALID = "checkpoint_invalid"
    OPEN_BREAKER = "open_breaker"
    UNKNOWN_SIDE_EFFECT = "unknown_side_effect"
    NON_REPEATABLE_AMBIGUOUS = "non_repeatable_ambiguous"
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    UNKNOWN = "unknown"


RETRYABLE_FAILURES = {
    FailureCategory.DEPENDENCY_UNAVAILABLE,
    FailureCategory.TIMEOUT,
    FailureCategory.RATE_LIMITED,
    FailureCategory.ARTIFACT_UNAVAILABLE,
}


class BreakerState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CompensationStatus(StrEnum):
    REQUESTED = "requested"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    TIMED_OUT = "timed_out"
    SKIPPED_BY_POLICY = "skipped_by_policy"
    MANUAL_FOLLOW_UP_REQUIRED = "manual_follow_up_required"


class DeadLetterStatus(StrEnum):
    OPEN = "open"
    REQUEUED = "requeued"
    COMPENSATING = "compensating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class RecommendedAction(StrEnum):
    REQUEUE = "requeue"
    COMPENSATE = "compensate"
    MARK_RESOLVED = "mark_resolved"
    OPERATOR_INTERVENTION = "operator_intervention"
    ESCALATE = "escalate"


class RecoveryOutcome(StrEnum):
    RESUMED = "resumed"
    DUPLICATE_SUPPRESSED = "duplicate_suppressed"
    COMPENSATION_REQUESTED = "compensation_requested"
    DEAD_LETTERED = "dead_lettered"
    OPERATOR_INTERVENTION_REQUIRED = "operator_intervention_required"
    STALE_TOKEN_SUPPRESSED = "stale_token_suppressed"


class SideEffectRepeatability(StrEnum):
    REPEATABLE = "repeatable"
    NON_REPEATABLE = "non_repeatable"
    COMPENSATABLE = "compensatable"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class ReliabilityPolicySettings:
    max_submitted_work: int = 1_000
    max_active_work: int = 250
    max_retry_attempts: int = 3
    retry_budget_per_window: int = 500
    fairness_weight: float = 1.0
    burst_multiplier: float = 1.5
    lease_expiry_seconds: int = 120
    lease_renewal_seconds: int = 30
    breaker_failure_threshold: int = 5
    breaker_cooldown_seconds: int = 60
    compensation_timeout_seconds: int = 300
    artifact_tenant_concurrency: int = 10
    artifact_global_concurrency: int = 100
    require_override_for_unsafe_changes: bool = True
    quotas_enabled: bool = True
    fairness_enabled: bool = True
    recovery_safety_enabled: bool = True
    containment_enabled: bool = True


@dataclass(slots=True, frozen=True)
class ReliabilityPolicy:
    tenant_id: UUID | None
    scope_type: ReliabilityScopeType
    scope_key: str | None
    settings: ReliabilityPolicySettings
    policy_id: UUID = field(default_factory=uuid4)
    policy_version: int = 1
    status: PolicyStatus = PolicyStatus.ACTIVE


@dataclass(slots=True, frozen=True)
class CapacitySnapshot:
    runnable_depth: int = 0
    delayed_depth: int = 0
    active_leases: int = 0
    recovery_backlog: int = 0
    retry_backlog: int = 0
    compensation_backlog: int = 0
    dead_letter_count: int = 0
    db_pool_wait_p95_ms: int = 0
    db_pool_in_use: int = 0
    db_pool_available: int = 1
    artifact_inflight: int = 0
    artifact_wait_p95_ms: int = 0
    open_breaker_count: int = 0
    fairness_debt_total: float = 0.0
    capacity_snapshot_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)


@dataclass(slots=True, frozen=True)
class AdmissionDecision:
    tenant_id: UUID
    decision: AdmissionDecisionKind
    reason_code: str
    policy_id: UUID
    policy_version: int
    workflow_run_id: UUID | None = None
    queue_job_id: UUID | None = None
    available_at: datetime | None = None
    capacity_snapshot_id: UUID | None = None
    trace_id: str | None = None
    admission_decision_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)


@dataclass(slots=True)
class QuotaCounter:
    tenant_id: UUID
    resource_kind: QuotaResourceKind
    limit_value: int
    used_value: int = 0
    window_start: datetime = field(default_factory=now_utc)
    window_end: datetime = field(
        default_factory=lambda: now_utc() + timedelta(minutes=1)
    )

    @property
    def remaining(self) -> int:
        return max(self.limit_value - self.used_value, 0)


@dataclass(slots=True)
class FairnessWindow:
    tenant_id: UUID
    weight: float = 1.0
    allocated_tokens: float = 0.0
    consumed_tokens: float = 0.0
    fairness_debt: float = 0.0
    burst_debt: float = 0.0

    @property
    def available_tokens(self) -> float:
        return self.allocated_tokens - self.consumed_tokens


@dataclass(slots=True, frozen=True)
class WorkerContext:
    tenant_id: UUID
    workflow_run_id: UUID
    worker_id: str
    worker_lease_id: UUID
    claim_attempt: int
    run_bundle_id: UUID
    bundle_digest: str
    trace_id: str
    policy_id: UUID
    policy_version: int
    run_step_id: UUID | None = None
