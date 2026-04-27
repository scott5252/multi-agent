from __future__ import annotations

from multi_agent_platform.storage.throughput import (
    ArtifactThroughputWindow,
    acquire_artifact_budget,
    artifact_metadata_only_record,
    release_artifact_budget,
)


def test_artifact_budget_throttles_tenant_and_keeps_payloads_out_of_db() -> None:
    window = ArtifactThroughputWindow(
        operation_kind="export",
        tenant_limit=1,
        global_limit=10,
    )
    assert acquire_artifact_budget(window) == "acquired"
    assert acquire_artifact_budget(window) == "tenant_throttled"
    release_artifact_budget(window)
    metadata = artifact_metadata_only_record(
        artifact_ref="s3://bucket/report.json",
        checksum="sha256",
        status="partial",
    )
    assert metadata["payload_stored_in_postgres"] is False
