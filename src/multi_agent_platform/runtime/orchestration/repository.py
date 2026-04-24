from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from multi_agent_platform.runtime.orchestration.events import RuntimeTimelineEvent
from multi_agent_platform.runtime.orchestration.models import (
    RuntimeExecutionBundle,
    WorkflowRun,
)


@dataclass(slots=True)
class InMemoryRuntimeRepository:
    runs: dict[UUID, WorkflowRun] = field(default_factory=dict)
    bundles: dict[UUID, RuntimeExecutionBundle] = field(default_factory=dict)
    timeline: dict[UUID, list[RuntimeTimelineEvent]] = field(default_factory=dict)

    async def create_run(
        self, run: WorkflowRun, bundle: RuntimeExecutionBundle
    ) -> WorkflowRun:
        self.runs[run.workflow_run_id] = run
        self.bundles[bundle.run_bundle_id] = bundle
        return run

    async def get_run(
        self, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRun | None:
        run = self.runs.get(workflow_run_id)
        if run is None or run.tenant_id != tenant_id:
            return None
        return run

    async def add_timeline_event(self, event: RuntimeTimelineEvent) -> None:
        self.timeline.setdefault(event.workflow_run_id, []).append(event)

    async def list_timeline(
        self, workflow_run_id: UUID, tenant_id: UUID | None, limit: int = 100
    ) -> list[RuntimeTimelineEvent]:
        run = await self.get_run(workflow_run_id, tenant_id)
        if run is None:
            return []
        return self.timeline.get(workflow_run_id, [])[:limit]
