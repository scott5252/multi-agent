from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant


def _configure_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    database_path = tmp_path / "react-admin.db"
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0020_live_model_credentials')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(tenant_id=tenant_id, slug="acme", display_name="Acme"),
                Tenant(
                    tenant_id=other_tenant_id,
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("APP_VERSION", "0.1.0")
    monkeypatch.setenv("COMMIT_SHA", "test-sha")
    monkeypatch.setenv("BUILD_TIME", "2026-05-04T00:00:00+00:00")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "skill-registry:install",
                        "skill-registry:bind",
                        "skill-execution:read",
                    ],
                },
                "tenant-user-acme": {
                    "catalog_key": "tenant-user-acme",
                    "display_name": "Tenant User",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user"],
                    "permission_codes": ["tenant:read"],
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "operations:read",
                        "admin:model-providers:write",
                        "skill-registry:publish",
                        "skill-execution:read",
                    ],
                },
                "auditor": {
                    "catalog_key": "auditor",
                    "display_name": "Auditor",
                    "role_codes": ["auditor"],
                    "permission_codes": ["operations:read"],
                },
            }
        ),
    )


def test_local_principal_react_admin_entry_and_bootstrap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bootstrap = client.get(
            f"/admin/app/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert "React Admin" in html.text
    assert "data-bootstrap-url" in html.text
    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["principal"]["auth_mode"] == "local_principal"
    assert payload["active_scope"]["tenant_id"] == str(tenant_id)
    assert payload["active_scope"]["label"] == "Acme"
    assert payload["feature_flags"]["react_admin_enabled"] is True
    assert payload["version"]["api_version"] == "qa034"
    workflow_nav = [
        item
        for group in payload["navigation"]
        for item in group["items"]
        if item["admin_area"] == "workflows"
    ][0]
    assert workflow_nav["href"] == f"/admin/app/workflows?tenant_id={tenant_id}"
    assert workflow_nav["fallback_kind"] == "react"
    assert payload["shell"]["product_name"] == "Multi-Agent Admin"
    assert payload["shell"]["breadcrumbs"][0]["label"] == "Admin"
    assert payload["shell"]["command_results"]
    assert "token_subject" not in json.dumps(payload)
    assert "raw-jti" not in json.dumps(payload)


def test_auth0_backed_principal_summary_uses_existing_context(
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
            trace_id="trace-auth0-react",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(f"/admin/app/bootstrap.json?tenant_id={tenant_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["principal"]["auth_mode"] == "auth0"
    assert payload["principal"]["principal_id"] == "auth0-reviewer"
    assert payload["shell"]["design_token_version"] == "qa034"
    assert "auth0|hidden" not in json.dumps(payload)


def test_react_admin_search_metadata_is_authorized_and_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
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
            trace_id="trace-auth0-search",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        tenant_search = client.get(
            f"/admin/app/search.json?tenant_id={tenant_id}&q=workflow",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/search.json")
        cross_tenant = client.get(
            f"/admin/app/search.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert tenant_search.status_code == 200
    payload = tenant_search.json()
    assert payload["query"] == "workflow"
    assert payload["results"]
    assert all("href" in result for result in payload["results"])
    assert "auth0|hidden" not in json.dumps(payload)
    assert missing.status_code == 401
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_search = client.get(
                f"/admin/app/search.json?tenant_id={tenant_id}&q=workflow"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_search.status_code == 200
    assert auth0_search.json()["results"]


def test_react_admin_patterns_envelope_is_authorized_and_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-patterns",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-patterns",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        tenant_page = client.get(
            f"/admin/app/patterns.json?tenant_id={tenant_id}&status=ready",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/patterns.json")
        cross_tenant = client.get(
            f"/admin/app/patterns.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/patterns?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert tenant_page.status_code == 200
    payload = tenant_page.json()
    assert payload["page_id"] == "react-admin-patterns"
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["filters"]["active_chips"][0]["label"] == "Status: ready"
    assert payload["pagination"]["page_size"] == 10
    assert payload["data"]["records"][0]["owner_scope"] == "Acme"
    assert "auth0|hidden" not in json.dumps(payload)
    assert "qa028-secret-value" not in json.dumps(payload)
    assert missing.status_code == 401
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text
    assert html.status_code == 200
    assert "React Admin" in html.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(f"/admin/app/patterns.json?tenant_id={tenant_id}")
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)


def test_react_admin_patterns_rejects_bad_filters_and_sorting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        bad_filter = client.get(
            f"/admin/app/patterns.json?tenant_id={tenant_id}&status=raw-secret",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bad_sort = client.get(
            f"/admin/app/patterns.json?tenant_id={tenant_id}&sort=provider_payload",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert bad_filter.status_code == 400
    assert bad_filter.json()["detail"]["reason_category"] == "validation_error"
    assert "raw-secret" not in bad_filter.text
    assert bad_sort.status_code == 400
    assert bad_sort.json()["detail"]["field_errors"][0]["field"] == "sort"


def test_react_admin_patterns_mutation_and_export_results_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        accepted = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "sample_name": "Preview",
                "revision": "sample-revision-current",
                "idempotency_key": "key-1",
                "confirmed": True,
                "outcome": "accepted",
            },
        )
        invalid = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "sample_name": "",
                "revision": "sample-revision-current",
                "idempotency_key": "key-2",
                "confirmed": False,
                "outcome": "accepted",
            },
        )
        stale = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "sample_name": "Preview",
                "revision": "stale-revision",
                "idempotency_key": "key-3",
                "confirmed": False,
                "outcome": "stale",
            },
        )
        replay = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "sample_name": "Preview",
                "revision": "sample-revision-current",
                "idempotency_key": "replay-key",
                "confirmed": False,
                "outcome": "replay",
            },
        )
        confirmation = client.post(
            f"/admin/app/patterns/actions/sample?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "sample_name": "Preview",
                "revision": "sample-revision-current",
                "idempotency_key": "key-4",
                "confirmed": False,
                "outcome": "confirmation",
            },
        )
        export = client.post(
            f"/admin/app/patterns/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"
    assert invalid.json()["status"] == "validation_error"
    assert invalid.json()["field_errors"][0]["field"] == "sample_name"
    assert stale.json()["status"] == "stale_conflict"
    assert stale.json()["stale_conflict"]["current_revision"]
    assert replay.json()["status"] == "replayed"
    assert replay.json()["idempotency"]["replayed"] is True
    assert confirmation.json()["status"] == "confirmation_required"
    assert confirmation.json()["confirmation"]["confirm_label"] == "Confirm preview"
    assert export.status_code == 200
    assert export.json()["status"] == "complete"
    assert not export.json()["artifact_reference_id"].startswith("/")
    assert "/Users/" not in json.dumps(export.json())


def test_react_admin_operations_workbench_platform_and_tenant_views_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_platform_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-platform",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            role_codes=("platform_admin",),
            permission_codes=("operations:read",),
            trace_id="trace-auth0-workbench",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/operations.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        auditor = client.get(
            "/admin/app/operations.json",
            headers={"X-Local-Principal": "auditor"},
        )
        tenant = client.get(
            f"/admin/app/operations.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/operations.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            "/admin/app/operations",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert platform.status_code == 200
    payload = platform.json()
    assert payload["page_id"] == "react-operations-workbench"
    assert payload["scope"]["scope_type"] == "platform"
    assert payload["time_range"]["preset"] == "60m"
    assert payload["refresh"]["interval_seconds"] == 30
    assert "Provider health" in json.dumps(payload)
    assert "qa029-secret-value" not in json.dumps(payload)
    assert "/Users/" not in json.dumps(payload)
    assert auditor.status_code == 200
    assert tenant.status_code == 200
    tenant_payload = tenant.json()
    assert tenant_payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Tenant run health" in json.dumps(tenant_payload)
    assert "Provider health" not in json.dumps(tenant_payload)
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text
    assert html.status_code == 200
    assert "React Admin" in html.text

    app.dependency_overrides[require_authorized_principal] = auth0_platform_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get("/admin/app/operations.json")
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["scope_type"] == "platform"


def test_react_admin_operations_workbench_filters_run_debug_and_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    run_id = "00000000-0000-0000-0000-000000000029"

    with TestClient(app) as client:
        filtered = client.get(
            "/admin/app/operations.json?severity=warning&subsystem=gateway",
            headers={"X-Local-Principal": "platform-admin"},
        )
        bad_range = client.get(
            "/admin/app/operations.json?range=24h",
            headers={"X-Local-Principal": "platform-admin"},
        )
        bad_subsystem = client.get(
            "/admin/app/operations.json?subsystem=provider_payload",
            headers={"X-Local-Principal": "platform-admin"},
        )
        run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        platform_run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        cross_run_debug = client.get(
            f"/admin/app/operations/runs/{run_id}.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing_export = client.post("/admin/app/operations/export")
        export = client.post(
            "/admin/app/operations/export",
            headers={"X-Local-Principal": "platform-admin"},
            json={
                "scope_type": "active",
                "range": "60m",
                "include_run_debug": True,
            },
        )
        tenant_export = client.post(
            f"/admin/app/operations/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"scope_type": "active", "range": "60m"},
        )
        cross_export = client.post(
            f"/admin/app/operations/export?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={"scope_type": "active", "range": "60m"},
        )

    assert filtered.status_code == 200
    assert filtered.json()["logs"][0]["subsystem"] == "gateway"
    assert bad_range.status_code == 400
    assert bad_range.json()["detail"]["field_errors"][0]["field"] == "range"
    assert "24h" not in bad_range.text
    assert bad_subsystem.status_code == 400
    assert "provider_payload" not in bad_subsystem.text
    assert run_debug.status_code == 200
    debug_payload = run_debug.json()
    assert debug_payload["workflow_run_id"] == run_id
    assert debug_payload["branches"]
    assert debug_payload["gateway_attempts"][0]["credential_diagnostic_category"]
    assert debug_payload["tool_calls"][0]["policy_outcome"] == "allowed_read_only"
    assert debug_payload["deliveries"][0]["failure_category"] == "mock_delivery_retry"
    assert platform_run_debug.status_code == 200
    assert platform_run_debug.json()["tenant_scope"] is None
    assert cross_run_debug.status_code == 403
    assert "Globex" not in cross_run_debug.text
    assert missing_export.status_code == 401
    assert export.status_code == 200
    export_payload = export.json()
    assert export_payload["status"] == "complete"
    assert export_payload["artifact_reference_id"] == "artifact-ref-qa029-platform"
    assert "/Users/" not in json.dumps(export_payload)
    assert "qa029-secret-value" not in json.dumps(export_payload)
    assert tenant_export.status_code == 200
    assert tenant_export.json()["artifact_reference_id"] == "artifact-ref-qa029-tenant"
    assert cross_export.status_code == 403
    assert "Globex" not in cross_export.text


def test_react_admin_workflow_builder_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-workflow-builder",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-workflow-builder",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/workflows/builder.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        lookups = client.get(
            f"/admin/app/workflows/lookups.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/workflows?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/workflows/builder.json")
        denied = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/workflows/builder.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    assert platform.json()["scope"]["scope_type"] == "platform"
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["page_id"] == "react-workflow-builder"
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["draft"]["graph"]["nodes"]
    assert payload["publish_readiness"]["required_evidence"]
    assert payload["json_inspector"]["artifact_reference_id"]
    assert "qa030-secret-value" not in json.dumps(payload)
    assert "raw prompt" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert lookups.status_code == 200
    assert lookups.json()["prompt_options"][0]["reference_id"]
    assert html.status_code == 200
    assert "React Admin" in html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/workflows/builder.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_workflow_builder_save_validate_and_publish_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    draft_id = "00000000-0000-0000-0000-000000000030"
    current_revision = "draft-rev-qa030-current"
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    save_payload = {
        "description": "Prepare a safe daily intelligence briefing for a tenant.",
        "idempotency_key": "save-key",
        "join_policy": "wait_for_required_branches",
        "name": "Daily briefing workflow",
        "revision": current_revision,
        "selected_profile_ref": "profile-briefing-safe",
        "selected_prompt_ref": "prompt-daily-briefing-v3",
    }

    with TestClient(app) as client:
        accepted = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/save?tenant_id={tenant_id}",
            headers=headers,
            json=save_payload,
        )
        stale = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/save?tenant_id={tenant_id}",
            headers=headers,
            json={**save_payload, "force_stale": True, "idempotency_key": "stale"},
        )
        blocked_validation = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/validate?tenant_id={tenant_id}",
            headers=headers,
        )
        ready_validation = client.post(
            (
                f"/admin/app/workflows/drafts/{draft_id}/validate"
                f"?tenant_id={tenant_id}&ready=true"
            ),
            headers=headers,
        )
        blocked_publish = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": False,
                "idempotency_key": "publish-blocked",
                "ready_fixture": False,
                "revision": current_revision,
            },
        )
        confirmation = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": False,
                "idempotency_key": "publish-confirm",
                "ready_fixture": True,
                "revision": current_revision,
            },
        )
        published = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={tenant_id}",
            headers=headers,
            json={
                "confirmed": True,
                "idempotency_key": "publish-accepted",
                "ready_fixture": True,
                "revision": current_revision,
            },
        )
        cross_publish = client.post(
            f"/admin/app/workflows/drafts/{draft_id}/publish?tenant_id={other_tenant_id}",
            headers=headers,
            json={
                "confirmed": True,
                "idempotency_key": "publish-cross",
                "ready_fixture": True,
                "revision": current_revision,
            },
        )

    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"
    assert accepted.json()["revision"] == "draft-rev-qa030-next"
    assert stale.json()["status"] == "stale_conflict"
    assert stale.json()["stale_conflict"]["submitted_revision"] == current_revision
    assert blocked_validation.json()["validation"]["findings"]
    assert ready_validation.json()["publish_readiness"]["confirmation"] is not None
    assert blocked_publish.json()["status"] == "validation_error"
    assert confirmation.json()["status"] == "confirmation_required"
    assert published.json()["status"] == "accepted"
    assert published.json()["publish_readiness"]["published_bundle_summary"]
    assert cross_publish.status_code == 403
    assert "Globex" not in cross_publish.text


