from __future__ import annotations

from uuid import UUID

from multi_agent_platform.runtime.orchestration.side_effects import (
    SideEffectIntent,
    SideEffectKind,
    SideEffectRepeatability,
    SideEffectStatus,
    recovery_safety_outcome,
)
from tests.fixtures.reliability import RUN_ID, STEP_ID, TENANT_ID


def test_side_effect_recovery_suppresses_applied_duplicate() -> None:
    intent = SideEffectIntent(
        tenant_id=TENANT_ID,
        workflow_run_id=RUN_ID,
        run_step_id=STEP_ID,
        intent_kind=SideEffectKind.HTTP_REQUEST,
        idempotency_key="idem",
        tool_policy_ref="policy",
        status=SideEffectStatus.APPLIED,
    )
    assert recovery_safety_outcome(intent) == "duplicate_suppressed"


def test_side_effect_recovery_routes_ambiguous_non_repeatable_to_intervention() -> None:
    intent = SideEffectIntent(
        tenant_id=TENANT_ID,
        workflow_run_id=RUN_ID,
        run_step_id=STEP_ID,
        intent_kind=SideEffectKind.EMAIL,
        idempotency_key="idem",
        tool_policy_ref="policy",
    )
    assert recovery_safety_outcome(intent) == "operator_intervention_required"


def test_side_effect_recovery_requests_declared_compensation() -> None:
    intent = SideEffectIntent(
        tenant_id=TENANT_ID,
        workflow_run_id=RUN_ID,
        run_step_id=STEP_ID,
        intent_kind=SideEffectKind.OBJECT_STORAGE_WRITE,
        idempotency_key="idem",
        tool_policy_ref="policy",
        compensation_hook_ref="undo",
        repeatability=SideEffectRepeatability.COMPENSATABLE,
        side_effect_intent_id=UUID("00000000-0000-0000-0000-000000000701"),
    )
    assert recovery_safety_outcome(intent) == "compensation_requested"
