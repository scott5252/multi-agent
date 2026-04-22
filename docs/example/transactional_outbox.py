from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class OutboxEvent:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    idempotency_key: str
    created_at: datetime


class UnitOfWork:
    """
    Tiny example showing how checkpoint writes and side-effect intents should
    commit together.
    """

    def __init__(self) -> None:
        self.workflow_rows: list[dict[str, Any]] = []
        self.outbox_rows: list[OutboxEvent] = []

    def persist_checkpoint(
        self,
        *,
        workflow_run_id: str,
        node_name: str,
        state_snapshot: dict[str, Any],
    ) -> None:
        self.workflow_rows.append(
            {
                "workflow_run_id": workflow_run_id,
                "node_name": node_name,
                "state_snapshot": state_snapshot,
                "created_at": datetime.now(timezone.utc),
            }
        )

    def enqueue_side_effect(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> None:
        self.outbox_rows.append(
            OutboxEvent(
                event_id=str(uuid4()),
                event_type=event_type,
                payload=payload,
                idempotency_key=idempotency_key or str(uuid4()),
                created_at=datetime.now(timezone.utc),
            )
        )


def persist_node_completion(uow: UnitOfWork) -> None:
    uow.persist_checkpoint(
        workflow_run_id="run-123",
        node_name="planner",
        state_snapshot={"status": "planner_complete"},
    )
    uow.enqueue_side_effect(
        event_type="telegram.reply_requested",
        payload={"chat_id": "12345", "message": "Plan is ready"},
        idempotency_key="run-123:planner:telegram",
    )