def test_react_admin_governance_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-governance",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-governance",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/governance/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        providers = client.get(
            f"/admin/app/governance/providers.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/governance?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/governance/bootstrap.json")
        denied = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/governance/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    platform_payload = platform.json()
    assert platform_payload["page_id"] == "react-governance"
    assert platform_payload["scope"]["scope_type"] == "platform"
    assert platform_payload["providers"][0]["authorized_actions"]
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["providers"][0]["authorized_actions"] == []
    assert payload["prompts"][0]["authorized_actions"]
    assert payload["routing_preview"]["direct_call_guardrail"]
    assert payload["run_provenance"][0]["credential_reference_evidence"]
    assert "qa031-secret-value" not in json.dumps(payload)
    assert "raw prompt" not in json.dumps(payload).lower()
    assert "raw completion" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert providers.status_code == 200
    assert providers.json()["providers"][0]["credential_reference"]["fingerprint"]
    assert html.status_code == 200
    assert "React Admin" in html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/governance/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_governance_actions_are_safe_and_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    tenant_headers = {"X-Local-Principal": "tenant-admin-acme"}
    platform_headers = {"X-Local-Principal": "platform-admin"}

    with TestClient(app) as client:
        probe = client.post(
            "/admin/app/governance/providers/openai-primary/probe",
            headers=platform_headers,
        )
        tenant_probe = client.post(
            "/admin/app/governance/providers/openai-primary/probe",
            headers=tenant_headers,
        )
        credential_reference = client.post(
            "/admin/app/governance/providers/openai-primary/credential-reference",
            headers=platform_headers,
            json={
                "credential_reference_id": "secret-ref-openai-primary",
                "revision": "provider-rev-qa031-current",
            },
        )
        prompt_save = client.post(
            f"/admin/app/governance/prompts/daily-briefing/save?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "prompt-save",
                "publish": False,
                "revision": "prompt-rev-qa031-current",
                "safe_summary": "Review fixture-safe prompt summary.",
            },
        )
        prompt_preview = client.post(
            f"/admin/app/governance/prompts/daily-briefing/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={"fixture_id": "qa031-unsafe-preview"},
        )
        profile_save = client.post(
            f"/admin/app/governance/profiles/briefing-runtime/save?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "profile-save",
                "model_binding": "gpt-qa031-safe-route",
                "provider_binding": "openai-primary",
                "revision": "profile-rev-qa031-current",
            },
        )
        profile_resolve = client.post(
            f"/admin/app/governance/profiles/briefing-runtime/resolve?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        routing = client.post(
            f"/admin/app/governance/routing/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "profile_id": "briefing-runtime",
                "skill_id": "weather-readonly",
                "workflow_context": "Daily briefing workflow",
            },
        )
        history = client.get(
            f"/admin/app/governance/history.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        provenance = client.get(
            f"/admin/app/governance/provenance/run-qa031-briefing.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        cross_history = client.get(
            f"/admin/app/governance/history.json?tenant_id={other_tenant_id}",
            headers=tenant_headers,
        )

    assert probe.status_code == 200
    assert (
        probe.json()["probe"]["credential_resolution_status"]
        == "safe reference selected"
    )
    assert "raw provider" not in probe.text.lower()
    assert tenant_probe.status_code == 403
    assert tenant_probe.json()["detail"] in {
        "insufficient_permission",
        "platform_admin_required",
    }
    assert credential_reference.status_code == 200
    assert credential_reference.json()["status"] == "accepted"
    assert "resolved credential" not in credential_reference.text.lower()
    assert prompt_save.json()["status"] == "accepted"
    assert prompt_preview.json()["status"] == "summarized"
    assert "raw prompt" not in prompt_preview.text.lower()
    assert "raw completion" not in prompt_preview.text.lower()
    assert profile_save.json()["profile_resolution"]["provider_route"]
    assert profile_resolve.json()["status"] == "ready"
    assert routing.json()["routing_preview"]["direct_call_guardrail"]
    assert "No live providers were invoked." in routing.text
    assert history.json()["history"][0]["audit_reference_id"]
    assert provenance.json()["credential_reference_evidence"]
    assert cross_history.status_code == 403
    assert "Globex" not in cross_history.text


