from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.service import AuthorizationError, AuthService
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)
from multi_agent_platform.tenancy.context import scope_for_principal

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_auth_service(
    container: ContainerDep,
    session: SessionDep,
) -> AuthService:
    access_repository = AccessControlRepository(session)
    audit_repository = AuditRepository(session)
    delegated_credential_repository = DelegatedCredentialRepository(session)
    audit_recorder = AccessAuditRecorder(
        access_repository,
        AuditService(audit_repository),
    )
    return AuthService(
        settings=container.settings,
        access_repository=access_repository,
        delegated_credential_repository=delegated_credential_repository,
        audit_recorder=audit_recorder,
        jwt_validator=container.jwt_validator,
        local_principal_catalog=container.local_principal_catalog,
        auth_failure_detail=container.auth_failure_detail,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def require_authorized_principal(
    request: Request,
    auth_service: AuthServiceDep,
) -> object:
    try:
        principal = await auth_service.authenticate_request(request)
        decision = await auth_service.authorize_request(request, principal)
    except AuthorizationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    if not decision.allowed:
        status_code = (
            status.HTTP_403_FORBIDDEN
            if decision.reason_code.value != "config_error"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        raise HTTPException(status_code=status_code, detail=decision.reason_code.value)

    if decision.support_override_request_id is not None:
        principal = principal.model_copy(
            update={
                "support_override_request_id": decision.support_override_request_id,
            }
        )

    scope = scope_for_principal(
        principal,
        trace_id=principal.trace_id,
        request_id=principal.request_id,
    )
    request.state.principal = principal
    request.state.scope_context = scope
    return principal
