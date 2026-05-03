from __future__ import annotations

from pathlib import Path


def test_usage_analytics_contract_defines_required_paths() -> None:
    contract = Path(
        "specs/016-token-usage-cost-analytics/contracts/usage-analytics.openapi.yaml"
    ).read_text(encoding="utf-8")

    for path in (
        "/admin/usage/api/summary",
        "/admin/usage/api/events",
        "/admin/usage/api/exports",
        "UsageSummaryResponse",
        "UsageExportResponse",
    ):
        assert path in contract
