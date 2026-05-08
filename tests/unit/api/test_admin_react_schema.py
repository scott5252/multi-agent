from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminActionMetadata,
    ReactAdminCommandSearchResult,
    ReactAdminEmptyStateMetadata,
    ReactAdminPageProvenance,
    ReactAdminPrincipal,
    ReactAdminScope,
    ReactAdminShellNotification,
    ReactAdminShellState,
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


def test_react_admin_provenance_and_empty_state_are_safe() -> None:
    provenance = ReactAdminPageProvenance(
        source_kind="empty_live_state",
        source_label="Workflow repository",
        source_detail="Repository returned no rows for the active tenant.",
    )
    empty_state = ReactAdminEmptyStateMetadata(
        reason="no_live_rows",
        title="No workflows",
        summary="Create a workflow draft before publish-gate evidence appears.",
        setup_hint="Use the workflow builder.",
        provenance=provenance,
    )
    shell_state = ReactAdminShellState(
        state="empty",
        title="No live records",
        summary="The page has no persisted rows for this scope.",
        provenance=provenance,
        empty_state=empty_state,
    )

    assert shell_state.provenance.source_kind == "empty_live_state"
    assert shell_state.empty_state.reason == "no_live_rows"

    with pytest.raises(ValidationError):
        ReactAdminPageProvenance(
            source_kind="computed_metadata",
            source_label="/Users/scott/raw.json",
        )

    with pytest.raises(ValidationError):
        ReactAdminEmptyStateMetadata(
            reason="dependency_unavailable",
            title="Provider payload",
            summary="safe",
            provenance=provenance,
        )


def test_react_admin_action_metadata_rejects_raw_identifiers() -> None:
    metadata = ReactAdminActionMetadata(
        revision="backend-revision-current",
        revision_source="backend",
        idempotency_key="client-generated-key",
        idempotency_source="generated_client_state",
        request_id="client-request-id",
        request_id_source="generated_client_state",
    )

    assert metadata.idempotency_source == "generated_client_state"

    with pytest.raises(ValidationError):
        ReactAdminActionMetadata(
            idempotency_key="/Users/scott/secrets/request",
            idempotency_source="generated_client_state",
        )
