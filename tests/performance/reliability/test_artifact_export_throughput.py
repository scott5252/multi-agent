from __future__ import annotations

import pytest

from multi_agent_platform.storage.throughput import (
    ArtifactThroughputWindow,
    acquire_artifact_budget,
)


@pytest.mark.performance
def test_artifact_export_throughput_throttles_global_limit() -> None:
    window = ArtifactThroughputWindow(
        operation_kind="export",
        tenant_limit=10,
        global_limit=1,
        global_inflight=1,
    )
    assert acquire_artifact_budget(window) == "global_throttled"
