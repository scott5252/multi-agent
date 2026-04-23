from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.local_principals import LocalPrincipalCatalog
from multi_agent_platform.auth.service import AuthorizationError, AuthService
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.delegated_credential import (
    DelegatedCredentialRepository,
)


def test_platform_secret_authorization_requires_tenant_alignment(
    session, settings
) -> None:
    service = AuthService(
        settings=settings,
        access_repository=AccessControlRepository(session),
        delegated_credential_repository=DelegatedCredentialRepository(session),
        audit_recorder=AccessAuditRecorder(
            AccessControlRepository(session),
            AuditService(AuditRepository(session)),
        ),
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
