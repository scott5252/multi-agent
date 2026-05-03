from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}
GLOBEX_HEADERS = {"X-Local-Principal": "tenant-admin-globex"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "agent-tests.db"
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
                "VALUES ('0015_agent_workflow_test_bench')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(
                    tenant_id=UUID(ACME_TENANT_ID),
                    slug="acme",
                    display_name="Acme",
                ),
                Tenant(
                    tenant_id=UUID(GLOBEX_TENANT_ID),
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "platform:admin",
                        "agent-tests:manage",
                        "agent-tests:run",
                        "agent-tests:read",
                        "agent-tests:gate",
                    ],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Acme Tenant Admin",
                    "tenant_id": ACME_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "agent-tests:manage",
                        "agent-tests:run",
                        "agent-tests:read",
                        "agent-tests:gate",
                    ],
                },
                "tenant-admin-globex": {
                    "catalog_key": "tenant-admin-globex",
                    "display_name": "Globex Tenant Admin",
                    "tenant_id": GLOBEX_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "agent-tests:manage",
                        "agent-tests:run",
                        "agent-tests:read",
                        "agent-tests:gate",
                    ],
                },
            }
        ),
    )


def test_agent_test_bench_api_crud_run_gate_and_tenant_denial(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/agent-tests/suites",
            headers=PLATFORM_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA015 Draft Workflow Guard",
                "target_type": "workflow_draft",
                "target_id": "qa015-draft-triage",
                "target_version": "draft-rev-1",
                "required_for_publish": True,
            },
        )
        suite_id = created.json()["suite_id"]
        case = client.post(
            f"/admin/agent-tests/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            json={
                "name": "Passing intake case",
                "fixture": {"request": "summarize intake", "api_key": "secret"},
                "expected_contract_shape": {"status": {}, "contract": {}},
                "assertions": [
                    {
                        "kind": "deterministic",
                        "path": "contract.summary",
                        "comparator": "contains",
                        "expected_value": "intake",
                    }
                ],
            },
        )
        run = client.post(
            f"/admin/agent-tests/suites/{suite_id}/runs",
            headers=ACME_HEADERS,
            json={
                "safe_mode": "real_model_side_effects_disabled",
                "target_version": "draft-rev-1",
                "idempotency_key": "api-run-1",
            },
        )
        gate = client.post(
            "/admin/agent-tests/publish-gates/evaluate",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "target_type": "workflow_draft",
                "target_id": "qa015-draft-triage",
                "target_version": "draft-rev-1",
            },
        )
        denied = client.get(
            f"/admin/agent-tests/suites/{suite_id}",
            headers=GLOBEX_HEADERS,
        )

    assert created.status_code == 201, created.text
    assert created.json()["required_for_publish"] is True
    assert case.status_code == 201, case.text
    assert case.json()["fixture_summary"]["preview"]["api_key"] == "[redacted]"
    assert run.status_code == 202, run.text
    assert run.json()["status"] == "passed"
    assert run.json()["blocked_side_effect_count"] == 1
    assert run.json()["steps"][0]["model_provider"] == "mocked-gateway"
    assert gate.status_code == 200
    assert gate.json()["status"] == "ready"
    assert gate.json()["passing_count"] == 1
    assert denied.status_code == 403


def test_agent_test_bench_ui_renders_and_runs_suite(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        index = client.get(
            f"/admin/agent-tests/ui?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        created = client.post(
            "/admin/agent-tests/ui/suites",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA015 Browser Guard",
                "target_type": "workflow_draft",
                "target_id": "qa015-draft-triage",
                "target_version": "draft-rev-1",
                "default_safe_mode": "mock_model",
                "pass_threshold": "1.0",
                "required_for_publish": "1",
            },
            follow_redirects=False,
        )
        suite_path = created.headers["location"]
        suite = client.get(suite_path, headers=ACME_HEADERS)
        case = client.post(
            f"{suite_path}/cases",
            headers=ACME_HEADERS,
            data={
                "name": "Passing browser case",
                "fixture_json": '{"request":"summarize intake"}',
                "expected_contract_shape": '{"status":{},"contract":{}}',
                "assertions_json": (
                    '[{"kind":"deterministic","path":"status",'
                    '"comparator":"equals","expected_value":"passed"}]'
                ),
            },
            follow_redirects=False,
        )
        run = client.post(
            f"{suite_path}/runs",
            headers=ACME_HEADERS,
            data={"safe_mode": "mock_tools", "target_version": "draft-rev-1"},
            follow_redirects=False,
        )
        run_detail = client.get(run.headers["location"], headers=ACME_HEADERS)

    assert index.status_code == 200
    assert "No agent test suites are visible" in index.text
    assert created.status_code == 303
    assert suite.status_code == 200
    assert "QA015 Browser Guard" in suite.text
    assert case.status_code == 303
    assert run.status_code == 303
    assert run_detail.status_code == 200
    assert "mock_tools" in run_detail.text
    assert "external_dependency.write blocked" in run_detail.text


