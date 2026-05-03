from __future__ import annotations

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models


def test_usage_tables_are_registered_in_metadata() -> None:
    import_models()

    for table in (
        "llm_usage_events",
        "llm_usage_rollups",
        "llm_pricing_versions",
        "usage_export_requests",
        "usage_reconciliation_records",
    ):
        assert table in Base.metadata.tables
