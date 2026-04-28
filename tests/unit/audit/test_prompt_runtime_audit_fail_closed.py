from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.capture import build_prompt_runtime_event
from multi_agent_platform.audit.models import CaptureCriticality


def test_prompt_runtime_security_events_are_security_governance_by_default() -> None:
    event = build_prompt_runtime_event(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        trace_id="trace",
        source_event_id="prompt-runtime:publish",
        action="publish",
        details={"prompt_version_id": str(uuid4())},
    )

    assert event.criticality is CaptureCriticality.SECURITY_GOVERNANCE
    assert "publish" in event.safe_summary
