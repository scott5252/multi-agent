from __future__ import annotations

from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from multi_agent_platform.tenancy.context import (
    ScopeContext,
    ScopeType,
    clear_scope_context,
    set_scope_context,
)


class TenancyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        tenant_header = request.headers.get("x-tenant-id")
        scope = ScopeContext(
            scope_type=ScopeType.TENANT if tenant_header else ScopeType.PLATFORM,
            tenant_id=UUID(tenant_header) if tenant_header else None,
            trace_id=request.headers.get("x-trace-id", uuid4().hex),
            request_id=request.headers.get("x-request-id"),
            principal_id=request.headers.get("x-principal-id", "system"),
        )
        set_scope_context(scope)
        request.state.scope_context = scope
        try:
            response = await call_next(request)
        finally:
            clear_scope_context()
        response.headers["x-trace-id"] = scope.trace_id
        return response
