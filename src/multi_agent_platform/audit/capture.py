from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from multi_agent_platform.audit.classification import (
    build_safe_summary,
    redact_payload,
    redaction_decisions,
)
from multi_agent_platform.audit.models import (
    CaptureCriticality,
    CaptureGapCreate,
    CaptureOutcome,
    CaptureResult,
    PolicyOutcome,
    RunStatusAfter,
    TimelineEventCategory,
    TimelineEventCreate,
    TraceRecordCreate,
    TraceStatus,
    TraceType,
)
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    CaptureGapRecord,
)
from multi_agent_platform.observability.logging import audit_log_context
from multi_agent_platform.observability.metrics import record_audit_capture

logger = logging.getLogger("multi_agent_platform.audit")


class AuditCaptureError(RuntimeError):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


class AuditCaptureRepository(Protocol):
    async def create_timeline_event(
        self, payload: TimelineEventCreate
    ) -> AuditTimelineEventRecord: ...

    async def create_capture_gap(
        self, payload: CaptureGapCreate
    ) -> CaptureGapRecord: ...

    async def create_trace_record(
        self, payload: TraceRecordCreate
    ) -> AuditRuntimeTraceRecord: ...


class AuditCaptureService:
    def __init__(self, repository: AuditCaptureRepository) -> None:
        self.repository = repository

    async def record_event(self, request: TimelineEventCreate) -> CaptureResult:
        started = datetime.now(UTC)
        safe_details = redact_payload(request.safe_details, viewer_role="operator")
        decisions = redaction_decisions(request.safe_details, viewer_role="operator")
        try:
            create = request.model_copy(update={"safe_details": safe_details})
            record = await self.repository.create_timeline_event(create)
        except Exception as exc:
            if request.criticality is CaptureCriticality.SECURITY_GOVERNANCE:
                record_audit_capture(
                    event_category=request.event_category.value,
                    criticality=request.criticality.value,
                    outcome=CaptureOutcome.BLOCKED.value,
                )
                raise AuditCaptureError("audit_write_unavailable", str(exc)) from exc
            marker = await self.repository.create_capture_gap(
                CaptureGapCreate(
                    tenant_id=request.tenant_id,
                    workflow_run_id=request.workflow_run_id,
                    trace_id=request.trace_id,
                    gap_type="capture_unavailable",
                    affected_trace_type=None,
                    criticality=request.criticality,
                    safe_reason="diagnostic audit capture unavailable",
                )
            )
            return CaptureResult(
                capture_outcome=CaptureOutcome.UNAVAILABLE,
                redaction_decisions=decisions,
                unavailable_marker_id=marker.capture_gap_id,
            )
        elapsed_ms = (datetime.now(UTC) - started).total_seconds() * 1000
        record_audit_capture(
            event_category=request.event_category.value,
            criticality=request.criticality.value,
            outcome=CaptureOutcome.RECORDED.value,
        )
        logger.info(
            "audit event recorded",
            extra=audit_log_context(
                action="record_event",
                tenant_id=str(request.tenant_id) if request.tenant_id else None,
                workflow_run_id=str(request.workflow_run_id),
                trace_id=request.trace_id,
                timeline_event_id=str(record.timeline_event_id),
                event_category=request.event_category.value,
                outcome="recorded",
                duration_ms=elapsed_ms,
            )["extra"],
        )
        return CaptureResult(
            timeline_event_id=record.timeline_event_id,
            sequence=record.sequence,
            recorded_at=record.recorded_at,
            capture_outcome=CaptureOutcome.RECORDED,
            redaction_decisions=decisions,
        )

    async def record_trace(self, request: TraceRecordCreate) -> CaptureResult:
        safe_request = request.model_copy(
            update={
                "safe_input_summary": redact_payload(
                    request.safe_input_summary, viewer_role="operator"
                ),
                "safe_output_summary": redact_payload(
                    request.safe_output_summary, viewer_role="operator"
                ),
                "safe_error_summary": redact_payload(
                    request.safe_error_summary, viewer_role="operator"
                ),
                "metadata": redact_payload(request.metadata, viewer_role="operator"),
            }
        )
        record = await self.repository.create_trace_record(safe_request)
        record_audit_capture(
            event_category=request.trace_type.value,
            criticality="trace",
            outcome=CaptureOutcome.RECORDED.value,
        )
        return CaptureResult(
            timeline_event_id=request.timeline_event_id,
            trace_record_id=record.trace_record_id,
            recorded_at=record.recorded_at,
            capture_outcome=CaptureOutcome.RECORDED,
        )


