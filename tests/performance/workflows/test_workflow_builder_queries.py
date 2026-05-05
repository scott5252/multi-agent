from __future__ import annotations

import time

from multi_agent_platform.admin.workflow_builder import build_graph_preview


def test_large_workflow_graph_preview_stays_bounded() -> None:
    started = time.perf_counter()
    graph = build_graph_preview(large=True)
    elapsed = time.perf_counter() - started

    assert len(graph.nodes) == 100
    assert len(graph.edges) == 99
    assert elapsed < 0.5
