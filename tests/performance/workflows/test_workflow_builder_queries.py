from __future__ import annotations

import time

from tests.unit.admin.test_workflow_builder_service import (
    _draft,
    _graph_preview,
    _principal,
    _tenant_scope,
)

from multi_agent_platform.admin.workflow_builder import build_workflow_builder_envelope


def test_large_workflow_graph_preview_projection_stays_bounded() -> None:
    started = time.perf_counter()
    envelope = build_workflow_builder_envelope(
        scope=_tenant_scope(),
        principal=_principal(),
        draft=_draft(),
        graph_preview=_graph_preview(size=100),
    )
    elapsed = time.perf_counter() - started

    assert envelope.draft is not None
    assert len(envelope.draft.graph.nodes) == 100
    assert elapsed < 0.5
