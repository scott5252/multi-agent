from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from multi_agent_platform.audit.classification import redact_payload
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    CaptureGapRecord,
    RunLineageLinkRecord,
    VersionBundleSnapshotRecord,
)


@dataclass(frozen=True, slots=True)
class TimelineView:
    run: dict[str, object]
    events: list[dict[str, object]]
    lineage: dict[str, object]
    bundle: dict[str, object] | None
    notifications: list[dict[str, object]] = field(default_factory=list)
    capture_gaps: list[dict[str, object]] = field(default_factory=list)


def timeline_event_to_dict(
    event: AuditTimelineEventRecord, traces: Iterable[AuditRuntimeTraceRecord]
) -> dict[str, object]:
    return {
        "timeline_event_id": str(event.timeline_event_id),
        "sequence": event.sequence,
        "event_category": event.event_category,
        "run_status_after": event.run_status_after,
        "trace_id": event.trace_id,
        "correlation_id": event.correlation_id,
        "occurred_at": event.occurred_at,
        "recorded_at": event.recorded_at,
        "safe_summary": event.safe_summary,
        "safe_details": event.safe_details,
        "traces": [trace_record_to_dict(trace) for trace in traces],
    }


def trace_record_to_dict(trace: AuditRuntimeTraceRecord) -> dict[str, object]:
    return {
        "trace_record_id": str(trace.trace_record_id),
        "timeline_event_id": str(trace.timeline_event_id),
        "trace_type": trace.trace_type,
        "trace_id": trace.trace_id,
        "correlation_id": trace.correlation_id,
        "status": trace.status,
        "outcome": trace.outcome,
        "duration_ms": trace.duration_ms,
        "policy_outcome": trace.policy_outcome,
        "subject_ref": trace.subject_ref,
        "safe_input_summary": trace.safe_input_summary,
        "safe_output_summary": trace.safe_output_summary,
        "safe_error_summary": trace.safe_error_summary,
        "metadata": trace.metadata_json,
    }


def assemble_timeline(
    *,
    workflow_run_id: UUID,
    tenant_id: UUID | None,
    events: Sequence[AuditTimelineEventRecord],
    traces_by_event: dict[UUID, list[AuditRuntimeTraceRecord]],
    lineage: dict[str, object] | None = None,
    bundle: VersionBundleSnapshotRecord | None = None,
    capture_gaps: Sequence[CaptureGapRecord] | None = None,
) -> TimelineView:
    ordered = sorted(events, key=lambda event: (event.sequence, event.occurred_at))
    latest = ordered[-1] if ordered else None
    run: dict[str, object] = {
        "workflow_run_id": str(workflow_run_id),
        "tenant_id": str(tenant_id) if tenant_id else None,
        "status": latest.run_status_after if latest else "unknown",
        "trace_id": latest.trace_id if latest else None,
        "latest_event_at": latest.occurred_at if latest else None,
    }
    return TimelineView(
        run=run,
        events=[
            timeline_event_to_dict(
                event, traces_by_event.get(event.timeline_event_id, [])
            )
            for event in ordered
        ],
        lineage=lineage or {"nodes": [], "edges": []},
        bundle=bundle_to_dict(bundle) if bundle is not None else None,
        capture_gaps=[capture_gap_to_dict(gap) for gap in capture_gaps or []],
    )


def assemble_replay_events(events: list[dict[str, object]]) -> list[dict[str, object]]:
    replay: list[dict[str, object]] = []
    for event in events:
        traces = event.get("traces", [])
        trace_count = len(traces) if isinstance(traces, list) else 0
        replay.append(
            {
                "sequence": event["sequence"],
                "timestamp": event["occurred_at"],
                "event_category": event["event_category"],
                "status_after": event["run_status_after"],
                "trace_id": event["trace_id"],
                "actor": event.get("actor_principal_id") or "system",
                "safe_summary": event["safe_summary"],
                "linked_trace_count": trace_count,
                "checkpoint": event["event_category"]
                in {
                    "accepted",
                    "started",
                    "waiting",
                    "resumed",
                    "retried",
                    "failed",
                    "completed",
                    "timed_out",
                },
            }
        )
    return replay


def bundle_to_dict(bundle: VersionBundleSnapshotRecord) -> dict[str, object]:
    return {
        "version_bundle_snapshot_id": str(bundle.version_bundle_snapshot_id),
        "workflow_run_id": str(bundle.workflow_run_id),
        "bundle_digest": bundle.bundle_digest,
        "workflow_version": bundle.workflow_version,
        "contract_version_refs": bundle.contract_version_refs,
        "prompt_version_refs": bundle.prompt_version_refs,
        "model_config_version_refs": bundle.model_config_version_refs,
        "tool_policy_version_refs": bundle.tool_policy_version_refs,
        "activation_state_at_acceptance": bundle.activation_state_at_acceptance,
        "accepted_at": bundle.accepted_at,
        "migration_record_refs": bundle.migration_record_refs,
        "safe_summary": bundle.safe_summary,
    }


def capture_gap_to_dict(gap: CaptureGapRecord) -> dict[str, object]:
    return {
        "capture_gap_id": str(gap.capture_gap_id),
        "timeline_event_id": str(gap.timeline_event_id)
        if gap.timeline_event_id
        else None,
        "trace_id": gap.trace_id,
        "gap_type": gap.gap_type,
        "affected_trace_type": gap.affected_trace_type,
        "criticality": gap.criticality,
        "safe_reason": gap.safe_reason,
        "recovery_status": gap.recovery_status,
    }


def build_lineage_graph(
    *,
    workflow_run_id: UUID,
    authorized_run_ids: set[UUID],
    links: Sequence[RunLineageLinkRecord],
) -> dict[str, object]:
    nodes: dict[str, dict[str, object]] = {
        str(workflow_run_id): {
            "workflow_run_id": str(workflow_run_id),
            "redacted": False,
        }
    }
    edges: list[dict[str, object]] = []
    for link in links:
        source_allowed = link.source_run_id in authorized_run_ids
        target_allowed = link.target_run_id in authorized_run_ids
        source_id = (
            str(link.source_run_id)
            if source_allowed
            else f"redacted:{link.run_lineage_link_id}:source"
        )
        target_id = (
            str(link.target_run_id)
            if target_allowed
            else f"redacted:{link.run_lineage_link_id}:target"
        )
        nodes.setdefault(
            source_id, {"workflow_run_id": source_id, "redacted": not source_allowed}
        )
        nodes.setdefault(
            target_id, {"workflow_run_id": target_id, "redacted": not target_allowed}
        )
        edges.append(
            {
                "source": source_id,
                "target": target_id,
                "relationship_type": link.relationship_type,
                "status": link.status,
                "safe_reason": link.safe_reason,
            }
        )
    return {"nodes": list(nodes.values()), "edges": edges}


def safe_export_manifest(
    timeline: TimelineView, *, viewer_role: str, generated_at: datetime
) -> dict[str, object]:
    return redact_payload(
        {
            "generated_at": generated_at.isoformat(),
            "run": timeline.run,
            "events": timeline.events,
            "lineage": timeline.lineage,
            "bundle": timeline.bundle,
            "capture_gaps": timeline.capture_gaps,
        },
        viewer_role=viewer_role,
    )
