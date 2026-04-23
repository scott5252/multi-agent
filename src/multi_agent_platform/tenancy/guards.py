from __future__ import annotations

from uuid import UUID

from multi_agent_platform.auth.principal import PrincipalContext
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


def require_workflow_scope_access(
    principal: PrincipalContext,
    *,
    scope_type: str,
    tenant_id: UUID | None,
) -> UUID | None:
    if scope_type == ScopeType.PLATFORM.value:
        if "platform_admin" not in principal.role_codes:
            raise ScopeError("platform-scoped workflows require platform_admin")
        return None
    if "tenant_admin" not in principal.role_codes or principal.tenant_id is None:
        raise ScopeError("tenant-scoped workflows require tenant_admin")
    if tenant_id is not None and tenant_id != principal.tenant_id:
        raise ScopeError("tenant scope mismatch")
    return principal.tenant_id


def can_view_workflow_scope(
    principal: PrincipalContext,
    *,
    scope_type: str,
    tenant_id: UUID | None,
) -> bool:
    if scope_type == ScopeType.PLATFORM.value:
        return "platform_admin" in principal.role_codes
    return principal.tenant_id == tenant_id and "tenant_admin" in principal.role_codes
