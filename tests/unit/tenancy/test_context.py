from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.tenancy.context import (
    ScopeContext,
    ScopeType,
    clear_scope_context,
    get_scope_context,
    set_scope_context,
)


def test_scope_context_round_trip() -> None:
    scope = ScopeContext(
        scope_type=ScopeType.TENANT,
        tenant_id=uuid4(),
        trace_id="trace",
        principal_id="user",
    )
    set_scope_context(scope)
    assert get_scope_context() == scope
    clear_scope_context()
    assert get_scope_context() is None
