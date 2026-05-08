from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from tests.integration.test_admin_react_routes import _configure_env


def test_transitional_label_gate_route_is_authorized_and_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        platform_response = client.get(
            "/admin/app/migration/transitional-labels.json?ci_mode=true",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_response = client.get(
            f"/admin/app/migration/transitional-labels.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/migration/transitional-labels.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform_response.status_code == 200
    assert tenant_response.status_code == 200
    assert cross_tenant.status_code == 403
    payload = platform_response.json()
    assert payload["page_id"] == "qa059-transitional-label-gate"
    assert payload["summary"]["blocked_count"] == 0
    assert payload["summary"]["allowed_reference_count"] >= 3
    assert payload["summary"]["ci_status"] == "pass"
    serialized = json.dumps(payload)
    assert "React Admin" not in serialized
    assert "qa059-secret-value" not in serialized
    assert "/Users/" not in serialized
    assert "Globex" not in cross_tenant.text


def test_transitional_label_gate_projection_is_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/app/migration/transitional-labels.json?tenant_id={tenant_id}&source_scan=false",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["blocked_count"] == 0
    assert payload["summary"]["allowed_reference_count"] == 3
    assert payload["evidence"][0]["evidence_id"] == "qa059-source-visible-text-scan"


def test_auth0_shaped_transitional_label_gate_principal_is_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-reviewer",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-qa059",
            token_subject="auth0|hidden-qa059",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/admin/app/migration/transitional-labels.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    serialized = json.dumps(response.json())
    assert "auth0|hidden-qa059" not in serialized
