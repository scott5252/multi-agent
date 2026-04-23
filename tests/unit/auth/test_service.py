from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.claims import NormalizedTokenClaims
from multi_agent_platform.auth.jwt_validator import JwtValidationError
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.auth.policy import SurfaceClassification
from multi_agent_platform.auth.service import AuthorizationError, AuthService
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.models.access_control import (
    AccessReasonCode,
    PrincipalIdentity,
)
from multi_agent_platform.db.models.delegated_credential import DelegatedCredentialLink
from multi_agent_platform.db.models.secret_reference import SecretReference
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)


def build_auth_service(session, settings) -> AuthService:
    access_repository = AccessControlRepository(session)
    audit_repository = AuditRepository(session)
    delegated_repository = DelegatedCredentialRepository(session)
    return AuthService(
        settings=settings,
        access_repository=access_repository,
        delegated_credential_repository=delegated_repository,
        audit_recorder=AccessAuditRecorder(
            access_repository,
            AuditService(audit_repository),
        ),
        jwt_validator=None,
        local_principal_catalog=LocalPrincipalCatalog(
            settings.local_principal_catalog_json
        ),
        auth_failure_detail=None,
    )


def build_auth0_service(session) -> AuthService:
    settings = Settings(
        app_env="test",
        auth_mode="auth0",
        auth0_domain="tenant.example.com",
        auth0_issuer="https://tenant.example.com/",
        auth0_audience="multi-agent-platform",
        auth0_algorithms=("HS256",),
    )
    access_repository = AccessControlRepository(session)
    audit_repository = AuditRepository(session)
    delegated_repository = DelegatedCredentialRepository(session)
    return AuthService(
        settings=settings,
        access_repository=access_repository,
        delegated_credential_repository=delegated_repository,
        audit_recorder=AccessAuditRecorder(
            access_repository,
            AuditService(audit_repository),
        ),
        jwt_validator=SimpleNamespace(),
        local_principal_catalog=LocalPrincipalCatalog(),
        auth_failure_detail=None,
    )


async def test_local_principal_authentication_creates_persisted_identity(
    session, settings
) -> None:
    service = build_auth_service(session, settings)
    request = SimpleNamespace(
        headers={settings.local_principal_header: "tenant-admin-acme"},
        state=SimpleNamespace(
            scope_context=SimpleNamespace(trace_id="trace-1", request_id="req-1")
        ),
    )

    principal = await service.authenticate_request(request)

    assert principal.principal_identity_id is not None
    assert principal.principal_id == "tenant-admin-acme"


async def test_authorize_delegated_credential_enforces_tool_boundaries(
    session, settings
) -> None:
    service = build_auth_service(session, settings)
    principal_identity_id = uuid4()
    tenant_id = uuid4()
    session.add(
        PrincipalIdentity(
            principal_identity_id=principal_identity_id,
            auth_provider="local_principal",
            external_subject="tenant-admin-acme",
        )
    )
    secret_reference = SecretReference(
        tenant_id=tenant_id,
        scope_type="user_delegated",
        name="delegated-google",
        provider_key="secret-manager/google",
        access_policy={},
    )
    session.add(secret_reference)
    await session.flush()
    link = DelegatedCredentialLink(
        secret_reference_id=secret_reference.secret_reference_id,
        owner_principal_id=principal_identity_id,
        tenant_id=tenant_id,
        approved_tool_ids=["gmail.send"],
        granted_scopes=["gmail.send"],
    )
    session.add(link)
    await session.flush()

    principal_context = service.local_principal_catalog.as_principal_context(
        "tenant-admin-acme",
        trace_id="trace",
        request_id="req",
    ).model_copy(
        update={
            "tenant_id": tenant_id,
            "principal_identity_id": principal_identity_id,
        }
    )

    allowed = await service.authorize_delegated_credential(
        principal=principal_context,
        delegated_credential_link_id=link.delegated_credential_link_id,
        tool_id="gmail.send",
        tenant_id=tenant_id,
    )
    assert allowed.delegated_credential_link_id == link.delegated_credential_link_id

    with pytest.raises(AuthorizationError):
        await service.authorize_delegated_credential(
            principal=principal_context,
            delegated_credential_link_id=link.delegated_credential_link_id,
            tool_id="calendar.read",
            tenant_id=tenant_id,
        )


