from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from multi_agent_platform.auth.principal import PrincipalContext


@dataclass(frozen=True, slots=True)
class AuditDebuggingFixture:
    tenant_id: UUID
    workflow_run_id: UUID
    child_run_id: UUID
    trace_id: str
    actor: PrincipalContext


def make_audit_fixture() -> AuditDebuggingFixture:
    tenant_id = uuid4()
    return AuditDebuggingFixture(
        tenant_id=tenant_id,
        workflow_run_id=uuid4(),
        child_run_id=uuid4(),
        trace_id="trace-audit",
        actor=PrincipalContext(
            principal_id="admin",
            tenant_id=tenant_id,
            role_codes=("tenant_admin",),
            trace_id="trace-audit",
        ),
    )
