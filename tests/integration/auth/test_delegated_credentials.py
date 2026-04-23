from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.auth.service import AuthorizationError, AuthService
from multi_agent_platform.db.models.access_control import PrincipalIdentity
from multi_agent_platform.db.models.delegated_credential import DelegatedCredentialLink
from multi_agent_platform.db.models.secret_reference import SecretReference
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)


async def test_delegated_credentials_remain_tenant_bound(session, settings) -> None:
    access_repository = AccessControlRepository(session)
    delegated_repository = DelegatedCredentialRepository(session)
    audit_service = AuditService(AuditRepository(session))
    service = AuthService(
        settings=settings,
        access_repository=access_repository,
        delegated_credential_repository=delegated_repository,
        audit_recorder=AccessAuditRecorder(access_repository, audit_service),
        jwt_validator=None,
        local_principal_catalog=LocalPrincipalCatalog(
            settings.local_principal_catalog_json
        ),
        auth_failure_detail=None,
    )
    tenant_id = uuid4()
    identity = await access_repository.upsert_principal(
        PrincipalIdentity(
            auth_provider="local_principal",
            external_subject="tenant-admin-acme",
        )
    )
    secret_reference = SecretReference(
        tenant_id=tenant_id,
        scope_type="user_delegated",
        name="gmail",
        provider_key="secret-manager/gmail",
        access_policy={},
    )
    session.add(secret_reference)
    await session.flush()
    delegated = await delegated_repository.create(
        DelegatedCredentialLink(
            secret_reference_id=secret_reference.secret_reference_id,
            owner_principal_id=identity.principal_identity_id,
            tenant_id=tenant_id,
            approved_tool_ids=["gmail.send"],
            granted_scopes=["gmail.send"],
        )
    )
    principal = service.local_principal_catalog.as_principal_context(
        "tenant-admin-acme",
        trace_id="trace",
        request_id="req",
    ).model_copy(
        update={
            "tenant_id": tenant_id,
            "principal_identity_id": identity.principal_identity_id,
        }
    )

    with pytest.raises(AuthorizationError):
        await service.authorize_delegated_credential(
            principal=principal,
            delegated_credential_link_id=delegated.delegated_credential_link_id,
            tool_id="gmail.send",
            tenant_id=uuid4(),
        )
