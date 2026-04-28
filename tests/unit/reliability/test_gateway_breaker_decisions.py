from __future__ import annotations

from multi_agent_platform.reliability.breakers import (
    gateway_breaker_scope,
    gateway_breaker_summary,
)
from multi_agent_platform.reliability.models import BreakerState


def test_gateway_breaker_scope_uses_provider_connection_and_model_identity() -> None:
    assert (
        gateway_breaker_scope(
            provider_connection_id="provider-1",
            model_id="gpt-test",
        )
        == "provider_connection:provider-1:model:gpt-test"
    )


def test_gateway_breaker_summary_keeps_tenant_and_run_as_evidence_only() -> None:
    summary = gateway_breaker_summary(
        provider_connection_id="provider-1",
        model_id="gpt-test",
        state=BreakerState.OPEN,
        tenant_id="tenant-1",
        workflow_run_id="run-1",
        workflow_run_step_id="step-1",
        trace_id="trace",
    )

    assert summary["scope"] == "provider_connection:provider-1:model:gpt-test"
    assert summary["allowed"] is False
    assert summary["evidence"]["tenant_id"] == "tenant-1"
