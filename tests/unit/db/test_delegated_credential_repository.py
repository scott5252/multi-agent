from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.access_control import PrincipalIdentity
from multi_agent_platform.db.models.delegated_credential import (
    DelegatedCredentialLink,
    DelegatedCredentialStatus,
)
from multi_agent_platform.db.models.secret_reference import SecretReference
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)


async def test_delegated_credential_repository_lists_and_filters_links(session) -> None:
    access_repository = AccessControlRepository(session)
    repository = DelegatedCredentialRepository(session)
    tenant_id = uuid4()
    owner = await access_repository.upsert_principal(
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
    link = await repository.create(
        DelegatedCredentialLink(
            secret_reference_id=secret_reference.secret_reference_id,
            owner_principal_id=owner.principal_identity_id,
            tenant_id=tenant_id,
            approved_tool_ids=["gmail.send"],
            granted_scopes=["gmail.send"],
            status=DelegatedCredentialStatus.REVOKED,
        )
    )

    assert await repository.get(link.delegated_credential_link_id) is not None
    assert await repository.list_for_principal(owner.principal_identity_id)
    assert (
        await repository.resolve_for_tool(
            delegated_credential_link_id=link.delegated_credential_link_id,
            tenant_id=tenant_id,
            tool_id="gmail.send",
        )
        is None
    )
