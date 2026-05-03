from __future__ import annotations

from multi_agent_platform.model_providers.models import (
    UsageAvailability,
    UsageValueStatus,
)
from multi_agent_platform.model_providers.usage import normalize_usage


def test_normalize_usage_accepts_openai_shape() -> None:
    usage = normalize_usage(
        {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
        provider_model_id="gpt-test",
    )

    assert usage.availability is UsageAvailability.AVAILABLE
    assert usage.total_tokens == 5
    assert usage.provider_model_id == "gpt-test"
    assert usage.total_token_status is UsageValueStatus.CONFIRMED


def test_normalize_usage_marks_malformed_values() -> None:
    usage = normalize_usage({"prompt_tokens": -1})

    assert usage.availability is UsageAvailability.MALFORMED


def test_normalize_usage_supports_cached_and_reasoning_tokens() -> None:
    usage = normalize_usage(
        {
            "input_tokens": 10,
            "output_tokens": 5,
            "prompt_tokens_details": {"cached_tokens": 4},
            "completion_tokens_details": {"reasoning_tokens": 2},
            "provider_billable_units": 11,
        }
    )

    assert usage.cached_tokens == 4
    assert usage.reasoning_tokens == 2
    assert usage.provider_billable_units == 11
    assert usage.total_tokens == 15
    assert usage.total_token_status is UsageValueStatus.ESTIMATED
