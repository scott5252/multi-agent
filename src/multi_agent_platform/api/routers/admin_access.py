from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.schemas.auth import (
    RoleGrantResponse,
    RoleGrantUpsertRequest,
    SupportOverrideApproveRequest,
    SupportOverrideCreateRequest,
    SupportOverrideResponse,
)
from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import (
    GrantSource,
    RoleCode,
    RoleGrant,
    RoleScopeType,
)
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository

router = APIRouter(prefix="/admin", tags=["admin"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _build_admin_service(session: AsyncSession) -> AdminService:
    access_repository = AccessControlRepository(session)
    audit_service = AuditService(AuditRepository(session))
    recorder = AccessAuditRecorder(access_repository, audit_service)
    return AdminService(
        access_repository=access_repository,
        audit_recorder=recorder,
    )


@router.get(
    "/tenants/{tenant_id}/role-grants",
    response_model=list[RoleGrantResponse],
)
async def list_tenant_role_grants(
    tenant_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> list[RoleGrantResponse]:
    service = _build_admin_service(session)
    grants = await service.list_role_grants_for_tenant(tenant_id)
    return [
        RoleGrantResponse(
            role_grant_id=grant.role_grant_id,
            principal_identity_id=grant.principal_identity_id,
            scope_type=grant.scope_type.value,
            tenant_id=grant.tenant_id,
            role_code=grant.role_code.value,
            status=grant.status.value,
        )
        for grant in grants
    ]


@router.post(
    "/role-grants",
    response_model=RoleGrantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upsert_role_grant(
    payload: RoleGrantUpsertRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> RoleGrantResponse:
    service = _build_admin_service(session)
    grant = await service.upsert_role_grant(
        RoleGrant(
            principal_identity_id=payload.principal_identity_id,
            scope_type=RoleScopeType(payload.scope_type),
            tenant_id=payload.tenant_id,
            role_code=RoleCode(payload.role_code),
            grant_source=GrantSource.ADMIN_ASSIGNMENT,
            granted_by_principal_id=principal.principal_identity_id,
        )
    )
    return RoleGrantResponse(
        role_grant_id=grant.role_grant_id,
        principal_identity_id=grant.principal_identity_id,
        scope_type=grant.scope_type.value,
        tenant_id=grant.tenant_id,
        role_code=grant.role_code.value,
        status=grant.status.value,
    )


@router.post(
    "/support-overrides",
    response_model=SupportOverrideResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_support_override(
    payload: SupportOverrideCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> SupportOverrideResponse:
    if principal.principal_identity_id is None:
        raise HTTPException(
            status_code=403,
            detail="support overrides require persisted identity",
        )
    service = _build_admin_service(session)
    request = await service.create_support_override(
        requester_principal_id=principal.principal_identity_id,
        target_tenant_id=payload.tenant_id,
        justification=payload.justification,
        trace_id=principal.trace_id,
        idempotency_key=payload.idempotency_key,
    )
    return SupportOverrideResponse(
        support_override_request_id=request.support_override_request_id,
        requester_principal_id=request.requester_principal_id,
        target_tenant_id=request.target_tenant_id,
        status=request.status.value,
        approver_principal_id=request.approver_principal_id,
        expires_at=request.expires_at,
    )


@router.post(
    "/support-overrides/{support_override_request_id}/approve",
    response_model=SupportOverrideResponse,
)
async def approve_support_override(
    support_override_request_id: UUID,
    payload: SupportOverrideApproveRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> SupportOverrideResponse:
    if principal.principal_identity_id is None:
        raise HTTPException(
            status_code=403,
            detail="support overrides require persisted identity",
        )
    service = _build_admin_service(session)
    try:
        request = await service.approve_support_override(
            support_override_request_id=support_override_request_id,
            approver_principal_id=principal.principal_identity_id,
            expires_in_hours=payload.expires_in_hours,
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if request is None:
        raise HTTPException(status_code=404, detail="support override not found")
    return SupportOverrideResponse(
        support_override_request_id=request.support_override_request_id,
        requester_principal_id=request.requester_principal_id,
        target_tenant_id=request.target_tenant_id,
        status=request.status.value,
        approver_principal_id=request.approver_principal_id,
        expires_at=request.expires_at,
    )
