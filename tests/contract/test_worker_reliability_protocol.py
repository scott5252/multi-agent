from __future__ import annotations


def test_worker_context_contains_required_protocol_fields(
    worker_context: object,
) -> None:
    required = {
        "tenant_id",
        "workflow_run_id",
        "run_step_id",
        "worker_id",
        "worker_lease_id",
        "claim_attempt",
        "run_bundle_id",
        "bundle_digest",
        "trace_id",
        "policy_id",
        "policy_version",
    }
    assert required <= set(worker_context.__dataclass_fields__)
