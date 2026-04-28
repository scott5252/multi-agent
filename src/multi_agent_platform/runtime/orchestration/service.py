from __future__ import annotations

from uuid import UUID, uuid4

from multi_agent_platform.audit.capture import (
    AuditCaptureService,
    build_lifecycle_event,
)
from multi_agent_platform.audit.models import RunStatusAfter, TimelineEventCategory
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    PinRunConfigurationRequest,
)
from multi_agent_platform.memory.models import RuntimeMemoryContext
from multi_agent_platform.memory.service import MemoryService
from multi_agent_platform.model_providers.gateway import ModelGateway
from multi_agent_platform.model_providers.models import GatewayResult
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
from multi_agent_platform.runtime.versioning import build_gateway_context_from_pins


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
        model_skill_config_service: ModelSkillConfigService | None = None,
        principal_context: PrincipalContext | None = None,
        audit_capture_service: AuditCaptureService | None = None,
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
        if (
            tenant_id is not None
            and model_skill_config_service is not None
            and principal_context is not None
        ):
            await model_skill_config_service.pin_run_configuration(
                principal=principal_context,
                request=PinRunConfigurationRequest(
                    tenant_id=tenant_id,
                    workflow_run_id=workflow_run_id,
                    run_bundle_id=bundle.run_bundle_id,
                    bundle_digest=bundle.bundle_digest,
                    workflow_lineage_id=None,
                    workflow_version_bundle_id=published_workflow_version_id,
                    initiating_principal_id=principal_context.principal_identity_id,
                    trace_id=run.trace_id,
                ),
            )
        await self.repository.add_timeline_event(
            RuntimeTimelineEvent(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_type=RuntimeEventType.START,
                trace_id=run.trace_id,
                payload={"status": run.status.value},
            )
        )
        if audit_capture_service is not None:
            await audit_capture_service.record_event(
                build_lifecycle_event(
                    tenant_id=tenant_id,
                    workflow_run_id=workflow_run_id,
                    category=TimelineEventCategory.ACCEPTED,
                    status_after=RunStatusAfter.QUEUED,
                    trace_id=run.trace_id,
                    source_event_id=f"runtime-start:{workflow_run_id}",
                    actor_principal_id=principal_id,
                    details={"bundle_digest": bundle.bundle_digest},
                )
            )
        return run

    async def pin_dynamic_agent_first_use(
        self,
        *,
        tenant_id: UUID,
        workflow_run_id: UUID,
        agent_key: str,
        agent_kind: str,
        agent_profile_version_id: UUID,
        prompt_version_ids: list[UUID],
        trace_id: str,
    ) -> None:
        await self.repository.add_timeline_event(
            RuntimeTimelineEvent(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                event_type=RuntimeEventType.CHECKPOINT,
                trace_id=trace_id,
                payload={
                    "runtime_pin_type": "dynamic_first_use",
                    "agent_key": agent_key,
                    "agent_kind": agent_kind,
                    "agent_profile_version_id": str(agent_profile_version_id),
                    "prompt_version_ids": [str(value) for value in prompt_version_ids],
                },
            )
        )

    async def invoke_model_gateway_step(
        self,
        *,
        model_gateway: ModelGateway,
        connection_id: UUID,
        model_id: str,
        messages: tuple[dict[str, str], ...],
        tenant_id: UUID,
        workflow_run_id: UUID,
        workflow_run_step_id: UUID,
        trace_id: str,
        idempotency_key: str,
        agent_key: str,
        agent_kind: str,
        agent_profile_version_id: UUID,
        prompt_version_ids: tuple[UUID, ...],
        prompt_reference_version_ids: tuple[UUID, ...],
        model_routing_provenance: dict[str, object],
        profile_provenance: dict[str, object] | None = None,
        memory_policy_context: dict[str, object] | None = None,
        tool_policy_expectations: dict[str, object] | None = None,
        output_contract_metadata: dict[str, object] | None = None,
    ) -> GatewayResult:
        context = build_gateway_context_from_pins(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            workflow_run_step_id=workflow_run_step_id,
            trace_id=trace_id,
            idempotency_key=idempotency_key,
            agent_key=agent_key,
            agent_kind=agent_kind,
            agent_profile_version_id=agent_profile_version_id,
            prompt_version_ids=prompt_version_ids,
            prompt_reference_version_ids=prompt_reference_version_ids,
            model_routing_provenance=model_routing_provenance,
            profile_provenance=profile_provenance,
            memory_policy_context=memory_policy_context,
            tool_policy_expectations=tool_policy_expectations,
            output_contract_metadata=output_contract_metadata,
        )
        return await model_gateway.invoke(
            connection_id=connection_id,
            model_id=model_id,
            messages=messages,
            context=context,
        )

    async def inspect_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRun | None:
        return await self.repository.get_run(workflow_run_id, tenant_id)

    async def cancel_run(
        self,
        *,
        workflow_run_id: UUID,
        tenant_id: UUID | None,
        reason: str,
        audit_capture_service: AuditCaptureService | None = None,
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
        if audit_capture_service is not None:
            await audit_capture_service.record_event(
                build_lifecycle_event(
                    tenant_id=tenant_id,
                    workflow_run_id=workflow_run_id,
                    category=TimelineEventCategory.CANCELLED,
                    status_after=RunStatusAfter.CANCELLED,
                    trace_id=run.trace_id,
                    source_event_id=f"runtime-cancel:{workflow_run_id}",
                    details={"safe_reason": reason},
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
