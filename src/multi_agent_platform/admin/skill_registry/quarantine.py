from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from multi_agent_platform.db.base import utcnow


@dataclass(frozen=True, slots=True)
class QuarantineDecision:
    quarantine_decision_id: str
    target_type: str
    target_id: str
    state: str
    reason: str
    actor_principal_id: str
    blocks_new_installs: bool = True
    blocks_readiness: bool = True
    blocks_bindings: bool = True
    blocks_runtime: bool = True
    safe_summary: dict[str, object] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    resolved_at: datetime | None = None


def quarantine_target(
    *,
    target_type: str,
    target_id: str,
    reason: str,
    actor_principal_id: str,
) -> QuarantineDecision:
    return QuarantineDecision(
        quarantine_decision_id=str(uuid4()),
        target_type=target_type,
        target_id=target_id,
        state="quarantined",
        reason=reason,
        actor_principal_id=actor_principal_id,
        safe_summary={"reason": reason, "target_type": target_type},
    )


def resolve_quarantine(
    decision: QuarantineDecision,
    *,
    actor_principal_id: str,
    reason: str,
) -> QuarantineDecision:
    return QuarantineDecision(
        quarantine_decision_id=decision.quarantine_decision_id,
        target_type=decision.target_type,
        target_id=decision.target_id,
        state="resolved",
        reason=reason,
        actor_principal_id=actor_principal_id,
        safe_summary={"reason": reason, "resolved_by": actor_principal_id},
        blocks_new_installs=False,
        blocks_readiness=False,
        blocks_bindings=False,
        blocks_runtime=False,
        created_at=decision.created_at,
        resolved_at=utcnow(),
    )
