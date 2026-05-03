from __future__ import annotations

from collections.abc import Mapping

from multi_agent_platform.model_providers.models import (
    GatewayUsage,
    UsageAvailability,
    UsageValueStatus,
)


def normalize_usage(
    usage: Mapping[str, object] | None,
    *,
    provider_model_id: str | None = None,
) -> GatewayUsage:
    if not usage:
        return GatewayUsage(provider_model_id=provider_model_id)
    try:
        input_tokens = _optional_int(
            usage.get("prompt_tokens") or usage.get("input_tokens")
        )
        output_tokens = _optional_int(
            usage.get("completion_tokens") or usage.get("output_tokens")
        )
        cached_tokens = _optional_int(
            _coalesce(
                _first_present(usage, "cached_tokens", "cached_input_tokens"),
                _nested_int_source(usage, "prompt_tokens_details", "cached_tokens"),
            )
        )
        reasoning_tokens = _optional_int(
            _coalesce(
                _first_present(usage, "reasoning_tokens", "output_reasoning_tokens"),
                _nested_int_source(
                    usage,
                    "completion_tokens_details",
                    "reasoning_tokens",
                ),
            )
        )
        total_tokens = _optional_int(usage.get("total_tokens"))
        provider_billable_units = _optional_int(
            usage.get("billable_units") or usage.get("provider_billable_units")
        )
    except (TypeError, ValueError):
        return GatewayUsage(
            availability=UsageAvailability.MALFORMED,
            provider_model_id=provider_model_id,
        )
    if total_tokens is None and (input_tokens is not None or output_tokens is not None):
        total_tokens = (input_tokens or 0) + (output_tokens or 0)
        total_status = UsageValueStatus.ESTIMATED
    elif total_tokens is not None:
        total_status = UsageValueStatus.CONFIRMED
    else:
        total_status = UsageValueStatus.UNAVAILABLE
    return GatewayUsage(
        availability=UsageAvailability.AVAILABLE,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        reasoning_tokens=reasoning_tokens,
        total_tokens=total_tokens,
        provider_billable_units=provider_billable_units,
        provider_model_id=provider_model_id,
        input_token_status=_present_status(input_tokens),
        output_token_status=_present_status(output_tokens),
        cached_token_status=_optional_category_status(cached_tokens),
        reasoning_token_status=_optional_category_status(reasoning_tokens),
        total_token_status=total_status,
        billable_unit_status=_present_status(provider_billable_units),
    )


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, str | bytes | bytearray | int | float):
        raise TypeError("usage token values must be scalar")
    converted = int(value)
    if converted < 0:
        raise ValueError("usage token values cannot be negative")
    return converted


def _first_present(usage: Mapping[str, object], *keys: str) -> object:
    for key in keys:
        value = usage.get(key)
        if value is not None:
            return value
    return None


def _nested_int_source(
    usage: Mapping[str, object],
    container_key: str,
    value_key: str,
) -> object:
    nested = usage.get(container_key)
    if isinstance(nested, Mapping):
        return nested.get(value_key)
    return None


def _coalesce(*values: object) -> object:
    for value in values:
        if value is not None:
            return value
    return None


def _present_status(value: int | None) -> UsageValueStatus:
    if value is None:
        return UsageValueStatus.UNAVAILABLE
    return UsageValueStatus.CONFIRMED


def _optional_category_status(value: int | None) -> UsageValueStatus:
    if value is None:
        return UsageValueStatus.NOT_APPLICABLE
    return UsageValueStatus.CONFIRMED
