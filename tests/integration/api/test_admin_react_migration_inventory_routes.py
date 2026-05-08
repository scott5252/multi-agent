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


def test_local_principal_decommission_inventory_is_authorized_and_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        platform_response = client.get(
            "/admin/app/migration/decommission-inventory.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_response = client.get(
            f"/admin/app/migration/decommission-inventory.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/migration/decommission-inventory.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform_response.status_code == 200
    assert tenant_response.status_code == 200
    assert cross_tenant.status_code == 403
    assert platform_response.json()["summary"]["template_count"] == 0
    tenant_payload = tenant_response.json()
    assert tenant_payload["summary"]["template_count"] == 0
    assert tenant_payload["summary"]["total_items"] == 0
    assert tenant_payload["groups"]
    serialized = json.dumps(tenant_payload)
    assert "qa038-secret-value" not in serialized
    assert "/Users/" not in serialized
    assert "Globex" not in cross_tenant.text


def test_auth0_shaped_decommission_inventory_principal_is_safe(
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
            trace_id="trace-auth0-inventory",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/admin/app/migration/decommission-inventory.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["total_items"] == 0
    assert "auth0|hidden" not in json.dumps(payload)


def test_migration_bootstrap_exposes_final_live_only_gate_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            "/admin/app/migration/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert response.status_code == 200
    payload = response.json()
    live_data = payload["live_data_inventory"]
    assert live_data["page_id"] == "qa058-live-only-gate"
    assert live_data["summary"]["blocking_findings"] == 0
    assert live_data["summary"]["mapped_legacy_findings"] == 0
    assert live_data["evidence"][0]["evidence_id"] == "qa058-live-only-source-scan"
