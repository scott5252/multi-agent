from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class GraphRuntimeState(BaseModel):
    workflow_run_id: UUID
    tenant_id: UUID | None = None
    bundle_digest: str
    current_step_key: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, Any]] = Field(default_factory=list)

    def thread_config(self) -> dict[str, dict[str, str]]:
        return {"configurable": {"thread_id": str(self.workflow_run_id)}}
