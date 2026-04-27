from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from multi_agent_platform.reliability.models import (
    RETRYABLE_FAILURES,
    BreakerState,
    FailureCategory,
    RetryScheduleStatus,
    now_utc,
)


@dataclass(slots=True, frozen=True)
class RetryDecision:
    status: RetryScheduleStatus
    next_eligible_at: datetime | None
    stop_reason: str | None


def classify_failure(error_code: str) -> FailureCategory:
    normalized = error_code.lower()
    if "timeout" in normalized:
        return FailureCategory.TIMEOUT
    if "rate" in normalized:
        return FailureCategory.RATE_LIMITED
    if "auth" in normalized or "forbidden" in normalized:
        return FailureCategory.AUTHORIZATION
    if "artifact" in normalized or "storage" in normalized:
        return FailureCategory.ARTIFACT_UNAVAILABLE
    if "dependency" in normalized or "unavailable" in normalized:
        return FailureCategory.DEPENDENCY_UNAVAILABLE
    return FailureCategory.UNKNOWN


def full_jitter_delay(
    *, attempt_count: int, base_seconds: float = 1.0, cap_seconds: float = 60.0
) -> float:
    if attempt_count < 0:
        raise ValueError("attempt_count cannot be negative")
    upper = min(cap_seconds, base_seconds * (2**attempt_count))
    return random.uniform(0, upper)


def decide_retry(
    *,
    failure_category: FailureCategory,
    attempt_count: int,
    max_attempts: int,
    tenant_retry_budget_remaining: int,
    breaker_state: BreakerState,
    deadline_at: datetime,
    now: datetime | None = None,
) -> RetryDecision:
    current = now or now_utc()
    if failure_category not in RETRYABLE_FAILURES:
        return RetryDecision(RetryScheduleStatus.STOPPED, None, "non_retryable")
    if breaker_state is BreakerState.OPEN:
        return RetryDecision(RetryScheduleStatus.STOPPED, None, "breaker_open")
    if tenant_retry_budget_remaining <= 0:
        return RetryDecision(
            RetryScheduleStatus.STOPPED,
            None,
            "retry_budget_exhausted",
        )
    if attempt_count >= max_attempts:
        return RetryDecision(
            RetryScheduleStatus.STOPPED,
            None,
            "max_attempts_exhausted",
        )
    next_at = current + timedelta(
        seconds=full_jitter_delay(attempt_count=attempt_count)
    )
    if next_at > deadline_at:
        return RetryDecision(RetryScheduleStatus.STOPPED, None, "deadline_exhausted")
    return RetryDecision(RetryScheduleStatus.SCHEDULED, next_at, None)