def test_react_admin_skill_lifecycle_platform_tenant_and_auth0_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-skills",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=(
                "tenant:read",
                "tenant:admin",
                "skill-registry:install",
                "skill-registry:bind",
                "skill-execution:read",
            ),
            trace_id="trace-auth0-skills",
            token_subject="auth0|hidden",
        )

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/skills/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        discovery = client.get(
            f"/admin/app/skills/discovery.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        diagnostics = client.get(
            f"/admin/app/skills/diagnostics.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        legacy_routes = client.get(
            f"/admin/app/skills/legacy-routes.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/skills?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        missing = client.get("/admin/app/skills/bootstrap.json")
        denied = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/skills/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    platform_payload = platform.json()
    assert platform_payload["page_id"] == "react-skill-lifecycle"
    assert platform_payload["scope"]["scope_type"] == "platform"
    assert platform_payload["platform_publication"]["candidate"]["manifest_source"]
    assert tenant.status_code == 200
    payload = tenant.json()
    assert payload["platform_publication"] is None
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert payload["tenant_discovery"]["grants"][0]["tenant_label"] == "Acme"
    assert payload["connector_diagnostics"][0]["connector_label"] == "Calendar"
    assert payload["binding_preview"]["eligible_tools"]
    assert payload["audit_timeline"][0]["audit_reference_id"]
    assert "qa032-secret-value" not in json.dumps(payload)
    assert "raw manifest" not in json.dumps(payload).lower()
    assert "resolved credential" not in json.dumps(payload).lower()
    assert "authorization header" not in json.dumps(payload).lower()
    assert "/Users/" not in json.dumps(payload)
    assert discovery.status_code == 200
    assert discovery.json()["discovery"]["available_versions"]
    assert diagnostics.status_code == 200
    assert (
        diagnostics.json()["diagnostics"][0]["gateway_decision"] == "allowed_read_only"
    )
    assert legacy_routes.status_code == 200
    assert legacy_routes.json()[0]["legacy_path"] == (
        "/admin/skill-registry/ui/packages"
    )
    assert legacy_routes.json()[-1]["react_path"] == "/admin/app/skills/diagnostics"
    assert html.status_code == 200
    assert "React Admin" in html.text
    assert missing.status_code == 401
    assert denied.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_page = client.get(
                f"/admin/app/skills/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_page.status_code == 200
    assert auth0_page.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in auth0_page.text


def test_react_admin_skill_lifecycle_actions_are_safe_and_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()
    tenant_headers = {"X-Local-Principal": "tenant-admin-acme"}
    platform_headers = {"X-Local-Principal": "platform-admin"}

    install_payload = {
        "idempotency_key": "install",
        "package_id": "package-daily-briefing-connectors",
        "revision": "installation-rev-qa032-current",
        "upgrade": False,
        "version_id": "package-version-daily-briefing-1-4-0",
    }

    with TestClient(app) as client:
        candidate = client.post(
            "/admin/app/skills/packages/candidates",
            headers=platform_headers,
            json={
                "candidate_revision": None,
                "idempotency_key": "candidate",
                "manifest_text": "unsafe sample text with qa032-secret-value",
                "uploaded_fixture_id": "qa032-uploaded-manifest",
            },
        )
        tenant_candidate = client.post(
            "/admin/app/skills/packages/candidates",
            headers=tenant_headers,
            json={
                "idempotency_key": "candidate",
                "manifest_text": "safe fixture",
                "uploaded_fixture_id": None,
            },
        )
        blocked_validation = client.post(
            "/admin/app/skills/packages/candidates/qa032-candidate/validate?ready=false",
            headers=platform_headers,
        )
        stale_publish = client.post(
            "/admin/app/skills/packages/candidates/qa032-candidate/publish",
            headers=platform_headers,
            json={
                "candidate_revision": "stale-revision",
                "confirmed": True,
                "idempotency_key": "publish-stale",
            },
        )
        published = client.post(
            "/admin/app/skills/packages/candidates/qa032-candidate/publish",
            headers=platform_headers,
            json={
                "candidate_revision": "candidate-rev-qa032-current",
                "confirmed": True,
                "idempotency_key": "publish",
            },
        )
        grant = client.post(
            "/admin/app/skills/packages/package-daily-briefing-connectors/grants",
            headers=platform_headers,
            json={
                "grant_enabled": True,
                "idempotency_key": "grant",
                "revision": "grant-rev-qa032-current",
                "tenant_id": str(tenant_id),
                "version_id": "package-version-daily-briefing-1-4-0",
            },
        )
        quarantine = client.post(
            "/admin/app/skills/packages/package-daily-briefing-connectors/quarantine",
            headers=platform_headers,
        )
        install = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/install?tenant_id={tenant_id}",
            headers=tenant_headers,
            json=install_payload,
        )
        stale_install = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/install?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={**install_payload, "revision": "stale-revision"},
        )
        credential = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/credentials?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "credential",
                "revision": "installation-rev-qa032-current",
                "selected_reference_id": "cred-ref-acme-briefing",
            },
        )
        bad_credential = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/credentials?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "credential-bad",
                "revision": "installation-rev-qa032-current",
                "selected_reference_id": "other-tenant-reference",
            },
        )
        smoke = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/smoke-tests?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "idempotency_key": "smoke",
                "revision": "installation-rev-qa032-current",
            },
        )
        binding = client.post(
            f"/admin/app/skills/installations/install-qa032-daily-briefing/eligibility/preview?tenant_id={tenant_id}",
            headers=tenant_headers,
            json={
                "package_id": "package-daily-briefing-connectors",
                "profile_id": "profile-briefing-runtime",
                "workflow_context": "Daily briefing workflow",
            },
        )
        diagnostic = client.post(
            f"/admin/app/skills/diagnostics/run?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        audit = client.get(
            f"/admin/app/skills/audit.json?tenant_id={tenant_id}",
            headers=tenant_headers,
        )
        cross_audit = client.get(
            f"/admin/app/skills/audit.json?tenant_id={other_tenant_id}",
            headers=tenant_headers,
        )

    assert candidate.status_code == 200
    assert candidate.json()["status"] == "accepted"
    assert "qa032-secret-value" not in candidate.text
    assert "uploaded manifest fixture took precedence" in candidate.text.lower()
    assert tenant_candidate.status_code == 403
    assert blocked_validation.json()["status"] == "validation_error"
    assert stale_publish.json()["status"] == "stale_conflict"
    assert published.json()["publication"]["lifecycle_status"] == "published"
    assert grant.json()["status"] == "accepted"
    assert quarantine.json()["publication"]["lifecycle_status"] == "quarantined"
    assert install.json()["installation"]["credential_readiness"] == "ready"
    assert stale_install.json()["status"] == "stale_conflict"
    assert credential.json()["credential"]["fingerprint"] == "fp_qa032_acme_briefing"
    assert "resolved credential" not in credential.text.lower()
    assert bad_credential.json()["status"] == "validation_error"
    assert smoke.json()["smoke_test"]["readiness"] == "queued"
    assert binding.json()["binding_preview"]["blocked_tools"] == ["email.send"]
    assert "No live tools" in binding.text
    assert diagnostic.json()["diagnostic"]["gateway_decision"] == "allowed_read_only"
    assert "connector request" not in diagnostic.text.lower()
    assert audit.json()["audit_timeline"][0]["audit_reference_id"]
    assert cross_audit.status_code == 403
    assert "Globex" not in cross_audit.text


