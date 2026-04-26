from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class AuditTimelineEventRecord(Base):
    __tablename__ = "audit_timeline_events"
    __table_args__ = (
        UniqueConstraint("tenant_id", "workflow_run_id", "sequence"),
        UniqueConstraint(
            "tenant_id",
            "workflow_run_id",
            "event_category",
            "source_event_id",
            name="uq_audit_timeline_idempotency",
        ),
        Index(
            "ix_audit_timeline_tenant_run_time",
            "tenant_id",
            "workflow_run_id",
            "occurred_at",
        ),
        Index(
            "ix_audit_timeline_tenant_category_time",
            "tenant_id",
            "event_category",
            "occurred_at",
        ),
    )

    timeline_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    parent_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    sequence: Mapped[int] = mapped_column(Integer)
    event_category: Mapped[str] = mapped_column(String(64))
    run_status_after: Mapped[str] = mapped_column(String(64))
    origin_type: Mapped[str] = mapped_column(String(64), default="system")
    origin_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_principal_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    trace_id: Mapped[str] = mapped_column(String(128))
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_event_id: Mapped[str] = mapped_column(String(255))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    criticality: Mapped[str] = mapped_column(String(64))
    safe_summary: Mapped[str] = mapped_column(Text())
    safe_details: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    classification_version: Mapped[str] = mapped_column(
        String(64), default="audit-debugging-v1"
    )
    supersedes_event_id: Mapped[UUID | None] = mapped_column(nullable=True)


class AuditRuntimeTraceRecord(Base):
    __tablename__ = "audit_runtime_trace_records"
    __table_args__ = (
        Index("ix_audit_trace_tenant_run", "tenant_id", "workflow_run_id"),
        Index("ix_audit_trace_timeline", "timeline_event_id"),
        Index("ix_audit_trace_type", "tenant_id", "trace_type"),
    )

    trace_record_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    timeline_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_timeline_events.timeline_event_id", ondelete="CASCADE")
    )
    run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_type: Mapped[str] = mapped_column(String(64))
    trace_id: Mapped[str] = mapped_column(String(128))
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="recorded")
    outcome: Mapped[str] = mapped_column(String(64), default="recorded")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    policy_outcome: Mapped[str] = mapped_column(String(64), default="not_applicable")
    subject_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    safe_input_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_output_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_error_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    metadata_json: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentHandoffTraceRecord(Base):
    __tablename__ = "audit_agent_handoff_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_agent_key: Mapped[str] = mapped_column(String(128))
    destination_agent_key: Mapped[str] = mapped_column(String(128))
    handoff_reason: Mapped[str] = mapped_column(String(255))
    handoff_outcome: Mapped[str] = mapped_column(String(64))
    handoff_contract_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_schema_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_digest: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_payload_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ContractValidationTraceRecord(Base):
    __tablename__ = "audit_contract_validation_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    contract_name: Mapped[str] = mapped_column(String(128))
    contract_version: Mapped[str] = mapped_column(String(64))
    validation_target: Mapped[str] = mapped_column(String(128))
    validation_outcome: Mapped[str] = mapped_column(String(64))
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    safe_error_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    prioritized_error_codes: Mapped[list[str]] = mapped_column(JSON, default=list)


class MemoryWriteAuditTraceRecord(Base):
    __tablename__ = "audit_memory_write_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    memory_scope_id: Mapped[UUID | None] = mapped_column(nullable=True)
    write_intent: Mapped[str] = mapped_column(String(128))
    requested_version_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    effective_version_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    projection_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    write_outcome: Mapped[str] = mapped_column(String(64))
    superseded_by_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    safe_memory_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class ToolUsageTraceRecord(Base):
    __tablename__ = "audit_tool_usage_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    tool_id: Mapped[str] = mapped_column(String(128))
    tool_name: Mapped[str] = mapped_column(String(128))
    action_category: Mapped[str] = mapped_column(String(128))
    policy_decision_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    policy_outcome: Mapped[str] = mapped_column(String(64))
    execution_outcome: Mapped[str] = mapped_column(String(64))
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_input_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_output_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)


class ModelSelectionTraceRecord(Base):
    __tablename__ = "audit_model_selection_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    model_provider_key: Mapped[str] = mapped_column(String(128))
    model_id: Mapped[str] = mapped_column(String(128))
    selection_source: Mapped[str] = mapped_column(String(128))
    model_routing_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    prompt_reference_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_bundle_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    step_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    selection_outcome: Mapped[str] = mapped_column(String(64))
    safe_trace_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class NotificationDeliveryTraceRecord(Base):
    __tablename__ = "audit_notification_delivery_traces"

    trace_record_id: Mapped[UUID] = mapped_column(
        ForeignKey("audit_runtime_trace_records.trace_record_id", ondelete="CASCADE"),
        primary_key=True,
    )
    notification_delivery_attempt_id: Mapped[UUID | None] = mapped_column(nullable=True)
    destination_category: Mapped[str] = mapped_column(String(128))
    delivery_status: Mapped[str] = mapped_column(String(64))
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    latest_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    safe_failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    triggering_timeline_event_id: Mapped[UUID | None] = mapped_column(nullable=True)
    provider_correlation_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )


