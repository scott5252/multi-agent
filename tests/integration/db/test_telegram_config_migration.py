from __future__ import annotations

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models


def test_telegram_config_tables_are_registered_in_metadata() -> None:
    import_models()

    for table in (
        "telegram_tenant_configs",
        "telegram_link_token_audits",
        "telegram_linked_identity_summaries",
        "telegram_diagnostic_events",
    ):
        assert table in Base.metadata.tables
