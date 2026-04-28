from __future__ import annotations

from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderTestSummary,
    TestOutcome,
)


def derive_health_state(
    *,
    active: bool,
    latest_test: ProviderTestSummary | None,
) -> tuple[HealthState, bool, str]:
    if not active:
        return HealthState.DISABLED, False, "connection is disabled"
    if latest_test is None:
        return HealthState.UNTESTED, False, "connection has not been tested"
    if latest_test.outcome is TestOutcome.SUCCESS:
        return HealthState.HEALTHY, True, "latest safe probe succeeded"
    if latest_test.normalized_reason in {
        ErrorCategory.TIMEOUT,
        ErrorCategory.PROVIDER_UNAVAILABLE,
    }:
        return HealthState.UNAVAILABLE, False, "provider is unavailable"
    if latest_test.normalized_reason is ErrorCategory.RATE_LIMIT:
        return HealthState.DEGRADED, False, "provider is rate limited"
    return HealthState.FAILING, False, "latest safe probe failed"
