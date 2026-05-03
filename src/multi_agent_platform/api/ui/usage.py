from __future__ import annotations

from pydantic import BaseModel

from multi_agent_platform.usage.models import (
    UsageEventView,
    UsageFilters,
    UsageRollup,
    UsageTotals,
)


class UsageDashboardPage(BaseModel):
    title: str = "Usage Analytics"
    filters: UsageFilters
    totals: UsageTotals
    rollups: tuple[UsageRollup, ...]
    events: tuple[UsageEventView, ...]
    can_export: bool
    export_action: str = "/admin/usage/exports"

    @property
    def has_events(self) -> bool:
        return bool(self.events)

    @property
    def estimated_cost_display(self) -> str:
        return f"${self.totals.estimated_cost_micros / 1_000_000:.6f}"


class UsageExportPage(BaseModel):
    title: str = "Usage Export"
    status: str
    row_count: int
    artifact_uri: str | None = None
    denial_reason: str | None = None
    failure_reason: str | None = None


def redaction_notice() -> str:
    return (
        "Usage analytics show normalized counts and safe identifiers only. Raw "
        "prompts, completions, secrets, memory content, and provider credentials "
        "are excluded."
    )
