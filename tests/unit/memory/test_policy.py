from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.memory.models import (
    MemoryAccessDeniedError,
    MemoryOperation,
    RuntimeMemoryContext,
)
from multi_agent_platform.memory.policy import (
    MemoryAccessPolicy,
    validate_runtime_context,
)


def test_policy_fails_closed_on_cross_tenant_access() -> None:
    policy = MemoryAccessPolicy(tenant_id=uuid4(), principal_id="tenant-user")

    with pytest.raises(MemoryAccessDeniedError):
        policy.assert_can_write(uuid4())


def test_policy_enforces_operation_budget() -> None:
    tenant_id = uuid4()
    policy = MemoryAccessPolicy(
        tenant_id=tenant_id,
        principal_id="tenant-user",
        operation_budget={MemoryOperation.READ: 1},
    )

    policy.assert_can_read_content(tenant_id)
    with pytest.raises(MemoryAccessDeniedError):
        policy.assert_can_read_content(tenant_id)


def test_runtime_protocol_version_is_validated() -> None:
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
        protocol_version="runtime-memory.v0",
    )

    with pytest.raises(MemoryAccessDeniedError):
        validate_runtime_context(context)
