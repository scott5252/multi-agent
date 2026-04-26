from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.channel_runs import (
    CallbackRegistrationRequest,
    NotificationSubscriptionRequest,
    RunInvocationRequest,
    RunStatusResponse,
)


def test_run_invocation_schema_defaults_to_web_api_channel() -> None:
    request = RunInvocationRequest(
        workflow_id="published-demo",
        inputs={"topic": "schema"},
    )

    assert request.channel == "web_api"
    assert request.inputs["topic"] == "schema"


def test_run_status_schema_uses_exact_user_visible_state() -> None:
    response = RunStatusResponse(
        run_id=uuid4(),
        state="queued",
        progress_summary="Queued",
        latest_timeline_cursor="1",
        permitted_actions=("status",),
        trace_id="trace-1",
    )

    assert response.state == "queued"
    assert response.terminal_outcome == "none"


def test_subscription_and_callback_event_types_are_validated() -> None:
    with pytest.raises(ValidationError):
        NotificationSubscriptionRequest(channel="web_api", event_types=("progress",))

    with pytest.raises(ValidationError):
        CallbackRegistrationRequest(
            callback_url="https://example.test",
            event_types=("unknown",),
        )
