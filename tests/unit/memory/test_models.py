from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.memory.models import (
    MemoryConflictError,
    MemoryConflictType,
    MemoryScopeIdentity,
    RuntimeMemoryContext,
    RuntimeSourceRef,
)


def test_scope_identity_normalizes_required_keys() -> None:
    scope = MemoryScopeIdentity(
        tenant_id=uuid4(),
        workflow_lineage_id=" workflow.demo ",
        agent_key=" triage ",
        memory_key=" prefs ",
    )

    assert scope.workflow_lineage_id == "workflow.demo"
    assert scope.agent_key == "triage"
    assert scope.memory_key == "prefs"


def test_runtime_source_requires_complete_bundle_context() -> None:
    source = RuntimeSourceRef(workflow_run_id=uuid4())

    with pytest.raises(ValueError):
        source.validate_runtime()


def test_conflict_error_exposes_type_and_latest_head() -> None:
    latest = uuid4()
    error = MemoryConflictError(
        MemoryConflictType.STALE_EXPECTED_HEAD,
        "stale",
        latest_memory_version_id=latest,
    )

    assert error.conflict_type is MemoryConflictType.STALE_EXPECTED_HEAD
    assert error.latest_memory_version_id == latest


def test_runtime_context_builds_source_ref() -> None:
    context = RuntimeMemoryContext(
        tenant_id=uuid4(),
        workflow_lineage_id="workflow.demo",
        agent_key="triage",
        memory_key="prefs",
        workflow_run_id=uuid4(),
        run_step_id=uuid4(),
        run_bundle_id=uuid4(),
        bundle_digest="a" * 64,
        actor_principal_id="runtime-worker",
        trace_id="trace",
    )

    assert context.source().bundle_digest == "a" * 64
