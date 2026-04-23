from __future__ import annotations

from typing import cast
from uuid import UUID

from starlette.requests import Request

from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.auth.jwt_validator import (
    Auth0JwtValidator,
    JwtValidationError,
)
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.auth.policy import (
    AuthorizationDecision,
    SurfaceClassification,
    principal_has_role,
    resolve_surface,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.models.access_control import (
    AccessReasonCode,
    AuthProviderType,
    PrincipalIdentity,
    RoleCode,
)
from multi_agent_platform.db.models.delegated_credential import DelegatedCredentialLink
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)
from multi_agent_platform.tenancy.context import ScopeType


class AuthorizationError(RuntimeError):
    def __init__(
        self,
        *,
        status_code: int,
        reason_code: AccessReasonCode,
        detail: str,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.reason_code = reason_code
        self.detail = detail


class AuthService:
    def __init__(
        self,
        *,
        settings: Settings,
        access_repository: AccessControlRepository,
        delegated_credential_repository: DelegatedCredentialRepository,
        audit_recorder: AccessAuditRecorder,
        jwt_validator: Auth0JwtValidator | None,
        local_principal_catalog: LocalPrincipalCatalog,
        auth_failure_detail: str | None,
    ) -> None:
        self.settings = settings
        self.access_repository = access_repository
        self.delegated_credential_repository = delegated_credential_repository
        self.audit_recorder = audit_recorder
        self.jwt_validator = jwt_validator
        self.local_principal_catalog = local_principal_catalog
        self.auth_failure_detail = auth_failure_detail

    async def authenticate_request(self, request: Request) -> PrincipalContext:
        trace_id = request.state.scope_context.trace_id
        request_id = request.state.scope_context.request_id
        if self.auth_failure_detail is not None:
            raise AuthorizationError(
                status_code=503,
                reason_code=AccessReasonCode.CONFIG_ERROR,
                detail=self.auth_failure_detail,
            )

        if self.settings.auth_mode is AuthMode.LOCAL_PRINCIPAL:
            header = request.headers.get(self.settings.local_principal_header)
            if not header:
                raise AuthorizationError(
                    status_code=401,
                    reason_code=AccessReasonCode.UNAUTHENTICATED,
                    detail="missing local principal header",
                )
            principal = self.local_principal_catalog.as_principal_context(
                header,
                trace_id=trace_id,
                request_id=request_id,
            )
            if principal is None:
                raise AuthorizationError(
                    status_code=401,
                    reason_code=AccessReasonCode.UNAUTHENTICATED,
                    detail="unknown local principal",
                )
            identity = await self.access_repository.get_principal_by_subject(header)
            if identity is None:
                identity = await self.access_repository.upsert_principal(
                    PrincipalIdentity(
                        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
                        external_subject=header,
                        display_name=header,
                    )
                )
            return principal.model_copy(
                update={"principal_identity_id": identity.principal_identity_id}
            )

        token = self._bearer_token(request)
        if token is None:
            raise AuthorizationError(
                status_code=401,
                reason_code=AccessReasonCode.UNAUTHENTICATED,
                detail="missing bearer token",
            )
        if self.jwt_validator is None:
            raise AuthorizationError(
                status_code=503,
                reason_code=AccessReasonCode.CONFIG_ERROR,
                detail="jwt validator is not configured",
            )
        try:
            claims = await self.jwt_validator.validate(token)
        except JwtValidationError as exc:
            raise AuthorizationError(
                status_code=401,
                reason_code=AccessReasonCode.INVALID_TOKEN,
                detail=exc.message,
            ) from exc

        identity = await self.access_repository.get_principal_by_subject(claims.subject)
        if identity is None:
            identity = await self.access_repository.upsert_principal(
                PrincipalIdentity(
                    auth_provider=AuthProviderType.AUTH0,
                    external_subject=claims.subject,
                    display_name=claims.display_name,
                    email=claims.email,
                )
            )
        grants = await self.access_repository.active_role_grants_for_principal(
            identity.principal_identity_id
        )
        role_codes = tuple(
            sorted(
                {
                    grant.role_code.value
                    for grant in grants
                    if grant.tenant_id is None or grant.tenant_id == claims.tenant_id
                }
            )
        )
        return PrincipalContext(
            principal_identity_id=identity.principal_identity_id,
            principal_id=identity.external_subject,
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=claims.tenant_id,
            org_id=claims.org_id,
            role_codes=role_codes,
            permission_codes=claims.permissions,
            scope_type=ScopeType.TENANT
            if claims.tenant_id is not None
            else ScopeType.PLATFORM,
            trace_id=trace_id,
            request_id=request_id,
            token_subject=claims.subject,
            token_jti=claims.jti,
        )

    async def authorize_request(
        self,
        request: Request,
        principal: PrincipalContext,
    ) -> AuthorizationDecision:
        route = cast(object, request.scope.get("route"))
        route_path = getattr(route, "path", request.url.path)
        surface = resolve_surface(request.method, route_path)
        target_tenant_id = self._target_tenant_id(request, principal)
        decision = await self._authorize_surface(
            principal,
            surface_key=surface.surface_key,
            requested_action=surface.requested_action,
            classification=surface.classification,
            required_roles=surface.required_roles,
            required_permissions=surface.required_permissions,
            target_tenant_id=target_tenant_id,
        )
        await self.audit_recorder.record_decision(
            principal=principal,
            decision=decision,
            auth_mode=principal.auth_mode.value,
            trace_id=principal.trace_id,
            request_id=principal.request_id,
        )
        return decision

    async def authorize_delegated_credential(
        self,
        *,
        principal: PrincipalContext,
        delegated_credential_link_id: UUID,
        tool_id: str,
        tenant_id: UUID,
    ) -> DelegatedCredentialLink:
        if principal.tenant_id != tenant_id:
            raise AuthorizationError(
                status_code=403,
                reason_code=AccessReasonCode.CROSS_TENANT,
                detail="delegated credential is scoped to a different tenant",
            )
        link = await self.delegated_credential_repository.resolve_for_tool(
            delegated_credential_link_id=delegated_credential_link_id,
            tenant_id=tenant_id,
            tool_id=tool_id,
        )
        if link is None:
            raise AuthorizationError(
                status_code=403,
                reason_code=AccessReasonCode.DELEGATED_CREDENTIAL_DENIED,
                detail="delegated credential is not approved for this tool",
            )
        if principal.principal_identity_id is not None and (
            link.owner_principal_id != principal.principal_identity_id
        ):
            raise AuthorizationError(
                status_code=403,
                reason_code=AccessReasonCode.DELEGATED_CREDENTIAL_DENIED,
                detail="delegated credential belongs to a different principal",
            )
        return link

    def authorize_platform_secret_action(
        self,
        *,
        principal: PrincipalContext,
        tenant_id: UUID | None,
    ) -> None:
        if tenant_id is not None and principal.tenant_id != tenant_id:
            raise AuthorizationError(
                status_code=403,
                reason_code=AccessReasonCode.CROSS_TENANT,
                detail="secret access must remain in-tenant",
            )
        if not principal_has_role(
            principal, RoleCode.TENANT_ADMIN.value, RoleCode.PLATFORM_ADMIN.value
        ):
            raise AuthorizationError(
                status_code=403,
                reason_code=AccessReasonCode.INSUFFICIENT_ROLE,
                detail="secret access requires elevated privileges",
            )

    def _bearer_token(self, request: Request) -> str | None:
        header = request.headers.get("authorization")
        if header is None or not header.startswith("Bearer "):
            return None
        return header.removeprefix("Bearer ").strip()

    def _target_tenant_id(
        self, request: Request, principal: PrincipalContext
    ) -> UUID | None:
        raw_value = request.path_params.get("tenant_id")
        if isinstance(raw_value, UUID):
            return raw_value
        if isinstance(raw_value, str) and raw_value:
            return UUID(raw_value)
        return principal.tenant_id

    async def _authorize_surface(
        self,
        principal: PrincipalContext,
        *,
        surface_key: str,
        requested_action: str,
        classification: SurfaceClassification,
        required_roles: tuple[str, ...],
        required_permissions: tuple[str, ...],
        target_tenant_id: UUID | None,
    ) -> AuthorizationDecision:
        if required_permissions and not set(required_permissions).issubset(
            set(principal.permission_codes)
        ):
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=False,
                reason_code=AccessReasonCode.INSUFFICIENT_PERMISSION,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
            )
        if classification is SurfaceClassification.AUTHENTICATED:
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=True,
                reason_code=AccessReasonCode.UNAUTHENTICATED,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
            )
        if classification is SurfaceClassification.PLATFORM_ADMIN:
            allowed = principal_has_role(principal, RoleCode.PLATFORM_ADMIN.value)
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=allowed,
                reason_code=AccessReasonCode.UNAUTHENTICATED
                if allowed
                else AccessReasonCode.INSUFFICIENT_ROLE,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
            )

        if target_tenant_id is None:
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=False,
                reason_code=AccessReasonCode.CROSS_TENANT,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
            )

        if principal.tenant_id == target_tenant_id:
            allowed = (
                classification is SurfaceClassification.TENANT_USER
                or principal_has_role(
                    principal,
                    RoleCode.TENANT_ADMIN.value,
                    RoleCode.PLATFORM_ADMIN.value,
                )
            )
            if (
                classification is SurfaceClassification.TENANT_USER
                and principal_has_role(
                    principal,
                    RoleCode.TENANT_USER.value,
                    RoleCode.TENANT_ADMIN.value,
                    RoleCode.PLATFORM_ADMIN.value,
                )
            ):
                allowed = True
            if classification is SurfaceClassification.TENANT_ADMIN:
                allowed = principal_has_role(
                    principal,
                    RoleCode.TENANT_ADMIN.value,
                    RoleCode.PLATFORM_ADMIN.value,
                )
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=allowed,
                reason_code=AccessReasonCode.UNAUTHENTICATED
                if allowed
                else AccessReasonCode.INSUFFICIENT_ROLE,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
            )

        if principal_has_role(principal, RoleCode.PLATFORM_ADMIN.value):
            support_override = None
            if principal.principal_identity_id is not None:
                support_override = (
                    await self.access_repository.find_active_support_override(
                        requester_principal_id=principal.principal_identity_id,
                        tenant_id=target_tenant_id,
                    )
                )
            if support_override is None:
                return AuthorizationDecision(
                    surface_key=surface_key,
                    requested_action=requested_action,
                    classification=classification,
                    allowed=False,
                    reason_code=AccessReasonCode.SUPPORT_OVERRIDE_REQUIRED,
                    required_roles=required_roles,
                    required_permissions=required_permissions,
                    target_tenant_id=target_tenant_id,
                )
            return AuthorizationDecision(
                surface_key=surface_key,
                requested_action=requested_action,
                classification=classification,
                allowed=True,
                reason_code=AccessReasonCode.UNAUTHENTICATED,
                required_roles=required_roles,
                required_permissions=required_permissions,
                target_tenant_id=target_tenant_id,
                support_override_request_id=support_override.support_override_request_id,
            )

        return AuthorizationDecision(
            surface_key=surface_key,
            requested_action=requested_action,
            classification=classification,
            allowed=False,
            reason_code=AccessReasonCode.CROSS_TENANT,
            required_roles=required_roles,
            required_permissions=required_permissions,
            target_tenant_id=target_tenant_id,
        )
