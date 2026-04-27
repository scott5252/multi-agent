from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.reliability.models import QuotaCounter


@dataclass(slots=True, frozen=True)
class QuotaDecision:
    allowed: bool
    reason_code: str
    remaining: int


def reserve_quota(counter: QuotaCounter, amount: int = 1) -> QuotaDecision:
    if amount <= 0:
        raise ValueError("quota reservation amount must be positive")
    if counter.used_value + amount > counter.limit_value:
        return QuotaDecision(
            allowed=False,
            reason_code="quota_exhausted",
            remaining=counter.remaining,
        )
    counter.used_value += amount
    return QuotaDecision(
        allowed=True,
        reason_code="quota_reserved",
        remaining=counter.remaining,
    )


def release_quota(counter: QuotaCounter, amount: int = 1) -> int:
    if amount <= 0:
        raise ValueError("quota release amount must be positive")
    counter.used_value = max(counter.used_value - amount, 0)
    return counter.remaining
