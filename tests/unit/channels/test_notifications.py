from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.channels.models import (
    ChannelRun,
    ChannelType,
    TerminalOutcome,
    UserVisibleRunState,
)
from multi_agent_platform.channels.notifications import (
    subscription_key,
    terminal_notification_payload,
)


def test_terminal_notification_payload_is_redacted_and_actionable() -> None:
    run = ChannelRun(
        run_id=uuid4(),
        tenant_id=None,
        requester_identity_id="user-1",
        channel_type=ChannelType.WEB_API,
        trace_id="trace-1",
        state=UserVisibleRunState.COMPLETED,
        terminal_outcome=TerminalOutcome.COMPLETED,
        progress_summary="Completed without embedding raw result.",
    )

    payload = terminal_notification_payload(run)

    assert payload["terminal_state"] == "completed"
    assert "artifacts" in payload["next_actions"]
    assert "raw" not in payload
    assert subscription_key("user-1", uuid4()).startswith("user-1:")
