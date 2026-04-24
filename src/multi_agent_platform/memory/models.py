from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from multi_agent_platform.memory.canonical import JsonValue

RUNTIME_MEMORY_PROTOCOL_VERSION = "runtime-memory.v1"


class MemorySourceType(StrEnum):
    API = "api"
    RUNTIME = "runtime"
    MIGRATION = "migration"
    SUPPORT = "support"


class MemoryAuditAction(StrEnum):
    CREATE_VERSION = "create_version"
    GET_HEAD = "get_head"
    GET_VERSION = "get_version"
    LIST_HISTORY = "list_history"
    REPLAY = "replay"
    DIFF = "diff"
    ARCHIVE_MARK = "archive_mark"


class MemoryAuditOutcome(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INVALID = "invalid"


class MemoryConflictType(StrEnum):
    HEAD_EXISTS = "head_exists"
    STALE_EXPECTED_HEAD = "stale_expected_head"
    IDEMPOTENCY_CONFLICT = "idempotency_conflict"


class MemoryOperation(StrEnum):
    READ = "read"
    WRITE = "write"
    HISTORY = "history"
    REPLAY = "replay"
    DIFF = "diff"
    AUDIT = "audit"


@dataclass(slots=True, frozen=True)
class MemoryScopeIdentity:
    tenant_id: UUID | None
    workflow_lineage_id: str
    agent_key: str
    memory_key: str

    def __post_init__(self) -> None:
        for name, value in (
            ("workflow_lineage_id", self.workflow_lineage_id),
            ("agent_key", self.agent_key),
            ("memory_key", self.memory_key),
        ):
            if not value or not value.strip():
                raise ValueError(f"{name} must be non-empty")
            object.__setattr__(self, name, value.strip())


@dataclass(slots=True, frozen=True)
class RuntimeSourceRef:
    workflow_run_id: UUID | None = None
    run_step_id: UUID | None = None
    run_bundle_id: UUID | None = None
    bundle_digest: str | None = None
    run_lineage_id: UUID | None = None

    def validate_runtime(self) -> None:
        fields = (
            self.workflow_run_id,
            self.run_step_id,
            self.run_bundle_id,
            self.bundle_digest,
        )
        if any(value is not None for value in fields) and not all(
            value is not None for value in fields
        ):
            raise ValueError("runtime source requires run, step, bundle, and digest")
        if self.bundle_digest is not None and len(self.bundle_digest) != 64:
            raise ValueError("bundle_digest must be 64 characters")


@dataclass(slots=True, frozen=True)
class RuntimeMemoryContext:
    tenant_id: UUID | None
    workflow_lineage_id: str
    agent_key: str
    memory_key: str
    workflow_run_id: UUID
    run_step_id: UUID
    run_bundle_id: UUID
    bundle_digest: str
    actor_principal_id: str
    trace_id: str
    protocol_version: str = RUNTIME_MEMORY_PROTOCOL_VERSION
    run_lineage_id: UUID | None = None

    def source(self) -> RuntimeSourceRef:
        return RuntimeSourceRef(
            workflow_run_id=self.workflow_run_id,
            run_step_id=self.run_step_id,
            run_bundle_id=self.run_bundle_id,
            bundle_digest=self.bundle_digest,
            run_lineage_id=self.run_lineage_id,
        )


@dataclass(slots=True, frozen=True)
class MemoryScope:
    memory_scope_id: UUID
    identity: MemoryScopeIdentity
    created_by_principal_id: str
    created_by_workflow_run_id: UUID | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class MemoryVersion:
    memory_version_id: UUID
    memory_scope_id: UUID
    tenant_id: UUID | None
    workflow_lineage_id: str
    agent_key: str
    memory_key: str
    previous_memory_version_id: UUID | None
    version_sequence: int
    content: JsonValue | None
    content_sha256: str
    content_size_bytes: int
    change_summary_redacted: str | None
    change_reason: str | None
    actor_principal_id: str
    source_type: MemorySourceType
    source: RuntimeSourceRef
    idempotency_key: str | None
    created_at: datetime


@dataclass(slots=True, frozen=True)
class MemoryHead:
    has_memory: bool
    scope: MemoryScopeIdentity
    memory_scope_id: UUID | None = None
    version: MemoryVersion | None = None


@dataclass(slots=True, frozen=True)
class MemoryWriteResult:
    scope: MemoryScope
    version: MemoryVersion
    head_advanced: bool


@dataclass(slots=True, frozen=True)
class MemoryDiffEntry:
    path: str
    before: JsonValue | None = None
    after: JsonValue | None = None


@dataclass(slots=True, frozen=True)
class MemoryDiffResult:
    base: MemoryVersion
    compare: MemoryVersion
    additions: tuple[MemoryDiffEntry, ...]
    removals: tuple[MemoryDiffEntry, ...]
    changes: tuple[MemoryDiffEntry, ...]


@dataclass(slots=True, frozen=True)
class MemoryReplayResult:
    target: MemoryVersion
    content: JsonValue
    lineage: tuple[MemoryVersion, ...]


@dataclass(slots=True, frozen=True)
class MemoryAuditEvent:
    memory_audit_event_id: UUID
    tenant_id: UUID | None
    action_type: MemoryAuditAction
    outcome: MemoryAuditOutcome
    created_at: datetime
    memory_scope_id: UUID | None = None
    memory_version_id: UUID | None = None
    previous_memory_version_id: UUID | None = None
    current_memory_version_id: UUID | None = None
    workflow_lineage_id: str | None = None
    agent_key: str | None = None
    memory_key: str | None = None
    workflow_run_id: UUID | None = None
    run_step_id: UUID | None = None
    run_bundle_id: UUID | None = None
    bundle_digest: str | None = None
    run_lineage_id: UUID | None = None
    actor_principal_id: str | None = None
    content_sha256: str | None = None
    base_memory_version_id: UUID | None = None
    compare_memory_version_id: UUID | None = None
    compared_content_sha256: str | None = None
    change_summary_redacted: str | None = None
    denial_reason: str | None = None
    trace_id: str | None = None


class MemoryError(RuntimeError):
    pass


class MemoryInvalidRequestError(MemoryError):
    pass


class MemoryNotFoundError(MemoryError):
    pass


class MemoryAccessDeniedError(MemoryError):
    pass


class MemoryConflictError(MemoryError):
    def __init__(
        self,
        conflict_type: MemoryConflictType,
        detail: str,
        *,
        latest_memory_version_id: UUID | None = None,
    ) -> None:
        super().__init__(detail)
        self.conflict_type = conflict_type
        self.detail = detail
        self.latest_memory_version_id = latest_memory_version_id
