from __future__ import annotations

from uuid import uuid4


def generate_trace_id() -> str:
    return uuid4().hex


def runtime_trace_attributes(
    *, workflow_run_id: str, tenant_id: str | None, bundle_digest: str | None
) -> dict[str, str]:
    attributes = {"workflow_run_id": workflow_run_id}
    if tenant_id is not None:
        attributes["tenant_id"] = tenant_id
    if bundle_digest is not None:
        attributes["bundle_digest"] = bundle_digest
    return attributes


def memory_trace_attributes(
    *,
    action: str,
    outcome: str,
    tenant_id: str | None = None,
    workflow_lineage_id: str | None = None,
    memory_scope_id: str | None = None,
    memory_version_id: str | None = None,
    workflow_run_id: str | None = None,
    run_bundle_id: str | None = None,
    bundle_digest: str | None = None,
) -> dict[str, str]:
    attributes = {"action": action, "outcome": outcome}
    optional = {
        "tenant_id": tenant_id,
        "workflow_lineage_id": workflow_lineage_id,
        "memory_scope_id": memory_scope_id,
        "memory_version_id": memory_version_id,
        "workflow_run_id": workflow_run_id,
        "run_bundle_id": run_bundle_id,
        "bundle_digest": bundle_digest,
    }
    attributes.update({key: value for key, value in optional.items() if value})
    return attributes


def channel_trace_attributes(
    *,
    action: str,
    channel: str,
    outcome: str,
    tenant_id: str | None = None,
    run_id: str | None = None,
    prompt_id: str | None = None,
    artifact_id: str | None = None,
) -> dict[str, str]:
    attributes = {
        "action": action,
        "channel": channel,
        "outcome": outcome,
    }
    optional = {
        "tenant_id": tenant_id,
        "run_id": run_id,
        "prompt_id": prompt_id,
        "artifact_id": artifact_id,
    }
    attributes.update({key: value for key, value in optional.items() if value})
    return attributes


def model_skill_trace_attributes(
    *,
    action: str,
    outcome: str,
    tenant_id: str | None = None,
    workflow_run_id: str | None = None,
    run_step_id: str | None = None,
    decision_category: str | None = None,
    resolution_digest: str | None = None,
) -> dict[str, str]:
    attributes = {"action": action, "outcome": outcome}
    optional = {
        "tenant_id": tenant_id,
        "workflow_run_id": workflow_run_id,
        "run_step_id": run_step_id,
        "decision_category": decision_category,
        "resolution_digest": resolution_digest,
    }
    attributes.update({key: value for key, value in optional.items() if value})
    return attributes


def model_provider_trace_attributes(
    *,
    action: str,
    outcome: str,
    provider_type: str | None = None,
    connection_id: str | None = None,
    model_id: str | None = None,
    tenant_id: str | None = None,
    normalized_error: str | None = None,
    usage_available: str | None = None,
) -> dict[str, str]:
    attributes = {"action": action, "outcome": outcome}
    optional = {
        "provider_type": provider_type,
        "connection_id": connection_id,
        "model_id": model_id,
        "tenant_id": tenant_id,
        "normalized_error": normalized_error,
        "usage_available": usage_available,
    }
    attributes.update({key: value for key, value in optional.items() if value})
    return attributes


def audit_trace_attributes(
    *,
    action: str,
    workflow_run_id: str,
    tenant_id: str | None,
    trace_id: str,
    correlation_id: str | None = None,
    timeline_event_id: str | None = None,
    trace_record_id: str | None = None,
) -> dict[str, str]:
    attributes = {
        "action": action,
        "workflow_run_id": workflow_run_id,
        "trace_id": trace_id,
    }
    optional = {
        "tenant_id": tenant_id,
        "correlation_id": correlation_id,
        "timeline_event_id": timeline_event_id,
        "trace_record_id": trace_record_id,
    }
    attributes.update({key: value for key, value in optional.items() if value})
    return attributes


def propagate_correlation_id(
    trace_id: str, correlation_id: str | None = None
) -> dict[str, str]:
    return {"trace_id": trace_id, "correlation_id": correlation_id or trace_id}
