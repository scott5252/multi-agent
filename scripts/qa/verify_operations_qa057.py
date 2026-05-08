from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    InspectionAccessAuditEventRecord,
)
from multi_agent_platform.db.models.model_providers import GatewayInvocationAttempt
from multi_agent_platform.db.models.reliability import CapacitySnapshotRecord

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA057_RUN_ID = UUID("57000000-0000-0000-0000-000000000057")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        acme_timeline = _count(
            session,
            select(func.count())
            .select_from(AuditTimelineEventRecord)
            .where(AuditTimelineEventRecord.tenant_id == ACME_TENANT_ID),
        )
        globex_timeline = _count(
            session,
            select(func.count())
            .select_from(AuditTimelineEventRecord)
            .where(AuditTimelineEventRecord.tenant_id == GLOBEX_TENANT_ID),
        )
        run_traces = _count(
            session,
            select(func.count())
            .select_from(AuditRuntimeTraceRecord)
            .where(AuditRuntimeTraceRecord.workflow_run_id == QA057_RUN_ID),
        )
        gateway_attempts = _count(
            session,
            select(func.count())
            .select_from(GatewayInvocationAttempt)
            .where(GatewayInvocationAttempt.workflow_run_id == QA057_RUN_ID),
        )
        capacity_snapshots = _count(
            session,
            select(func.count()).select_from(CapacitySnapshotRecord),
        )
        browser_exports = list(
            session.scalars(
                select(InspectionAccessAuditEventRecord)
                .where(
                    InspectionAccessAuditEventRecord.action == "export_create",
                    InspectionAccessAuditEventRecord.authorization_outcome == "allowed",
                    InspectionAccessAuditEventRecord.export_id.is_not(None),
                )
                .order_by(InspectionAccessAuditEventRecord.created_at.desc())
                .limit(5)
            )
        )
        latest_export = browser_exports[0] if browser_exports else None
        if acme_timeline < 3:
            raise RuntimeError(
                f"Expected at least 3 Acme timeline rows, found {acme_timeline}"
            )
        if globex_timeline != 0:
            raise RuntimeError("Globex should remain empty for QA057 timeline rows")
        if run_traces < 2:
            raise RuntimeError(f"Expected at least 2 run traces, found {run_traces}")
        if gateway_attempts != 1:
            raise RuntimeError(
                "Expected 1 gateway attempt for the QA057 run, "
                f"found {gateway_attempts}"
            )
        if capacity_snapshots < 1:
            raise RuntimeError("Expected a live capacity snapshot")
        if latest_export is None:
            raise RuntimeError(
                "Expected a completed operations export audit row after the UI action"
            )
        metadata = latest_export.safe_metadata or {}
        if int(metadata.get("row_count") or 0) < 1:
            raise RuntimeError("Expected export audit metadata with row_count")
        if not str(metadata.get("artifact_reference_id") or "").startswith(
            "operations-export:"
        ):
            raise RuntimeError("Expected safe operations-export artifact reference")
        if not metadata.get("artifact_sha256"):
            raise RuntimeError("Expected export audit metadata with checksum")
    print("Verified QA057 operations live-data persistence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_run_id={QA057_RUN_ID}")
    print(f"acme_timeline_events={acme_timeline}")
    print(f"globex_timeline_events={globex_timeline}")
    print(f"run_traces={run_traces}")
    print(f"gateway_attempts={gateway_attempts}")
    print(f"capacity_snapshots={capacity_snapshots}")
    print(f"browser_export_reference=operations-export:{latest_export.export_id}")
    print(f"browser_export_rows={metadata.get('row_count')}")
    print(f"browser_export_checksum=sha256:{str(metadata['artifact_sha256'])[:12]}")
    return 0


def _count(session: Session, stmt) -> int:
    return int(session.scalar(stmt) or 0)


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
