from __future__ import annotations

from multi_agent_platform.api.ui.usage import UsageDashboardPage, redaction_notice
from multi_agent_platform.usage.models import UsageFilters, UsageTotals


def test_usage_dashboard_formats_estimated_cost() -> None:
    page = UsageDashboardPage(
        filters=UsageFilters(),
        totals=UsageTotals(estimated_cost_micros=1234),
        rollups=(),
        events=(),
        can_export=True,
    )

    assert page.estimated_cost_display == "$0.001234"
    assert "Raw prompts" in redaction_notice()
