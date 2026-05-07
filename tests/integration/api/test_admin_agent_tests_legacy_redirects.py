from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app

from .test_admin_agent_tests_api import (
    ACME_HEADERS,
    ACME_TENANT_ID,
    GLOBEX_HEADERS,
    PLATFORM_HEADERS,
    _configure_env,
)


def test_legacy_agent_test_get_routes_redirect_to_react(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/agent-tests/suites",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA043 Legacy Redirect Guard",
                "target_type": "workflow_draft",
                "target_id": "qa043-draft",
                "target_version": "draft-rev-1",
                "required_for_publish": True,
            },
        )
        suite_id = created.json()["suite_id"]
        case = client.post(
            f"/admin/agent-tests/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            json={
                "name": "QA043 passing case",
                "fixture": {"request": "summarized only"},
                "expected_contract_shape": {"status": {}},
                "assertions": [
                    {
                        "kind": "deterministic",
                        "path": "status",
                        "comparator": "equals",
                        "expected_value": "passed",
                    }
                ],
            },
        )
        run = client.post(
            f"/admin/agent-tests/suites/{suite_id}/runs",
            headers=ACME_HEADERS,
            json={
                "safe_mode": "mock_model",
                "target_version": "draft-rev-1",
                "idempotency_key": "qa043-redirect-run",
            },
        )
        index = client.get(
            f"/admin/agent-tests/ui?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        new_suite = client.get(
            f"/admin/agent-tests/ui/suites/new?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        suite = client.get(
            f"/admin/agent-tests/ui/suites/{suite_id}?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )
        run_detail = client.get(
            f"/admin/agent-tests/ui/runs/{run.json()['run_id']}?tenant_id={ACME_TENANT_ID}",
            headers=ACME_HEADERS,
            follow_redirects=False,
        )

    assert case.status_code == 201
    assert index.status_code == 303
    assert index.headers["location"] == (
        f"/admin/app/test-bench?tenant_id={ACME_TENANT_ID}"
    )
    assert new_suite.status_code == 303
    assert new_suite.headers["location"] == (
        f"/admin/app/test-bench?tenant_id={ACME_TENANT_ID}&mode=create-suite"
    )
    assert suite.status_code == 303
    suite_query = parse_qs(urlparse(suite.headers["location"]).query)
    assert suite_query["tenant_id"] == [ACME_TENANT_ID]
    assert suite_query["suite_id"] == [suite_id]
    assert run_detail.status_code == 303
    run_query = parse_qs(urlparse(run_detail.headers["location"]).query)
    assert run_query["tenant_id"] == [ACME_TENANT_ID]
    assert run_query["run_id"] == [run.json()["run_id"]]
    assert "QA043 Legacy Redirect Guard" not in run_detail.text


def test_legacy_agent_test_form_posts_redirect_to_react(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/agent-tests/ui/suites",
            headers=ACME_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA043 Browser Guard",
                "target_type": "workflow_draft",
                "target_id": "qa043-draft",
                "target_version": "draft-rev-1",
                "default_safe_mode": "mock_model",
                "pass_threshold": "1.0",
                "required_for_publish": "1",
            },
            follow_redirects=False,
        )
        suite_query = parse_qs(urlparse(created.headers["location"]).query)
        suite_id = suite_query["suite_id"][0]
        case = client.post(
            f"/admin/agent-tests/ui/suites/{suite_id}/cases",
            headers=ACME_HEADERS,
            data={
                "name": "QA043 case",
                "fixture_json": '{"request":"summarized only"}',
                "expected_contract_shape": '{"status":{}}',
                "assertions_json": (
                    '[{"kind":"deterministic","path":"status",'
                    '"comparator":"equals","expected_value":"passed"}]'
                ),
            },
            follow_redirects=False,
        )
        run = client.post(
            f"/admin/agent-tests/ui/suites/{suite_id}/runs",
            headers=ACME_HEADERS,
            data={
                "safe_mode": "mock_model",
                "target_version": "draft-rev-1",
                "idempotency_key": "qa043-ui-run",
            },
            follow_redirects=False,
        )

    assert created.status_code == 303
    assert suite_query["tenant_id"] == [ACME_TENANT_ID]
    assert suite_query["mutation"] == ["created"]
    assert case.status_code == 303
    assert parse_qs(urlparse(case.headers["location"]).query)["mutation"] == [
        "case-created"
    ]
    assert run.status_code == 303
    run_query = parse_qs(urlparse(run.headers["location"]).query)
    assert run_query["mutation"] == ["run-launched"]
    assert "run_id" in run_query


def test_legacy_agent_test_redirects_fail_closed_for_unsafe_scope(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        created = client.post(
            "/admin/agent-tests/suites",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "name": "QA043 Tenant Private Guard",
                "target_type": "workflow_draft",
                "target_id": "qa043-private-draft",
                "target_version": "draft-rev-1",
                "required_for_publish": True,
            },
        )
        suite_id = created.json()["suite_id"]
        cross_tenant = client.get(
            f"/admin/agent-tests/ui/suites/{suite_id}",
            headers=GLOBEX_HEADERS,
            follow_redirects=False,
        )
        invalid_tenant = client.get(
            "/admin/agent-tests/ui?tenant_id=not-a-uuid",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )

    assert cross_tenant.status_code == 403
    assert "QA043 Tenant Private Guard" not in cross_tenant.text
    assert invalid_tenant.status_code == 400
