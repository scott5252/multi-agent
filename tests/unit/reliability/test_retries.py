from __future__ import annotations

from datetime import timedelta

from multi_agent_platform.reliability.models import (
    BreakerState,
    FailureCategory,
    RetryScheduleStatus,
    now_utc,
)
from multi_agent_platform.reliability.retries import classify_failure, decide_retry


def test_retry_classifier_and_stop_reasons() -> None:
    assert (
        classify_failure("dependency unavailable")
        is FailureCategory.DEPENDENCY_UNAVAILABLE
    )
    stopped = decide_retry(
        failure_category=FailureCategory.AUTHORIZATION,
        attempt_count=0,
        max_attempts=3,
        tenant_retry_budget_remaining=10,
        breaker_state=BreakerState.CLOSED,
        deadline_at=now_utc() + timedelta(minutes=5),
    )
    assert stopped.status is RetryScheduleStatus.STOPPED
    assert stopped.stop_reason == "non_retryable"


def test_retry_schedules_retryable_failure() -> None:
    scheduled = decide_retry(
        failure_category=FailureCategory.TIMEOUT,
        attempt_count=1,
        max_attempts=3,
        tenant_retry_budget_remaining=10,
        breaker_state=BreakerState.CLOSED,
        deadline_at=now_utc() + timedelta(minutes=5),
    )
    assert scheduled.status is RetryScheduleStatus.SCHEDULED
    assert scheduled.next_eligible_at is not None
