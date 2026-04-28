from __future__ import annotations

from multi_agent_platform.model_providers.models import ErrorCategory
from multi_agent_platform.reliability.models import FailureCategory
from multi_agent_platform.reliability.retries import (
    gateway_retry_summary,
    map_gateway_error_to_failure_category,
)


def test_gateway_retry_mapping_normalizes_provider_errors() -> None:
    assert (
        map_gateway_error_to_failure_category(ErrorCategory.TIMEOUT)
        is FailureCategory.TIMEOUT
    )
    assert (
        map_gateway_error_to_failure_category(ErrorCategory.RATE_LIMIT)
        is FailureCategory.RATE_LIMITED
    )
    assert (
        map_gateway_error_to_failure_category(ErrorCategory.PROVIDER_UNAVAILABLE)
        is FailureCategory.DEPENDENCY_UNAVAILABLE
    )
    assert gateway_retry_summary(ErrorCategory.NONE)["category"] == "skipped"
    assert gateway_retry_summary(ErrorCategory.AUTHORIZATION_FAILURE)["category"] == (
        "non-retryable"
    )
