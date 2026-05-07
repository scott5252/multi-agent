from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_operations_api import (
    PLATFORM_HEADERS,
    _configure_env,
)


def test_admin_run_inspection_ui_redirects_to_react(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()
    run_id = "00000000-0000-0000-0000-000000000123"

    with TestClient(app) as client:
        search = client.get(
            "/admin/runs?status=failed",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        detail = client.get(
            f"/admin/runs/{run_id}?tenant_id=11111111-1111-1111-1111-111111111111",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        replay = client.get(
            f"/admin/runs/{run_id}/replay?from_sequence=2",
            headers={**PLATFORM_HEADERS, "accept": "text/html"},
            follow_redirects=False,
        )

    assert search.status_code == 303
    assert (
        search.headers["location"] == "/admin/app/operations?status=failed&panel=runs"
    )
    assert detail.status_code == 303
    assert detail.headers["location"] == (
        "/admin/app/operations?"
        "tenant_id=11111111-1111-1111-1111-111111111111"
        f"&run_id={run_id}"
    )
    assert replay.status_code == 303
    assert replay.headers["location"] == (
        f"/admin/app/operations?from_sequence=2&run_id={run_id}&panel=replay"
    )