async def test_authorize_delegated_credential_rejects_owner_mismatch(
    session, settings
) -> None:
    service = build_auth_service(session, settings)
    tenant_id = uuid4()
    owner = PrincipalIdentity(
        principal_identity_id=uuid4(),
        auth_provider="local_principal",
        external_subject="owner",
    )
    session.add(owner)
    secret_reference = SecretReference(
        tenant_id=tenant_id,
        scope_type="user_delegated",
        name="delegated-google",
        provider_key="secret-manager/google",
        access_policy={},
    )
    session.add(secret_reference)
    await session.flush()
    link = DelegatedCredentialLink(
        secret_reference_id=secret_reference.secret_reference_id,
        owner_principal_id=owner.principal_identity_id,
        tenant_id=tenant_id,
        approved_tool_ids=["gmail.send"],
        granted_scopes=["gmail.send"],
    )
    session.add(link)
    await session.flush()
    principal_context = service.local_principal_catalog.as_principal_context(
        "tenant-admin-acme",
        trace_id="trace",
        request_id="req",
    ).model_copy(update={"tenant_id": tenant_id, "principal_identity_id": uuid4()})

    with pytest.raises(AuthorizationError):
        await service.authorize_delegated_credential(
            principal=principal_context,
            delegated_credential_link_id=link.delegated_credential_link_id,
            tool_id="gmail.send",
            tenant_id=tenant_id,
        )


async def test_auth0_authentication_requires_bearer_token(session) -> None:
    service = build_auth0_service(session)
    request = SimpleNamespace(
        headers={},
        state=SimpleNamespace(
            scope_context=SimpleNamespace(trace_id="trace-1", request_id="req-1")
        ),
    )

    with pytest.raises(AuthorizationError):
        await service.authenticate_request(request)


async def test_auth0_authentication_rejects_invalid_token(session) -> None:
    service = build_auth0_service(session)

    async def validate(token: str) -> NormalizedTokenClaims:
        raise JwtValidationError("bad token")

    service.jwt_validator = SimpleNamespace(validate=validate)
    request = SimpleNamespace(
        headers={"authorization": "Bearer bad-token"},
        state=SimpleNamespace(
            scope_context=SimpleNamespace(trace_id="trace-1", request_id="req-1")
        ),
    )

    with pytest.raises(AuthorizationError):
        await service.authenticate_request(request)


async def test_auth0_authentication_builds_context_from_claims(session) -> None:
    service = build_auth0_service(session)

    async def validate(token: str) -> NormalizedTokenClaims:
        return NormalizedTokenClaims(
            subject="auth0|user-1",
            issuer="https://tenant.example.com/",
            audience=("multi-agent-platform",),
            permissions=("tenant:read",),
            org_id="org-acme",
            tenant_id=uuid4(),
        )

    service.jwt_validator = SimpleNamespace(validate=validate)
    request = SimpleNamespace(
        headers={"authorization": "Bearer good-token"},
        state=SimpleNamespace(
            scope_context=SimpleNamespace(trace_id="trace-1", request_id="req-1")
        ),
    )

    principal = await service.authenticate_request(request)
    assert principal.auth_provider == "auth0"
    assert principal.token_subject == "auth0|user-1"


async def test_authorize_surface_requires_support_override_for_platform_admin(
    session, settings
) -> None:
    service = build_auth_service(session, settings)
    principal = service.local_principal_catalog.as_principal_context(
        "platform-admin",
        trace_id="trace",
        request_id="req",
    ).model_copy(update={"permission_codes": ("tenant:admin",)})

    decision = await service._authorize_surface(
        principal,
        surface_key="GET:/admin/tenants/{tenant_id}/role-grants",
        requested_action="list_tenant_role_grants",
        classification=SurfaceClassification.TENANT_ADMIN,
        required_roles=("tenant_admin",),
        required_permissions=("tenant:admin",),
        target_tenant_id=uuid4(),
    )

    assert decision.allowed is False
    assert decision.reason_code == AccessReasonCode.SUPPORT_OVERRIDE_REQUIRED


def test_secret_action_authorization_rejects_cross_tenant(settings) -> None:
    service = AuthService(
        settings=settings,
        access_repository=SimpleNamespace(),
        delegated_credential_repository=SimpleNamespace(),
        audit_recorder=SimpleNamespace(),
        jwt_validator=None,
        local_principal_catalog=LocalPrincipalCatalog(
            settings.local_principal_catalog_json
        ),
        auth_failure_detail=None,
    )
    principal = service.local_principal_catalog.as_principal_context(
        "tenant-admin-acme",
        trace_id="trace",
        request_id="req",
    )

    with pytest.raises(AuthorizationError):
        service.authorize_platform_secret_action(
            principal=principal,
            tenant_id=uuid4(),
        )


def test_secret_action_authorization_rejects_underprivileged_user(settings) -> None:
    service = AuthService(
        settings=settings,
        access_repository=SimpleNamespace(),
        delegated_credential_repository=SimpleNamespace(),
        audit_recorder=SimpleNamespace(),
        jwt_validator=None,
        local_principal_catalog=LocalPrincipalCatalog(
            {
                "tenant-user": settings.local_principal_catalog_json[
                    "tenant-admin-acme"
                ].model_copy(update={"role_codes": ("tenant_user",)})
            }
        ),
        auth_failure_detail=None,
    )
    principal = service.local_principal_catalog.as_principal_context(
        "tenant-user",
        trace_id="trace",
        request_id="req",
    )

    with pytest.raises(AuthorizationError):
        service.authorize_platform_secret_action(
            principal=principal,
            tenant_id=principal.tenant_id,
        )
