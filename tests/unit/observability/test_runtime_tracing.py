from __future__ import annotations

from multi_agent_platform.observability.tracing import runtime_trace_attributes


def test_runtime_trace_attributes_omit_missing_optional_values() -> None:
    assert runtime_trace_attributes(
        workflow_run_id="run",
        tenant_id=None,
        bundle_digest=None,
    ) == {"workflow_run_id": "run"}

    assert runtime_trace_attributes(
        workflow_run_id="run",
        tenant_id="tenant",
        bundle_digest="digest",
    ) == {
        "workflow_run_id": "run",
        "tenant_id": "tenant",
        "bundle_digest": "digest",
    }
