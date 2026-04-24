from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.contracts import sha256_digest
from multi_agent_platform.runtime.orchestration.models import now_utc


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ApprovalDecisionValue(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"


@dataclass(slots=True)
class ApprovalDecision:
    approval_gate_id: UUID
    tenant_id: UUID | None
    principal_id: str
    decision: ApprovalDecisionValue
    decision_payload: dict[str, object]
    approval_decision_id: UUID = field(default_factory=uuid4)
    accepted: bool = False
    rejection_reason: str | None = None
    created_at: datetime = field(default_factory=now_utc)

    @property
    def decision_payload_hash(self) -> str:
        return sha256_digest(self.decision_payload)


@dataclass(slots=True)
class ApprovalGate:
    tenant_id: UUID | None
    workflow_run_id: UUID
    run_step_id: UUID
    approval_key: str
    requested_action: dict[str, object]
    approver_policy: dict[str, object]
    timeout_seconds: int | None = None
    approval_gate_id: UUID = field(default_factory=uuid4)
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_id: UUID | None = None
    created_at: datetime = field(default_factory=now_utc)
    decided_at: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.timeout_seconds is not None:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout_seconds)

    def decide(self, decision: ApprovalDecision) -> ApprovalDecision:
        if self.status is not ApprovalStatus.PENDING:
            decision.rejection_reason = "approval gate already decided"
            return decision
        if not _principal_allowed(decision.principal_id, self.approver_policy):
            decision.rejection_reason = "principal is not authorized to decide"
            return decision
        if self.expires_at is not None and self.expires_at <= now_utc():
            self.status = ApprovalStatus.TIMED_OUT
            decision.rejection_reason = "approval gate timed out"
            return decision
        decision.accepted = True
        self.decision_id = decision.approval_decision_id
        self.decided_at = now_utc()
        if decision.decision is ApprovalDecisionValue.APPROVE:
            self.status = ApprovalStatus.APPROVED
        elif decision.decision is ApprovalDecisionValue.REJECT:
            self.status = ApprovalStatus.REJECTED
        else:
            self.status = ApprovalStatus.CANCELLED
        return decision

    def resume_payload(self, decision: ApprovalDecision) -> dict[str, object]:
        if not decision.accepted:
            raise ValueError("only accepted decisions can resume a graph")
        return {
            "approval_gate_id": str(self.approval_gate_id),
            "decision": decision.decision.value,
            "decision_payload": decision.decision_payload,
        }


def _principal_allowed(principal_id: str, policy: dict[str, object]) -> bool:
    allowed = policy.get("principal_ids")
    if allowed is None:
        return True
    return isinstance(allowed, list) and principal_id in allowed
