from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


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


class ErrorResponse(BaseModel):
    detail: str


class RunStartRequest(BaseModel):
    published_workflow_version_id: UUID
    input: dict[str, Any]
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=128)
    trace_id: str | None = None
    delegated_credential_refs: list[str] = Field(default_factory=list)


class RunStartResponse(BaseModel):
    workflow_run_id: UUID
    status: RunStatus
    run_bundle_id: UUID
    bundle_digest: str
    created_at: datetime


class RunStatusResponse(BaseModel):
    workflow_run_id: UUID
    tenant_id: UUID | None
    status: RunStatus
    bundle_digest: str
    created_at: datetime
    active_step_key: str | None = None
    pause_reason: str | None = None
    current_checkpoint_id: str | None = None
    terminal_reason: str | None = None
    updated_at: datetime | None = None
    finished_at: datetime | None = None


class RunCancelRequest(BaseModel):
    reason: str = Field(min_length=1)
    child_cancellation_override: str = "use_workflow_policy"


class TimelineEvent(BaseModel):
    runtime_timeline_event_id: UUID
    event_type: str
    severity: str
    payload: dict[str, Any]
    trace_id: str
    created_at: datetime


class RunTimelineResponse(BaseModel):
    items: list[TimelineEvent]


class ApprovalDecisionRequest(BaseModel):
    decision: str
    decision_payload: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecisionResponse(BaseModel):
    approval_gate_id: UUID
    approval_decision_id: UUID
    accepted: bool
    status: str
    resume_queued: bool
    rejection_reason: str | None = None


class ApprovalGateResponse(BaseModel):
    approval_gate_id: UUID
    status: str
    approval_key: str
    requested_action: dict[str, Any]
    created_at: datetime


class ApprovalGateListResponse(BaseModel):
    items: list[ApprovalGateResponse]


class HandoffEnvelopeResponse(BaseModel):
    handoff_envelope_id: UUID
    status: str
    receiver_step_key: str
    contract_id: str
    contract_version: str
    contract_digest: str
    validation_errors: list[dict[str, Any]] = Field(default_factory=list)


class HandoffEnvelopeListResponse(BaseModel):
    items: list[HandoffEnvelopeResponse]


class SideEffectIntentResponse(BaseModel):
    side_effect_intent_id: UUID
    status: str
    intent_kind: str
    idempotency_key: str


class SideEffectIntentListResponse(BaseModel):
    items: list[SideEffectIntentResponse]


class LineageNode(BaseModel):
    workflow_run_id: UUID
    status: str
    bundle_digest: str | None = None


class LineageEdge(BaseModel):
    parent_run_id: UUID
    child_run_id: UUID
    parent_step_id: UUID
    join_policy: str
    child_cancellation_policy: str


class RunLineageResponse(BaseModel):
    nodes: list[LineageNode]
    edges: list[LineageEdge]
