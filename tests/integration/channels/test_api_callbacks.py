from __future__ import annotations

from multi_agent_platform.channels.callbacks import sign_callback_payload


def test_callback_payload_signature_includes_event_and_trace() -> None:
    payload = {
        "event_id": "event-1",
        "run_id": "run-1",
        "trace_id": "trace-1",
        "state": "completed",
    }

    assert sign_callback_payload(payload, "secret")