def test_react_admin_test_bench_routes_are_safe_and_dual_auth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            f"/admin/app/test-bench?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        bootstrap = client.get(
            f"/admin/app/test-bench/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        suites = client.get(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        run_detail = client.get(
            f"/admin/app/test-bench/runs/run-qa033-failing.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        gates = client.get(
            f"/admin/app/test-bench/gates.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        artifact = client.get(
            f"/admin/app/test-bench/artifacts/artifact-qa033-summary.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        audit = client.get(
            f"/admin/app/test-bench/audit.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/test-bench/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["title"] == "Test Bench"
    assert (
        payload["selected_suite"]["summary"]["default_safe_mode"] == "mock_model_tools"
    )
    assert payload["gate_alerts"][0]["evidence_status"] == "stale"
    assert suites.status_code == 200
    assert suites.json()["form_metadata"]["default_pass_threshold"] == 0.9
    assert run_detail.status_code == 200
    assert run_detail.json()["summary"]["status"] == "failed"
    assert run_detail.json()["assertion_diagnostics"][0]["category"] == (
        "failed_assertion"
    )
    assert gates.status_code == 200
    assert {gate["evidence_status"] for gate in gates.json()["gates"]} >= {
        "missing",
        "stale",
        "passed",
    }
    assert artifact.status_code == 200
    assert artifact.json()["authorized_href"].endswith(".json")
    assert audit.status_code == 200
    assert audit.json()["audit_timeline"][0]["tenant_scope_label"] == "Acme"
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    serialized = json.dumps(payload).lower()
    assert "qa033-secret-value" not in serialized
    assert "raw prompt" not in serialized
    assert "raw completion" not in serialized
    assert "connector request" not in serialized
    assert "storage path" not in serialized

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-test-bench-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-test-bench",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_bootstrap = client.get(
                f"/admin/app/test-bench/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_bootstrap.status_code == 200
    assert auth0_bootstrap.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in json.dumps(auth0_bootstrap.json())


