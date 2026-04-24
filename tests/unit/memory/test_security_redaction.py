from __future__ import annotations

from multi_agent_platform.observability.logging import memory_log_context
from multi_agent_platform.observability.tracing import memory_trace_attributes


def test_memory_observability_helpers_do_not_accept_raw_content() -> None:
    log_context = memory_log_context(
        action="create_version",
        trace_id="trace",
        content_sha256="a" * 64,
    )
    trace_attributes = memory_trace_attributes(
        action="diff",
        outcome="allowed",
        memory_version_id="version",
    )

    assert "content" not in log_context["extra"]
    assert "content" not in trace_attributes
