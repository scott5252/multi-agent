from __future__ import annotations

from multi_agent_platform.audit.classification import redact_payload
from multi_agent_platform.observability.logging import REDACTED


def test_runtime_decision_payloads_are_redacted_for_viewer() -> None:
    payload = {
        "handoff_payload": {"customer": "private"},
        "contract_errors": ["bad private body"],
        "tool_input": {"api_key": "secret"},
        "model_prompt": "prompt text",
        "safe_reason": "policy denied",
    }
    redacted = redact_payload(payload)
    assert redacted["handoff_payload"] == REDACTED
    assert redacted["tool_input"] == REDACTED
    assert redacted["model_prompt"] == REDACTED
    assert redacted["safe_reason"] == "policy denied"
