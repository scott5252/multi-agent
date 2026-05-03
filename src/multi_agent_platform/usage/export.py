from __future__ import annotations

import csv
import hashlib
import io
from uuid import UUID

from multi_agent_platform.storage.base import StorageProvider, build_artifact_key
from multi_agent_platform.usage.models import UsageEventView

CSV_COLUMNS = (
    "usage_event_id",
    "tenant_id",
    "principal_id",
    "provider_key",
    "model_id",
    "workflow_run_id",
    "workflow_run_step_id",
    "agent_key",
    "sub_agent_key",
    "prompt_version_id",
    "execution_mode",
    "input_tokens",
    "output_tokens",
    "cached_tokens",
    "reasoning_tokens",
    "total_tokens",
    "provider_billable_units",
    "latency_ms",
    "estimated_cost_micros",
    "currency",
    "usage_status",
    "recorded_at",
)


def usage_events_to_csv(events: list[UsageEventView]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "usage_event_id": str(event.llm_usage_event_id),
                "tenant_id": str(event.tenant_id),
                "principal_id": event.principal_id or "",
                "provider_key": event.provider_key,
                "model_id": event.model_id,
                "workflow_run_id": str(event.workflow_run_id or ""),
                "workflow_run_step_id": str(event.workflow_run_step_id or ""),
                "agent_key": event.agent_key or "",
                "sub_agent_key": event.sub_agent_key or "",
                "prompt_version_id": str(event.prompt_version_id or ""),
                "execution_mode": event.execution_mode,
                "input_tokens": event.input_tokens or "",
                "output_tokens": event.output_tokens or "",
                "cached_tokens": event.cached_tokens or "",
                "reasoning_tokens": event.reasoning_tokens or "",
                "total_tokens": event.total_tokens or "",
                "provider_billable_units": event.provider_billable_units or "",
                "latency_ms": event.latency_ms,
                "estimated_cost_micros": event.estimated_cost_micros or "",
                "currency": event.currency,
                "usage_status": event.usage_status.value,
                "recorded_at": event.recorded_at.isoformat(),
            }
        )
    return buffer.getvalue().encode("utf-8")


async def store_usage_csv_export(
    *,
    storage_provider: StorageProvider,
    export_id: UUID,
    tenant_label: str,
    events: list[UsageEventView],
) -> tuple[str, str, int]:
    payload = usage_events_to_csv(events)
    checksum = hashlib.sha256(payload).hexdigest()
    key = build_artifact_key(
        "usage-exports",
        tenant_label,
        f"{export_id}.csv",
    )
    handle = await storage_provider.put(key, payload)
    return handle.url, checksum, handle.size_bytes
