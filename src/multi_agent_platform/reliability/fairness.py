from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.reliability.models import FairnessWindow


@dataclass(slots=True, frozen=True)
class FairnessSelection:
    tenant_id: UUID
    score: float
    reason_code: str


def allocate_tokens(
    windows: list[FairnessWindow], *, total_tokens: float
) -> list[FairnessWindow]:
    if total_tokens < 0:
        raise ValueError("total_tokens cannot be negative")
    total_weight = sum(window.weight for window in windows) or 1.0
    for window in windows:
        window.allocated_tokens = total_tokens * (window.weight / total_weight)
    return windows


def tenant_priority_score(window: FairnessWindow) -> float:
    return window.available_tokens + window.fairness_debt - window.burst_debt


def choose_next_tenant(windows: list[FairnessWindow]) -> FairnessSelection | None:
    demanded = [window for window in windows if window.available_tokens > 0]
    if not demanded:
        return None
    chosen = max(demanded, key=tenant_priority_score)
    return FairnessSelection(
        tenant_id=chosen.tenant_id,
        score=tenant_priority_score(chosen),
        reason_code="fair_share_selected",
    )


def consume_token(window: FairnessWindow, *, burst_allowed: bool = True) -> None:
    if window.available_tokens >= 1:
        window.consumed_tokens += 1
        return
    if not burst_allowed:
        window.fairness_debt += 1
        raise ValueError("tenant has no fair-share tokens")
    window.consumed_tokens += 1
    window.burst_debt += 1
