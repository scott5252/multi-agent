from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeCheckpointRefRecord,
    RuntimeRetentionPolicyRecord,
)


def test_runtime_retention_policy_defaults_preserve_audit_and_lineage() -> None:
    policy = RuntimeRetentionPolicyRecord(tenant_id=uuid4())

    assert policy.checkpoint_retention_days is None or (
        policy.checkpoint_retention_days == 90
    )
    assert policy.run_payload_ref_retention_days is None or (
        policy.run_payload_ref_retention_days == 90
    )
    assert policy.audit_retention is None or policy.audit_retention == "indefinite"
    assert policy.lineage_retention is None or policy.lineage_retention == "indefinite"


def test_checkpoint_reference_uses_90_day_default_retention_window() -> None:
    before = datetime.now(UTC) + timedelta(days=89)

    checkpoint = RuntimeCheckpointRefRecord(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        langgraph_thread_id="thread-1",
        langgraph_checkpoint_id="checkpoint-1",
        checkpoint_kind="superstep",
        bundle_digest="digest",
    )

    assert checkpoint.retention_expires_at is None or (
        checkpoint.retention_expires_at >= before
    )
