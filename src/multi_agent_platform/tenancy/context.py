from __future__ import annotations

from contextvars import ContextVar
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class ScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class ScopeContext(BaseModel):
    scope_type: ScopeType
    tenant_id: UUID | None = None
    trace_id: str
    request_id: str | None = None
    principal_id: str = "system"


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
