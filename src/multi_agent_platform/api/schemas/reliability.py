from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.reliability.models import (
    AdmissionDecisionKind,
    BreakerState,
    CompensationStatus,
    DeadLetterStatus,
    RecommendedAction,
)


class ReliabilityDashboard(BaseModel):
    tenant_id: UUID | None = None
    status: str = "available"
    runnable_depth: int = 0
    delayed_depth: int = 0
    active_leases: int = 0
    retry_backlog: int = 0
    compensation_backlog: int = 0
    dead_letter_count: int = 0
    db_pool_wait_p95_ms: int = 0
    open_breaker_count: int = 0
    partial: bool = False
    redacted: bool = False


class ReliabilityPolicy(BaseModel):
    policy_id: UUID
    tenant_id: UUID | None = None
    scope_type: str
    scope_key: str | None = None
    policy_version: int
    settings: dict[str, object] = Field(default_factory=dict)
    status: str
    effective_at: datetime | None = None


class PolicyChangeRequest(BaseModel):
    tenant_id: UUID | None = None
    scope_type: str
    scope_key: str | None = None
    settings: dict[str, object] = Field(default_factory=dict)
    reason: str
    unsafe_override: bool = False


class OperationalControlChange(BaseModel):
    control_change_id: UUID
    tenant_id: UUID | None = None
    policy_id: UUID | None = None
    actor_id: str
    actor_role: str
    scope_type: str
    scope_key: str | None = None
    validation_outcome: str


class AdmissionDecision(BaseModel):
    admission_decision_id: UUID
    tenant_id: UUID
    workflow_run_id: UUID | None = None
    queue_job_id: UUID | None = None
    decision: AdmissionDecisionKind
    reason_code: str
    available_at: datetime | None = None
    trace_id: str | None = None
    created_at: datetime


class CircuitBreaker(BaseModel):
    circuit_breaker_id: UUID
    tenant_id: UUID | None = None
    scope_type: str
    scope_key: str
    state: BreakerState
    reason_code: str
    cooldown_until: datetime | None = None
    half_open_tokens: int = 0


class BreakerResetRequest(BaseModel):
    reason: str
    target_state: BreakerState = BreakerState.CLOSED
    probe_result: dict[str, object] | None = None


class RetrySchedule(BaseModel):
    retry_schedule_id: UUID
    tenant_id: UUID
    workflow_run_id: UUID | None = None
    run_step_id: UUID | None = None
    failure_category: str
    attempt_count: int
    max_attempts: int
    next_eligible_at: datetime | None = None
    status: str
    stop_reason: str | None = None


class CompensationRequest(BaseModel):
    compensation_request_id: UUID
    tenant_id: UUID
    workflow_run_id: UUID
    run_step_id: UUID
    side_effect_intent_id: UUID
    hook_ref: str
    status: CompensationStatus


class DeadLetterRecord(BaseModel):
    dead_letter_id: UUID
    tenant_id: UUID
    source_kind: str
    source_id: UUID
    failure_category: str
    latest_state: dict[str, object]
    recommended_action: RecommendedAction
    artifact_refs: list[dict[str, object]] = Field(default_factory=list)
    status: DeadLetterStatus


class LoadTestReport(BaseModel):
    report_id: UUID
    profile: str
    seed: int
    tenant_count: int
    active_users: int
    artifact_ref: str
    accepted_throughput_retention: float


class ListResponse[T](BaseModel):
    items: list[T] = Field(default_factory=list)
