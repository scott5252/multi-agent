from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.events import (
    RuntimeEventType,
    RuntimeTimelineEvent,
    TimelineSeverity,
    runtime_audit_action,
)


def test_runtime_timeline_event_defaults_are_operator_readable() -> None:
    tenant_id = uuid4()
    workflow_run_id = uuid4()

    event = RuntimeTimelineEvent(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        event_type=RuntimeEventType.CHECKPOINT,
        trace_id="trace-runtime",
        payload={"checkpoint_id": "checkpoint-1"},
    )

    assert event.tenant_id == tenant_id
    assert event.workflow_run_id == workflow_run_id
    assert event.severity is TimelineSeverity.INFO
    assert event.payload == {"checkpoint_id": "checkpoint-1"}
    assert event.runtime_timeline_event_id is not None
    assert event.created_at.tzinfo is not None


def test_runtime_audit_action_uses_stable_namespace() -> None:
    assert runtime_audit_action(RuntimeEventType.APPROVAL) == "runtime.approval"
