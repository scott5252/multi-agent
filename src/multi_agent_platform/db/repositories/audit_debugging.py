from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.audit.models import (
    CaptureGapCreate,
    DebugEvidenceExportCreate,
    ExportStatus,
    RunLineageLinkCreate,
    TimelineEventCreate,
    TraceRecordCreate,
    VersionBundleSnapshotCreate,
)
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    CaptureGapRecord,
    DebugEvidenceExportRecord,
    InspectionAccessAuditEventRecord,
    RunLineageLinkRecord,
    SecretAccessAuditRecord,
    VersionBundleSnapshotRecord,
)


def filters_digest(filters: dict[str, object]) -> str:
    payload = json.dumps(filters, default=str, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditDebuggingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_timeline_event(
        self, payload: TimelineEventCreate
    ) -> AuditTimelineEventRecord:
        existing = await self.get_timeline_event_by_source(
            tenant_id=payload.tenant_id,
            workflow_run_id=payload.workflow_run_id,
            event_category=payload.event_category.value,
            source_event_id=payload.source_event_id,
        )
        if existing is not None:
            return existing
        max_sequence = await self.session.scalar(
            select(func.max(AuditTimelineEventRecord.sequence)).where(
                AuditTimelineEventRecord.tenant_id == payload.tenant_id,
                AuditTimelineEventRecord.workflow_run_id == payload.workflow_run_id,
            )
        )
        record = AuditTimelineEventRecord(
            tenant_id=payload.tenant_id,
            workflow_run_id=payload.workflow_run_id,
            parent_run_id=payload.parent_run_id,
            run_step_id=payload.run_step_id,
            sequence=(max_sequence or 0) + 1,
            event_category=payload.event_category.value,
            run_status_after=payload.run_status_after.value,
            origin_type=payload.origin_type,
            origin_ref=payload.origin_ref,
            actor_principal_id=payload.actor_principal_id,
            trace_id=payload.trace_id,
            correlation_id=payload.correlation_id,
            source_event_id=payload.source_event_id,
            occurred_at=payload.occurred_at,
            criticality=payload.criticality.value,
            safe_summary=payload.safe_summary,
            safe_details=payload.safe_details,
            classification_version=payload.classification_version,
            supersedes_event_id=payload.supersedes_event_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_timeline_event_by_source(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        event_category: str,
        source_event_id: str,
    ) -> AuditTimelineEventRecord | None:
        stmt = select(AuditTimelineEventRecord).where(
            AuditTimelineEventRecord.tenant_id == tenant_id,
            AuditTimelineEventRecord.workflow_run_id == workflow_run_id,
            AuditTimelineEventRecord.event_category == event_category,
            AuditTimelineEventRecord.source_event_id == source_event_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_trace_record(
        self, payload: TraceRecordCreate
    ) -> AuditRuntimeTraceRecord:
        timeline = await self.session.get(
            AuditTimelineEventRecord, payload.timeline_event_id
        )
        if (
            timeline is None
            or timeline.workflow_run_id != payload.workflow_run_id
            or timeline.tenant_id != payload.tenant_id
        ):
            raise ValueError("trace must link to a same-tenant timeline event")
        record = AuditRuntimeTraceRecord(
            tenant_id=payload.tenant_id,
            workflow_run_id=payload.workflow_run_id,
            timeline_event_id=payload.timeline_event_id,
            run_step_id=payload.run_step_id,
            trace_type=payload.trace_type.value,
            trace_id=payload.trace_id,
            correlation_id=payload.correlation_id,
            status=payload.status.value,
            outcome=payload.outcome,
            duration_ms=payload.duration_ms,
            policy_outcome=payload.policy_outcome.value,
            subject_ref=payload.subject_ref,
            safe_input_summary=payload.safe_input_summary,
            safe_output_summary=payload.safe_output_summary,
            safe_error_summary=payload.safe_error_summary,
            metadata_json=payload.metadata,
            occurred_at=payload.occurred_at,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_capture_gap(self, payload: CaptureGapCreate) -> CaptureGapRecord:
        record = CaptureGapRecord(
            tenant_id=payload.tenant_id,
            workflow_run_id=payload.workflow_run_id,
            timeline_event_id=payload.timeline_event_id,
            trace_id=payload.trace_id,
            gap_type=payload.gap_type,
            affected_trace_type=payload.affected_trace_type.value
            if payload.affected_trace_type
            else None,
            criticality=payload.criticality.value,
            safe_reason=payload.safe_reason,
            recovery_status=payload.recovery_status,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_timeline_events(
        self, *, tenant_id: UUID | None, workflow_run_id: UUID, limit: int = 200
    ) -> list[AuditTimelineEventRecord]:
        stmt = (
            select(AuditTimelineEventRecord)
            .where(
                AuditTimelineEventRecord.tenant_id == tenant_id,
                AuditTimelineEventRecord.workflow_run_id == workflow_run_id,
            )
            .order_by(AuditTimelineEventRecord.sequence)
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_trace_records(
        self, *, tenant_id: UUID | None, workflow_run_id: UUID
    ) -> list[AuditRuntimeTraceRecord]:
        stmt = select(AuditRuntimeTraceRecord).where(
            AuditRuntimeTraceRecord.tenant_id == tenant_id,
            AuditRuntimeTraceRecord.workflow_run_id == workflow_run_id,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_capture_gaps(
        self, *, tenant_id: UUID | None, workflow_run_id: UUID
    ) -> list[CaptureGapRecord]:
        stmt = select(CaptureGapRecord).where(
            CaptureGapRecord.tenant_id == tenant_id,
            CaptureGapRecord.workflow_run_id == workflow_run_id,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def search_runs(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID | None = None,
        status: str | None = None,
        failure_category: str | None = None,
        limit: int = 50,
    ) -> list[AuditTimelineEventRecord]:
        latest_rows = (
            select(
                AuditTimelineEventRecord.workflow_run_id.label("workflow_run_id"),
                func.max(AuditTimelineEventRecord.sequence).label("latest_sequence"),
            )
            .where(AuditTimelineEventRecord.tenant_id == tenant_id)
            .group_by(AuditTimelineEventRecord.workflow_run_id)
            .subquery()
        )
        stmt = (
            select(AuditTimelineEventRecord)
            .join(
                latest_rows,
                (
                    AuditTimelineEventRecord.workflow_run_id
                    == latest_rows.c.workflow_run_id
                )
                & (AuditTimelineEventRecord.sequence == latest_rows.c.latest_sequence),
            )
            .where(
                AuditTimelineEventRecord.tenant_id == tenant_id,
            )
            .order_by(AuditTimelineEventRecord.occurred_at.desc())
            .limit(limit)
        )
        if workflow_run_id is not None:
            stmt = stmt.where(
                AuditTimelineEventRecord.workflow_run_id == workflow_run_id
            )
        if status is not None:
            stmt = stmt.where(AuditTimelineEventRecord.run_status_after == status)
        if failure_category is not None:
            stmt = stmt.where(
                AuditTimelineEventRecord.safe_details["category"].as_string()
                == failure_category
            )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_version_bundle_snapshot(
        self, payload: VersionBundleSnapshotCreate
    ) -> VersionBundleSnapshotRecord:
        existing = await self.get_version_bundle_snapshot(
            tenant_id=payload.tenant_id,
            workflow_run_id=payload.workflow_run_id,
        )
        if existing is not None:
            return existing
        record = VersionBundleSnapshotRecord(**payload.model_dump())
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_version_bundle_snapshot(
        self, *, tenant_id: UUID | None, workflow_run_id: UUID
    ) -> VersionBundleSnapshotRecord | None:
        stmt = select(VersionBundleSnapshotRecord).where(
            VersionBundleSnapshotRecord.tenant_id == tenant_id,
            VersionBundleSnapshotRecord.workflow_run_id == workflow_run_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_lineage_link(
        self, payload: RunLineageLinkCreate
    ) -> RunLineageLinkRecord:
        record = RunLineageLinkRecord(
            tenant_id=payload.tenant_id,
            source_run_id=payload.source_run_id,
            target_run_id=payload.target_run_id,
            relationship_type=payload.relationship_type.value,
            source_timeline_event_id=payload.source_timeline_event_id,
            source_trace_record_id=payload.source_trace_record_id,
            status=payload.status,
            safe_reason=payload.safe_reason,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_lineage_links(
        self, *, tenant_id: UUID | None, workflow_run_id: UUID
    ) -> list[RunLineageLinkRecord]:
        stmt = select(RunLineageLinkRecord).where(
            RunLineageLinkRecord.tenant_id == tenant_id,
            or_(
                RunLineageLinkRecord.source_run_id == workflow_run_id,
                RunLineageLinkRecord.target_run_id == workflow_run_id,
            ),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_inspection_access_event(
        self,
        *,
        tenant_id: UUID | None,
        actor_principal_id: str,
        actor_role: str,
        action: str,
        authorization_outcome: str,
        target_run_id: UUID | None = None,
        denial_category: str | None = None,
        filters: dict[str, object] | None = None,
        export_id: UUID | None = None,
        trace_id: str | None = None,
        safe_metadata: dict[str, object] | None = None,
    ) -> InspectionAccessAuditEventRecord:
        record = InspectionAccessAuditEventRecord(
            tenant_id=tenant_id,
            actor_principal_id=actor_principal_id,
            actor_role=actor_role,
            action=action,
            target_run_id=target_run_id,
            authorization_outcome=authorization_outcome,
            denial_category=denial_category,
            filters_digest=filters_digest(filters) if filters is not None else None,
            export_id=export_id,
            trace_id=trace_id,
            safe_metadata=safe_metadata or {},
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_export(
        self, payload: DebugEvidenceExportCreate
    ) -> DebugEvidenceExportRecord:
        record = DebugEvidenceExportRecord(
            tenant_id=payload.tenant_id,
            requested_by=payload.requested_by,
            workflow_run_id=payload.workflow_run_id,
            lineage_scope=payload.lineage_scope,
            recipient_scope=payload.recipient_scope,
            redaction_profile=payload.redaction_profile,
            included_sections=payload.included_sections,
            excluded_sections=payload.excluded_sections,
            expires_at=payload.expires_at,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def find_export(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        requested_by: str,
        lineage_scope: str,
        recipient_scope: str,
        included_sections: list[str],
    ) -> DebugEvidenceExportRecord | None:
        stmt = select(DebugEvidenceExportRecord).where(
            DebugEvidenceExportRecord.tenant_id == tenant_id,
            DebugEvidenceExportRecord.workflow_run_id == workflow_run_id,
            DebugEvidenceExportRecord.requested_by == requested_by,
            DebugEvidenceExportRecord.lineage_scope == lineage_scope,
            DebugEvidenceExportRecord.recipient_scope == recipient_scope,
        )
        records = list((await self.session.execute(stmt)).scalars().all())
        for record in records:
            if list(record.included_sections) == included_sections:
                return record
        return None

    async def update_export_status(
        self,
        export_id: UUID,
        status: ExportStatus,
        *,
        artifact_id: UUID | None = None,
        artifact_ref: str | None = None,
        safe_failure_reason: str | None = None,
    ) -> DebugEvidenceExportRecord:
        values: dict[str, object] = {
            "status": status.value,
            "artifact_id": artifact_id,
            "artifact_ref": artifact_ref,
            "safe_failure_reason": safe_failure_reason,
        }
        if status in {ExportStatus.AVAILABLE, ExportStatus.FAILED}:
            values["completed_at"] = datetime.now(UTC)
        await self.session.execute(
            update(DebugEvidenceExportRecord)
            .where(DebugEvidenceExportRecord.debug_evidence_export_id == export_id)
            .values(**values)
        )
        await self.session.flush()
        record = await self.session.get(DebugEvidenceExportRecord, export_id)
        if record is None:
            raise LookupError("export not found")
        return record

    async def create_secret_access_record(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        requester_type: str,
        requester_ref: str,
        secret_reference_id: str,
        policy_outcome: str,
        access_outcome: str,
        trace_id: str,
        timeline_event_id: UUID | None = None,
        trace_record_id: UUID | None = None,
        secret_reference_version: str | None = None,
        credential_scope: str | None = None,
        reason_code: str | None = None,
        safe_reason: str = "",
    ) -> SecretAccessAuditRecord:
        record = SecretAccessAuditRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            timeline_event_id=timeline_event_id,
            trace_record_id=trace_record_id,
            requester_type=requester_type,
            requester_ref=requester_ref,
            secret_reference_id=secret_reference_id,
            secret_reference_version=secret_reference_version,
            credential_scope=credential_scope,
            policy_outcome=policy_outcome,
            access_outcome=access_outcome,
            reason_code=reason_code,
            safe_reason=safe_reason,
            trace_id=trace_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record
