from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.checkpointing import (
    CheckpointKind,
    RuntimeCheckpointReference,
    assert_checkpoint_compatible,
    default_retention_expires_at,
)


def test_checkpoint_reference_uses_run_thread_and_bundle_digest() -> None:
    run_id = uuid4()
    checkpoint = RuntimeCheckpointReference(
        tenant_id=uuid4(),
        workflow_run_id=run_id,
        langgraph_thread_id=str(run_id),
        langgraph_checkpoint_id="checkpoint-1",
        checkpoint_kind=CheckpointKind.SUPERSTEP,
        bundle_digest="digest",
        retention_expires_at=default_retention_expires_at(),
    )

    assert checkpoint.langgraph_thread_id == str(run_id)
    assert_checkpoint_compatible(
        checkpoint_bundle_digest=checkpoint.bundle_digest,
        run_bundle_digest="digest",
    )
