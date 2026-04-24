from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


def now_utc() -> datetime:
    return datetime.now(UTC)


class RunStatus(StrEnum):
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


TERMINAL_RUN_STATUSES = {
    RunStatus.CANCELLED,
    RunStatus.SUCCEEDED,
    RunStatus.FAILED,
}


class RunStepStatus(StrEnum):
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


class StepType(StrEnum):
    AGENT = "agent"
    HANDOFF = "handoff"
    SUBWORKFLOW = "subworkflow"
    APPROVAL = "approval"
    TOOL = "tool"
    COMPENSATION = "compensation"
    SYSTEM = "system"


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    jitter_seconds: float = 0.1

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


@dataclass(slots=True, frozen=True)
class RuntimeExecutionBundle:
    tenant_id: UUID | None
    workflow_run_id: UUID
    published_workflow_version_id: UUID
    bundle_digest: str
    workflow_version: dict[str, object] = field(default_factory=dict)
    contract_versions: dict[str, object] = field(default_factory=dict)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    checkpoint_policy: dict[str, object] = field(default_factory=dict)
    approval_timeout_policy: dict[str, object] = field(default_factory=dict)
    child_cancellation_policy: str = "cascade_cancel"
    run_bundle_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)

    def assert_digest(self, digest: str) -> None:
        if digest != self.bundle_digest:
            raise ValueError("bundle digest mismatch")


@dataclass(slots=True)
class WorkflowRun:
    tenant_id: UUID | None
    scope_type: str
    initiating_principal_id: str
    run_bundle_id: UUID
    bundle_digest: str
    idempotency_key: str
    trace_id: str
    workflow_run_id: UUID = field(default_factory=uuid4)
    status: RunStatus = RunStatus.PENDING
    current_step_id: UUID | None = None
    current_checkpoint_id: str | None = None
    pause_reason: str | None = None
    terminal_reason: str | None = None
    created_at: datetime = field(default_factory=now_utc)
    started_at: datetime | None = None
    updated_at: datetime = field(default_factory=now_utc)
    finished_at: datetime | None = None

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_RUN_STATUSES

    def transition(self, status: RunStatus, *, reason: str | None = None) -> None:
        if self.is_terminal:
            raise ValueError("terminal runs cannot be mutated")
        self.status = status
        self.updated_at = now_utc()
        if status is RunStatus.RUNNING and self.started_at is None:
            self.started_at = self.updated_at
        if status in TERMINAL_RUN_STATUSES:
            self.terminal_reason = reason
            self.finished_at = self.updated_at


@dataclass(slots=True)
class RunStep:
    workflow_run_id: UUID
    tenant_id: UUID | None
    step_key: str
    step_type: StepType
    max_attempts: int = 3
    run_step_id: UUID = field(default_factory=uuid4)
    status: RunStepStatus = RunStepStatus.PENDING
    attempt: int = 0
    next_retry_at: datetime | None = None
    input_ref: dict[str, object] | None = None
    output_ref: dict[str, object] | None = None
    error_ref: dict[str, object] | None = None
    checkpoint_before_id: str | None = None
    checkpoint_after_id: str | None = None
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)
    finished_at: datetime | None = None

    def record_attempt(self) -> int:
        if self.attempt >= self.max_attempts:
            raise ValueError("retry budget exhausted")
        self.attempt += 1
        self.updated_at = now_utc()
        return self.attempt
