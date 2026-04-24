from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.models import now_utc


class LineageReason(StrEnum):
    SUBWORKFLOW = "subworkflow"
    COMPENSATION = "compensation"
    MANUAL_RESUME = "manual_resume"
    REPLAY = "replay"


@dataclass(slots=True)
class RunLineage:
    tenant_id: UUID | None
    parent_run_id: UUID
    parent_step_id: UUID
    child_run_id: UUID
    relationship_reason: LineageReason = LineageReason.SUBWORKFLOW
    join_policy: str = "wait_all"
    child_cancellation_policy: str = "cascade_cancel"
    run_lineage_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)
    resolved_at: datetime | None = None

    def assert_same_tenant(self, child_tenant_id: UUID | None) -> None:
        if child_tenant_id != self.tenant_id:
            raise ValueError("parent and child runs must share tenant")

    def resolve(self) -> None:
        self.resolved_at = now_utc()
