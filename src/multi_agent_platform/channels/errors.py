from __future__ import annotations

from http import HTTPStatus

from multi_agent_platform.channels.models import ErrorCategory

ERROR_STATUS: dict[ErrorCategory, int] = {
    ErrorCategory.UNAUTHORIZED: HTTPStatus.FORBIDDEN,
    ErrorCategory.MISSING_INPUT: HTTPStatus.BAD_REQUEST,
    ErrorCategory.INVALID_RUN_ID: HTTPStatus.NOT_FOUND,
    ErrorCategory.UNAVAILABLE_CHANNEL_DELIVERY: HTTPStatus.SERVICE_UNAVAILABLE,
    ErrorCategory.INVALID_LIFECYCLE_ACTION: HTTPStatus.CONFLICT,
    ErrorCategory.IDEMPOTENCY_CONFLICT: HTTPStatus.CONFLICT,
    ErrorCategory.RATE_LIMITED: HTTPStatus.TOO_MANY_REQUESTS,
    ErrorCategory.ARTIFACT_UNAVAILABLE: HTTPStatus.NOT_FOUND,
    ErrorCategory.CALLBACK_DELIVERY_FAILED: HTTPStatus.BAD_GATEWAY,
    ErrorCategory.PLATFORM_FAILURE: HTTPStatus.INTERNAL_SERVER_ERROR,
}

DEFAULT_MESSAGES: dict[ErrorCategory, str] = {
    ErrorCategory.UNAUTHORIZED: (
        "The authenticated user is not authorized for this action."
    ),
    ErrorCategory.MISSING_INPUT: "Required channel input is missing or invalid.",
    ErrorCategory.INVALID_RUN_ID: "The run could not be found for this tenant.",
    ErrorCategory.UNAVAILABLE_CHANNEL_DELIVERY: (
        "The channel cannot deliver this message right now."
    ),
    ErrorCategory.INVALID_LIFECYCLE_ACTION: (
        "The run is not in a state that accepts this action."
    ),
    ErrorCategory.IDEMPOTENCY_CONFLICT: (
        "The idempotency key was reused with different input."
    ),
    ErrorCategory.RATE_LIMITED: "This channel action is temporarily rate limited.",
    ErrorCategory.ARTIFACT_UNAVAILABLE: "The requested artifact is unavailable.",
    ErrorCategory.CALLBACK_DELIVERY_FAILED: "The callback could not be delivered.",
    ErrorCategory.PLATFORM_FAILURE: (
        "The platform could not complete the channel action."
    ),
}


class ChannelError(RuntimeError):
    def __init__(
        self,
        category: ErrorCategory,
        message: str | None = None,
        *,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message or DEFAULT_MESSAGES[category])
        self.category = category
        self.message = message or DEFAULT_MESSAGES[category]
        self.trace_id = trace_id

    @property
    def status_code(self) -> int:
        return int(ERROR_STATUS[self.category])


def telegram_error_message(category: ErrorCategory) -> str:
    messages = {
        ErrorCategory.UNAUTHORIZED: "I could not verify access to that run.",
        ErrorCategory.MISSING_INPUT: "I need more information before I can do that.",
        ErrorCategory.INVALID_RUN_ID: "I could not find that run for your account.",
        ErrorCategory.INVALID_LIFECYCLE_ACTION: (
            "That run is no longer waiting for this action."
        ),
        ErrorCategory.RATE_LIMITED: "That action is temporarily rate limited.",
        ErrorCategory.PLATFORM_FAILURE: (
            "The platform could not complete that action. Try again with the run id."
        ),
    }
    return messages.get(category, DEFAULT_MESSAGES[category])
