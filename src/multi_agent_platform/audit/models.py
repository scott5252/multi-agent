from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.db.models.audit import AuditActorType


class AuditEventCreate(BaseModel):
    tenant_id: UUID | None = None
    scope_type: str
    actor_type: AuditActorType = AuditActorType.SYSTEM
    actor_id: str = "system"
    action: str
    entity_type: str
    entity_id: str
    trace_id: str
    request_id: str | None = None
    payload_redacted: dict[str, str] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TimelineEventCategory(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    STARTED = "started"
    WAITING = "waiting"
    RESUMED = "resumed"
    RETRIED = "retried"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    RUNTIME_DECISION = "runtime_decision"
    AGENT_HANDOFF = "agent_handoff"
    CONTRACT_VALIDATION = "contract_validation"
    MEMORY_WRITE = "memory_write"
    TOOL_USAGE = "tool_usage"
    MODEL_SELECTION = "model_selection"
    NOTIFICATION_DELIVERY = "notification_delivery"
    SECRET_ACCESS = "secret_access"
    EXPORT = "export"
    INSPECTION_DENIED = "inspection_denied"
    CAPTURE_GAP = "capture_gap"
    CORRECTION = "correction"
    REDACTION = "redaction"
    SUPERSESSION = "supersession"


class RunStatusAfter(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    RESUMED = "resumed"
    RETRYING = "retrying"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    UNKNOWN = "unknown"


class TraceType(StrEnum):
    AGENT_HANDOFF = "agent_handoff"
    CONTRACT_VALIDATION = "contract_validation"
    MEMORY_WRITE = "memory_write"
    TOOL_USAGE = "tool_usage"
    MODEL_SELECTION = "model_selection"
    NOTIFICATION_DELIVERY = "notification_delivery"
    SECRET_ACCESS = "secret_access"
    CAPTURE_GAP = "capture_gap"
    LIFECYCLE = "lifecycle"


class TraceStatus(StrEnum):
    RECORDED = "recorded"
    UNAVAILABLE = "unavailable"
    REDACTED = "redacted"


class CaptureCriticality(StrEnum):
    SECURITY_GOVERNANCE = "security_governance"
    RUNTIME_REQUIRED = "runtime_required"
    DIAGNOSTIC = "diagnostic"


class CaptureOutcome(StrEnum):
    RECORDED = "recorded"
    IDEMPOTENT_REPLAY = "idempotent_replay"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"


class PolicyOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class InspectionAction(StrEnum):
    SEARCH = "search"
    TIMELINE = "timeline"
    REPLAY = "replay"
    LINEAGE = "lineage"
    BUNDLE = "bundle"
    EXPORT_CREATE = "export_create"
    EXPORT_READ = "export_read"
    DENIED = "denied"


class AuthorizationOutcome(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_FOUND = "not_found"


class ExportStatus(StrEnum):
    REQUESTED = "requested"
    GENERATING = "generating"
    AVAILABLE = "available"
    FAILED = "failed"
    EXPIRED = "expired"
    REVOKED = "revoked"


class LineageRelationship(StrEnum):
    PARENT_CHILD = "parent_child"
    RETRY = "retry"
    RESUMPTION = "resumption"
    DELEGATION = "delegation"


class NotificationStatus(StrEnum):
    SCHEDULED = "scheduled"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    SUPPRESSED = "suppressed"
    UNAVAILABLE = "unavailable"


class SensitivityLabel(StrEnum):
    PUBLIC_IDENTIFIER = "public_identifier"
    SAFE_METADATA = "safe_metadata"
    PROMPT_CONTENT = "prompt_content"
    MEMORY_CONTENT = "memory_content"
    CREDENTIAL = "credential"
    SECRET = "secret"
    RAW_PAYLOAD = "raw_payload"
    UNKNOWN_DYNAMIC = "unknown_dynamic"


class RedactionAction(StrEnum):
    ALLOW = "allow"
    MASK = "mask"
    SUMMARIZE = "summarize"
    DROP = "drop"


class TimelineEventCreate(BaseModel):
    tenant_id: UUID | None
    workflow_run_id: UUID
    parent_run_id: UUID | None = None
    run_step_id: UUID | None = None
    event_category: TimelineEventCategory
    run_status_after: RunStatusAfter = RunStatusAfter.UNKNOWN
    origin_type: str = "system"
    origin_ref: str | None = None
    actor_principal_id: str | None = None
    trace_id: str
    correlation_id: str | None = None
    source_event_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    criticality: CaptureCriticality = CaptureCriticality.DIAGNOSTIC
    safe_summary: str
    safe_details: dict[str, object] = Field(default_factory=dict)
    classification_version: str = "audit-debugging-v1"
    supersedes_event_id: UUID | None = None


class TraceRecordCreate(BaseModel):
    tenant_id: UUID | None
    workflow_run_id: UUID
    timeline_event_id: UUID
    run_step_id: UUID | None = None
    trace_type: TraceType
    trace_id: str
    correlation_id: str | None = None
    status: TraceStatus = TraceStatus.RECORDED
    outcome: str = "recorded"
    duration_ms: int | None = None
    policy_outcome: PolicyOutcome = PolicyOutcome.NOT_APPLICABLE
    subject_ref: str | None = None
    safe_input_summary: dict[str, object] = Field(default_factory=dict)
    safe_output_summary: dict[str, object] = Field(default_factory=dict)
    safe_error_summary: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CaptureGapCreate(BaseModel):
    tenant_id: UUID | None
    workflow_run_id: UUID
    timeline_event_id: UUID | None = None
    trace_id: str
    gap_type: str
    affected_trace_type: TraceType | None = None
    criticality: CaptureCriticality = CaptureCriticality.DIAGNOSTIC
    safe_reason: str
    recovery_status: str = "open"


class CaptureResult(BaseModel):
    timeline_event_id: UUID | None = None
    trace_record_id: UUID | None = None
    sequence: int | None = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    capture_outcome: CaptureOutcome
    redaction_decisions: dict[str, str] = Field(default_factory=dict)
    unavailable_marker_id: UUID | None = None


class VersionBundleSnapshotCreate(BaseModel):
    tenant_id: UUID | None
    workflow_run_id: UUID
    workflow_lineage_id: UUID | None = None
    workflow_version_bundle_id: UUID | None = None
    execution_bundle_id: UUID | None = None
    bundle_digest: str
    workflow_version: dict[str, object] = Field(default_factory=dict)
    contract_version_refs: dict[str, object] = Field(default_factory=dict)
    prompt_version_refs: dict[str, object] = Field(default_factory=dict)
    model_config_version_refs: dict[str, object] = Field(default_factory=dict)
    tool_policy_version_refs: dict[str, object] = Field(default_factory=dict)
    activation_state_at_acceptance: str = "active"
    accepted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    migration_record_refs: list[str] = Field(default_factory=list)
    safe_summary: dict[str, object] = Field(default_factory=dict)


class RunLineageLinkCreate(BaseModel):
    tenant_id: UUID | None
    source_run_id: UUID
    target_run_id: UUID
    relationship_type: LineageRelationship
    source_timeline_event_id: UUID | None = None
    source_trace_record_id: UUID | None = None
    status: str = "active"
    safe_reason: str = ""


class DebugEvidenceExportCreate(BaseModel):
    tenant_id: UUID | None
    requested_by: str
    workflow_run_id: UUID
    lineage_scope: str
    recipient_scope: str
    redaction_profile: str = "viewer-aware"
    included_sections: list[str] = Field(default_factory=list)
    excluded_sections: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


def agent_handoff_trace_details(
    *,
    source_agent_key: str,
    destination_agent_key: str,
    handoff_reason: str,
    handoff_outcome: str,
    handoff_contract_ref: str | None = None,
    payload_digest: str | None = None,
) -> dict[str, object]:
    return {
        "source_agent_key": source_agent_key,
        "destination_agent_key": destination_agent_key,
        "handoff_reason": handoff_reason,
        "handoff_outcome": handoff_outcome,
        "handoff_contract_ref": handoff_contract_ref,
        "payload_digest": payload_digest,
    }


def contract_validation_trace_details(
    *,
    contract_name: str,
    contract_version: str,
    validation_outcome: str,
    error_count: int = 0,
) -> dict[str, object]:
    return {
        "contract_name": contract_name,
        "contract_version": contract_version,
        "validation_outcome": validation_outcome,
        "error_count": error_count,
    }


def memory_write_trace_details(
    *,
    memory_scope_id: UUID | None,
    write_intent: str,
    write_outcome: str,
    effective_version_ref: str | None = None,
) -> dict[str, object]:
    return {
        "memory_scope_id": str(memory_scope_id) if memory_scope_id else None,
        "write_intent": write_intent,
        "write_outcome": write_outcome,
        "effective_version_ref": effective_version_ref,
    }


def tool_usage_trace_details(
    *,
    tool_id: str,
    action_category: str,
    policy_outcome: PolicyOutcome,
    execution_outcome: str,
    duration_ms: int | None = None,
) -> dict[str, object]:
    return {
        "tool_id": tool_id,
        "action_category": action_category,
        "policy_outcome": policy_outcome.value,
        "execution_outcome": execution_outcome,
        "duration_ms": duration_ms,
    }


def model_selection_trace_details(
    *,
    model_provider_key: str,
    model_id: str,
    selection_source: str,
    selection_outcome: str,
) -> dict[str, object]:
    return {
        "model_provider_key": model_provider_key,
        "model_id": model_id,
        "selection_source": selection_source,
        "selection_outcome": selection_outcome,
    }


def capture_gap_trace_details(
    *, gap_type: str, affected_trace_type: TraceType | None, safe_reason: str
) -> dict[str, object]:
    return {
        "gap_type": gap_type,
        "affected_trace_type": affected_trace_type.value
        if affected_trace_type is not None
        else None,
        "safe_reason": safe_reason,
    }
