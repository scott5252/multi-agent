from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.channels.adapters import ChannelAdapter
from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelRun,
    ChannelType,
    TerminalOutcome,
    UserVisibleRunState,
)
from multi_agent_platform.channels.notifications import (
    notification_audit_summary,
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


def test_terminal_failure_notifications_and_adapter_contract_are_safe() -> None:
    class WebApiAdapter:
        channel_type = ChannelType.WEB_API

        def actor(self) -> ChannelActor:
            return ChannelActor(
                tenant_id=None,
                platform_identity_id="user-1",
                channel_type=self.channel_type,
                trace_id="trace-1",
            )

    adapter: ChannelAdapter = WebApiAdapter()
    actor = adapter.actor()
    run = ChannelRun(
        run_id=uuid4(),
        tenant_id=actor.tenant_id,
        requester_identity_id=actor.platform_identity_id,
        channel_type=adapter.channel_type,
        trace_id=actor.trace_id,
        state=UserVisibleRunState.FAILED,
        terminal_outcome=TerminalOutcome.FAILED,
        progress_summary="Failed with a safe summary.",
    )

    payload = terminal_notification_payload(run)
    audit_summary = notification_audit_summary(
        destination_category="webhook",
        delivery_status="failed",
        attempt_count=2,
        safe_failure_reason="timeout",
    )

    assert payload["next_actions"] == ["status", "result"]
    assert audit_summary["safe_failure_reason"] == "timeout"
