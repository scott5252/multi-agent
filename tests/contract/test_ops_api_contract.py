from __future__ import annotations

from pathlib import Path

import yaml

from multi_agent_platform.api.main import create_app


def test_operational_openapi_paths_match_contract() -> None:
    contract = yaml.safe_load(
        Path("specs/001-platform-foundation/contracts/ops-api.openapi.yaml").read_text()
    )
    app = create_app()
    app_paths = app.openapi()["paths"]
    for path in contract["paths"]:
        assert path in app_paths
