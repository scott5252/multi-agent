from __future__ import annotations

from pydantic import BaseModel

from multi_agent_platform.operations.models import (
    OperationsDashboardSnapshot,
    OperationsLogFilters,
)
from multi_agent_platform.operations.redaction import redaction_notice


class OperationsConsolePage(BaseModel):
    title: str = "Operations Console"
    dashboard: OperationsDashboardSnapshot
    filters: OperationsLogFilters
    can_export: bool
    export_action: str = "/admin/operations/logs/export"

    @property
    def has_logs(self) -> bool:
        return bool(self.dashboard.logs)

    @property
    def request_latency_display(self) -> str:
        for card in self.dashboard.status_cards:
            if card.label == "Request Latency":
                return card.value
        return "0 ms"

    @property
    def token_throughput_display(self) -> str:
        return str(self.dashboard.usage.token_throughput)


def operations_redaction_notice() -> str:
    return redaction_notice()
