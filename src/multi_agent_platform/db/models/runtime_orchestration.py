from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


def _retention_default() -> datetime:
    return datetime.now(UTC) + timedelta(days=90)


class RuntimeRunStatus(StrEnum):
    PENDING = "pending"
    RUNNABLE = "runnable"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_CHILD = "waiting_child"
    RECOVERABLE_FAILED = "recoverable_failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RuntimeStepStatus(StrEnum):
    PENDING = "pending"
    RUNNABLE = "runnable"
    LEASED = "leased"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_CHILD = "waiting_child"
    RETRY_SCHEDULED = "retry_scheduled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPENSATED = "compensated"


class RuntimeWorkerLeaseStatus(StrEnum):
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    COMPLETED = "completed"
    LOST = "lost"


class RuntimeHandoffStatus(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    CONSUMED = "consumed"
    FAILED_ROUTE_APPLIED = "failed_route_applied"


class RuntimeSideEffectStatus(StrEnum):
    PLANNED = "planned"
    EXECUTING = "executing"
    APPLIED = "applied"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    CANCELLED = "cancelled"


class RuntimeApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class RuntimeExecutionBundleRecord(Base):
    __tablename__ = "runtime_execution_bundles"
    __table_args__ = (UniqueConstraint("workflow_run_id"),)

    run_bundle_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(unique=True)
    published_workflow_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_version_bundles.workflow_version_bundle_id")
    )
    bundle_digest: Mapped[str] = mapped_column(String(64))
    workflow_version: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    subworkflow_versions: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    contract_versions: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    prompt_versions: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    model_config_versions: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    tool_policy_versions: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    retry_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    checkpoint_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    approval_timeout_policy: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    child_cancellation_policy: Mapped[str] = mapped_column(
        String(64), default="cascade_cancel"
    )
    compiled_graph_ref: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class WorkflowRunRecord(Base, TimestampMixin):
    __tablename__ = "runtime_workflow_runs"

    workflow_run_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    initiating_principal_id: Mapped[str] = mapped_column(String(128))
    run_bundle_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_execution_bundles.run_bundle_id")
    )
    status: Mapped[RuntimeRunStatus] = mapped_column(
        Enum(RuntimeRunStatus, native_enum=False), default=RuntimeRunStatus.PENDING
    )
    current_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    current_checkpoint_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    pause_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    terminal_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    trace_id: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RunStepRecord(Base, TimestampMixin):
    __tablename__ = "runtime_run_steps"
    __table_args__ = (UniqueConstraint("workflow_run_id", "step_key", "attempt"),)

    run_step_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    step_key: Mapped[str] = mapped_column(String(128))
    step_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[RuntimeStepStatus] = mapped_column(
        Enum(RuntimeStepStatus, native_enum=False), default=RuntimeStepStatus.PENDING
    )
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    input_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    output_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    error_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    checkpoint_before_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    checkpoint_after_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class WorkerLeaseRecord(Base):
    __tablename__ = "runtime_worker_leases"

    worker_lease_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    run_step_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("runtime_run_steps.run_step_id"), nullable=True
    )
    worker_id: Mapped[str] = mapped_column(String(128))
    lease_status: Mapped[RuntimeWorkerLeaseStatus] = mapped_column(
        Enum(RuntimeWorkerLeaseStatus, native_enum=False),
        default=RuntimeWorkerLeaseStatus.ACTIVE,
    )
    claimed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_renewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    claim_attempt: Mapped[int] = mapped_column(Integer, default=1)


class RuntimeCheckpointRefRecord(Base):
    __tablename__ = "runtime_checkpoint_refs"

    runtime_checkpoint_ref_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    langgraph_thread_id: Mapped[str] = mapped_column(String(128))
    langgraph_checkpoint_id: Mapped[str] = mapped_column(String(128))
    checkpoint_kind: Mapped[str] = mapped_column(String(64))
    bundle_digest: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    retention_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=_retention_default, nullable=True
    )


