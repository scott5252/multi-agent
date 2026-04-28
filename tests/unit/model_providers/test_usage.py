from __future__ import annotations

from multi_agent_platform.model_providers.models import UsageAvailability
from multi_agent_platform.model_providers.usage import normalize_usage


def test_normalize_usage_accepts_openai_shape() -> None:
    usage = normalize_usage(
        {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5},
        provider_model_id="gpt-test",
    )

    assert usage.availability is UsageAvailability.AVAILABLE
    assert usage.total_tokens == 5
    assert usage.provider_model_id == "gpt-test"


def test_normalize_usage_marks_malformed_values() -> None:
    usage = normalize_usage({"prompt_tokens": -1})

    assert usage.availability is UsageAvailability.MALFORMED
