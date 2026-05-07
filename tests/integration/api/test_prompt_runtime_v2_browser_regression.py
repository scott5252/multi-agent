from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.api.routers.admin_run_inspection import (
    build_combined_gateway_provenance_view,
)
from tests.integration.test_admin_react_routes import _configure_env


def test_admin_run_detail_contract_has_gateway_metadata_unavailable_state() -> None:
    projection = build_combined_gateway_provenance_view(None)

    assert projection["metadata_status"] == "pre_v2_metadata_unavailable"
    assert projection["gateway_operation_id"] is None


def test_prompt_runtime_legacy_script_is_retired_and_routes_redirect(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = uuid4()
    _configure_env(monkeypatch, tmp_path, tenant_id, uuid4())
    app = create_app()

    with TestClient(app) as client:
        response = client.get(
            f"/admin/prompt-runtime/prompts?tenant_id={tenant_id}&q=daily",
            headers={"X-Local-Principal": "tenant-admin-acme"},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == f"/admin/app/governance/prompts?tenant_id={tenant_id}&q=daily"
    )
    assert not Path(
        "src/multi_agent_platform/web_admin/static/prompt_runtime.js"
    ).exists()
