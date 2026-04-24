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