def build_lifecycle_event(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    category: TimelineEventCategory,
    status_after: RunStatusAfter,
    trace_id: str,
    source_event_id: str,
    actor_principal_id: str | None = None,
    details: Mapping[str, object] | None = None,
    criticality: CaptureCriticality = CaptureCriticality.RUNTIME_REQUIRED,
) -> TimelineEventCreate:
    safe_details = build_safe_summary(details or {})
    return TimelineEventCreate(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        event_category=category,
        run_status_after=status_after,
        actor_principal_id=actor_principal_id,
        trace_id=trace_id,
        source_event_id=source_event_id,
        criticality=criticality,
        safe_summary=f"Run {category.value}",
        safe_details=safe_details,
    )


def build_failed_stage_event(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    trace_id: str,
    source_event_id: str,
    failed_stage: str,
    safe_failure_reason: str,
    investigation_category: str,
) -> TimelineEventCreate:
    return TimelineEventCreate(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        event_category=TimelineEventCategory.FAILED,
        run_status_after=RunStatusAfter.FAILED,
        trace_id=trace_id,
        source_event_id=source_event_id,
        criticality=CaptureCriticality.RUNTIME_REQUIRED,
        safe_summary=f"Run failed at {failed_stage}",
        safe_details={
            "failed_stage": failed_stage,
            "safe_reason": safe_failure_reason,
            "category": investigation_category,
        },
    )


def build_trace_record(
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    timeline_event_id: UUID,
    trace_type: TraceType,
    trace_id: str,
    subject_ref: str | None = None,
    outcome: str = "recorded",
    policy_outcome: PolicyOutcome = PolicyOutcome.NOT_APPLICABLE,
    safe_input_summary: Mapping[str, object] | None = None,
    safe_output_summary: Mapping[str, object] | None = None,
    safe_error_summary: Mapping[str, object] | None = None,
    metadata: Mapping[str, object] | None = None,
) -> TraceRecordCreate:
    return TraceRecordCreate(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        timeline_event_id=timeline_event_id,
        trace_type=trace_type,
        trace_id=trace_id,
        status=TraceStatus.RECORDED,
        outcome=outcome,
        policy_outcome=policy_outcome,
        subject_ref=subject_ref,
        safe_input_summary=build_safe_summary(safe_input_summary or {}),
        safe_output_summary=build_safe_summary(safe_output_summary or {}),
        safe_error_summary=build_safe_summary(safe_error_summary or {}),
        metadata=build_safe_summary(metadata or {}),
    )


def build_agent_handoff_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.AGENT_HANDOFF
    return build_trace_record(**kwargs)  # type: ignore[arg-type]


def build_contract_validation_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.CONTRACT_VALIDATION
    return build_trace_record(**kwargs)  # type: ignore[arg-type]


def build_memory_write_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.MEMORY_WRITE
    return build_trace_record(**kwargs)  # type: ignore[arg-type]


def build_tool_usage_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.TOOL_USAGE
    return build_trace_record(**kwargs)  # type: ignore[arg-type]


def build_model_selection_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.MODEL_SELECTION
    return build_trace_record(**kwargs)  # type: ignore[arg-type]


def build_model_gateway_trace(**kwargs: object) -> TraceRecordCreate:
    kwargs["trace_type"] = TraceType.MODEL_SELECTION
    return build_trace_record(**kwargs)  # type: ignore[arg-type]
