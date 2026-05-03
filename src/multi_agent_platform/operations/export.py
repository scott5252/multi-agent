from __future__ import annotations

import csv
import hashlib
import io
from uuid import UUID

from multi_agent_platform.operations.models import OperationalLogEvent
from multi_agent_platform.storage.base import StorageProvider, build_artifact_key

CSV_COLUMNS = (
    "event_id",
    "source",
    "occurred_at",
    "tenant_id",
    "trace_id",
    "run_id",
    "component",
    "severity",
    "status",
    "dependency",
    "summary",
    "latency_ms",
)


def operation_log_events_to_csv(events: list[OperationalLogEvent]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "event_id": event.event_id,
                "source": event.source,
                "occurred_at": event.occurred_at.isoformat(),
                "tenant_id": str(event.tenant_id or ""),
                "trace_id": event.trace_id or "",
                "run_id": str(event.run_id or ""),
                "component": event.component,
                "severity": event.severity,
                "status": event.status,
                "dependency": event.dependency or "",
                "summary": event.summary,
                "latency_ms": event.latency_ms or "",
            }
        )
    return buffer.getvalue().encode("utf-8")


async def store_operations_csv_export(
    *,
    storage_provider: StorageProvider,
    export_id: UUID,
    principal_id: str,
    events: list[OperationalLogEvent],
) -> tuple[str, str, int]:
    payload = operation_log_events_to_csv(events)
    checksum = hashlib.sha256(payload).hexdigest()
    key = build_artifact_key("operations-exports", principal_id, f"{export_id}.csv")
    handle = await storage_provider.put(key, payload)
    return handle.url, checksum, handle.size_bytes
