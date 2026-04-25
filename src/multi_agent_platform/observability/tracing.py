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
