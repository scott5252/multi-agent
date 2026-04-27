from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


def _now() -> datetime:
    return datetime.now(UTC)


class ReliabilityPolicyStatusRecord(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class ReliabilityDecisionRecord(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    DELAYED = "delayed"
    THROTTLED = "throttled"
    REJECTED = "rejected"
    RETRY_ELIGIBLE = "retry_eligible"


class ReliabilityBreakerStateRecord(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ReliabilityPolicyRecord(Base, TimestampMixin):
    __tablename__ = "reliability_policies"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "scope_type",
            "scope_key",
            "policy_version",
            name="uq_reliability_policy_scope_version",
        ),
    )

    policy_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(64))
    scope_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[ReliabilityPolicyStatusRecord] = mapped_column(
        Enum(ReliabilityPolicyStatusRecord, native_enum=False),
        default=ReliabilityPolicyStatusRecord.ACTIVE,
    )
    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    retired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String(128), default="system")
    created_reason: Mapped[str] = mapped_column(String(255), default="initial")


class AdmissionDecisionRecord(Base):
    __tablename__ = "reliability_admission_decisions"

    admission_decision_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    queue_job_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_id: Mapped[UUID] = mapped_column()
    policy_version: Mapped[int] = mapped_column(Integer)
    decision: Mapped[ReliabilityDecisionRecord] = mapped_column(
        Enum(ReliabilityDecisionRecord, native_enum=False)
    )
    reason_code: Mapped[str] = mapped_column(String(128))
    available_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    capacity_snapshot_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class TenantQuotaCounterRecord(Base, TimestampMixin):
    __tablename__ = "reliability_tenant_quota_counters"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "resource_kind",
            "window_start",
            name="uq_reliability_quota_counter_window",
        ),
    )

    quota_counter_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    resource_kind: Mapped[str] = mapped_column(String(64))
    limit_value: Mapped[int] = mapped_column(Integer)
    used_value: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)


class FairnessWindowRecord(Base, TimestampMixin):
    __tablename__ = "reliability_fairness_windows"

    fairness_window_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    weight: Mapped[int] = mapped_column(Integer, default=1)
    allocated_tokens: Mapped[int] = mapped_column(Integer, default=0)
    consumed_tokens: Mapped[int] = mapped_column(Integer, default=0)
    fairness_debt: Mapped[int] = mapped_column(Integer, default=0)
    burst_debt: Mapped[int] = mapped_column(Integer, default=0)


class CapacitySnapshotRecord(Base):
    __tablename__ = "reliability_capacity_snapshots"

    capacity_snapshot_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    snapshot_scope: Mapped[str] = mapped_column(String(64), default="global")
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    worker_pool: Mapped[str | None] = mapped_column(String(128), nullable=True)
    runnable_depth: Mapped[int] = mapped_column(Integer, default=0)
    delayed_depth: Mapped[int] = mapped_column(Integer, default=0)
    active_leases: Mapped[int] = mapped_column(Integer, default=0)
    recovery_backlog: Mapped[int] = mapped_column(Integer, default=0)
    retry_backlog: Mapped[int] = mapped_column(Integer, default=0)
    compensation_backlog: Mapped[int] = mapped_column(Integer, default=0)
    dead_letter_count: Mapped[int] = mapped_column(Integer, default=0)
    db_pool_wait_p95_ms: Mapped[int] = mapped_column(Integer, default=0)
    db_pool_in_use: Mapped[int] = mapped_column(Integer, default=0)
    db_pool_available: Mapped[int] = mapped_column(Integer, default=0)
    artifact_inflight: Mapped[int] = mapped_column(Integer, default=0)
    artifact_wait_p95_ms: Mapped[int] = mapped_column(Integer, default=0)
    open_breaker_count: Mapped[int] = mapped_column(Integer, default=0)
    fairness_debt_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WorkerPoolScalingDecisionRecord(Base):
    __tablename__ = "reliability_worker_pool_scaling_decisions"

    scaling_decision_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    worker_pool: Mapped[str] = mapped_column(String(128))
    decision: Mapped[str] = mapped_column(String(64))
    current_workers: Mapped[int] = mapped_column(Integer)
    target_workers: Mapped[int] = mapped_column(Integer)
    reason_code: Mapped[str] = mapped_column(String(128))
    capacity_snapshot_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class RetryScheduleRecord(Base, TimestampMixin):
    __tablename__ = "reliability_retry_schedules"

    retry_schedule_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    queue_job_id: Mapped[UUID | None] = mapped_column(nullable=True)
    failure_category: Mapped[str] = mapped_column(String(64))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    next_eligible_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(64), default="scheduled")
    stop_reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)


