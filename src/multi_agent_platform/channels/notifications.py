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


def notification_audit_summary(
    *,
    destination_category: str,
    delivery_status: str,
    attempt_count: int,
    provider_correlation_ref: str | None = None,
    safe_failure_reason: str | None = None,
) -> dict[str, object]:
    return {
        "destination_category": destination_category,
        "delivery_status": delivery_status,
        "attempt_count": attempt_count,
        "provider_correlation_ref": provider_correlation_ref,
        "safe_failure_reason": safe_failure_reason,
    }
