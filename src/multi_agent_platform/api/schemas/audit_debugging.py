from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class VersionBundleSummary(BaseModel):
    bundle_digest: str | None = None
    workflow_version: dict[str, object] = Field(default_factory=dict)
    activation_state_at_acceptance: str | None = None


class VersionBundleSnapshot(VersionBundleSummary):
    version_bundle_snapshot_id: UUID | None = None
    workflow_run_id: UUID
    contract_version_refs: dict[str, object] = Field(default_factory=dict)
    prompt_version_refs: dict[str, object] = Field(default_factory=dict)
    model_config_version_refs: dict[str, object] = Field(default_factory=dict)
    tool_policy_version_refs: dict[str, object] = Field(default_factory=dict)
    accepted_at: datetime | None = None
    migration_record_refs: list[str] = Field(default_factory=list)
    safe_summary: dict[str, object] = Field(default_factory=dict)


class RuntimeTraceRecordResponse(BaseModel):
    trace_record_id: UUID
    timeline_event_id: UUID
    trace_type: str
    trace_id: str
    correlation_id: str | None = None
    status: str
    outcome: str
    duration_ms: int | None = None
    policy_outcome: str
    subject_ref: str | None = None
    safe_input_summary: dict[str, object] = Field(default_factory=dict)
    safe_output_summary: dict[str, object] = Field(default_factory=dict)
    safe_error_summary: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class TimelineEventResponse(BaseModel):
    timeline_event_id: UUID
    sequence: int
    event_category: str
    run_status_after: str
    trace_id: str
    correlation_id: str | None = None
    occurred_at: datetime
    recorded_at: datetime
    safe_summary: str
    safe_details: dict[str, object] = Field(default_factory=dict)
    traces: list[RuntimeTraceRecordResponse] = Field(default_factory=list)


class CaptureGapResponse(BaseModel):
    capture_gap_id: UUID
    timeline_event_id: UUID | None = None
    trace_id: str
    gap_type: str
    affected_trace_type: str | None = None
    criticality: str
    safe_reason: str
    recovery_status: str


class RunSummary(BaseModel):
    workflow_run_id: UUID
    tenant_id: UUID | None = None
    status: str
    trace_id: str | None = None
    latest_event_at: datetime | None = None
    failure_category: str | None = None
    safe_failure_reason: str | None = None


class LineageNode(BaseModel):
    workflow_run_id: str
    redacted: bool = False
    status: str | None = None


class LineageEdge(BaseModel):
    source: str
    target: str
    relationship_type: str
    status: str
    safe_reason: str = ""


class RunLineageGraphResponse(BaseModel):
    nodes: list[LineageNode]
    edges: list[LineageEdge]


class NotificationDeliveryState(BaseModel):
    destination_category: str
    delivery_status: str
    attempt_count: int = 0
    latest_attempt_at: datetime | None = None
    safe_failure_reason: str | None = None
    provider_correlation_ref: str | None = None


class RunTimelineResponse(BaseModel):
    run: RunSummary
    events: list[TimelineEventResponse]
    lineage: RunLineageGraphResponse
    bundle: VersionBundleSnapshot | None = None
    notifications: list[NotificationDeliveryState] = Field(default_factory=list)
    capture_gaps: list[CaptureGapResponse] = Field(default_factory=list)


class ReplayEvent(BaseModel):
    sequence: int
    timestamp: datetime
    event_category: str
    status_after: str
    trace_id: str
    actor: str
    safe_summary: str
    linked_trace_count: int
    checkpoint: bool


class RunReplayResponse(BaseModel):
    workflow_run_id: UUID
    tenant_id: UUID | None = None
    events: list[ReplayEvent]


class RunDebugSearchItem(BaseModel):
    workflow_run_id: UUID
    tenant_id: UUID | None = None
    workflow_id: str = "unknown"
    status: str
    started_at: datetime
    latest_event_at: datetime
    trace_id: str
    failure_category: str | None = None
    bundle: VersionBundleSummary = Field(default_factory=VersionBundleSummary)


class RunDebugSearchResponse(BaseModel):
    items: list[RunDebugSearchItem]
    next_cursor: str | None = None


class CreateDebugEvidenceExportRequest(BaseModel):
    tenant_id: UUID | None = None
    recipient_scope: str
    lineage_scope: str = "run_only"
    included_sections: list[str] = Field(default_factory=list)
    excluded_sections: list[str] = Field(default_factory=list)
    reason: str


class DebugEvidenceExport(BaseModel):
    debug_evidence_export_id: UUID
    tenant_id: UUID | None = None
    requested_by: str
    workflow_run_id: UUID
    lineage_scope: str
    recipient_scope: str
    redaction_profile: str
    status: str
    artifact_id: UUID | None = None
    artifact_ref: str | None = None
    included_sections: list[str] = Field(default_factory=list)
    excluded_sections: list[str] = Field(default_factory=list)
    safe_failure_reason: str | None = None
    requested_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime | None = None


class InspectionError(BaseModel):
    category: str
    message: str
    trace_id: str | None = None
