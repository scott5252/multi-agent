from __future__ import annotations

import pytest

from multi_agent_platform.reliability.breakers import CircuitBreaker, record_failure
from multi_agent_platform.reliability.models import BreakerState


@pytest.mark.performance
def test_retry_storm_opens_breaker() -> None:
    breaker = CircuitBreaker(scope_key="dependency", failure_threshold=1)
    assert record_failure(breaker) is BreakerState.OPEN
