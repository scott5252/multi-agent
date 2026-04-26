from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.audit.export import DebugEvidenceExportService
from multi_agent_platform.audit.inspection import TimelineView
from multi_agent_platform.audit.models import ExportStatus
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.storage.base import ArtifactHandle, StorageProvider


class FakeStorage(StorageProvider):
    provider_name = "fake"

    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        return ArtifactHandle(
            provider=self.provider_name,
            key=key,
            url=f"fake://{key}",
            size_bytes=len(payload),
        )

    async def get(self, key: str) -> bytes:
        return key.encode()


async def test_export_request_is_idempotent_and_status_transitions(session) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    service = DebugEvidenceExportService(repository)
    first = await service.request_export(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        requested_by="admin",
        lineage_scope="authorized_children",
        recipient_scope="tenant_auditor",
        included_sections=["timeline"],
    )
    second = await service.request_export(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        requested_by="admin",
        lineage_scope="authorized_children",
        recipient_scope="tenant_auditor",
        included_sections=["timeline"],
    )
    assert first.debug_evidence_export_id == second.debug_evidence_export_id
    updated = await repository.update_export_status(
        first.debug_evidence_export_id, ExportStatus.AVAILABLE, artifact_ref="artifact"
    )
    assert updated.status == "available"


async def test_export_generation_and_reconciliation(session) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    repository = AuditDebuggingRepository(session)
    service = DebugEvidenceExportService(repository, FakeStorage())
    export = await service.request_export(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        requested_by="admin",
        lineage_scope="run_only",
        recipient_scope="tenant_auditor",
        included_sections=["timeline"],
    )
    generated = await service.generate_export(
        export,
        TimelineView(
            run={"workflow_run_id": str(run_id), "tenant_id": str(tenant_id)},
            events=[],
            lineage={"nodes": [], "edges": []},
            bundle=None,
        ),
    )
    assert generated.status == "available"
    interrupted = await repository.update_export_status(
        generated.debug_evidence_export_id, ExportStatus.GENERATING
    )
    reconciled = await service.reconcile_export(interrupted)
    assert reconciled.status == "failed"
