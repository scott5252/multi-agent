from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class MemoryVersion:
    memory_id: str
    version_no: int
    scope_type: str
    scope_id: str
    content: dict[str, Any]
    created_by_agent: str
    workflow_run_id: str
    created_at: datetime
    parent_version_no: int | None


class ImmutableMemoryStore:
    """
    Small in-memory example of append-only versioned memory.

    A production implementation would persist versions and head pointers in
    PostgreSQL inside the same transaction as workflow checkpoint updates.
    """

    def __init__(self) -> None:
        self._versions: dict[str, list[MemoryVersion]] = {}

    def append(
        self,
        *,
        scope_type: str,
        scope_id: str,
        content: dict[str, Any],
        created_by_agent: str,
        workflow_run_id: str,
        memory_id: str | None = None,
    ) -> MemoryVersion:
        resolved_memory_id = memory_id or str(uuid4())
        history = self._versions.setdefault(resolved_memory_id, [])
        version_no = len(history) + 1
        parent_version_no = history[-1].version_no if history else None

        version = MemoryVersion(
            memory_id=resolved_memory_id,
            version_no=version_no,
            scope_type=scope_type,
            scope_id=scope_id,
            content=content,
            created_by_agent=created_by_agent,
            workflow_run_id=workflow_run_id,
            created_at=datetime.now(timezone.utc),
            parent_version_no=parent_version_no,
        )
        history.append(version)
        return version

    def head(self, memory_id: str) -> MemoryVersion:
        try:
            return self._versions[memory_id][-1]
        except KeyError as exc:
            raise KeyError(f"unknown memory_id: {memory_id}") from exc

    def history(self, memory_id: str) -> list[MemoryVersion]:
        return list(self._versions.get(memory_id, []))
