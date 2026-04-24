from __future__ import annotations

from uuid import UUID

from multi_agent_platform.memory.canonical import (
    canonical_dumps,
    content_sha256,
    content_size_bytes,
    validate_json_value,
)
from multi_agent_platform.memory.diff import diff_json
from multi_agent_platform.memory.models import (
    MemoryAuditAction,
    MemoryAuditEvent,
    MemoryAuditOutcome,
    MemoryConflictError,
    MemoryDiffResult,
    MemoryHead,
    MemoryInvalidRequestError,
    MemoryNotFoundError,
    MemoryReplayResult,
    MemoryScopeIdentity,
    MemorySourceType,
    MemoryVersion,
    MemoryWriteResult,
    RuntimeMemoryContext,
    RuntimeSourceRef,
)
from multi_agent_platform.memory.policy import (
    MemoryAccessPolicy,
    validate_runtime_context,
)
from multi_agent_platform.memory.replay import build_replay_result
from multi_agent_platform.memory.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository

    async def write_version(
        self,
        *,
        policy: MemoryAccessPolicy,
        workflow_lineage_id: str,
        agent_key: str,
        memory_key: str,
        content: object,
        expected_current_version_id: UUID | None,
        assert_no_current_head: bool,
        idempotency_key: str | None = None,
        change_reason: str | None = None,
        change_summary_redacted: str | None = None,
        source: RuntimeSourceRef | None = None,
        source_type: MemorySourceType = MemorySourceType.API,
        trace_id: str = "trace",
    ) -> MemoryWriteResult:
        policy.assert_can_write(policy.tenant_id)
        normalized = validate_json_value(content)
        canonical_dumps(normalized)
        scope = MemoryScopeIdentity(
            tenant_id=policy.tenant_id,
            workflow_lineage_id=workflow_lineage_id,
            agent_key=agent_key,
            memory_key=memory_key,
        )
        source = source or RuntimeSourceRef()
        try:
            return await self.repository.write_version(
                scope=scope,
                content=normalized,
                content_sha256=content_sha256(normalized),
                content_size_bytes=content_size_bytes(normalized),
                actor_principal_id=policy.principal_id,
                source_type=source_type,
                source=source,
                expected_current_version_id=expected_current_version_id,
                assert_no_current_head=assert_no_current_head,
                idempotency_key=idempotency_key,
                change_reason=change_reason,
                change_summary_redacted=change_summary_redacted,
                trace_id=trace_id,
            )
        except MemoryConflictError as exc:
            await self.repository.add_audit_event(
                tenant_id=policy.tenant_id,
                action_type=MemoryAuditAction.CREATE_VERSION,
                outcome=MemoryAuditOutcome.CONFLICT,
                actor_principal_id=policy.principal_id,
                trace_id=trace_id,
                current_memory_version_id=exc.latest_memory_version_id,
                workflow_lineage_id=workflow_lineage_id,
                agent_key=agent_key,
                memory_key=memory_key,
                source=source,
                content_sha256=content_sha256(normalized),
                change_summary_redacted=change_summary_redacted,
                denial_reason=exc.conflict_type.value,
            )
            raise

    async def get_current_head(
        self,
        *,
        policy: MemoryAccessPolicy,
        workflow_lineage_id: str,
        agent_key: str,
        memory_key: str,
        include_content: bool = True,
        trace_id: str = "trace",
    ) -> MemoryHead:
        policy.assert_can_read_content(policy.tenant_id)
        scope = MemoryScopeIdentity(
            tenant_id=policy.tenant_id,
            workflow_lineage_id=workflow_lineage_id,
            agent_key=agent_key,
            memory_key=memory_key,
        )
        head = await self.repository.get_current_head(
            scope=scope, include_content=include_content
        )
        await self.repository.add_audit_event(
            tenant_id=policy.tenant_id,
            action_type=MemoryAuditAction.GET_HEAD,
            outcome=MemoryAuditOutcome.ALLOWED
            if head.has_memory
            else MemoryAuditOutcome.NOT_FOUND,
            actor_principal_id=policy.principal_id,
            trace_id=trace_id,
            memory_scope_id=head.memory_scope_id,
            memory_version_id=head.version.memory_version_id if head.version else None,
            current_memory_version_id=head.version.memory_version_id
            if head.version
            else None,
            workflow_lineage_id=workflow_lineage_id,
            agent_key=agent_key,
            memory_key=memory_key,
            content_sha256=head.version.content_sha256 if head.version else None,
        )
        return head

    async def get_version(
        self,
        *,
        policy: MemoryAccessPolicy,
        memory_version_id: UUID,
        include_content: bool = True,
        trace_id: str = "trace",
    ) -> MemoryVersion:
        policy.assert_can_read_content(policy.tenant_id)
        version = await self.repository.get_version(
            tenant_id=policy.tenant_id,
            memory_version_id=memory_version_id,
            include_content=include_content,
        )
        await self.repository.add_audit_event(
            tenant_id=policy.tenant_id,
            action_type=MemoryAuditAction.GET_VERSION,
            outcome=MemoryAuditOutcome.ALLOWED
            if version is not None
            else MemoryAuditOutcome.NOT_FOUND,
            actor_principal_id=policy.principal_id,
            trace_id=trace_id,
            memory_scope_id=version.memory_scope_id if version else None,
            memory_version_id=memory_version_id,
            current_memory_version_id=memory_version_id if version else None,
            workflow_lineage_id=version.workflow_lineage_id if version else None,
            agent_key=version.agent_key if version else None,
            memory_key=version.memory_key if version else None,
            content_sha256=version.content_sha256 if version else None,
        )
        if version is None:
            raise MemoryNotFoundError("memory version not found")
        return version

    async def list_history(
        self,
        *,
        policy: MemoryAccessPolicy,
        memory_scope_id: UUID,
        include_content: bool,
        limit: int = 100,
        cursor: str | None = None,
        trace_id: str = "trace",
    ) -> tuple[MemoryScopeIdentity, list[MemoryVersion], str | None]:
        policy.assert_can_history(policy.tenant_id)
        scope, versions, next_cursor = await self.repository.list_history(
            tenant_id=policy.tenant_id,
            memory_scope_id=memory_scope_id,
            include_content=include_content,
            limit=min(max(limit, 1), 500),
            cursor=cursor,
        )
        await self.repository.add_audit_event(
            tenant_id=policy.tenant_id,
            action_type=MemoryAuditAction.LIST_HISTORY,
            outcome=MemoryAuditOutcome.ALLOWED
            if scope is not None
            else MemoryAuditOutcome.NOT_FOUND,
            actor_principal_id=policy.principal_id,
            trace_id=trace_id,
            memory_scope_id=memory_scope_id,
            workflow_lineage_id=scope.workflow_lineage_id if scope else None,
            agent_key=scope.agent_key if scope else None,
            memory_key=scope.memory_key if scope else None,
        )
        if scope is None:
            raise MemoryNotFoundError("memory scope not found")
        return scope, versions, next_cursor

    async def replay_version(
        self,
        *,
        policy: MemoryAccessPolicy,
        memory_version_id: UUID,
        trace_id: str = "trace",
    ) -> MemoryReplayResult:
        policy.assert_can_replay(policy.tenant_id)
        lineage = await self.repository.lineage_to_version(
            tenant_id=policy.tenant_id, memory_version_id=memory_version_id
        )
        if not lineage:
            await self.repository.add_audit_event(
                tenant_id=policy.tenant_id,
                action_type=MemoryAuditAction.REPLAY,
                outcome=MemoryAuditOutcome.NOT_FOUND,
                actor_principal_id=policy.principal_id,
                trace_id=trace_id,
                memory_version_id=memory_version_id,
            )
            raise MemoryNotFoundError("memory version not found")
        target = lineage[-1]
        result = build_replay_result(target=target, lineage=lineage)
        await self.repository.add_audit_event(
            tenant_id=policy.tenant_id,
            action_type=MemoryAuditAction.REPLAY,
            outcome=MemoryAuditOutcome.ALLOWED,
            actor_principal_id=policy.principal_id,
            trace_id=trace_id,
            memory_scope_id=target.memory_scope_id,
            memory_version_id=target.memory_version_id,
            workflow_lineage_id=target.workflow_lineage_id,
            agent_key=target.agent_key,
            memory_key=target.memory_key,
            content_sha256=target.content_sha256,
        )
        return result

    async def diff_versions(
        self,
        *,
        policy: MemoryAccessPolicy,
        base_memory_version_id: UUID,
        compare_memory_version_id: UUID,
        trace_id: str = "trace",
    ) -> MemoryDiffResult:
        policy.assert_can_diff(policy.tenant_id)
        base, compare = await self.repository.load_version_pair(
            tenant_id=policy.tenant_id,
            base_version_id=base_memory_version_id,
            compare_version_id=compare_memory_version_id,
        )
        if base is None or compare is None:
            await self.repository.add_audit_event(
                tenant_id=policy.tenant_id,
                action_type=MemoryAuditAction.DIFF,
                outcome=MemoryAuditOutcome.NOT_FOUND,
                actor_principal_id=policy.principal_id,
                trace_id=trace_id,
                base_memory_version_id=base_memory_version_id,
                compare_memory_version_id=compare_memory_version_id,
            )
            raise MemoryNotFoundError("memory version not found")
        if base.memory_scope_id != compare.memory_scope_id:
            await self.repository.add_audit_event(
                tenant_id=policy.tenant_id,
                action_type=MemoryAuditAction.DIFF,
                outcome=MemoryAuditOutcome.INVALID,
                actor_principal_id=policy.principal_id,
                trace_id=trace_id,
                base_memory_version_id=base_memory_version_id,
                compare_memory_version_id=compare_memory_version_id,
                denial_reason="incompatible_memory_scopes",
            )
            raise MemoryInvalidRequestError("versions are not in the same memory scope")
        if base.content is None or compare.content is None:
            raise MemoryInvalidRequestError("diff requires memory content")
        additions, removals, changes = diff_json(base.content, compare.content)
        await self.repository.add_audit_event(
            tenant_id=policy.tenant_id,
            action_type=MemoryAuditAction.DIFF,
            outcome=MemoryAuditOutcome.ALLOWED,
            actor_principal_id=policy.principal_id,
            trace_id=trace_id,
            memory_scope_id=base.memory_scope_id,
            base_memory_version_id=base.memory_version_id,
            compare_memory_version_id=compare.memory_version_id,
            content_sha256=base.content_sha256,
            compared_content_sha256=compare.content_sha256,
        )
        return MemoryDiffResult(
            base=base,
            compare=compare,
            additions=additions,
            removals=removals,
            changes=changes,
        )

    async def list_audit(
        self,
        *,
        policy: MemoryAccessPolicy,
        memory_scope_id: UUID | None = None,
        memory_version_id: UUID | None = None,
        workflow_run_id: UUID | None = None,
        action_type: MemoryAuditAction | None = None,
        outcome: MemoryAuditOutcome | None = None,
        base_memory_version_id: UUID | None = None,
        compare_memory_version_id: UUID | None = None,
        limit: int = 100,
    ) -> list[MemoryAuditEvent]:
        policy.assert_can_audit(policy.tenant_id)
        return await self.repository.list_audit_events(
            tenant_id=policy.tenant_id,
            memory_scope_id=memory_scope_id,
            memory_version_id=memory_version_id,
            workflow_run_id=workflow_run_id,
            action_type=action_type,
            outcome=outcome,
            base_memory_version_id=base_memory_version_id,
            compare_memory_version_id=compare_memory_version_id,
            limit=min(max(limit, 1), 500),
        )

    async def get_current_head_for_runtime(
        self,
        *,
        context: RuntimeMemoryContext,
        include_content: bool = True,
    ) -> MemoryHead:
        validate_runtime_context(context)
        policy = MemoryAccessPolicy(
            tenant_id=context.tenant_id,
            principal_id=context.actor_principal_id,
            role_codes=("runtime_worker",),
        )
        return await self.get_current_head(
            policy=policy,
            workflow_lineage_id=context.workflow_lineage_id,
            agent_key=context.agent_key,
            memory_key=context.memory_key,
            include_content=include_content,
            trace_id=context.trace_id,
        )

    async def write_version_for_runtime(
        self,
        *,
        context: RuntimeMemoryContext,
        content: object,
        expected_current_version_id: UUID | None,
        assert_no_current_head: bool,
        idempotency_key: str | None,
        change_reason: str | None = None,
        change_summary_redacted: str | None = None,
    ) -> MemoryWriteResult:
        validate_runtime_context(context)
        policy = MemoryAccessPolicy(
            tenant_id=context.tenant_id,
            principal_id=context.actor_principal_id,
            role_codes=("runtime_worker",),
        )
        return await self.write_version(
            policy=policy,
            workflow_lineage_id=context.workflow_lineage_id,
            agent_key=context.agent_key,
            memory_key=context.memory_key,
            content=content,
            expected_current_version_id=expected_current_version_id,
            assert_no_current_head=assert_no_current_head,
            idempotency_key=idempotency_key,
            change_reason=change_reason,
            change_summary_redacted=change_summary_redacted,
            source=context.source(),
            source_type=MemorySourceType.RUNTIME,
            trace_id=context.trace_id,
        )
