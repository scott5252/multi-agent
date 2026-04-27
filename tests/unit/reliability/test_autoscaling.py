from __future__ import annotations

from multi_agent_platform.reliability.autoscaling import recommend_worker_scale
from multi_agent_platform.reliability.models import (
    CapacitySnapshot,
    ScalingDecisionKind,
)


def test_autoscaling_blocks_scale_out_when_pool_is_unhealthy() -> None:
    decision = recommend_worker_scale(
        snapshots=[CapacitySnapshot(runnable_depth=100, db_pool_available=0)],
        current_workers=2,
    )
    assert decision.decision is ScalingDecisionKind.BLOCK_SCALE_OUT


def test_autoscaling_scales_out_on_sustained_depth() -> None:
    decision = recommend_worker_scale(
        snapshots=[
            CapacitySnapshot(runnable_depth=100, db_pool_available=10),
            CapacitySnapshot(runnable_depth=110, db_pool_available=10),
            CapacitySnapshot(runnable_depth=120, db_pool_available=10),
        ],
        current_workers=2,
    )
    assert decision.decision is ScalingDecisionKind.SCALE_OUT
