from __future__ import annotations

from pathlib import Path


def test_operations_console_contract_covers_required_routes() -> None:
    contract = Path(
        "specs/019-operations-console-logs-performance/contracts/"
        "operations-console.openapi.yaml"
    ).read_text(encoding="utf-8")

    for route in (
        "/admin/operations/api/dashboard",
        "/admin/operations/api/logs",
        "/admin/operations/api/logs/export",
        "OperationsDashboard",
        "OperationalLogEvent",
    ):
        assert route in contract
