from __future__ import annotations

from uuid import UUID

from multi_agent_platform.channels.models import ChannelRun, TerminalOutcome


def terminal_notification_payload(run: ChannelRun) -> dict[str, object]:
    next_actions = ["status"]
    if run.terminal_outcome is TerminalOutcome.COMPLETED:
        next_actions.extend(["result", "artifacts"])
    elif run.terminal_outcome in {TerminalOutcome.FAILED, TerminalOutcome.CANCELED}:
        next_actions.append("result")
    return {
        "run_id": str(run.run_id),
        "terminal_state": run.state.value,
        "summary": run.progress_summary,
        "next_actions": next_actions,
        "trace_id": run.trace_id,
    }


def subscription_key(platform_identity_id: str, channel_session_id: UUID) -> str:
    return f"{platform_identity_id}:{channel_session_id}"
