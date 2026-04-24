from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.side_effects import (
    SideEffectIntent,
    SideEffectKind,
    make_idempotency_key,
)


def test_resume_reuses_applied_side_effect_result() -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    step_id = uuid4()
    key = make_idempotency_key(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        run_step_id=step_id,
        bundle_digest="digest",
        operation_kind="tool_call",
        attempt=1,
    )
    intent = SideEffectIntent(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        run_step_id=step_id,
        intent_kind=SideEffectKind.TOOL_CALL,
        idempotency_key=key,
        tool_policy_ref="policy",
    )
    intent.begin()
    intent.mark_applied({"external_id": "ok"})

    assert intent.reuse_applied_result() == {"external_id": "ok"}
