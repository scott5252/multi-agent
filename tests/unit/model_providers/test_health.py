from __future__ import annotations

from multi_agent_platform.model_providers.health import derive_health_state
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderTestSummary,
    TestOutcome,
)


def test_derive_health_state_requires_active_connection() -> None:
    health, selectable, reason = derive_health_state(active=False, latest_test=None)

    assert health is HealthState.DISABLED
    assert selectable is False
    assert "disabled" in reason


def test_derive_health_state_selects_only_successful_probe() -> None:
    health, selectable, _reason = derive_health_state(
        active=True,
        latest_test=ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=7,
            safe_diagnostic_summary="safe",
        ),
    )

    assert health is HealthState.HEALTHY
    assert selectable is True


def test_derive_health_state_handles_missing_and_failed_probes() -> None:
    untested_health, untested_selectable, untested_reason = derive_health_state(
        active=True,
        latest_test=None,
    )
    unavailable_health, unavailable_selectable, _reason = derive_health_state(
        active=True,
        latest_test=ProviderTestSummary(
            outcome=TestOutcome.FAILURE,
            normalized_reason=ErrorCategory.TIMEOUT,
            latency_ms=20,
            safe_diagnostic_summary="timeout",
        ),
    )
    degraded_health, degraded_selectable, _reason = derive_health_state(
        active=True,
        latest_test=ProviderTestSummary(
            outcome=TestOutcome.FAILURE,
            normalized_reason=ErrorCategory.RATE_LIMIT,
            latency_ms=20,
            safe_diagnostic_summary="limited",
        ),
    )
    failing_health, failing_selectable, _reason = derive_health_state(
        active=True,
        latest_test=ProviderTestSummary(
            outcome=TestOutcome.FAILURE,
            normalized_reason=ErrorCategory.INVALID_MODEL,
            latency_ms=20,
            safe_diagnostic_summary="bad model",
        ),
    )

    assert untested_health is HealthState.UNTESTED
    assert untested_selectable is False
    assert "not been tested" in untested_reason
    assert unavailable_health is HealthState.UNAVAILABLE
    assert unavailable_selectable is False
    assert degraded_health is HealthState.DEGRADED
    assert degraded_selectable is False
    assert failing_health is HealthState.FAILING
    assert failing_selectable is False
