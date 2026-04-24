from __future__ import annotations

from typing import Protocol
from uuid import UUID

from multi_agent_platform.memory.canonical import JsonValue
from multi_agent_platform.memory.models import (
    MemoryAuditAction,
    MemoryAuditEvent,
    MemoryAuditOutcome,
    MemoryHead,
    MemoryScopeIdentity,
    MemorySourceType,
    MemoryVersion,
    MemoryWriteResult,
    RuntimeSourceRef,
)


class MemoryRepository(Protocol):
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
    ) -> MemoryWriteResult: ...

    async def get_current_head(
        self, *, scope: MemoryScopeIdentity, include_content: bool
    ) -> MemoryHead: ...

    async def get_version(
        self, *, tenant_id: UUID | None, memory_version_id: UUID, include_content: bool
    ) -> MemoryVersion | None: ...

    async def list_history(
        self,
        *,
        tenant_id: UUID | None,
        memory_scope_id: UUID,
        include_content: bool,
        limit: int,
        cursor: str | None,
    ) -> tuple[MemoryScopeIdentity | None, list[MemoryVersion], str | None]: ...

    async def lineage_to_version(
        self, *, tenant_id: UUID | None, memory_version_id: UUID
    ) -> list[MemoryVersion]: ...

    async def load_version_pair(
        self, *, tenant_id: UUID | None, base_version_id: UUID, compare_version_id: UUID
    ) -> tuple[MemoryVersion | None, MemoryVersion | None]: ...

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
    ) -> MemoryAuditEvent: ...

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
    ) -> list[MemoryAuditEvent]: ...
