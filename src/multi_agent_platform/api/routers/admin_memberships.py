from __future__ import annotations

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.memberships.models import (
    InvitationStatus,
    MembershipAccessScope,
    MembershipAuditAction,
    MembershipAuditDecision,
    MembershipConflictError,
    MembershipPermissionError,
    MembershipScopeType,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.redaction import mask_email, mask_identifier
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
    MembershipSnapshot,
)
from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.memberships import (
    MembershipAccessHistoryResponse,
    MembershipAuditResponse,
    MembershipInvitationCreateRequest,
    MembershipInvitationResponse,
    MembershipPrincipalLinkRequest,
    MembershipPrincipalResponse,
    MembershipRoleGrantCreateRequest,
    MembershipRoleGrantResponse,
    MembershipSnapshotResponse,
    TenantMembershipResponse,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    build_common_state,
    is_platform_admin,
)
from multi_agent_platform.api.ui.memberships import (
    MembershipAdministrationPage,
    redaction_notice,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    PrincipalIdentity,
    RoleCode,
    RoleGrant,
    RoleScopeType,
)
from multi_agent_platform.db.models.user_management import (
    MembershipAuditRecord,
    TenantMembership,
    UserInvitation,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository

router = APIRouter(prefix="/admin/memberships", tags=["memberships"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _service(session: AsyncSession) -> MembershipAdministrationService:
    return MembershipAdministrationService(MembershipRepository(session))


@router.get("/api/users", response_model=MembershipSnapshotResponse)
async def memberships_snapshot_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    q: str | None = None,
) -> MembershipSnapshotResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    snapshot = await service.snapshot(scope, query=q)
    return _snapshot_response(snapshot)


@router.post(
    "/api/invitations",
    response_model=MembershipInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation_api(
    payload: MembershipInvitationCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipInvitationResponse:
    service = _service(session)
    scope = _access_scope(principal, payload.tenant_id)
    try:
        result = await service.create_invitation(
            access_scope=scope,
            tenant_id=payload.tenant_id,
            email=str(payload.email),
            requested_roles=payload.requested_roles,
            idempotency_key=payload.idempotency_key,
        )
    except MembershipPermissionError as exc:
        await service.record_denial(
            access_scope=scope,
            reason=str(exc),
            metadata={"masked_email": mask_email(str(payload.email))},
        )
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    return _invitation_response(result.invitation, replayed=result.replayed)


@router.post("/api/principals/link", response_model=MembershipPrincipalResponse)
async def link_principal_api(
    payload: MembershipPrincipalLinkRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipPrincipalResponse:
    service = _service(session)
    scope = _access_scope(principal, None)
    try:
        record = await service.link_auth0_principal(
            access_scope=scope,
            auth0_subject=payload.auth0_subject,
            email=str(payload.email) if payload.email else None,
            display_name=payload.display_name,
            principal_identity_id=payload.principal_identity_id,
        )
    except MembershipPermissionError as exc:
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    except MembershipConflictError as exc:
        raise HTTPException(status_code=409, detail="Auth0 subject conflict") from exc
    return _principal_response(record)


@router.post(
    "/api/role-grants",
    response_model=MembershipRoleGrantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role_grant_api(
    payload: MembershipRoleGrantCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipRoleGrantResponse:
    service = _service(session)
    scope = _access_scope(principal, payload.tenant_id)
    try:
        record = await service.create_role_grant(
            access_scope=scope,
            principal_identity_id=payload.principal_identity_id,
            scope_type=payload.scope_type,
            tenant_id=payload.tenant_id,
            role_code=payload.role_code,
        )
    except MembershipPermissionError as exc:
        await service.record_denial(
            access_scope=scope,
            reason=str(exc),
            metadata={
                "scope_type": payload.scope_type.value,
                "role_code": payload.role_code.value,
            },
        )
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="principal not found") from exc
    return _role_grant_response(record)


@router.post(
    "/api/role-grants/{role_grant_id}/revoke",
    response_model=MembershipRoleGrantResponse,
)
async def revoke_role_grant_api(
    role_grant_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipRoleGrantResponse:
    service = _service(session)
    scope = _access_scope(principal, None)
    try:
        record = await service.revoke_role_grant(
            access_scope=scope,
            role_grant_id=role_grant_id,
        )
    except MembershipPermissionError as exc:
        await service.record_denial(
            access_scope=scope,
            reason=str(exc),
            metadata={"role_grant_id": str(role_grant_id)},
        )
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="role grant not found")
    return _role_grant_response(record)


@router.post(
    "/api/principals/{principal_identity_id}/suspend",
    response_model=MembershipPrincipalResponse,
)
async def suspend_principal_api(
    principal_identity_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipPrincipalResponse:
    service = _service(session)
    scope = _access_scope(principal, None)
    try:
        record = await service.suspend_principal(
            access_scope=scope,
            principal_identity_id=principal_identity_id,
        )
    except MembershipPermissionError as exc:
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="principal not found")
    return _principal_response(record)


@router.post(
    "/api/principals/{principal_identity_id}/reactivate",
    response_model=MembershipPrincipalResponse,
)
async def reactivate_principal_api(
    principal_identity_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
) -> MembershipPrincipalResponse:
    service = _service(session)
    scope = _access_scope(principal, None)
    try:
        record = await service.reactivate_principal(
            access_scope=scope,
            principal_identity_id=principal_identity_id,
        )
    except MembershipPermissionError as exc:
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="principal not found")
    return _principal_response(record)


@router.post(
    "/api/memberships/{tenant_membership_id}/{membership_status}",
    response_model=TenantMembershipResponse,
)
async def update_membership_status_api(
    tenant_membership_id: UUID,
    membership_status: TenantMembershipStatus,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
) -> TenantMembershipResponse:
    service = _service(session)
    scope = _tenant_access_scope(principal, tenant_id)
    record = await service.update_membership_status(
        access_scope=scope,
        tenant_membership_id=tenant_membership_id,
        status=membership_status,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="membership not found")
    return _membership_response(record)


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def memberships_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    q: str | None = None,
) -> HTMLResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    snapshot = await service.snapshot(scope, query=q)
    page = _page_from_snapshot(snapshot, scope)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Membership Administration",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Membership Administration",
                href="/admin/memberships",
            ),
        ),
        common_state=None
        if page.principals or page.invitations or page.memberships
        else build_common_state(
            CommonStateType.EMPTY,
            title="No memberships yet",
            summary="Create an invitation or link an Auth0 principal to begin.",
            trace_id=principal.trace_id,
        ),
    )
    return cast(
        HTMLResponse,
        request.app.state.container.workflow_ui_templates.TemplateResponse(
            request,
            "memberships/index.html",
            {
                "shell": shell,
                "page": page,
                "principal": principal,
                "redaction_notice": redaction_notice(),
                "tenant_roles": [RoleCode.TENANT_USER, RoleCode.TENANT_ADMIN],
                "role_codes": list(RoleCode),
                "scope_types": list(RoleScopeType),
            },
        ),
    )


@router.post("/invitations", response_class=HTMLResponse, include_in_schema=False)
async def create_invitation_page(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
    email: Annotated[str, Form()] = "",
    requested_roles: Annotated[list[str] | None, Form()] = None,
    idempotency_key: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    selected_roles = requested_roles or [RoleCode.TENANT_USER.value]
    roles = tuple(RoleCode(role) for role in selected_roles)
    try:
        await service.create_invitation(
            access_scope=scope,
            tenant_id=tenant_id,
            email=email,
            requested_roles=roles,
            idempotency_key=idempotency_key,
        )
    except MembershipPermissionError as exc:
        await service.record_denial(
            access_scope=scope,
            reason=str(exc),
            metadata={"masked_email": mask_email(email)},
        )
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    return RedirectResponse(
        _redirect_target(scope),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/role-grants", response_class=HTMLResponse, include_in_schema=False)
async def create_role_grant_page(
    principal: PrincipalDep,
    session: SessionDep,
    principal_identity_id: Annotated[UUID, Form()],
    scope_type: Annotated[RoleScopeType, Form()],
    role_code: Annotated[RoleCode, Form()],
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    try:
        await service.create_role_grant(
            access_scope=scope,
            principal_identity_id=principal_identity_id,
            scope_type=scope_type,
            tenant_id=tenant_id,
            role_code=role_code,
        )
    except MembershipPermissionError as exc:
        await service.record_denial(
            access_scope=scope,
            reason=str(exc),
            metadata={"role_code": role_code.value},
        )
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    return RedirectResponse(
        _redirect_target(scope),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/role-grants/{role_grant_id}/revoke",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def revoke_role_grant_page(
    role_grant_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    try:
        record = await service.revoke_role_grant(
            access_scope=scope,
            role_grant_id=role_grant_id,
        )
    except MembershipPermissionError as exc:
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="role grant not found")
    return RedirectResponse(
        _redirect_target(scope),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/principals/{principal_identity_id}/{principal_action}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def principal_status_page(
    principal_identity_id: UUID,
    principal_action: str,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> Response:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    try:
        if principal_action == "suspend":
            record = await service.suspend_principal(
                access_scope=scope,
                principal_identity_id=principal_identity_id,
            )
        elif principal_action == "reactivate":
            record = await service.reactivate_principal(
                access_scope=scope,
                principal_identity_id=principal_identity_id,
            )
        else:
            raise HTTPException(status_code=404, detail="unknown principal action")
    except MembershipPermissionError as exc:
        raise HTTPException(status_code=403, detail="membership action denied") from exc
    if record is None:
        raise HTTPException(status_code=404, detail="principal not found")
    return RedirectResponse(
        _redirect_target(scope),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post(
    "/memberships/{tenant_membership_id}/{membership_status}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def membership_status_page(
    tenant_membership_id: UUID,
    membership_status: TenantMembershipStatus,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> Response:
    service = _service(session)
    scope = _tenant_access_scope(principal, tenant_id)
    record = await service.update_membership_status(
        access_scope=scope,
        tenant_membership_id=tenant_membership_id,
        status=membership_status,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="membership not found")
    return RedirectResponse(
        _redirect_target(scope),
        status_code=status.HTTP_303_SEE_OTHER,
    )


def _access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> MembershipAccessScope:
    platform = is_platform_admin(principal)
    if platform and tenant_id is None:
        return MembershipAccessScope(
            scope_type=MembershipScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=True,
            trace_id=principal.trace_id,
        )
    selected_tenant = tenant_id or principal.tenant_id
    if selected_tenant is None:
        raise HTTPException(status_code=403, detail="tenant membership scope required")
    if not platform and selected_tenant != principal.tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope is not authorized")
    return MembershipAccessScope(
        scope_type=MembershipScopeType.TENANT,
        tenant_id=selected_tenant,
        principal_id=principal.principal_id,
        platform_admin=platform,
        trace_id=principal.trace_id,
    )


def _tenant_access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> MembershipAccessScope:
    scope = _access_scope(principal, tenant_id)
    if scope.tenant_id is None:
        raise HTTPException(status_code=403, detail="tenant membership scope required")
    return scope


def _redirect_target(scope: MembershipAccessScope) -> str:
    if scope.tenant_id is None:
        return "/admin/memberships"
    return f"/admin/memberships?tenant_id={scope.tenant_id}"


def _page_from_snapshot(
    snapshot: MembershipSnapshot,
    scope: MembershipAccessScope,
) -> MembershipAdministrationPage:
    response = _snapshot_response(snapshot)
    return MembershipAdministrationPage(
        tenant_id=scope.tenant_id,
        platform_scope=scope.scope_type is MembershipScopeType.PLATFORM,
        principals=response.principals,
        invitations=response.invitations,
        memberships=response.memberships,
        role_grants=response.role_grants,
        access_history=response.access_history,
        audit_records=response.audit_records,
    )


def _snapshot_response(snapshot: MembershipSnapshot) -> MembershipSnapshotResponse:
    return MembershipSnapshotResponse(
        principals=tuple(_principal_response(item) for item in snapshot.principals),
        invitations=tuple(
            _invitation_response(item, replayed=False) for item in snapshot.invitations
        ),
        memberships=tuple(_membership_response(item) for item in snapshot.memberships),
        role_grants=tuple(_role_grant_response(item) for item in snapshot.role_grants),
        access_history=tuple(
            _access_history_response(item) for item in snapshot.access_history
        ),
        audit_records=tuple(_audit_response(item) for item in snapshot.audit_records),
    )


def _principal_response(record: PrincipalIdentity) -> MembershipPrincipalResponse:
    return MembershipPrincipalResponse(
        principal_identity_id=record.principal_identity_id,
        auth_provider=record.auth_provider,
        external_subject=record.external_subject,
        subject_display=mask_identifier(record.external_subject),
        display_name=record.display_name,
        masked_email=mask_email(record.email) if record.email else None,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _invitation_response(
    record: UserInvitation, *, replayed: bool
) -> MembershipInvitationResponse:
    return MembershipInvitationResponse(
        user_invitation_id=record.user_invitation_id,
        tenant_id=record.tenant_id,
        masked_email=record.masked_email,
        email_hash=record.invited_email_hash[:16],
        requested_roles=tuple(RoleCode(role) for role in record.requested_roles),
        status=InvitationStatus(record.status),
        idempotency_key=record.idempotency_key,
        invited_by_principal_id=record.invited_by_principal_id,
        principal_identity_id=record.principal_identity_id,
        expires_at=record.expires_at,
        created_at=record.created_at,
        updated_at=record.updated_at,
        replayed=replayed,
    )


def _membership_response(record: TenantMembership) -> TenantMembershipResponse:
    return TenantMembershipResponse(
        tenant_membership_id=record.tenant_membership_id,
        tenant_id=record.tenant_id,
        principal_identity_id=record.principal_identity_id,
        status=TenantMembershipStatus(record.status),
        revision_token=record.revision_token,
        membership_source=record.membership_source,
        created_by_principal_id=record.created_by_principal_id,
        updated_by_principal_id=record.updated_by_principal_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        suspended_at=record.suspended_at,
        removed_at=record.removed_at,
    )


def _role_grant_response(record: RoleGrant) -> MembershipRoleGrantResponse:
    return MembershipRoleGrantResponse(
        role_grant_id=record.role_grant_id,
        principal_identity_id=record.principal_identity_id,
        scope_type=record.scope_type,
        tenant_id=record.tenant_id,
        role_code=record.role_code,
        status=record.status,
        effective_at=record.effective_at,
        expires_at=record.expires_at,
        revoked_at=record.revoked_at,
        updated_at=record.updated_at,
    )


def _access_history_response(
    record: AccessDecisionRecord,
) -> MembershipAccessHistoryResponse:
    return MembershipAccessHistoryResponse(
        access_decision_record_id=record.access_decision_record_id,
        principal_identity_id=record.principal_identity_id,
        tenant_id=record.tenant_id,
        surface_key=record.surface_key,
        requested_action=record.requested_action,
        decision=record.decision,
        reason_code=record.reason_code,
        trace_id=record.trace_id,
        occurred_at=record.occurred_at,
    )


def _audit_response(record: MembershipAuditRecord) -> MembershipAuditResponse:
    return MembershipAuditResponse(
        membership_audit_record_id=record.membership_audit_record_id,
        tenant_id=record.tenant_id,
        actor_principal_id=record.actor_principal_id,
        target_principal_identity_id=record.target_principal_identity_id,
        action=MembershipAuditAction(record.action),
        decision=MembershipAuditDecision(record.decision),
        summary=record.summary,
        trace_id=record.trace_id,
        redacted_metadata=record.redacted_metadata,
        created_at=record.created_at,
    )
