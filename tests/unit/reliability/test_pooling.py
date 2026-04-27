from __future__ import annotations

from multi_agent_platform.reliability.pooling import (
    PoolPressure,
    has_connection_reserve,
    should_delay_for_pool_pressure,
)


def test_pool_pressure_preserves_connection_reserve() -> None:
    healthy = PoolPressure(wait_p95_ms=10, in_use=8, available=2)
    exhausted = PoolPressure(wait_p95_ms=300, in_use=10, available=0)
    assert has_connection_reserve(healthy)
    assert should_delay_for_pool_pressure(exhausted)
