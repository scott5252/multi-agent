from __future__ import annotations

from collections.abc import Mapping

BUILDER_METRIC_PREFIX = "workflow_builder"
BUILDER_ACTIONS = {
    "draft_save": "workflow_builder_draft_save_total",
    "validation": "workflow_builder_validation_total",
    "publish_gate": "workflow_builder_publish_gate_total",
    "publish": "workflow_builder_publish_total",
    "conflict": "workflow_builder_conflict_total",
    "denial": "workflow_builder_denial_total",
    "reference_lookup_denial": "workflow_builder_reference_lookup_denial_total",
}


def builder_log_context(
    *,
    action: str,
    scope_type: str,
    trace_id: str,
    request_id: str | None = None,
    workflow_draft_id: str | None = None,
    workflow_draft_revision_id: str | None = None,
    validation_result_id: str | None = None,
    publish_gate_id: str | None = None,
    outcome: str | None = None,
) -> dict[str, str]:
    context = {
        "builder_action": action,
        "scope_type": scope_type,
        "trace_id": trace_id,
    }
    optional = {
        "request_id": request_id,
        "workflow_draft_id": workflow_draft_id,
        "workflow_draft_revision_id": workflow_draft_revision_id,
        "validation_result_id": validation_result_id,
        "publish_gate_id": publish_gate_id,
        "outcome": outcome,
    }
    context.update(
        {key: value for key, value in optional.items() if isinstance(value, str)}
    )
    return context


def safe_observability_payload(
    payload: Mapping[str, object],
) -> dict[str, str]:
    safe: dict[str, str] = {}
    for key, value in payload.items():
        lowered = key.lower()
        if any(marker in lowered for marker in ("secret", "token", "credential")):
            continue
        if value is None:
            continue
        safe[str(key)] = str(value)
    return safe
