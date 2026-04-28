from __future__ import annotations

from pathlib import Path

from multi_agent_platform.model_providers.guardrails import (
    ALLOWED_PROVIDER_TRANSPORT_MODULES,
    scan_provider_call_violations,
)


def test_static_guardrail_allows_only_declared_adapter_transport_modules() -> None:
    violations = scan_provider_call_violations([Path("src/multi_agent_platform")])

    assert not violations
    assert "src/multi_agent_platform/model_providers/adapters.py" in (
        ALLOWED_PROVIDER_TRANSPORT_MODULES
    )
