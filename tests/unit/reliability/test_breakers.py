from __future__ import annotations

from datetime import timedelta

from multi_agent_platform.reliability.breakers import (
    CircuitBreaker,
    allow_protected_work,
    maybe_enter_half_open,
    record_failure,
    record_success,
    reset_breaker,
)
from multi_agent_platform.reliability.models import BreakerState, now_utc


def test_breaker_opens_cools_down_and_closes_after_probe_success() -> None:
    breaker = CircuitBreaker(scope_key="model-api", failure_threshold=1)
    record_failure(breaker)
    assert breaker.state is BreakerState.OPEN
    breaker.cooldown_until = now_utc() - timedelta(seconds=1)
    assert maybe_enter_half_open(breaker, probe_success=True) is BreakerState.HALF_OPEN
    assert allow_protected_work(breaker)
    assert record_success(breaker) is BreakerState.CLOSED


def test_breaker_reset_requires_actor_and_reason() -> None:
    breaker = CircuitBreaker(scope_key="model-api", state=BreakerState.OPEN)
    reset_breaker(breaker, actor_id="admin", reason="dependency recovered")
    assert breaker.state is BreakerState.CLOSED
