from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.approvals import (
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalGate,
    ApprovalStatus,
)
from multi_agent_platform.runtime.orchestration.models import now_utc


def test_approval_accepts_first_authorized_decision() -> None:
    gate = ApprovalGate(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        approval_key="human-review",
        requested_action={"summary": "approve?"},
        approver_policy={"principal_ids": ["alice"]},
    )
    decision = ApprovalDecision(
        approval_gate_id=gate.approval_gate_id,
        tenant_id=gate.tenant_id,
        principal_id="alice",
        decision=ApprovalDecisionValue.APPROVE,
        decision_payload={"approved": True},
    )

    accepted = gate.decide(decision)

    assert accepted.accepted
    assert gate.status is ApprovalStatus.APPROVED
    assert gate.resume_payload(accepted)["decision"] == "approve"


def test_approval_rejects_unauthorized_decision() -> None:
    gate = ApprovalGate(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        approval_key="human-review",
        requested_action={},
        approver_policy={"principal_ids": ["alice"]},
    )
    decision = ApprovalDecision(
        approval_gate_id=gate.approval_gate_id,
        tenant_id=gate.tenant_id,
        principal_id="bob",
        decision=ApprovalDecisionValue.REJECT,
        decision_payload={},
    )

    rejected = gate.decide(decision)

    assert not rejected.accepted
    assert rejected.rejection_reason == "principal is not authorized to decide"
    assert gate.status is ApprovalStatus.PENDING


def test_approval_rejects_duplicate_and_late_decisions() -> None:
    gate = ApprovalGate(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        approval_key="human-review",
        requested_action={},
        approver_policy={},
        timeout_seconds=1,
    )
    gate.expires_at = now_utc()
    late = ApprovalDecision(
        approval_gate_id=gate.approval_gate_id,
        tenant_id=gate.tenant_id,
        principal_id="alice",
        decision=ApprovalDecisionValue.APPROVE,
        decision_payload={},
    )

    assert gate.decide(late).rejection_reason == "approval gate timed out"

    decided_gate = ApprovalGate(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        approval_key="human-review",
        requested_action={},
        approver_policy={},
    )
    first = ApprovalDecision(
        approval_gate_id=decided_gate.approval_gate_id,
        tenant_id=decided_gate.tenant_id,
        principal_id="alice",
        decision=ApprovalDecisionValue.CANCEL,
        decision_payload={},
    )
    second = ApprovalDecision(
        approval_gate_id=decided_gate.approval_gate_id,
        tenant_id=decided_gate.tenant_id,
        principal_id="alice",
        decision=ApprovalDecisionValue.REJECT,
        decision_payload={},
    )

    decided_gate.decide(first)

    assert decided_gate.status is ApprovalStatus.CANCELLED
    assert (
        decided_gate.decide(second).rejection_reason == "approval gate already decided"
    )
