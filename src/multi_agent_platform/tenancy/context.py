from __future__ import annotations

from contextvars import ContextVar
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from multi_agent_platform.auth.principal import PrincipalContext


class ScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class ScopeContext(BaseModel):
    scope_type: ScopeType
    tenant_id: UUID | None = None
    trace_id: str
    request_id: str | None = None
    principal_id: str = "system"
    principal: object | None = None


def scope_for_principal(
    principal: PrincipalContext,
    *,
    trace_id: str,
    request_id: str | None,
) -> ScopeContext:
    return ScopeContext(
        scope_type=principal.scope_type,
        tenant_id=principal.tenant_id,
        trace_id=trace_id,
        request_id=request_id,
        principal_id=principal.principal_id,
        principal=principal,
    )


_scope_context: ContextVar[ScopeContext | None] = ContextVar(
    "scope_context", default=None
)


def get_scope_context() -> ScopeContext | None:
    return _scope_context.get()


def set_scope_context(scope: ScopeContext) -> ScopeContext:
    _scope_context.set(scope)
    return scope


def clear_scope_context() -> None:
    _scope_context.set(None)
