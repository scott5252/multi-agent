from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.side_effects import (
    SideEffectIntent,
    SideEffectKind,
    SideEffectStatus,
    make_idempotency_key,
)


def test_idempotency_key_is_deterministic() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    step_id = uuid4()

    first = make_idempotency_key(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        run_step_id=step_id,
        bundle_digest="digest",
        operation_kind="tool",
        attempt=1,
    )
    second = make_idempotency_key(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        run_step_id=step_id,
        bundle_digest="digest",
        operation_kind="tool",
        attempt=1,
    )

    assert first == second


def test_applied_side_effect_reuses_recorded_result() -> None:
    intent = SideEffectIntent(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        intent_kind=SideEffectKind.TOOL_CALL,
        idempotency_key="idem",
        tool_policy_ref="policy",
    )

    intent.begin()
    intent.mark_applied({"value": 42})

    assert intent.status is SideEffectStatus.APPLIED
    assert intent.reuse_applied_result() == {"value": 42}
