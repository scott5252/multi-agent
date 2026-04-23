from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from multi_agent_platform.api.deps import ContainerDep
from multi_agent_platform.api.schemas.auth import PrincipalContextResponse
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import AuthMode, PrincipalContext

router = APIRouter(prefix="/auth", tags=["auth"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]


@router.get("/me", response_model=PrincipalContextResponse)
async def auth_me(
    principal: PrincipalDep,
) -> PrincipalContextResponse:
    return PrincipalContextResponse(
        principal_id=principal.principal_id,
        auth_mode=principal.auth_mode.value,
        auth_provider=principal.auth_provider.value,
        tenant_id=principal.tenant_id,
        org_id=principal.org_id,
        role_codes=list(principal.role_codes),
        permission_codes=list(principal.permission_codes),
        scope_type=principal.scope_type.value,
        support_override_request_id=principal.support_override_request_id,
    )


@router.get("/tenant-context/{tenant_id}", response_model=PrincipalContextResponse)
async def tenant_context(
    tenant_id: UUID,
    principal: PrincipalDep,
) -> PrincipalContextResponse:
    return PrincipalContextResponse(
        principal_id=principal.principal_id,
        auth_mode=principal.auth_mode.value,
        auth_provider=principal.auth_provider.value,
        tenant_id=tenant_id,
        org_id=principal.org_id,
        role_codes=list(principal.role_codes),
        permission_codes=list(principal.permission_codes),
        scope_type="tenant",
        support_override_request_id=principal.support_override_request_id,
    )


@router.get(
    "/local-login",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def local_login_page(
    request: Request,
    container: ContainerDep,
    redirect_to: str = "/admin/workflows/ui",
) -> HTMLResponse:
    settings = container.settings
    if settings.auth_mode is not AuthMode.LOCAL_PRINCIPAL:
        raise HTTPException(status_code=404, detail="local login is unavailable")
    principals = sorted(
        (
            entry
            for entry in settings.local_principal_catalog_json.values()
            if entry.enabled
        ),
        key=lambda entry: entry.catalog_key,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "auth/local_login.html",
        {
            "principals": principals,
            "redirect_to": redirect_to,
            "current_principal": request.cookies.get(
                settings.local_principal_cookie_name
            ),
        },
    )


@router.post("/local-login", include_in_schema=False)
async def local_login_submit(
    container: ContainerDep,
    principal: str = Form(),
    redirect_to: str = Form(default="/admin/workflows/ui"),
) -> RedirectResponse:
    settings = container.settings
    if settings.auth_mode is not AuthMode.LOCAL_PRINCIPAL:
        raise HTTPException(status_code=404, detail="local login is unavailable")
    if principal not in settings.local_principal_catalog_json:
        raise HTTPException(status_code=400, detail="unknown local principal")
    response = RedirectResponse(url=redirect_to, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key=settings.local_principal_cookie_name,
        value=principal,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/local-logout", include_in_schema=False)
async def local_logout(
    container: ContainerDep,
    redirect_to: str = "/auth/local-login",
) -> RedirectResponse:
    response = RedirectResponse(url=redirect_to, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(container.settings.local_principal_cookie_name)
    return response