class HandoffEnvelopeRecord(Base):
    __tablename__ = "runtime_handoff_envelopes"

    handoff_envelope_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    sender_step_id: Mapped[UUID] = mapped_column()
    receiver_step_key: Mapped[str] = mapped_column(String(128))
    contract_id: Mapped[str] = mapped_column(String(128))
    contract_version: Mapped[str] = mapped_column(String(64))
    contract_digest: Mapped[str] = mapped_column(String(64))
    status: Mapped[RuntimeHandoffStatus] = mapped_column(
        Enum(RuntimeHandoffStatus, native_enum=False),
        default=RuntimeHandoffStatus.CREATED,
    )
    payload_hash: Mapped[str] = mapped_column(String(64))
    payload_ref: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    validation_errors: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    validated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class SideEffectIntentRecord(Base, TimestampMixin):
    __tablename__ = "runtime_side_effect_intents"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "workflow_run_id", "run_step_id", "idempotency_key"
        ),
    )

    side_effect_intent_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    run_step_id: Mapped[UUID] = mapped_column()
    intent_kind: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    status: Mapped[RuntimeSideEffectStatus] = mapped_column(
        Enum(RuntimeSideEffectStatus, native_enum=False),
        default=RuntimeSideEffectStatus.PLANNED,
    )
    tool_policy_ref: Mapped[str] = mapped_column(String(255))
    delegated_credential_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    request_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    result_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    error_ref: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    compensation_hook_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ApprovalGateRecord(Base):
    __tablename__ = "runtime_approval_gates"

    approval_gate_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_workflow_runs.workflow_run_id", ondelete="CASCADE")
    )
    run_step_id: Mapped[UUID] = mapped_column()
    status: Mapped[RuntimeApprovalStatus] = mapped_column(
        Enum(RuntimeApprovalStatus, native_enum=False),
        default=RuntimeApprovalStatus.PENDING,
    )
    approval_key: Mapped[str] = mapped_column(String(128))
    requested_action: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    approver_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    timeout_behavior: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    decision_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ApprovalDecisionRecord(Base):
    __tablename__ = "runtime_approval_decisions"

    approval_decision_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    approval_gate_id: Mapped[UUID] = mapped_column(
        ForeignKey("runtime_approval_gates.approval_gate_id", ondelete="CASCADE")
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    principal_id: Mapped[str] = mapped_column(String(128))
    decision: Mapped[str] = mapped_column(String(32))
    decision_payload_hash: Mapped[str] = mapped_column(String(64))
    decision_payload_ref: Mapped[dict[str, object] | None] = mapped_column(
        JSON, nullable=True
    )
    accepted: Mapped[bool]
    rejection_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class RunLineageRecord(Base):
    __tablename__ = "runtime_run_lineage"

    run_lineage_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    parent_run_id: Mapped[UUID] = mapped_column()
    parent_step_id: Mapped[UUID] = mapped_column()
    child_run_id: Mapped[UUID] = mapped_column()
    relationship_reason: Mapped[str] = mapped_column(String(64), default="subworkflow")
    join_policy: Mapped[str] = mapped_column(String(64), default="wait_all")
    child_cancellation_policy: Mapped[str] = mapped_column(
        String(64), default="cascade_cancel"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RuntimeTimelineEventRecord(Base):
    __tablename__ = "runtime_timeline_events"

    runtime_timeline_event_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column()
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32), default="info")
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    trace_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class RuntimeRetentionPolicyRecord(Base, TimestampMixin):
    __tablename__ = "runtime_retention_policies"

    runtime_retention_policy_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True, unique=True
    )
    checkpoint_retention_days: Mapped[int] = mapped_column(Integer, default=90)
    run_payload_ref_retention_days: Mapped[int] = mapped_column(Integer, default=90)
    audit_retention: Mapped[str] = mapped_column(String(32), default="indefinite")
    lineage_retention: Mapped[str] = mapped_column(String(32), default="indefinite")