class SecretAccessAuditRecord(Base):
    __tablename__ = "audit_secret_access_records"
    __table_args__ = (
        Index("ix_audit_secret_access_tenant_run", "tenant_id", "workflow_run_id"),
    )

    secret_access_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    timeline_event_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_record_id: Mapped[UUID | None] = mapped_column(nullable=True)
    requester_type: Mapped[str] = mapped_column(String(64))
    requester_ref: Mapped[str] = mapped_column(String(255))
    secret_reference_id: Mapped[str] = mapped_column(String(255))
    secret_reference_version: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    credential_scope: Mapped[str | None] = mapped_column(String(128), nullable=True)
    policy_outcome: Mapped[str] = mapped_column(String(64))
    access_outcome: Mapped[str] = mapped_column(String(64))
    reason_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_reason: Mapped[str] = mapped_column(Text(), default="")
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    trace_id: Mapped[str] = mapped_column(String(128))


class VersionBundleSnapshotRecord(Base):
    __tablename__ = "audit_version_bundle_snapshots"
    __table_args__ = (UniqueConstraint("tenant_id", "workflow_run_id"),)

    version_bundle_snapshot_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    execution_bundle_id: Mapped[UUID | None] = mapped_column(nullable=True)
    bundle_digest: Mapped[str] = mapped_column(String(128))
    workflow_version: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    contract_version_refs: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    prompt_version_refs: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    model_config_version_refs: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    tool_policy_version_refs: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    activation_state_at_acceptance: Mapped[str] = mapped_column(String(64))
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    migration_record_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)


class RunLineageLinkRecord(Base):
    __tablename__ = "audit_run_lineage_links"
    __table_args__ = (
        Index("ix_audit_lineage_tenant_source", "tenant_id", "source_run_id"),
    )

    run_lineage_link_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    source_run_id: Mapped[UUID] = mapped_column(nullable=False)
    target_run_id: Mapped[UUID] = mapped_column(nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(64))
    source_timeline_event_id: Mapped[UUID | None] = mapped_column(nullable=True)
    source_trace_record_id: Mapped[UUID | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    status: Mapped[str] = mapped_column(String(64), default="active")
    safe_reason: Mapped[str] = mapped_column(Text(), default="")


class CaptureGapRecord(Base):
    __tablename__ = "audit_capture_gaps"
    __table_args__ = (
        Index("ix_audit_capture_gaps_tenant_run", "tenant_id", "workflow_run_id"),
    )

    capture_gap_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    timeline_event_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_id: Mapped[str] = mapped_column(String(128))
    gap_type: Mapped[str] = mapped_column(String(128))
    affected_trace_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    criticality: Mapped[str] = mapped_column(String(64))
    safe_reason: Mapped[str] = mapped_column(Text())
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    recovery_status: Mapped[str] = mapped_column(String(64), default="open")


class InspectionAccessAuditEventRecord(Base):
    __tablename__ = "audit_inspection_access_events"
    __table_args__ = (
        Index(
            "ix_audit_inspection_tenant_target",
            "tenant_id",
            "target_run_id",
            "created_at",
        ),
    )

    inspection_access_audit_event_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    actor_role: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    target_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    target_trace_record_id: Mapped[UUID | None] = mapped_column(nullable=True)
    authorization_outcome: Mapped[str] = mapped_column(String(64))
    denial_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    filters_digest: Mapped[str | None] = mapped_column(String(128), nullable=True)
    export_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DebugEvidenceExportRecord(Base):
    __tablename__ = "audit_debug_exports"
    __table_args__ = (
        Index("ix_audit_debug_exports_tenant_run", "tenant_id", "workflow_run_id"),
        Index("ix_audit_debug_exports_status", "tenant_id", "status"),
    )

    debug_evidence_export_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    requested_by: Mapped[str] = mapped_column(String(128))
    workflow_run_id: Mapped[UUID] = mapped_column(nullable=False)
    lineage_scope: Mapped[str] = mapped_column(String(64))
    recipient_scope: Mapped[str] = mapped_column(String(64))
    redaction_profile: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(64), default="requested")
    artifact_id: Mapped[UUID | None] = mapped_column(nullable=True)
    artifact_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    included_sections: Mapped[list[str]] = mapped_column(JSON, default=list)
    excluded_sections: Mapped[list[str]] = mapped_column(JSON, default=list)
    safe_failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class RedactionClassificationRecord(Base):
    __tablename__ = "audit_redaction_classification_records"
    __table_args__ = (
        Index(
            "ix_audit_redaction_source",
            "tenant_id",
            "source_record_type",
            "source_record_id",
        ),
    )

    redaction_classification_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    source_record_type: Mapped[str] = mapped_column(String(64))
    source_record_id: Mapped[str] = mapped_column(String(128))
    classification_version: Mapped[str] = mapped_column(String(64))
    field_name: Mapped[str] = mapped_column(String(128))
    sensitivity_label: Mapped[str] = mapped_column(String(64))
    redaction_action: Mapped[str] = mapped_column(String(64))
    viewer_role: Mapped[str] = mapped_column(String(64))
    decision_reason: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
