from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.model_providers.models import GatewayUsage, UsageValueStatus

DEFAULT_CURRENCY = "USD"
DEFAULT_INPUT_TOKEN_MICROS = 1
DEFAULT_OUTPUT_TOKEN_MICROS = 3
DEFAULT_CACHED_TOKEN_MICROS = 0
DEFAULT_REASONING_TOKEN_MICROS = 3


@dataclass(frozen=True, slots=True)
class PricingEstimate:
    estimated_cost_micros: int
    currency: str
    cost_status: UsageValueStatus


@dataclass(frozen=True, slots=True)
class PricingRate:
    currency: str = DEFAULT_CURRENCY
    input_token_micros: int = DEFAULT_INPUT_TOKEN_MICROS
    output_token_micros: int = DEFAULT_OUTPUT_TOKEN_MICROS
    cached_token_micros: int = DEFAULT_CACHED_TOKEN_MICROS
    reasoning_token_micros: int = DEFAULT_REASONING_TOKEN_MICROS
    billable_unit_micros: int | None = None


def estimate_usage_cost(
    usage: GatewayUsage,
    *,
    rate: PricingRate | None = None,
) -> PricingEstimate:
    selected = rate or PricingRate()
    if usage.availability.value == "malformed":
        return PricingEstimate(
            estimated_cost_micros=0,
            currency=selected.currency,
            cost_status=UsageValueStatus.UNAVAILABLE,
        )
    if (
        usage.input_tokens is None
        and usage.output_tokens is None
        and usage.provider_billable_units is None
    ):
        return PricingEstimate(
            estimated_cost_micros=0,
            currency=selected.currency,
            cost_status=UsageValueStatus.UNAVAILABLE,
        )
    if usage.provider_billable_units is not None and selected.billable_unit_micros:
        return PricingEstimate(
            estimated_cost_micros=usage.provider_billable_units
            * selected.billable_unit_micros,
            currency=selected.currency,
            cost_status=UsageValueStatus.ESTIMATED,
        )
    cost = (
        (usage.input_tokens or 0) * selected.input_token_micros
        + (usage.output_tokens or 0) * selected.output_token_micros
        + (usage.cached_tokens or 0) * selected.cached_token_micros
        + (usage.reasoning_tokens or 0) * selected.reasoning_token_micros
    )
    return PricingEstimate(
        estimated_cost_micros=cost,
        currency=selected.currency,
        cost_status=UsageValueStatus.ESTIMATED,
    )
