from __future__ import annotations

from multi_agent_platform.channels.errors import ChannelError, telegram_error_message
from multi_agent_platform.channels.models import ErrorCategory


def test_channel_error_carries_status_and_safe_message() -> None:
    error = ChannelError(ErrorCategory.IDEMPOTENCY_CONFLICT, trace_id="trace-1")

    assert error.status_code == 409
    assert error.category == ErrorCategory.IDEMPOTENCY_CONFLICT
    assert error.trace_id == "trace-1"


def test_telegram_error_messages_are_concise() -> None:
    assert "could not find" in telegram_error_message(ErrorCategory.INVALID_RUN_ID)
    assert "temporarily rate limited" in telegram_error_message(
        ErrorCategory.RATE_LIMITED
    )
