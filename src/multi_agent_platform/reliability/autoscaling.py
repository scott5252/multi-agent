from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.reliability.models import (
    CapacitySnapshot,
    ScalingDecisionKind,
)


@dataclass(slots=True, frozen=True)
class ScalingDecision:
    decision: ScalingDecisionKind
    current_workers: int
    target_workers: int
    reason_code: str


def recommend_worker_scale(
    *,
    snapshots: list[CapacitySnapshot],
    current_workers: int,
    runnable_per_worker_target: int = 10,
    min_db_pool_available: int = 2,
) -> ScalingDecision:
    if current_workers < 1:
        raise ValueError("current_workers must be positive")
    if not snapshots:
        return ScalingDecision(
            ScalingDecisionKind.HOLD, current_workers, current_workers, "no_snapshots"
        )
    latest = snapshots[-1]
    if latest.db_pool_available < min_db_pool_available or latest.open_breaker_count:
        return ScalingDecision(
            ScalingDecisionKind.BLOCK_SCALE_OUT,
            current_workers,
            current_workers,
            "dependency_or_pool_unhealthy",
        )
    sustained_pressure = all(
        snap.runnable_depth / current_workers > runnable_per_worker_target
        for snap in snapshots[-3:]
    )
    if len(snapshots) >= 3 and sustained_pressure:
        return ScalingDecision(
            ScalingDecisionKind.SCALE_OUT,
            current_workers,
            current_workers + 1,
            "sustained_runnable_depth",
        )
    quiet = all(
        snap.runnable_depth == 0
        and snap.delayed_depth == 0
        and snap.recovery_backlog == 0
        and snap.fairness_debt_total == 0
        for snap in snapshots[-2:]
    )
    if current_workers > 1 and len(snapshots) >= 2 and quiet:
        return ScalingDecision(
            ScalingDecisionKind.SCALE_IN,
            current_workers,
            current_workers - 1,
            "sustained_low_backlog",
        )
    return ScalingDecision(
        ScalingDecisionKind.HOLD, current_workers, current_workers, "within_target"
    )
