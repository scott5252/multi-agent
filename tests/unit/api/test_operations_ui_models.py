from __future__ import annotations

from multi_agent_platform.api.ui.operations import (
    OperationsConsolePage,
    operations_redaction_notice,
)
from multi_agent_platform.operations.models import (
    OperationsCapacitySummary,
    OperationsDashboardSnapshot,
    OperationsLogFilters,
    OperationsStatusCard,
)


def test_operations_console_page_exposes_displays() -> None:
    dashboard = OperationsDashboardSnapshot(
        health_status="ready",
        status_cards=(
            OperationsStatusCard(
                label="Request Latency",
                value="42 ms",
                status="ready",
                summary="p95",
            ),
        ),
        dependencies=(),
        capacity=OperationsCapacitySummary(),
        filters=OperationsLogFilters(),
        redaction_notice=operations_redaction_notice(),
    )

    page = OperationsConsolePage(
        dashboard=dashboard,
        filters=OperationsLogFilters(),
        can_export=True,
    )

    assert page.request_latency_display == "42 ms"
    assert page.token_throughput_display == "0"
    assert "Raw prompts" in operations_redaction_notice()
