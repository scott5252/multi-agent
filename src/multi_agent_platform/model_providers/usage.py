from __future__ import annotations

from collections.abc import Mapping

from multi_agent_platform.model_providers.models import (
    GatewayUsage,
    UsageAvailability,
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
        total_tokens = _optional_int(usage.get("total_tokens"))
    except (TypeError, ValueError):
        return GatewayUsage(
            availability=UsageAvailability.MALFORMED,
            provider_model_id=provider_model_id,
        )
    return GatewayUsage(
        availability=UsageAvailability.AVAILABLE,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        provider_model_id=provider_model_id,
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
