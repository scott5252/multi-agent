from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from multi_agent_platform.memory.models import (
    MemorySourceType,
    MemoryVersion,
    RuntimeSourceRef,
)
from multi_agent_platform.memory.replay import build_replay_result


def _version(sequence: int, previous: object | None, scope_id) -> MemoryVersion:
    return MemoryVersion(
        memory_version_id=uuid4(),
        memory_scope_id=scope_id,
        tenant_id=uuid4(),
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        previous_memory_version_id=previous,  # type: ignore[arg-type]
        version_sequence=sequence,
        content={"sequence": sequence},
        content_sha256="a" * 64,
        content_size_bytes=16,
        change_summary_redacted=None,
        change_reason=None,
        actor_principal_id="tenant-admin",
        source_type=MemorySourceType.API,
        source=RuntimeSourceRef(),
        idempotency_key=None,
        created_at=datetime.now(UTC),
    )


def test_replay_returns_target_snapshot_and_ordered_lineage() -> None:
    scope_id = uuid4()
    first = _version(1, None, scope_id)
    second = _version(2, first.memory_version_id, scope_id)

    replay = build_replay_result(target=second, lineage=[second, first])

    assert replay.content == {"sequence": 2}
    assert [version.version_sequence for version in replay.lineage] == [1, 2]


def test_replay_rejects_non_contiguous_lineage() -> None:
    scope_id = uuid4()
    first = _version(1, uuid4(), scope_id)

    with pytest.raises(ValueError):
        build_replay_result(target=first, lineage=[first])
