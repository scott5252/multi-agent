from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import UUID

from multi_agent_platform.audit.inspection import TimelineView, safe_export_manifest
from multi_agent_platform.audit.models import DebugEvidenceExportCreate, ExportStatus
from multi_agent_platform.db.models.audit_debugging import DebugEvidenceExportRecord
from multi_agent_platform.storage.base import StorageProvider


class DebugEvidenceExportRepository(Protocol):
    async def find_export(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        requested_by: str,
        lineage_scope: str,
        recipient_scope: str,
        included_sections: list[str],
    ) -> DebugEvidenceExportRecord | None: ...

    async def create_export(
        self, payload: DebugEvidenceExportCreate
    ) -> DebugEvidenceExportRecord: ...

    async def update_export_status(
        self,
        export_id: UUID,
        status: ExportStatus,
        *,
        artifact_id: UUID | None = None,
        artifact_ref: str | None = None,
        safe_failure_reason: str | None = None,
    ) -> DebugEvidenceExportRecord: ...


class DebugEvidenceExportService:
    def __init__(
        self,
        repository: DebugEvidenceExportRepository,
        storage_provider: StorageProvider | None = None,
    ) -> None:
        self.repository = repository
        self.storage_provider = storage_provider

    async def request_export(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        requested_by: str,
        lineage_scope: str,
        recipient_scope: str,
        included_sections: list[str],
        excluded_sections: list[str] | None = None,
    ) -> DebugEvidenceExportRecord:
        existing = await self.repository.find_export(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            requested_by=requested_by,
            lineage_scope=lineage_scope,
            recipient_scope=recipient_scope,
            included_sections=included_sections,
        )
        if existing is not None:
            return existing
        return await self.repository.create_export(
            DebugEvidenceExportCreate(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                requested_by=requested_by,
                lineage_scope=lineage_scope,
                recipient_scope=recipient_scope,
                included_sections=included_sections,
                excluded_sections=excluded_sections or [],
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
        )

    async def generate_export(
        self, export_record: DebugEvidenceExportRecord, timeline: TimelineView
    ) -> DebugEvidenceExportRecord:
        await self.repository.update_export_status(
            export_record.debug_evidence_export_id, ExportStatus.GENERATING
        )
        try:
            manifest = safe_export_manifest(
                timeline, viewer_role="auditor", generated_at=datetime.now(UTC)
            )
            body = json.dumps(manifest, default=str, sort_keys=True).encode("utf-8")
            artifact_ref = f"audit-debug/{export_record.debug_evidence_export_id}.json"
            artifact_id = None
            if self.storage_provider is not None:
                artifact = await self.storage_provider.put(artifact_ref, body)
                artifact_ref = artifact.url
            return await self.repository.update_export_status(
                export_record.debug_evidence_export_id,
                ExportStatus.AVAILABLE,
                artifact_id=artifact_id,
                artifact_ref=artifact_ref,
            )
        except Exception as exc:
            return await self.repository.update_export_status(
                export_record.debug_evidence_export_id,
                ExportStatus.FAILED,
                safe_failure_reason=str(exc)[:255],
            )

    async def reconcile_export(
        self, export_record: DebugEvidenceExportRecord
    ) -> DebugEvidenceExportRecord:
        if export_record.status == ExportStatus.GENERATING.value:
            return await self.repository.update_export_status(
                export_record.debug_evidence_export_id,
                ExportStatus.FAILED,
                safe_failure_reason=(
                    "generation interrupted before artifact availability"
                ),
            )
        return export_record