def test_react_admin_test_bench_mutations_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        suite_save = client.post(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Daily briefing release gate",
                "target_type": "workflow_draft",
                "target_id": "workflow-draft-qa033-daily-briefing",
                "target_revision": "workflow-draft-rev-qa033-current",
                "default_safe_mode": "mock_model_tools",
                "pass_threshold": 0.9,
                "required_for_publish": True,
                "revision": "suite-rev-qa033-current",
                "idempotency_key": "suite-save-route",
            },
        )
        stale_suite = client.post(
            f"/admin/app/test-bench/suites?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Daily briefing release gate",
                "target_type": "workflow_draft",
                "target_id": "workflow-draft-qa033-daily-briefing",
                "target_revision": "workflow-draft-rev-qa033-current",
                "default_safe_mode": "mock_model_tools",
                "pass_threshold": 0.9,
                "required_for_publish": True,
                "revision": "stale-suite-revision",
                "idempotency_key": "suite-save-route",
            },
        )
        case_save = client.post(
            f"/admin/app/test-bench/suites/suite-qa033-daily-briefing/cases?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Briefing summary contract",
                "fixture_summary": "Fixture includes weather metadata summary.",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "evaluator_reference_id": "evaluator-qa033-safe-summary",
                "revision": "case-rev-qa033-current",
                "idempotency_key": "case-save-route",
            },
        )
        launch = client.post(
            f"/admin/app/test-bench/suites/suite-qa033-daily-briefing/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": "workflow-draft-rev-qa033-current",
                "safe_mode": "side_effect_disabled_gateway",
                "run_reason": "Release confidence",
                "idempotency_key": "run-launch-route",
            },
        )
        probe_denied = client.post(
            f"/admin/app/test-bench/suites/suite-qa033-daily-briefing/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": "workflow-draft-rev-qa033-current",
                "safe_mode": "real_dependency_probe",
                "run_reason": "Release confidence",
                "idempotency_key": "run-probe-route",
            },
        )
        gate_refresh = client.post(
            f"/admin/app/test-bench/gates/gate-qa033-passed/refresh?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "target_revision": "workflow-draft-rev-qa033-current",
                "idempotency_key": "gate-refresh-route",
            },
        )
        unsafe_fixture = client.post(
            f"/admin/app/test-bench/suites/suite-qa033-daily-briefing/cases?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "name": "Unsafe case",
                "fixture_summary": "raw prompt copied into browser",
                "expected_contract_summary": "Summary status is required.",
                "assertions": [],
                "revision": "case-rev-qa033-current",
                "idempotency_key": "unsafe-case-route",
            },
        )

    assert suite_save.status_code == 200
    assert suite_save.json()["status"] == "accepted"
    assert stale_suite.status_code == 200
    assert stale_suite.json()["status"] == "stale_conflict"
    assert case_save.status_code == 200
    assert case_save.json()["case"]["case_revision"] == "case-rev-qa033-current"
    assert launch.status_code == 200
    assert launch.json()["run"]["progress"]["status"] == "running"
    assert probe_denied.status_code == 200
    assert probe_denied.json()["status"] == "validation_error"
    assert gate_refresh.status_code == 200
    assert gate_refresh.json()["gate"]["evidence_status"] == "passed"
    assert unsafe_fixture.status_code == 422


