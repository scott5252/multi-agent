from __future__ import annotations

from datetime import UTC, datetime

from multi_agent_platform.audit.inspection import assemble_replay_events


def test_replay_assembly_is_ordered_immutable_view_without_side_effects() -> None:
    events = [
        {
            "sequence": 1,
            "occurred_at": datetime.now(UTC),
            "event_category": "started",
            "run_status_after": "running",
            "trace_id": "trace",
            "safe_summary": "started",
            "traces": [{}],
        }
    ]
    replay = assemble_replay_events(events)
    assert replay == [
        {
            "sequence": 1,
            "timestamp": events[0]["occurred_at"],
            "event_category": "started",
            "status_after": "running",
            "trace_id": "trace",
            "actor": "system",
            "safe_summary": "started",
            "linked_trace_count": 1,
            "checkpoint": True,
        }
    ]
