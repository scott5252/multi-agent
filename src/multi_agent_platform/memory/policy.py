from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from multi_agent_platform.memory.models import (
    MemoryAccessDeniedError,
    MemoryOperation,
    RuntimeMemoryContext,
)


@dataclass(slots=True)
class MemoryAccessPolicy:
    tenant_id: UUID | None
    principal_id: str
    role_codes: tuple[str, ...] = ()
    permission_codes: tuple[str, ...] = ()
    operation_budget: dict[MemoryOperation, int] = field(default_factory=dict)

    def assert_tenant(self, tenant_id: UUID | None) -> None:
        if self.tenant_id != tenant_id:
            raise MemoryAccessDeniedError("memory access is scoped to another tenant")

    def assert_operation(self, operation: MemoryOperation) -> None:
        remaining = self.operation_budget.get(operation)
        if remaining is None:
            return
        if remaining <= 0:
            raise MemoryAccessDeniedError(f"memory {operation.value} budget exceeded")
        self.operation_budget[operation] = remaining - 1

    def assert_can_read_content(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.READ)

    def assert_can_write(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.WRITE)

    def assert_can_history(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.HISTORY)

    def assert_can_replay(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.REPLAY)

    def assert_can_diff(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.DIFF)

    def assert_can_audit(self, tenant_id: UUID | None) -> None:
        self.assert_tenant(tenant_id)
        self.assert_operation(MemoryOperation.AUDIT)


def validate_runtime_context(context: RuntimeMemoryContext) -> None:
    if context.protocol_version != "runtime-memory.v1":
        raise MemoryAccessDeniedError("unsupported runtime memory protocol")
    if len(context.bundle_digest) != 64:
        raise MemoryAccessDeniedError("runtime bundle digest is invalid")
