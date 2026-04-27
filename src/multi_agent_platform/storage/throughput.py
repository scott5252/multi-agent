from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ArtifactThroughputWindow:
    operation_kind: str
    tenant_limit: int
    global_limit: int
    tenant_inflight: int = 0
    global_inflight: int = 0
    object_store_breaker_open: bool = False


def acquire_artifact_budget(window: ArtifactThroughputWindow) -> str:
    if window.object_store_breaker_open:
        return "blocked_by_breaker"
    if window.global_inflight >= window.global_limit:
        return "global_throttled"
    if window.tenant_inflight >= window.tenant_limit:
        return "tenant_throttled"
    window.tenant_inflight += 1
    window.global_inflight += 1
    return "acquired"


def release_artifact_budget(window: ArtifactThroughputWindow) -> None:
    window.tenant_inflight = max(window.tenant_inflight - 1, 0)
    window.global_inflight = max(window.global_inflight - 1, 0)


def artifact_metadata_only_record(
    *, artifact_ref: str, checksum: str | None, status: str
) -> dict[str, object]:
    return {
        "artifact_ref": artifact_ref,
        "checksum": checksum,
        "status": status,
        "payload_stored_in_postgres": False,
    }
