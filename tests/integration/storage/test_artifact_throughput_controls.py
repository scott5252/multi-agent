from __future__ import annotations

from multi_agent_platform.storage.throughput import (
    ArtifactThroughputWindow,
    acquire_artifact_budget,
)


def test_object_store_breaker_blocks_artifact_work() -> None:
    window = ArtifactThroughputWindow(
        operation_kind="export",
        tenant_limit=1,
        global_limit=1,
        object_store_breaker_open=True,
    )
    assert acquire_artifact_budget(window) == "blocked_by_breaker"
