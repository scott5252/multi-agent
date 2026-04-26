from __future__ import annotations

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models


def test_audit_debugging_metadata_contains_required_tables_and_indexes() -> None:
    import_models()
    tables = Base.metadata.tables
    for table in (
        "audit_timeline_events",
        "audit_runtime_trace_records",
        "audit_capture_gaps",
        "audit_inspection_access_events",
        "audit_debug_exports",
        "audit_redaction_classification_records",
        "audit_run_lineage_links",
        "audit_version_bundle_snapshots",
        "audit_notification_delivery_traces",
        "audit_secret_access_records",
    ):
        assert table in tables
    assert "uq_audit_timeline_idempotency" in {
        constraint.name for constraint in tables["audit_timeline_events"].constraints
    }
    assert "ix_audit_timeline_tenant_run_time" in {
        index.name for index in tables["audit_timeline_events"].indexes
    }
