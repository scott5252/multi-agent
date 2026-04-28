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


@dataclass(frozen=True, slots=True)
class MemoryPolicyCompatibilityFinding:
    code: str
    severity: str
    message: str
    field_path: str

    def to_json(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "field_path": self.field_path,
        }


ALLOWED_MEMORY_SCOPE_MODES = {"none", "read_only", "read_write"}
ALLOWED_MEMORY_RETENTION_MODES = {"run", "workflow", "tenant"}


def validate_profile_memory_policy(
    policy: dict[str, object],
) -> tuple[MemoryPolicyCompatibilityFinding, ...]:
    findings: list[MemoryPolicyCompatibilityFinding] = []
    if "scope_mode" not in policy and "retention_mode" not in policy:
        return ()
    scope_mode = str(policy.get("scope_mode", "")).strip()
    retention_mode = str(policy.get("retention_mode", "")).strip()
    allow_writes = bool(policy.get("allow_writes", False))

    if scope_mode not in ALLOWED_MEMORY_SCOPE_MODES:
        findings.append(
            MemoryPolicyCompatibilityFinding(
                code="invalid_memory_scope_mode",
                severity="blocking",
                message="Memory scope mode must be none, read_only, or read_write.",
                field_path="memory_scope_policy.scope_mode",
            )
        )
    if retention_mode not in ALLOWED_MEMORY_RETENTION_MODES:
        findings.append(
            MemoryPolicyCompatibilityFinding(
                code="invalid_memory_retention_mode",
                severity="blocking",
                message="Memory retention mode must be run, workflow, or tenant.",
                field_path="memory_scope_policy.retention_mode",
            )
        )
    if allow_writes and scope_mode != "read_write":
        findings.append(
            MemoryPolicyCompatibilityFinding(
                code="memory_write_requires_read_write_scope",
                severity="blocking",
                message="Memory writes require read_write scope mode.",
                field_path="memory_scope_policy.allow_writes",
            )
        )
    return tuple(findings)
