from __future__ import annotations

from uuid import UUID

from multi_agent_platform.tenancy.context import ScopeContext, ScopeType


class ScopeError(RuntimeError):
    """Raised when code attempts to cross a scope boundary."""


def require_tenant_scope(scope: ScopeContext) -> UUID:
    if scope.scope_type is not ScopeType.TENANT or scope.tenant_id is None:
        raise ScopeError("tenant scope is required")
    return scope.tenant_id


def require_platform_scope(scope: ScopeContext) -> None:
    if scope.scope_type is not ScopeType.PLATFORM:
        raise ScopeError("platform scope is required")


def ensure_scope_matches(scope: ScopeContext, tenant_id: UUID | None) -> None:
    if scope.scope_type is ScopeType.PLATFORM:
        return
    if tenant_id != scope.tenant_id:
        raise ScopeError("tenant scope mismatch")
