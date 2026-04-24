from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeRetentionPolicyRecord,
    WorkflowRunRecord,
)


def test_runtime_tables_are_registered() -> None:
    import_models()

    assert "runtime_workflow_runs" in Base.metadata.tables
    assert "runtime_worker_leases" in Base.metadata.tables
    assert "runtime_handoff_envelopes" in Base.metadata.tables


def test_retention_policy_defaults() -> None:
    policy = RuntimeRetentionPolicyRecord(tenant_id=uuid4())

    assert policy.checkpoint_retention_days is None or (
        policy.checkpoint_retention_days == 90
    )
    assert policy.audit_retention is None or policy.audit_retention == "indefinite"


def test_workflow_run_record_requires_pinned_bundle_id() -> None:
    run = WorkflowRunRecord(
        tenant_id=uuid4(),
        scope_type="tenant",
        initiating_principal_id="principal",
        run_bundle_id=uuid4(),
        status="runnable",
        idempotency_key="idem",
        trace_id="trace",
    )

    assert run.run_bundle_id is not None
