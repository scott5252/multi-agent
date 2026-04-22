from __future__ import annotations

from types import SimpleNamespace

from multi_agent_platform.api.deps import get_scope
from multi_agent_platform.tenancy.context import ScopeContext, ScopeType


def test_get_scope_reads_request_state() -> None:
    scope = ScopeContext(scope_type=ScopeType.PLATFORM, trace_id="trace")
    request = SimpleNamespace(state=SimpleNamespace(scope_context=scope))
    assert get_scope(request) == scope
