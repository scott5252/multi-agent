from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.models import now_utc


class TimelineSeverity(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RuntimeEventType(StrEnum):
    START = "start"
    BUNDLE_PIN = "bundle_pin"
    CLAIM = "claim"
    RENEW = "renew"
    CHECKPOINT = "checkpoint"
    HANDOFF = "handoff"
    SIDE_EFFECT = "side_effect"
    APPROVAL = "approval"
    CHILD_RUN = "child_run"
    RETRY = "retry"
    COMPENSATION = "compensation"
    CANCEL = "cancel"
    TERMINAL = "terminal"
    RETENTION = "retention"


@dataclass(slots=True, frozen=True)
class RuntimeTimelineEvent:
    tenant_id: UUID | None
    workflow_run_id: UUID
    event_type: RuntimeEventType
    trace_id: str
    run_step_id: UUID | None = None
    severity: TimelineSeverity = TimelineSeverity.INFO
    payload: dict[str, object] = field(default_factory=dict)
    runtime_timeline_event_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)


def runtime_audit_action(event_type: RuntimeEventType) -> str:
    return f"runtime.{event_type.value}"


def lifecycle_audit_category(event_type: RuntimeEventType) -> str:
    mapping = {
        RuntimeEventType.START: "started",
        RuntimeEventType.CLAIM: "queued",
        RuntimeEventType.CHECKPOINT: "runtime_decision",
        RuntimeEventType.HANDOFF: "agent_handoff",
        RuntimeEventType.SIDE_EFFECT: "tool_usage",
        RuntimeEventType.APPROVAL: "waiting",
        RuntimeEventType.RETRY: "retried",
        RuntimeEventType.CANCEL: "cancelled",
        RuntimeEventType.TERMINAL: "completed",
    }
    return mapping.get(event_type, "runtime_decision")


def audit_safe_details(event: RuntimeTimelineEvent) -> dict[str, object]:
    return {
        "event_type": event.event_type.value,
        "severity": event.severity.value,
        "payload_field_count": len(event.payload),
        "runtime_timeline_event_id": str(event.runtime_timeline_event_id),
    }
