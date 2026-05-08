from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.usage import LlmUsageEvent, UsageExportRequest
from multi_agent_platform.usage.models import UsageExportStatus

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA056_EXPORT_ID = UUID("56000000-0000-0000-0000-000000000056")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        acme_events = _count(
            session,
            select(func.count())
            .select_from(LlmUsageEvent)
            .where(LlmUsageEvent.tenant_id == ACME_TENANT_ID),
        )
        globex_events = _count(
            session,
            select(func.count())
            .select_from(LlmUsageEvent)
            .where(LlmUsageEvent.tenant_id == GLOBEX_TENANT_ID),
        )
        seeded_export = session.get(UsageExportRequest, QA056_EXPORT_ID)
        completed_exports = _count(
            session,
            select(func.count())
            .select_from(UsageExportRequest)
            .where(
                UsageExportRequest.status == UsageExportStatus.COMPLETED,
                UsageExportRequest.row_count >= 2,
            ),
        )
        browser_exports = list(
            session.scalars(
                select(UsageExportRequest)
                .where(
                    UsageExportRequest.status == UsageExportStatus.COMPLETED,
                    UsageExportRequest.row_count >= 2,
                    UsageExportRequest.usage_export_request_id != QA056_EXPORT_ID,
                )
                .order_by(UsageExportRequest.created_at.desc())
                .limit(5)
            )
        )
        latest_browser_export = browser_exports[0] if browser_exports else None
        if acme_events != 2:
            raise RuntimeError(f"Expected 2 Acme usage events, found {acme_events}")
        if globex_events != 0:
            raise RuntimeError("Globex should remain empty for QA056 usage events")
        if seeded_export is None or seeded_export.status != UsageExportStatus.COMPLETED:
            raise RuntimeError("Expected the seeded QA056 completed export row")
        if latest_browser_export is None:
            raise RuntimeError(
                "Expected a completed export created by API or Playwright after seed"
            )
        if latest_browser_export.artifact_uri is None:
            raise RuntimeError("Expected persisted storage metadata for the export")
        if not latest_browser_export.artifact_sha256:
            raise RuntimeError("Expected persisted checksum metadata for the export")
        if latest_browser_export.artifact_uri.startswith("usage-export:"):
            raise RuntimeError("Database artifact URI should not be a UI reference")
    print("Verified QA056 usage live-data persistence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"acme_events={acme_events}")
    print(f"globex_events={globex_events}")
    print(f"completed_exports={completed_exports}")
    print(
        "browser_export_reference="
        f"usage-export:{latest_browser_export.usage_export_request_id}"
    )
    print(f"browser_export_rows={latest_browser_export.row_count}")
    print(
        f"browser_export_checksum=sha256:{latest_browser_export.artifact_sha256[:12]}"
    )
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
