from __future__ import annotations

import subprocess

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app


def test_openapi_contains_jinja_inventory_contract() -> None:
    schema = TestClient(create_app()).get("/openapi.json").json()

    assert "/admin/app/migration/jinja-inventory.json" in schema["paths"]
    components = schema["components"]["schemas"]
    assert "JinjaInventoryDashboard" in components
    assert "JinjaInventorySummary" in components
    assert "JinjaInventoryGroup" in components
    assert "JinjaInventoryItem" in components
    assert "JinjaInventoryEvidence" in components


def test_generated_types_include_jinja_inventory_contract() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/frontend/generate_admin_react_types.py",
            "--check",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
