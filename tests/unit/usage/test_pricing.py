from __future__ import annotations

from multi_agent_platform.model_providers.models import GatewayUsage, UsageValueStatus
from multi_agent_platform.usage.pricing import PricingRate, estimate_usage_cost


def test_usage_pricing_estimates_by_token_category() -> None:
    estimate = estimate_usage_cost(
        GatewayUsage(
            input_tokens=10,
            output_tokens=5,
            cached_tokens=4,
            reasoning_tokens=2,
        ),
        rate=PricingRate(
            input_token_micros=1,
            output_token_micros=4,
            cached_token_micros=0,
            reasoning_token_micros=6,
        ),
    )

    assert estimate.estimated_cost_micros == 42
    assert estimate.cost_status is UsageValueStatus.ESTIMATED


def test_usage_pricing_marks_missing_usage_unavailable() -> None:
    estimate = estimate_usage_cost(GatewayUsage())

    assert estimate.estimated_cost_micros == 0
    assert estimate.cost_status is UsageValueStatus.UNAVAILABLE
