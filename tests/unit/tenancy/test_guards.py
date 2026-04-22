from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.tenancy.context import ScopeContext, ScopeType
from multi_agent_platform.tenancy.guards import (
    ScopeError,
    ensure_scope_matches,
    require_tenant_scope,
)


def test_require_tenant_scope_returns_tenant_id() -> None:
    tenant_id = uuid4()
    scope = ScopeContext(
        scope_type=ScopeType.TENANT, tenant_id=tenant_id, trace_id="trace"
    )
    assert require_tenant_scope(scope) == tenant_id


def test_ensure_scope_matches_is_fail_closed() -> None:
    scope = ScopeContext(
        scope_type=ScopeType.TENANT, tenant_id=uuid4(), trace_id="trace"
    )
    with pytest.raises(ScopeError):
        ensure_scope_matches(scope, uuid4())
