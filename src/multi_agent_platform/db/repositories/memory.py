from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.memory import (
    MemoryAuditEventRecord,
    MemoryHeadRecord,
    MemoryScopeRecord,
    MemoryVersionRecord,
)
from multi_agent_platform.memory.canonical import JsonValue
from multi_agent_platform.memory.models import (
    MemoryAuditAction,
    MemoryAuditEvent,
    MemoryAuditOutcome,
    MemoryConflictError,
    MemoryConflictType,
    MemoryHead,
    MemoryScope,
    MemoryScopeIdentity,
    MemorySourceType,
    MemoryVersion,
    MemoryWriteResult,
    RuntimeSourceRef,
)


class SqlAlchemyMemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def write_version(
        self,
        *,
        scope: MemoryScopeIdentity,
        content: JsonValue,
        content_sha256: str,
        content_size_bytes: int,
        actor_principal_id: str,
        source_type: MemorySourceType,
        source: RuntimeSourceRef,
        expected_current_version_id: UUID | None,
        assert_no_current_head: bool,
        idempotency_key: str | None,
        change_reason: str | None,
        change_summary_redacted: str | None,
        trace_id: str,
    ) -> MemoryWriteResult:
        source.validate_runtime()
        scope_record = await self._get_or_create_scope(
            scope=scope,
            actor_principal_id=actor_principal_id,
            workflow_run_id=source.workflow_run_id,
        )
        existing = await self._find_idempotent_version(
            tenant_id=scope.tenant_id,
            memory_scope_id=scope_record.memory_scope_id,
            idempotency_key=idempotency_key,
        )
        if existing is not None:
            expected_previous = expected_current_version_id
            if assert_no_current_head:
                expected_previous = None
            if (
                existing.content_sha256 == content_sha256
                and existing.previous_memory_version_id == expected_previous
            ):
                return MemoryWriteResult(
                    scope=self._scope_to_domain(scope_record),
                    version=self._version_to_domain(existing, scope_record, True),
                    head_advanced=False,
                )
            raise MemoryConflictError(
                MemoryConflictType.IDEMPOTENCY_CONFLICT,
                "idempotency key was already used with different memory content",
                latest_memory_version_id=existing.memory_version_id,
            )

        head = await self._get_head(scope_record.memory_scope_id, lock=True)
        if assert_no_current_head:
            if head is not None:
                raise MemoryConflictError(
                    MemoryConflictType.HEAD_EXISTS,
                    "memory head already exists",
                    latest_memory_version_id=head.current_memory_version_id,
                )
            previous_id = None
            sequence = 1
        else:
            if expected_current_version_id is None:
                raise MemoryConflictError(
                    MemoryConflictType.STALE_EXPECTED_HEAD,
                    "expected_current_version_id is required for non-initial writes",
                    latest_memory_version_id=head.current_memory_version_id
                    if head is not None
                    else None,
                )
            if (
                head is None
                or head.current_memory_version_id != expected_current_version_id
            ):
                raise MemoryConflictError(
                    MemoryConflictType.STALE_EXPECTED_HEAD,
                    "expected current memory version is stale",
                    latest_memory_version_id=head.current_memory_version_id
                    if head is not None
                    else None,
                )
            previous_id = head.current_memory_version_id
            sequence = head.version_sequence + 1

        version_record = MemoryVersionRecord(
            tenant_id=scope.tenant_id,
            memory_scope_id=scope_record.memory_scope_id,
            previous_memory_version_id=previous_id,
            version_sequence=sequence,
            content=content,
            content_sha256=content_sha256,
            content_size_bytes=content_size_bytes,
            change_summary_redacted=change_summary_redacted,
            change_reason=change_reason,
            actor_principal_id=actor_principal_id,
            source_type=source_type.value,
            workflow_run_id=source.workflow_run_id,
            run_step_id=source.run_step_id,
            run_bundle_id=source.run_bundle_id,
            bundle_digest=source.bundle_digest,
            run_lineage_id=source.run_lineage_id,
            idempotency_key=idempotency_key,
        )
        self.session.add(version_record)
        await self.session.flush()

        now = utcnow()
        if head is None:
            head = MemoryHeadRecord(
                memory_scope_id=scope_record.memory_scope_id,
                tenant_id=scope.tenant_id,
                workflow_lineage_id=scope.workflow_lineage_id,
                agent_key=scope.agent_key,
                memory_key=scope.memory_key,
                current_memory_version_id=version_record.memory_version_id,
                version_sequence=sequence,
                content_sha256=content_sha256,
                updated_by_principal_id=actor_principal_id,
                updated_by_workflow_run_id=source.workflow_run_id,
                updated_at=now,
            )
            self.session.add(head)
        else:
            head.current_memory_version_id = version_record.memory_version_id
            head.version_sequence = sequence
            head.content_sha256 = content_sha256
            head.updated_by_principal_id = actor_principal_id
            head.updated_by_workflow_run_id = source.workflow_run_id
            head.updated_at = now

        await self.add_audit_event(
            tenant_id=scope.tenant_id,
            action_type=MemoryAuditAction.CREATE_VERSION,
            outcome=MemoryAuditOutcome.ALLOWED,
            actor_principal_id=actor_principal_id,
            trace_id=trace_id,
            memory_scope_id=scope_record.memory_scope_id,
            memory_version_id=version_record.memory_version_id,
            previous_memory_version_id=previous_id,
            current_memory_version_id=version_record.memory_version_id,
            workflow_lineage_id=scope.workflow_lineage_id,
            agent_key=scope.agent_key,
            memory_key=scope.memory_key,
            source=source,
            content_sha256=content_sha256,
            change_summary_redacted=change_summary_redacted,
        )
        await self.session.flush()
        return MemoryWriteResult(
            scope=self._scope_to_domain(scope_record),
            version=self._version_to_domain(version_record, scope_record, True),
            head_advanced=True,
        )

    async def get_current_head(
        self, *, scope: MemoryScopeIdentity, include_content: bool
    ) -> MemoryHead:
        scope_record = await self._get_scope(scope)
        if scope_record is None:
            return MemoryHead(has_memory=False, scope=scope)
        head = await self._get_head(scope_record.memory_scope_id, lock=False)
        if head is None:
            return MemoryHead(
                has_memory=False,
                scope=scope,
                memory_scope_id=scope_record.memory_scope_id,
            )
        version = await self.get_version(
            tenant_id=scope.tenant_id,
            memory_version_id=head.current_memory_version_id,
            include_content=include_content,
        )
        return MemoryHead(
            has_memory=version is not None,
            scope=scope,
            memory_scope_id=scope_record.memory_scope_id,
            version=version,
        )

    async def get_version(
        self, *, tenant_id: UUID | None, memory_version_id: UUID, include_content: bool
    ) -> MemoryVersion | None:
        stmt = (
            select(MemoryVersionRecord, MemoryScopeRecord)
            .join(
                MemoryScopeRecord,
                MemoryVersionRecord.memory_scope_id
                == MemoryScopeRecord.memory_scope_id,
            )
            .where(
                MemoryVersionRecord.memory_version_id == memory_version_id,
                MemoryVersionRecord.tenant_id == tenant_id,
            )
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return None
        version, scope = row
        return self._version_to_domain(version, scope, include_content)

    async def list_history(
        self,
        *,
        tenant_id: UUID | None,
        memory_scope_id: UUID,
        include_content: bool,
        limit: int,
        cursor: str | None,
    ) -> tuple[MemoryScopeIdentity | None, list[MemoryVersion], str | None]:
        scope = await self.session.get(MemoryScopeRecord, memory_scope_id)
        if scope is None or scope.tenant_id != tenant_id:
            return None, [], None
        stmt = select(MemoryVersionRecord).where(
            MemoryVersionRecord.tenant_id == tenant_id,
            MemoryVersionRecord.memory_scope_id == memory_scope_id,
        )
        if cursor is not None:
            stmt = stmt.where(MemoryVersionRecord.version_sequence < int(cursor))
        stmt = stmt.order_by(MemoryVersionRecord.version_sequence.desc()).limit(
            limit + 1
        )
        records = list((await self.session.execute(stmt)).scalars().all())
        next_cursor = None
        if len(records) > limit:
            next_cursor = str(records[limit].version_sequence)
            records = records[:limit]
        return (
            self._scope_identity(scope),
            [
                self._version_to_domain(record, scope, include_content)
                for record in records
            ],
            next_cursor,
        )

    async def lineage_to_version(
        self, *, tenant_id: UUID | None, memory_version_id: UUID
    ) -> list[MemoryVersion]:
        target = await self.get_version(
            tenant_id=tenant_id,
            memory_version_id=memory_version_id,
            include_content=True,
        )
        if target is None:
            return []
        stmt = (
            select(MemoryVersionRecord, MemoryScopeRecord)
            .join(
                MemoryScopeRecord,
                MemoryVersionRecord.memory_scope_id
                == MemoryScopeRecord.memory_scope_id,
            )
            .where(
                MemoryVersionRecord.tenant_id == tenant_id,
                MemoryVersionRecord.memory_scope_id == target.memory_scope_id,
                MemoryVersionRecord.version_sequence <= target.version_sequence,
            )
            .order_by(MemoryVersionRecord.version_sequence.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            self._version_to_domain(version, scope, True) for version, scope in rows
        ]

    async def load_version_pair(
        self, *, tenant_id: UUID | None, base_version_id: UUID, compare_version_id: UUID
    ) -> tuple[MemoryVersion | None, MemoryVersion | None]:
        base = await self.get_version(
            tenant_id=tenant_id,
            memory_version_id=base_version_id,
            include_content=True,
        )
        compare = await self.get_version(
            tenant_id=tenant_id,
            memory_version_id=compare_version_id,
            include_content=True,
        )
        return base, compare

    async def add_audit_event(
        self,
        *,
        tenant_id: UUID | None,
        action_type: MemoryAuditAction,
        outcome: MemoryAuditOutcome,
        actor_principal_id: str,
        trace_id: str,
        memory_scope_id: UUID | None = None,
        memory_version_id: UUID | None = None,
        previous_memory_version_id: UUID | None = None,
        current_memory_version_id: UUID | None = None,
        workflow_lineage_id: str | None = None,
        agent_key: str | None = None,
        memory_key: str | None = None,
        source: RuntimeSourceRef | None = None,
        content_sha256: str | None = None,
        base_memory_version_id: UUID | None = None,
        compare_memory_version_id: UUID | None = None,
        compared_content_sha256: str | None = None,
        change_summary_redacted: str | None = None,
        denial_reason: str | None = None,
    ) -> MemoryAuditEvent:
        source = source or RuntimeSourceRef()
        event = MemoryAuditEventRecord(
            tenant_id=tenant_id,
            memory_scope_id=memory_scope_id,
            memory_version_id=memory_version_id,
            previous_memory_version_id=previous_memory_version_id,
            current_memory_version_id=current_memory_version_id,
            workflow_lineage_id=workflow_lineage_id,
            agent_key=agent_key,
            memory_key=memory_key,
            workflow_run_id=source.workflow_run_id,
            run_step_id=source.run_step_id,
            run_bundle_id=source.run_bundle_id,
            bundle_digest=source.bundle_digest,
            run_lineage_id=source.run_lineage_id,
            actor_principal_id=actor_principal_id,
            action_type=action_type.value,
            outcome=outcome.value,
            content_sha256=content_sha256,
            base_memory_version_id=base_memory_version_id,
            compare_memory_version_id=compare_memory_version_id,
            compared_content_sha256=compared_content_sha256,
            change_summary_redacted=change_summary_redacted,
            denial_reason=denial_reason,
            trace_id=trace_id,
        )
        self.session.add(event)
        await self.session.flush()
        return self._audit_to_domain(event)

    async def list_audit_events(
        self,
        *,
        tenant_id: UUID | None,
        memory_scope_id: UUID | None,
        memory_version_id: UUID | None,
        workflow_run_id: UUID | None,
        action_type: MemoryAuditAction | None,
        outcome: MemoryAuditOutcome | None,
        base_memory_version_id: UUID | None,
        compare_memory_version_id: UUID | None,
        limit: int,
    ) -> list[MemoryAuditEvent]:
        stmt = select(MemoryAuditEventRecord).where(
            MemoryAuditEventRecord.tenant_id == tenant_id
        )
        if memory_scope_id is not None:
            stmt = stmt.where(MemoryAuditEventRecord.memory_scope_id == memory_scope_id)
        if memory_version_id is not None:
            stmt = stmt.where(
                MemoryAuditEventRecord.memory_version_id == memory_version_id
            )
        if workflow_run_id is not None:
            stmt = stmt.where(MemoryAuditEventRecord.workflow_run_id == workflow_run_id)
        if action_type is not None:
            stmt = stmt.where(MemoryAuditEventRecord.action_type == action_type.value)
        if outcome is not None:
            stmt = stmt.where(MemoryAuditEventRecord.outcome == outcome.value)
        if base_memory_version_id is not None:
            stmt = stmt.where(
                MemoryAuditEventRecord.base_memory_version_id == base_memory_version_id
            )
        if compare_memory_version_id is not None:
            stmt = stmt.where(
                MemoryAuditEventRecord.compare_memory_version_id
                == compare_memory_version_id
            )
        stmt = stmt.order_by(MemoryAuditEventRecord.created_at.desc()).limit(limit)
        return [
            self._audit_to_domain(record)
            for record in (await self.session.execute(stmt)).scalars().all()
        ]

    async def _get_or_create_scope(
        self,
        *,
        scope: MemoryScopeIdentity,
        actor_principal_id: str,
        workflow_run_id: UUID | None,
    ) -> MemoryScopeRecord:
        existing = await self._get_scope(scope)
        if existing is not None:
            return existing
        created = MemoryScopeRecord(
            tenant_id=scope.tenant_id,
            workflow_lineage_id=scope.workflow_lineage_id,
            agent_key=scope.agent_key,
            memory_key=scope.memory_key,
            created_by_principal_id=actor_principal_id,
            created_by_workflow_run_id=workflow_run_id,
        )
        self.session.add(created)
        await self.session.flush()
        return created

    async def _get_scope(self, scope: MemoryScopeIdentity) -> MemoryScopeRecord | None:
        stmt = select(MemoryScopeRecord).where(
            MemoryScopeRecord.tenant_id == scope.tenant_id,
            MemoryScopeRecord.workflow_lineage_id == scope.workflow_lineage_id,
            MemoryScopeRecord.agent_key == scope.agent_key,
            MemoryScopeRecord.memory_key == scope.memory_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def _get_head(
        self, memory_scope_id: UUID, *, lock: bool
    ) -> MemoryHeadRecord | None:
        stmt: Select[tuple[MemoryHeadRecord]] = select(MemoryHeadRecord).where(
            MemoryHeadRecord.memory_scope_id == memory_scope_id
        )
        if lock:
            stmt = stmt.with_for_update()
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def _find_idempotent_version(
        self,
        *,
        tenant_id: UUID | None,
        memory_scope_id: UUID,
        idempotency_key: str | None,
    ) -> MemoryVersionRecord | None:
        if idempotency_key is None:
            return None
        stmt = select(MemoryVersionRecord).where(
            MemoryVersionRecord.tenant_id == tenant_id,
            MemoryVersionRecord.memory_scope_id == memory_scope_id,
            MemoryVersionRecord.idempotency_key == idempotency_key,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    def _scope_identity(self, scope: MemoryScopeRecord) -> MemoryScopeIdentity:
        return MemoryScopeIdentity(
            tenant_id=scope.tenant_id,
            workflow_lineage_id=scope.workflow_lineage_id,
            agent_key=scope.agent_key,
            memory_key=scope.memory_key,
        )

    def _scope_to_domain(self, scope: MemoryScopeRecord) -> MemoryScope:
        return MemoryScope(
            memory_scope_id=scope.memory_scope_id,
            identity=self._scope_identity(scope),
            created_by_principal_id=scope.created_by_principal_id,
            created_by_workflow_run_id=scope.created_by_workflow_run_id,
            created_at=scope.created_at,
        )

    def _version_to_domain(
        self,
        version: MemoryVersionRecord,
        scope: MemoryScopeRecord,
        include_content: bool,
    ) -> MemoryVersion:
        return MemoryVersion(
            memory_version_id=version.memory_version_id,
            memory_scope_id=version.memory_scope_id,
            tenant_id=version.tenant_id,
            workflow_lineage_id=scope.workflow_lineage_id,
            agent_key=scope.agent_key,
            memory_key=scope.memory_key,
            previous_memory_version_id=version.previous_memory_version_id,
            version_sequence=version.version_sequence,
            content=cast(JsonValue, version.content) if include_content else None,
            content_sha256=version.content_sha256,
            content_size_bytes=version.content_size_bytes,
            change_summary_redacted=version.change_summary_redacted,
            change_reason=version.change_reason,
            actor_principal_id=version.actor_principal_id,
            source_type=MemorySourceType(version.source_type),
            source=RuntimeSourceRef(
                workflow_run_id=version.workflow_run_id,
                run_step_id=version.run_step_id,
                run_bundle_id=version.run_bundle_id,
                bundle_digest=version.bundle_digest,
                run_lineage_id=version.run_lineage_id,
            ),
            idempotency_key=version.idempotency_key,
            created_at=version.created_at,
        )

    def _audit_to_domain(self, event: MemoryAuditEventRecord) -> MemoryAuditEvent:
        return MemoryAuditEvent(
            memory_audit_event_id=event.memory_audit_event_id,
            tenant_id=event.tenant_id,
            memory_scope_id=event.memory_scope_id,
            memory_version_id=event.memory_version_id,
            previous_memory_version_id=event.previous_memory_version_id,
            current_memory_version_id=event.current_memory_version_id,
            workflow_lineage_id=event.workflow_lineage_id,
            agent_key=event.agent_key,
            memory_key=event.memory_key,
            workflow_run_id=event.workflow_run_id,
            run_step_id=event.run_step_id,
            run_bundle_id=event.run_bundle_id,
            bundle_digest=event.bundle_digest,
            run_lineage_id=event.run_lineage_id,
            actor_principal_id=event.actor_principal_id,
            action_type=MemoryAuditAction(event.action_type),
            outcome=MemoryAuditOutcome(event.outcome),
            content_sha256=event.content_sha256,
            base_memory_version_id=event.base_memory_version_id,
            compare_memory_version_id=event.compare_memory_version_id,
            compared_content_sha256=event.compared_content_sha256,
            change_summary_redacted=event.change_summary_redacted,
            denial_reason=event.denial_reason,
            trace_id=event.trace_id,
            created_at=event.created_at,
        )
