from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PoolPressure:
    wait_p95_ms: int
    in_use: int
    available: int
    reserve_fraction: float = 0.2


def has_connection_reserve(pressure: PoolPressure) -> bool:
    total = pressure.in_use + pressure.available
    if total <= 0:
        return False
    return pressure.available / total >= pressure.reserve_fraction


def should_delay_for_pool_pressure(
    pressure: PoolPressure, *, max_wait_p95_ms: int = 250
) -> bool:
    return pressure.wait_p95_ms > max_wait_p95_ms or not has_connection_reserve(
        pressure
    )