def test_react_admin_memberships_platform_and_tenant_flows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            "/admin/app/memberships",
            headers={"X-Local-Principal": "platform-admin"},
        )
        platform_bootstrap = client.get(
            "/admin/app/memberships/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_bootstrap = client.get(
            f"/admin/app/memberships/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        invite_replay = client.post(
            f"/admin/app/memberships/invitations?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "email": "invite.replay@example.test",
                "requested_roles": ["tenant_user"],
                "tenant_id": str(tenant_id),
                "idempotency_key": "invite-ui-qa034-replay",
            },
        )
        platform_role_denied = client.post(
            f"/admin/app/memberships/role-grants?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "confirmed": True,
                "idempotency_key": "role-grant-ui-qa034",
                "principal_identity_id": "principal-qa034-maya",
                "role_code": "platform_admin",
                "scope_type": "platform",
            },
        )
        principal_link_denied = client.post(
            f"/admin/app/memberships/principals/link?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "display_name": "Linked Reviewer",
                "email": "linked@example.test",
                "external_subject": "auth0-safe-subject-7788",
                "idempotency_key": "principal-link-ui-qa034",
            },
        )
        access_history = client.get(
            f"/admin/app/memberships/access-history.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        audit = client.get(
            f"/admin/app/memberships/audit.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/memberships/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert platform_bootstrap.status_code == 200
    assert platform_bootstrap.json()["title"] == "Membership Administration"
    assert "Globex" in json.dumps(platform_bootstrap.json())
    assert tenant_bootstrap.status_code == 200
    tenant_payload = tenant_bootstrap.json()
    serialized_tenant = json.dumps(tenant_payload)
    assert "Globex" not in serialized_tenant
    assert "platform_admin" not in serialized_tenant
    assert tenant_payload["directory"][0]["raw_identifier_detail"] is None
    assert invite_replay.status_code == 200
    assert invite_replay.json()["status"] == "replayed"
    assert invite_replay.json()["invitation"]["masked_email"] == "i***@example.test"
    assert platform_role_denied.status_code == 200
    assert platform_role_denied.json()["status"] == "validation_error"
    assert principal_link_denied.status_code == 200
    assert principal_link_denied.json()["status"] == "validation_error"
    assert access_history.status_code == 200
    assert access_history.json()["records"][0]["decision"] == "allow"
    assert audit.status_code == 200
    assert audit.json()["records"][0]["redaction_class"] == "safe-summary"
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text

    serialized = json.dumps(platform_bootstrap.json()).lower()
    assert "qa034-secret-value" not in serialized
    assert "raw email" not in serialized
    assert "full subject" not in serialized
    assert "authorization header" not in serialized


def test_react_admin_memberships_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-membership-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-membership",
            token_subject="auth0|hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            response = client.get(
                f"/admin/app/memberships/bootstrap.json?tenant_id={tenant_id}"
            )
            role_denied = client.post(
                f"/admin/app/memberships/role-grants?tenant_id={tenant_id}",
                json={
                    "confirmed": True,
                    "idempotency_key": "role-grant-ui-qa034",
                    "principal_identity_id": "principal-qa034-maya",
                    "role_code": "platform_admin",
                    "scope_type": "platform",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|hidden" not in json.dumps(response.json())
    assert role_denied.status_code == 200
    assert role_denied.json()["field_errors"][0]["code"] == "scope_denied"


def test_react_admin_usage_local_principal_platform_tenant_and_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        html = client.get(
            "/admin/app/usage",
            headers={"X-Local-Principal": "platform-admin"},
        )
        platform_dashboard = client.get(
            "/admin/app/usage/bootstrap.json?group_by=tenant",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_dashboard = client.get(
            f"/admin/app/usage/bootstrap.json?tenant_id={tenant_id}&group_by=provider",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        grouped = client.get(
            "/admin/app/usage/bootstrap.json?group_by=gateway_operation",
            headers={"X-Local-Principal": "platform-admin"},
        )
        events = client.get(
            "/admin/app/usage/events.json?group_by=governed_tool",
            headers={"X-Local-Principal": "platform-admin"},
        )
        export = client.post(
            f"/admin/app/usage/exports?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "filters": {"tenant_id": str(tenant_id), "range": "Last 7 days"},
                "requested_group_by": "provider",
                "idempotency_key": "usage-export-ui-qa035",
            },
        )
        denied_export = client.post(
            f"/admin/app/usage/exports?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            json={
                "filters": {"tenant_id": str(other_tenant_id)},
                "requested_group_by": "provider",
                "idempotency_key": "usage-export-ui-qa035-denied",
            },
        )
        export_detail = client.get(
            "/admin/app/usage/exports/35000000-0000-0000-0000-000000000035.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        export_detail_html = client.get(
            "/admin/app/usage/exports/35000000-0000-0000-0000-000000000035",
            headers={"X-Local-Principal": "platform-admin"},
        )
        cross_tenant = client.get(
            f"/admin/app/usage/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert html.status_code == 200
    assert platform_dashboard.status_code == 200
    assert "Globex" in json.dumps(platform_dashboard.json())
    assert tenant_dashboard.status_code == 200
    serialized_tenant = json.dumps(tenant_dashboard.json())
    assert "Usage and Cost Analytics" in serialized_tenant
    assert "Globex" not in serialized_tenant
    assert grouped.status_code == 200
    assert grouped.json()["rollup"]["group_by"] == "gateway_operation"
    assert events.status_code == 200
    assert events.json()["rows"][0]["tool_label"]
    assert export.status_code == 200
    assert export.json()["status"] == "completed"
    assert export.json()["audit_reference"] == "audit-usage-qa035-export-created"
    assert denied_export.status_code == 200
    assert denied_export.json()["status"] == "denied"
    assert export_detail.status_code == 200
    assert export_detail.json()["artifact_reference"] == "usage-export-artifact-qa035"
    assert export_detail_html.status_code == 200
    assert "React Admin" in export_detail_html.text
    assert cross_tenant.status_code == 403
    unsafe = json.dumps(platform_dashboard.json()).lower()
    assert "qa035-secret-value" not in unsafe
    assert "raw prompt" not in unsafe
    assert "authorization header" not in unsafe


def test_react_admin_usage_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-usage-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-usage",
            token_subject="auth0|usage-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            dashboard = client.get(
                f"/admin/app/usage/bootstrap.json?tenant_id={tenant_id}"
            )
            export = client.post(
                f"/admin/app/usage/exports?tenant_id={tenant_id}",
                json={
                    "filters": {"tenant_id": str(tenant_id)},
                    "requested_group_by": "provider",
                    "idempotency_key": "usage-export-auth0-qa035",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Globex" not in json.dumps(payload)
    assert "auth0|usage-hidden" not in json.dumps(payload)
    assert export.status_code == 200
    assert export.json()["audit_reference"] == "audit-usage-qa035-export-created"


def test_react_admin_fails_closed_for_unauthorized_and_cross_tenant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        missing = client.get("/admin/app")
        not_admin = client.get(
            "/admin/app",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert missing.status_code == 401
    assert missing.json()["detail"] == "missing local principal header or cookie"
    assert not_admin.status_code == 403
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_bootstrap_fails_closed_when_navigation_audit_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())

    async def fail_audit(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("audit store unavailable")

    monkeypatch.setattr(
        AuditService,
        "record_admin_navigation_visibility",
        fail_audit,
    )
    app = create_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            f"/admin/app/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "audit_unavailable"


def test_manifest_and_non_jinja_fallbacks_remain_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    monkeypatch.setenv(
        "REACT_ADMIN_MANIFEST_PATH",
        str(tmp_path / "missing-manifest.json"),
    )
    app = create_app()

    with TestClient(app) as client:
        manifest = client.get(
            "/admin/app/manifest.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        fallback = client.get(
            "/admin",
            headers={"X-Local-Principal": "platform-admin"},
        )
        disabled_route = client.get(
            "/admin/app/workflows",
            headers={"X-Local-Principal": "platform-admin"},
        )

    assert manifest.status_code == 200
    assert manifest.json()["available"] is False
    assert "src/multi_agent_platform" not in manifest.text
    assert fallback.status_code == 200
    assert fallback.headers["X-React-Admin-Host"] == "non-jinja"
    assert "React admin built assets are unavailable" in fallback.text
    assert "Admin Console" not in fallback.text
    assert disabled_route.status_code == 200
    assert "React Admin" in disabled_route.text


def test_react_channels_platform_and_tenant_dashboards_are_scoped(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        platform = client.get(
            "/admin/app/channels/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant = client.get(
            f"/admin/app/channels/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        html = client.get(
            f"/admin/app/channels?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        runs_html = client.get(
            f"/admin/app/channels/runs?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        cross_tenant = client.get(
            f"/admin/app/channels/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert platform.status_code == 200
    assert "Globex" in json.dumps(platform.json())
    assert "qa036-secret-value" not in json.dumps(platform.json())
    assert tenant.status_code == 200
    tenant_payload = tenant.json()
    assert tenant_payload["scope"]["tenant_id"] == str(tenant_id)
    assert "Globex" not in json.dumps(tenant_payload)
    assert "pair-code" not in json.dumps(tenant_payload)
    assert html.status_code == 200
    assert "React Admin" in html.text
    assert runs_html.status_code == 200
    assert "React Admin" in runs_html.text
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_react_channels_mutations_link_token_and_run_status_are_safe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()
    query = f"?tenant_id={tenant_id}"
    headers = {"X-Local-Principal": "tenant-admin-acme"}

    with TestClient(app) as client:
        config = client.post(
            f"/admin/app/channels/telegram/config{query}",
            headers=headers,
            json={
                "enabled": True,
                "bot_token_reference_label": "Telegram provider ref ready",
                "webhook_signing_reference_label": "Webhook signing ref ready",
                "revision": "telegram-config-rev-qa036",
                "idempotency_key": "qa036-config",
            },
        )
        webhook = client.post(
            f"/admin/app/channels/telegram/webhook/validate{query}",
            headers=headers,
            json={
                "tenant_id": str(tenant_id),
                "revision": "telegram-config-rev-qa036",
                "idempotency_key": "qa036-webhook-replay",
            },
        )
        alias = client.post(
            f"/admin/app/channels/telegram/aliases{query}",
            headers=headers,
            json={
                "alias_text": "Morning briefing",
                "target_summary": "Daily briefing workflow",
                "idempotency_key": "qa036-alias",
            },
        )
        token = client.post(
            f"/admin/app/channels/telegram/link-tokens{query}",
            headers=headers,
            json={
                "principal_label": "Acme briefing user",
                "expires_in_minutes": 10,
                "idempotency_key": "qa036-link-token",
            },
        )
        deliveries = client.get(
            f"/admin/app/channels/telegram/deliveries.json{query}",
            headers=headers,
        )
        run = client.get(
            f"/admin/app/channels/runs/qa036-run-morning-briefing/status.json{query}",
            headers=headers,
        )

    assert config.status_code == 200
    assert config.json()["status"] == "accepted"
    assert webhook.status_code == 200
    assert webhook.json()["status"] == "replayed"
    assert alias.status_code == 200
    assert alias.json()["audit_reference"] == "audit-qa036-alias-save"
    assert token.status_code == 200
    assert token.json()["token_value"] == "pair-code-10-qa036"
    assert deliveries.status_code == 200
    assert deliveries.json()["attempts"][0]["bot_api_boundary_status"] == "mocked"
    assert run.status_code == 200
    run_text = json.dumps(run.json())
    assert "raw prompt" not in run_text.lower()
    assert "run result" not in run_text.lower()


def test_react_channels_preference_routes_support_user_and_auth0_principal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        preferences = client.get(
            f"/admin/app/channels/briefing/preferences.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        save = client.post(
            f"/admin/app/channels/briefing/preferences?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
            json={
                "timezone": "America/New_York",
                "location_summary": "Metro area summary",
                "news_topics_summary": "4 topic categories",
                "vip_sender_summary": "3 masked sender hints",
                "workday_hours": "08:30-17:30",
                "commute_mode": "transit",
                "default_account_summary": "2 masked account refs",
                "output_style": "executive",
                "scheduled_time_summary": "Profile preference 07:45",
                "idempotency_key": "qa036-pref-save",
            },
        )
        export = client.post(
            f"/admin/app/channels/briefing/preferences/export?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
            json={"format": "json", "idempotency_key": "qa036-pref-export"},
        )

    assert preferences.status_code == 200
    assert preferences.json()["current_user_profile"]["timezone"] == "America/New_York"
    assert "raw preference" not in json.dumps(preferences.json()).lower()
    assert save.status_code == 200
    assert save.json()["status"] == "accepted"
    assert export.status_code == 200
    assert export.json()["artifact_reference"] == "preference-export-artifact-qa036"

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-channel-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-channel",
            token_subject="auth0|channel-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            auth0_dashboard = client.get(
                f"/admin/app/channels/bootstrap.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert auth0_dashboard.status_code == 200
    assert auth0_dashboard.json()["scope"]["tenant_id"] == str(tenant_id)
    assert "auth0|channel-hidden" not in json.dumps(auth0_dashboard.json())


def test_react_migration_hardening_platform_tenant_and_user_scopes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    app = create_app()

    with TestClient(app) as client:
        root_html = client.get(
            f"/admin/app?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        platform_dashboard = client.get(
            "/admin/app/migration/bootstrap.json",
            headers={"X-Local-Principal": "platform-admin"},
        )
        tenant_dashboard = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        tenant_user_dashboard = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        route_list = client.get(
            f"/admin/app/migration/routes.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        rollback = client.get(
            f"/admin/app/migration/rollback.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )
        tenant_user_shell = client.get(
            f"/admin/app/migration/shell.json?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-user-acme"},
        )
        missing = client.get("/admin/app/migration/bootstrap.json")
        cross_tenant = client.get(
            f"/admin/app/migration/bootstrap.json?tenant_id={other_tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-acme"},
        )

    assert root_html.status_code == 200
    assert platform_dashboard.status_code == 200
    platform_payload = platform_dashboard.json()
    assert platform_payload["summary"]["total_destinations"] >= 8
    assert "qa037-secret-value" not in json.dumps(platform_payload)
    assert platform_payload["title"] == "React-only browser UI"
    assert not any(
        entry["decision"] == "retained_fallback"
        for group in platform_payload["route_groups"]
        for entry in group["entries"]
    )
    assert platform_payload["jinja_inventory"]["summary"]["template_count"] == 0
    assert tenant_dashboard.status_code == 200
    tenant_payload = tenant_dashboard.json()
    assert all(
        entry["scope_requirement"] in {"tenant_admin", "tenant_user", "mixed"}
        for group in tenant_payload["route_groups"]
        for entry in group["entries"]
    )
    assert tenant_user_dashboard.status_code == 200
    assert any(
        state["reason"] == "user_scope_limited"
        for state in tenant_user_dashboard.json()["states"]
    )
    assert route_list.status_code == 200
    assert isinstance(route_list.json(), list)
    assert rollback.status_code == 200
    assert rollback.json()["status"] == "ready"
    assert tenant_user_shell.status_code == 200
    assert missing.status_code == 401
    assert cross_tenant.status_code == 403
    assert "Globex" not in cross_tenant.text


def test_react_migration_hardening_auth0_principal_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    async def auth0_principal() -> PrincipalContext:
        return PrincipalContext(
            principal_id="auth0-migration-admin",
            auth_provider=AuthProvider.AUTH0,
            auth_mode=AuthMode.AUTH0,
            tenant_id=tenant_id,
            org_id="org-acme",
            role_codes=("tenant_user", "tenant_admin"),
            permission_codes=("tenant:read", "tenant:admin"),
            trace_id="trace-auth0-migration",
            token_subject="auth0|migration-hidden",
        )

    app.dependency_overrides[require_authorized_principal] = auth0_principal
    try:
        with TestClient(app) as client:
            dashboard = client.get(
                f"/admin/app/migration/bootstrap.json?tenant_id={tenant_id}"
            )
            routes = client.get(
                f"/admin/app/migration/routes.json?tenant_id={tenant_id}"
            )
    finally:
        app.dependency_overrides.clear()

    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["scope"]["tenant_id"] == str(tenant_id)
    assert routes.status_code == 200
    assert "auth0|migration-hidden" not in json.dumps(payload)
