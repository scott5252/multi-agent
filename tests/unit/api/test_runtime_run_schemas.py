from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.runtime_runs import RunStartRequest


def test_run_start_request_accepts_open_input_payload() -> None:
    request = RunStartRequest(
        published_workflow_version_id=uuid4(),
        idempotency_key="demo-run-001",
        input={"prompt": "hello", "metadata": {"priority": "normal"}},
    )

    assert request.input["metadata"] == {"priority": "normal"}
