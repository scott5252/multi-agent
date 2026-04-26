from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.observability.tracing import model_skill_trace_attributes
from multi_agent_platform.runtime.orchestration.events import (
    RuntimeEventType,
    RuntimeTimelineEvent,
)


def test_model_skill_trace_attributes_include_replay_keys_only_when_present() -> None:
    attributes = model_skill_trace_attributes(
        action="evaluate_tool_use",
        outcome="deny",
        tenant_id="tenant-1",
        workflow_run_id="run-1",
        decision_category="tool",
        resolution_digest="digest",
    )

    assert attributes == {
        "action": "evaluate_tool_use",
        "outcome": "deny",
        "tenant_id": "tenant-1",
        "workflow_run_id": "run-1",
        "decision_category": "tool",
        "resolution_digest": "digest",
    }


def test_runtime_timeline_can_record_model_skill_replay_metadata() -> None:
    event = RuntimeTimelineEvent(
        tenant_id=None,
        workflow_run_id=uuid4(),
        event_type=RuntimeEventType.SIDE_EFFECT,
        trace_id="trace",
        payload={
            "decision_category": "tool",
            "runtime_policy_decision_id": "decision-1",
            "replay_supported": True,
        },
    )

    assert event.payload["replay_supported"] is True
