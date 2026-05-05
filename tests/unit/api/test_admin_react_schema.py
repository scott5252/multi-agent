from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminCommandSearchResult,
    ReactAdminPrincipal,
    ReactAdminScope,
    ReactAdminShellNotification,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def test_react_admin_principal_is_safe_summary_only() -> None:
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=uuid4(),
        role_codes=("tenant_admin", "tenant_user"),
        permission_codes=("tenant:read", "secret:raw"),
        token_subject="auth0|secret-subject",
        token_jti="raw-jti",
        trace_id="trace-react-admin",
    )

    payload = ReactAdminPrincipal.from_context(principal).model_dump()

    assert payload == {
        "principal_id": "tenant-admin-acme",
        "display_name": "tenant-admin-acme",
        "role_codes": ("tenant_admin", "tenant_user"),
        "auth_mode": "local_principal",
        "trace_id": "trace-react-admin",
    }
    assert "token_subject" not in payload
    assert "permission_codes" not in payload


def test_react_admin_scope_requires_safe_label() -> None:
    tenant_id = uuid4()
    scope = ReactAdminScope(
        scope_type="tenant",
        tenant_id=tenant_id,
        label="  Acme  ",
    )

    assert scope.label == "Acme"
    assert scope.tenant_id == tenant_id

    with pytest.raises(ValidationError):
        ReactAdminScope(scope_type="tenant", tenant_id=tenant_id, label=" ")


def test_shell_summaries_are_trimmed_and_reject_empty_values() -> None:
    result = ReactAdminCommandSearchResult(
        result_id="workflow",
        label="  Workflow Registry  ",
        description="  Open authorized workflow pages  ",
        group="  Workflows  ",
        href="/admin/workflows/ui",
        required_scope="either",
        fallback_kind="jinja",
    )

    assert result.label == "Workflow Registry"
    assert result.description == "Open authorized workflow pages"
    assert result.group == "Workflows"

    with pytest.raises(ValidationError):
        ReactAdminShellNotification(
            notification_id="unsafe-empty",
            tone="info",
            title=" ",
            summary="safe",
        )
