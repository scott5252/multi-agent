from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.models import now_utc


class CheckpointKind(StrEnum):
    RUN_START = "run_start"
    SUPERSTEP = "superstep"
    HANDOFF = "handoff"
    SIDE_EFFECT = "side_effect"
    APPROVAL_WAIT = "approval_wait"
    APPROVAL_RESUME = "approval_resume"
    CHILD_START = "child_start"
    CHILD_COMPLETE = "child_complete"
    TERMINAL = "terminal"


@dataclass(slots=True, frozen=True)
class RuntimeCheckpointReference:
    tenant_id: UUID | None
    workflow_run_id: UUID
    langgraph_thread_id: str
    langgraph_checkpoint_id: str
    checkpoint_kind: CheckpointKind
    bundle_digest: str
    run_step_id: UUID | None = None
    runtime_checkpoint_ref_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=now_utc)
    retention_expires_at: datetime | None = None


def default_retention_expires_at(days: int = 90) -> datetime:
    return now_utc() + timedelta(days=days)


def assert_checkpoint_compatible(
    *, checkpoint_bundle_digest: str, run_bundle_digest: str
) -> None:
    if checkpoint_bundle_digest != run_bundle_digest:
        raise ValueError("checkpoint bundle digest does not match pinned run bundle")


class LangGraphCheckpointerFactory:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    async def create_async_postgres_saver(self) -> object:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        return AsyncPostgresSaver.from_conn_string(self.database_url)
