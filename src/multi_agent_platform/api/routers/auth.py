from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from multi_agent_platform.api.schemas.auth import PrincipalContextResponse
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext

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
