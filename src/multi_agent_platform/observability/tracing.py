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
