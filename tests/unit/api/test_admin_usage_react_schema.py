from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_usage_react import (
    UsageReactConfidenceStatus,
    UsageReactDashboard,
    UsageReactDashboardQuery,
    UsageReactEventDrilldown,
    UsageReactEventRow,
    UsageReactExportStatus,
    UsageReactExportSummary,
    UsageReactFilterMetadata,
    UsageReactGroupBy,
    UsageReactRange,
    UsageReactRollupSection,
    UsageReactSummaryCard,
    UsageReactTone,
    safe_usage_text,
)


def test_safe_usage_text_rejects_unsafe_markers() -> None:
    for marker in (
        "qa035-secret-value",
        "raw prompt",
        "authorization header",
        "credential value",
        "/Users/scott/project",
    ):
        with pytest.raises(ValueError):
            safe_usage_text(marker)


def test_dashboard_query_validates_range() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValueError):
        UsageReactDashboardQuery(start=now, end=now - timedelta(minutes=1))


def test_usage_dashboard_schema_accepts_safe_payload() -> None:
    now = datetime.now(UTC)
    filters = UsageReactFilterMetadata(
        selected_range=UsageReactRange(
            label="Last 7 days",
            start=now - timedelta(days=7),
            end=now,
        ),
        group_by_options=(),
        selected_group_by=UsageReactGroupBy.PROVIDER,
    )
    drilldown = UsageReactEventDrilldown(
        rows=(
            UsageReactEventRow(
                event_id=UUID("35000000-0000-0000-0000-000000000001"),
                recorded_at=now,
                tenant_label="Acme",
                provider_label="OpenAI",
                model_label="gpt-4.1-mini",
                total_tokens=10,
                estimated_cost_display="$0.0001",
                latency_ms=10,
                usage_status=UsageReactConfidenceStatus.CONFIRMED,
                cost_status=UsageReactConfidenceStatus.ESTIMATED,
                safe_attribution_summary="Safe attribution.",
            ),
        ),
        total_rows=1,
    )
    dashboard = UsageReactDashboard(
        page_id="usage",
        title="Usage",
        description="Safe usage dashboard.",
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.TENANT,
            tenant_id=UUID("11111111-1111-1111-1111-111111111111"),
            label="Acme",
        ),
        filters=filters,
        summary_cards=(
            UsageReactSummaryCard(
                card_id="tokens",
                label="Tokens",
                value="10",
                unit="tokens",
                status=UsageReactConfidenceStatus.CONFIRMED,
                tone=UsageReactTone.SUCCESS,
                detail="Confirmed tokens.",
            ),
        ),
        trend=(),
        rollup=UsageReactRollupSection(
            group_by=UsageReactGroupBy.PROVIDER,
            rows=(),
            total_rows=0,
        ),
        drilldown=drilldown,
        updated_at=now,
    )

    assert dashboard.summary_cards[0].status is UsageReactConfidenceStatus.CONFIRMED


def test_export_summary_hides_storage_paths() -> None:
    with pytest.raises(ValueError):
        UsageReactExportSummary(
            usage_export_request_id=UUID("35000000-0000-0000-0000-000000000035"),
            status=UsageReactExportStatus.COMPLETED,
            scope_label="Platform",
            requested_by_label="platform-admin",
            filter_snapshot={},
            row_count=1,
            artifact_reference="/Users/scott/usage.csv",
            created_at=datetime.now(UTC),
            audit_reference="audit-usage-export",
            next_step="Review export.",
        )