def test_agent_test_bench_api_and_ui_cover_error_and_update_paths(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        platform_index = client.get("/admin/agent-tests/ui", headers=PLATFORM_HEADERS)
        new_form = client.get(
            f"/admin/agent-tests/ui/suites/new?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        missing_tenant = client.post(
            "/admin/agent-tests/ui/suites",
            headers=PLATFORM_HEADERS,
            data={"name": "Missing tenant"},
        )
        created = client.post(
            "/admin/agent-tests/suites",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA015 API Update Guard",
                "target_type": "workflow_draft",
                "target_id": "qa015-update-target",
                "target_version": "draft-rev-1",
                "required_for_publish": True,
            },
        )
        suite_id = created.json()["suite_id"]
        listed = client.get(
            f"/admin/agent-tests/suites?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
        )
        fetched = client.get(
            f"/admin/agent-tests/suites/{suite_id}",
            headers=ACME_HEADERS,
        )
        updated = client.patch(
            f"/admin/agent-tests/suites/{suite_id}",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA015 API Updated Guard",
                "target_type": "workflow_draft",
                "target_id": "qa015-update-target",
                "target_version": "draft-rev-2",
                "default_safe_mode": "mock_tools",
                "model_mode": "mock",
                "tool_mode": "mock",
                "pass_threshold": 0.9,
                "required_for_publish": True,
                "revision": fetched.json()["revision"],
            },
        )
        no_cases_run = client.post(
            f"/admin/agent-tests/suites/{suite_id}/runs",
            headers=ACME_HEADERS,
            json={"safe_mode": "mock_model", "target_version": "draft-rev-2"},
        )
        invalid_fixture = client.post(
            f"/admin/agent-tests/ui/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            data={
                "name": "Invalid fixture",
                "fixture_json": "[]",
                "expected_contract_shape": "{}",
                "assertions_json": "[]",
            },
        )
        invalid_assertions = client.post(
            f"/admin/agent-tests/ui/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            data={
                "name": "Invalid assertions",
                "fixture_json": "{}",
                "expected_contract_shape": "{}",
                "assertions_json": "{}",
            },
        )
        case = client.post(
            f"/admin/agent-tests/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            json={
                "name": "Evaluator case",
                "fixture": {"request": "summarize intake"},
                "expected_contract_shape": {"status": {}, "contract": {}},
                "assertions": [{"kind": "evaluator", "threshold": 0.8}],
            },
        )
        blocked_probe = client.post(
            f"/admin/agent-tests/suites/{suite_id}/runs",
            headers=ACME_HEADERS,
            json={
                "safe_mode": "approved_real_probe",
                "target_version": "draft-rev-2",
                "idempotency_key": "blocked-probe",
            },
        )
        runs = client.get(
            f"/admin/agent-tests/runs?suite_id={suite_id}",
            headers=ACME_HEADERS,
        )
        run_detail = client.get(
            f"/admin/agent-tests/runs/{blocked_probe.json()['run_id']}",
            headers=ACME_HEADERS,
        )
        ui_missing_run = client.get(
            "/admin/agent-tests/ui/runs/00000000-0000-0000-0000-000000000001",
            headers=ACME_HEADERS,
        )
        missing_run = client.get(
            "/admin/agent-tests/runs/00000000-0000-0000-0000-000000000001",
            headers=ACME_HEADERS,
        )
        missing_gate = client.post(
            "/admin/agent-tests/publish-gates/evaluate",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "target_type": "workflow_draft",
                "target_id": "qa015-update-target",
                "target_version": "draft-rev-2",
            },
        )

    assert platform_index.status_code == 200
    assert "Create Suite" in platform_index.text
    assert new_form.status_code == 200
    assert "QA015 Draft Workflow Guard" in new_form.text
    assert missing_tenant.status_code == 400
    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["suite_id"] == suite_id
    assert fetched.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["name"] == "QA015 API Updated Guard"
    assert updated.json()["default_safe_mode"] == "mock_tools"
    assert no_cases_run.status_code == 400
    assert invalid_fixture.status_code == 400
    assert invalid_assertions.status_code == 400
    assert case.status_code == 201
    assert blocked_probe.status_code == 202
    assert blocked_probe.json()["status"] == "blocked"
    assert "approved real dependency probe" in blocked_probe.json()["failure_summary"]
    assert runs.status_code == 200
    assert len(runs.json()) == 1
    assert run_detail.status_code == 200
    assert run_detail.json()["pass_status"] == "blocked"
    assert ui_missing_run.status_code == 404
    assert missing_run.status_code == 404
    assert missing_gate.status_code == 200
    assert missing_gate.json()["status"] == "blocked"
    assert missing_gate.json()["safe_reasons"] == ["Required test evidence is missing."]
