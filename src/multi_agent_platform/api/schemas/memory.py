from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ErrorResponse(BaseModel):
    detail: str


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


class RuntimeSourceRef(BaseModel):
    workflow_run_id: UUID | None = None
    run_step_id: UUID | None = None
    run_bundle_id: UUID | None = None
    bundle_digest: str | None = Field(default=None, min_length=64, max_length=64)
    run_lineage_id: UUID | None = None


class MemoryScopeRef(BaseModel):
    workflow_lineage_id: str = Field(min_length=1)
    agent_key: str = Field(min_length=1)
    memory_key: str = Field(min_length=1)
    memory_scope_id: UUID | None = None


class MemoryVersionSummary(BaseModel):
    memory_version_id: UUID
    memory_scope_id: UUID
    previous_memory_version_id: UUID | None = None
    version_sequence: int = Field(ge=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    change_summary_redacted: str | None = None
    source: RuntimeSourceRef = Field(default_factory=RuntimeSourceRef)
    created_at: datetime


class MemoryVersionResponse(MemoryVersionSummary):
    scope: MemoryScopeRef | None = None
    content: Any | None = None


class MemoryHeadResponse(BaseModel):
    has_memory: bool
    scope: MemoryScopeRef
    head: MemoryVersionSummary | None = None
    content: Any | None = None


class MemoryWriteRequest(BaseModel):
    scope: MemoryScopeRef
    content: Any
    expected_current_version_id: UUID | None = None
    assert_no_current_head: bool = False
    idempotency_key: str | None = Field(default=None, max_length=128)
    change_reason: str | None = Field(default=None, max_length=500)
    change_summary_redacted: str | None = Field(default=None, max_length=1000)
    source: RuntimeSourceRef | None = None

    @model_validator(mode="after")
    def validate_precondition(self) -> MemoryWriteRequest:
        if self.assert_no_current_head and self.expected_current_version_id is not None:
            raise ValueError(
                "initial writes cannot include expected_current_version_id"
            )
        if not self.assert_no_current_head and self.expected_current_version_id is None:
            raise ValueError("non-initial writes require expected_current_version_id")
        return self


class MemoryWriteResponse(BaseModel):
    scope: MemoryScopeRef
    version: MemoryVersionSummary
    head_advanced: bool


class MemoryConflictResponse(BaseModel):
    detail: str
    conflict_type: str
    latest_memory_version_id: UUID | None = None


class MemoryHistoryResponse(BaseModel):
    scope: MemoryScopeRef
    versions: list[MemoryVersionResponse]
    next_cursor: str | None = None


class MemoryReplayResponse(BaseModel):
    target: MemoryVersionSummary
    content: Any
    lineage: list[MemoryVersionSummary]


class MemoryDiffRequest(BaseModel):
    base_memory_version_id: UUID
    compare_memory_version_id: UUID


class MemoryDiffEntry(BaseModel):
    path: str
    before: Any | None = None
    after: Any | None = None


class MemoryDiffResponse(BaseModel):
    base: MemoryVersionSummary
    compare: MemoryVersionSummary
    additions: list[MemoryDiffEntry]
    removals: list[MemoryDiffEntry]
    changes: list[MemoryDiffEntry]


class MemoryAuditEvent(BaseModel):
    memory_audit_event_id: UUID
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


class MemoryAuditResponse(BaseModel):
    events: list[MemoryAuditEvent]
    next_cursor: str | None = None
