from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.auth.service import AuthorizationError


async def test_require_authorized_principal_updates_request_scope() -> None:
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        tenant_id="11111111-1111-1111-1111-111111111111",
        role_codes=("tenant_admin",),
        permission_codes=("tenant:admin",),
        scope_type="tenant",
        trace_id="trace-1",
        request_id="req-1",
    )
    request = SimpleNamespace(
        state=SimpleNamespace(),
        scope={},
    )

    async def authenticate_request(request):
        return principal

    async def authorize_request(request, principal):
        return SimpleNamespace(
            allowed=True,
            support_override_request_id=None,
        )

    service = SimpleNamespace(
        authenticate_request=authenticate_request,
        authorize_request=authorize_request,
    )

    resolved = await require_authorized_principal(request, service)

    assert resolved.principal_id == "tenant-admin-acme"
    assert request.state.scope_context.principal_id == "tenant-admin-acme"


async def test_require_authorized_principal_maps_denials_to_http_errors() -> None:
    request = SimpleNamespace(state=SimpleNamespace(), scope={})

    async def authenticate_request(request):
        raise AuthorizationError(
            status_code=401,
            reason_code="unauthenticated",
            detail="missing auth",
        )

    service = SimpleNamespace(authenticate_request=authenticate_request)
    with pytest.raises(HTTPException):
        await require_authorized_principal(request, service)
