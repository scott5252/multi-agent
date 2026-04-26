from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.api.schemas.audit_debugging import (
    RunReplayResponse,
    RunTimelineResponse,
)


def test_run_timeline_schema_parses_contract_shape() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    event_id = uuid4()
    now = datetime.now(UTC)
    model = RunTimelineResponse.model_validate(
        {
            "run": {
                "workflow_run_id": run_id,
                "tenant_id": tenant_id,
                "status": "completed",
                "trace_id": "trace",
            },
            "events": [
                {
                    "timeline_event_id": event_id,
                    "sequence": 1,
                    "event_category": "completed",
                    "run_status_after": "completed",
                    "trace_id": "trace",
                    "occurred_at": now,
                    "recorded_at": now,
                    "safe_summary": "Run completed",
                }
            ],
            "lineage": {"nodes": [], "edges": []},
            "bundle": None,
            "notifications": [],
            "capture_gaps": [],
        }
    )
    assert model.events[0].timeline_event_id == event_id


def test_replay_schema_parses_events() -> None:
    run_id = uuid4()
    model = RunReplayResponse.model_validate(
        {
            "workflow_run_id": run_id,
            "tenant_id": None,
            "events": [
                {
                    "sequence": 1,
                    "timestamp": datetime.now(UTC),
                    "event_category": "started",
                    "status_after": "running",
                    "trace_id": "trace",
                    "actor": "system",
                    "safe_summary": "Run started",
                    "linked_trace_count": 0,
                    "checkpoint": True,
                }
            ],
        }
    )
    assert model.workflow_run_id == run_id
