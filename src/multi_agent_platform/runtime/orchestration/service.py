from __future__ import annotations

from uuid import UUID, uuid4

from multi_agent_platform.memory.models import RuntimeMemoryContext
from multi_agent_platform.memory.service import MemoryService
from multi_agent_platform.observability.tracing import generate_trace_id
from multi_agent_platform.runtime.orchestration.compiler import (
    PublishedWorkflowBundle,
    clone_execution_bundle,
)
from multi_agent_platform.runtime.orchestration.events import (
    RuntimeEventType,
    RuntimeTimelineEvent,
)
from multi_agent_platform.runtime.orchestration.models import RunStatus, WorkflowRun
from multi_agent_platform.runtime.orchestration.repository import (
    InMemoryRuntimeRepository,
)


class RuntimeOrchestrationService:
    def __init__(self, repository: InMemoryRuntimeRepository | None = None) -> None:
        self.repository = repository or InMemoryRuntimeRepository()

    async def start_run(
        self,
        *,
        tenant_id: UUID | None,
        scope_type: str,
        principal_id: str,
        published_workflow_version_id: UUID,
        input_payload: dict[str, object],
        idempotency_key: str | None,
        trace_id: str | None = None,
    ) -> WorkflowRun:
        workflow_run_id = uuid4()
        published_bundle = PublishedWorkflowBundle(
            published_workflow_version_id=published_workflow_version_id,
            workflow={"input": input_payload},
            contracts={},
            retry_policy={"max_attempts": 3},
            checkpoint_policy={"semantic_boundaries": True},
        )
        bundle = clone_execution_bundle(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            published_bundle=published_bundle,
        )
        run = WorkflowRun(
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            scope_type=scope_type,
            initiating_principal_id=principal_id,
            run_bundle_id=bundle.run_bundle_id,
            bundle_digest=bundle.bundle_digest,
            idempotency_key=idempotency_key or str(workflow_run_id),
            trace_id=trace_id or generate_trace_id(),
            status=RunStatus.RUNNABLE,
        )
        await self.repository.create_run(run, bundle)
        await self.repository.add_timeline_event(
            RuntimeTimelineEvent(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_type=RuntimeEventType.START,
                trace_id=run.trace_id,
                payload={"status": run.status.value},
            )
        )
        return run

    async def inspect_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRun | None:
        return await self.repository.get_run(workflow_run_id, tenant_id)

    async def cancel_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None, reason: str
    ) -> WorkflowRun:
        run = await self.repository.get_run(workflow_run_id, tenant_id)
        if run is None:
            raise LookupError("run not found")
        run.transition(RunStatus.CANCELLED, reason=reason)
        await self.repository.add_timeline_event(
            RuntimeTimelineEvent(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_type=RuntimeEventType.CANCEL,
                trace_id=run.trace_id,
                payload={"reason": reason},
            )
        )
        return run

    async def get_current_memory_head(
        self,
        *,
        memory_service: MemoryService,
        context: RuntimeMemoryContext,
    ) -> object:
        return await memory_service.get_current_head_for_runtime(context=context)

    async def write_memory_version(
        self,
        *,
        memory_service: MemoryService,
        context: RuntimeMemoryContext,
        content: object,
        expected_current_version_id: UUID | None,
        assert_no_current_head: bool,
        idempotency_key: str | None,
    ) -> object:
        result = await memory_service.write_version_for_runtime(
            context=context,
            content=content,
            expected_current_version_id=expected_current_version_id,
            assert_no_current_head=assert_no_current_head,
            idempotency_key=idempotency_key,
        )
        await self.repository.add_timeline_event(
            RuntimeTimelineEvent(
                tenant_id=context.tenant_id,
                workflow_run_id=context.workflow_run_id,
                event_type=RuntimeEventType.CHECKPOINT,
                trace_id=context.trace_id,
                payload={
                    "memory_action": "create_version",
                    "memory_scope_id": str(result.scope.memory_scope_id),
                    "memory_version_id": str(result.version.memory_version_id),
                    "content_sha256": result.version.content_sha256,
                },
            )
        )
        return result
