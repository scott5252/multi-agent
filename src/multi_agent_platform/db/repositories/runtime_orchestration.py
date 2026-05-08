from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.runtime_orchestration import (
    ApprovalGateRecord,
    HandoffEnvelopeRecord,
    RunStepRecord,
    RuntimeCheckpointRefRecord,
    RuntimeExecutionBundleRecord,
    RuntimeHandoffStatus,
    RuntimeRetentionPolicyRecord,
    RuntimeRunStatus,
    RuntimeSideEffectStatus,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    RuntimeWorkerLeaseStatus,
    SideEffectIntentRecord,
    WorkerLeaseRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.runtime.orchestration.contracts import sha256_digest


class RuntimeOrchestrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        *,
        run: WorkflowRunRecord,
        bundle: RuntimeExecutionBundleRecord,
    ) -> WorkflowRunRecord:
        self.session.add(bundle)
        await self.session.flush()
        run.run_bundle_id = bundle.run_bundle_id
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRunRecord | None:
        stmt = select(WorkflowRunRecord).where(
            WorkflowRunRecord.workflow_run_id == workflow_run_id,
            WorkflowRunRecord.tenant_id == tenant_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_run_by_id(self, *, workflow_run_id: UUID) -> WorkflowRunRecord | None:
        return await self.session.get(WorkflowRunRecord, workflow_run_id)

    async def list_recent_runs(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 12
    ) -> list[WorkflowRunRecord]:
        stmt = select(WorkflowRunRecord)
        if not platform_scope:
            stmt = stmt.where(WorkflowRunRecord.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(WorkflowRunRecord.tenant_id == tenant_id)
        stmt = stmt.order_by(WorkflowRunRecord.updated_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_execution_bundle(
        self, *, run_bundle_id: UUID
    ) -> RuntimeExecutionBundleRecord | None:
        return await self.session.get(RuntimeExecutionBundleRecord, run_bundle_id)

    async def get_workflow_version_bundle(
        self, *, workflow_version_bundle_id: UUID
    ) -> WorkflowVersionBundle | None:
        return await self.session.get(WorkflowVersionBundle, workflow_version_bundle_id)

    async def list_timeline(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None, limit: int = 100
    ) -> list[RuntimeTimelineEventRecord]:
        stmt = (
            select(RuntimeTimelineEventRecord)
            .where(
                RuntimeTimelineEventRecord.workflow_run_id == workflow_run_id,
                RuntimeTimelineEventRecord.tenant_id == tenant_id,
            )
            .order_by(RuntimeTimelineEventRecord.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def create_timeline_event(
        self, event: RuntimeTimelineEventRecord
    ) -> RuntimeTimelineEventRecord:
        self.session.add(event)
        await self.session.flush()
        return event

    async def create_graph_timeline_event(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        run_step_id: UUID | None = None,
        event_type: str,
        payload: dict[str, object],
        trace_id: str,
        severity: str = "info",
    ) -> RuntimeTimelineEventRecord:
        return await self.create_timeline_event(
            RuntimeTimelineEventRecord(
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                run_step_id=run_step_id,
                event_type=event_type,
                severity=severity,
                payload=payload,
                trace_id=trace_id,
            )
        )

    async def list_run_steps(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[RunStepRecord]:
        stmt = (
            select(RunStepRecord)
            .where(
                RunStepRecord.workflow_run_id == workflow_run_id,
                RunStepRecord.tenant_id == tenant_id,
            )
            .order_by(RunStepRecord.created_at.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_latest_run_step(
        self, *, workflow_run_id: UUID, step_key: str
    ) -> RunStepRecord | None:
        stmt = (
            select(RunStepRecord)
            .where(
                RunStepRecord.workflow_run_id == workflow_run_id,
                RunStepRecord.step_key == step_key,
            )
            .order_by(RunStepRecord.attempt.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_run_step(
        self,
        *,
        workflow_run_id: UUID,
        tenant_id: UUID | None,
        step_key: str,
        step_type: str,
        status: RuntimeStepStatus,
        input_ref: dict[str, object] | None = None,
    ) -> RunStepRecord:
        latest = await self.get_latest_run_step(
            workflow_run_id=workflow_run_id,
            step_key=step_key,
        )
        attempt = 1 if latest is None else latest.attempt + 1
        record = RunStepRecord(
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            step_key=step_key,
            step_type=step_type,
            status=status,
            attempt=attempt,
            input_ref=input_ref,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update_run_step(
        self,
        *,
        run_step_id: UUID,
        status: RuntimeStepStatus,
        output_ref: dict[str, object] | None = None,
        error_ref: dict[str, object] | None = None,
    ) -> RunStepRecord:
        record = await self.session.get(RunStepRecord, run_step_id)
        if record is None:
            raise LookupError("run step not found")
        record.status = status
        if output_ref is not None:
            record.output_ref = output_ref
        if error_ref is not None:
            record.error_ref = error_ref
        if status in {
            RuntimeStepStatus.SUCCEEDED,
            RuntimeStepStatus.FAILED,
            RuntimeStepStatus.CANCELLED,
            RuntimeStepStatus.PAUSED,
        }:
            record.finished_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def update_run_status(
        self,
        *,
        workflow_run_id: UUID,
        status: RuntimeRunStatus,
        pause_reason: str | None = None,
        terminal_reason: str | None = None,
    ) -> WorkflowRunRecord:
        record = await self.session.get(WorkflowRunRecord, workflow_run_id)
        if record is None:
            raise LookupError("workflow run not found")
        record.status = status
        if status == RuntimeRunStatus.RUNNING and record.started_at is None:
            record.started_at = datetime.now(UTC)
        if status == RuntimeRunStatus.PAUSED:
            record.pause_reason = pause_reason
        if status in {
            RuntimeRunStatus.SUCCEEDED,
            RuntimeRunStatus.FAILED,
            RuntimeRunStatus.CANCELLED,
        }:
            record.terminal_reason = terminal_reason
            record.finished_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def create_checkpoint_ref(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        run_step_id: UUID,
        checkpoint_id: str,
        checkpoint_kind: str,
        bundle_digest: str,
    ) -> RuntimeCheckpointRefRecord:
        record = RuntimeCheckpointRefRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=run_step_id,
            langgraph_thread_id=str(workflow_run_id),
            langgraph_checkpoint_id=checkpoint_id,
            checkpoint_kind=checkpoint_kind,
            bundle_digest=bundle_digest,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_handoff_envelope(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        sender_step_id: UUID,
        receiver_step_key: str,
        contract_id: str,
        contract_version: str,
        contract_digest: str,
        payload_ref: dict[str, object],
    ) -> HandoffEnvelopeRecord:
        record = HandoffEnvelopeRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            sender_step_id=sender_step_id,
            receiver_step_key=receiver_step_key,
            contract_id=contract_id,
            contract_version=contract_version,
            contract_digest=contract_digest,
            status=RuntimeHandoffStatus.VALID,
            payload_hash=sha256_digest(payload_ref),
            payload_ref=payload_ref,
            validated_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_side_effect_intent(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        run_step_id: UUID,
        intent_kind: str,
        idempotency_key: str,
        tool_policy_ref: str,
        request_ref: dict[str, object] | None = None,
        result_ref: dict[str, object] | None = None,
    ) -> SideEffectIntentRecord:
        record = SideEffectIntentRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=run_step_id,
            intent_kind=intent_kind,
            idempotency_key=idempotency_key,
            status=RuntimeSideEffectStatus.APPLIED,
            tool_policy_ref=tool_policy_ref,
            request_ref=request_ref,
            result_ref=result_ref,
            executed_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def create_approval_gate(
        self,
        *,
        tenant_id: UUID | None,
        workflow_run_id: UUID,
        run_step_id: UUID,
        approval_key: str,
        requested_action: dict[str, object],
    ) -> ApprovalGateRecord:
        record = ApprovalGateRecord(
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=run_step_id,
            approval_key=approval_key,
            requested_action=requested_action,
            approver_policy={"scope": "manual_resolution"},
            timeout_behavior={"on_timeout": "remain_paused"},
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def claim_next_run(
        self, *, worker_id: str, lease_seconds: int = 120
    ) -> WorkerLeaseRecord | None:
        stmt = (
            select(WorkflowRunRecord)
            .where(WorkflowRunRecord.status == RuntimeRunStatus.RUNNABLE)
            .order_by(WorkflowRunRecord.created_at.asc())
            .limit(1)
        )
        run = (await self.session.execute(stmt)).scalar_one_or_none()
        if run is None:
            return None
        run.status = RuntimeRunStatus.RUNNING
        now = datetime.now(UTC)
        lease = WorkerLeaseRecord(
            tenant_id=run.tenant_id,
            workflow_run_id=run.workflow_run_id,
            worker_id=worker_id,
            lease_status=RuntimeWorkerLeaseStatus.ACTIVE,
            claimed_at=now,
            expires_at=now + timedelta(seconds=lease_seconds),
        )
        self.session.add(lease)
        await self.session.flush()
        return lease

    async def get_or_create_retention_policy(
        self, tenant_id: UUID | None
    ) -> RuntimeRetentionPolicyRecord:
        stmt = select(RuntimeRetentionPolicyRecord).where(
            RuntimeRetentionPolicyRecord.tenant_id == tenant_id
        )
        policy = (await self.session.execute(stmt)).scalar_one_or_none()
        if policy is not None:
            return policy
        policy = RuntimeRetentionPolicyRecord(tenant_id=tenant_id)
        self.session.add(policy)
        await self.session.flush()
        return policy