class CircuitBreakerRecord(Base):
    __tablename__ = "reliability_circuit_breakers"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "scope_type",
            "scope_key",
            name="uq_reliability_breaker_scope",
        ),
    )

    circuit_breaker_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(64))
    scope_key: Mapped[str] = mapped_column(String(255))
    state: Mapped[ReliabilityBreakerStateRecord] = mapped_column(
        Enum(ReliabilityBreakerStateRecord, native_enum=False),
        default=ReliabilityBreakerStateRecord.CLOSED,
    )
    reason_code: Mapped[str] = mapped_column(String(128), default="initial")
    thresholds: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    cooldown_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    probe_required: Mapped[bool] = mapped_column(default=False)
    half_open_tokens: Mapped[int] = mapped_column(Integer, default=0)
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)
    last_transition_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )


class CircuitBreakerEventRecord(Base):
    __tablename__ = "reliability_circuit_breaker_events"

    breaker_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    circuit_breaker_id: Mapped[UUID] = mapped_column(
        ForeignKey("reliability_circuit_breakers.circuit_breaker_id")
    )
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    from_state: Mapped[str] = mapped_column(String(64))
    to_state: Mapped[str] = mapped_column(String(64))
    reason_code: Mapped[str] = mapped_column(String(128))
    probe_result: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    override_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CompensationRequestRecord(Base, TimestampMixin):
    __tablename__ = "reliability_compensation_requests"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "side_effect_intent_id",
            "hook_ref",
            name="uq_reliability_compensation_intent_hook",
        ),
    )

    compensation_request_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    workflow_run_id: Mapped[UUID] = mapped_column()
    run_step_id: Mapped[UUID] = mapped_column()
    side_effect_intent_id: Mapped[UUID] = mapped_column()
    hook_ref: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64), default="requested")
    retry_schedule_id: Mapped[UUID | None] = mapped_column(nullable=True)
    dead_letter_id: Mapped[UUID | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class DeadLetterRecordModel(Base, TimestampMixin):
    __tablename__ = "reliability_dead_letters"

    dead_letter_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    source_kind: Mapped[str] = mapped_column(String(64))
    source_id: Mapped[UUID] = mapped_column()
    failure_category: Mapped[str] = mapped_column(String(64))
    latest_state: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    recommended_action: Mapped[str] = mapped_column(String(64))
    artifact_refs: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(64), default="open")
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class OperationalControlChangeRecord(Base):
    __tablename__ = "reliability_operational_control_changes"

    control_change_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    actor_id: Mapped[str] = mapped_column(String(128))
    actor_role: Mapped[str] = mapped_column(String(64))
    scope_type: Mapped[str] = mapped_column(String(64))
    scope_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    previous_value: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    new_value: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    validation_outcome: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ArtifactThroughputWindowRecord(Base, TimestampMixin):
    __tablename__ = "reliability_artifact_throughput_windows"

    artifact_window_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    operation_kind: Mapped[str] = mapped_column(String(64))
    inflight_count: Mapped[int] = mapped_column(Integer, default=0)
    limit_value: Mapped[int] = mapped_column(Integer)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    policy_id: Mapped[UUID | None] = mapped_column(nullable=True)
    policy_version: Mapped[int] = mapped_column(Integer, default=1)


class FailureInjectionRecord(Base):
    __tablename__ = "reliability_failure_injection_records"

    failure_injection_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    injection_point: Mapped[str] = mapped_column(String(128))
    seed: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
