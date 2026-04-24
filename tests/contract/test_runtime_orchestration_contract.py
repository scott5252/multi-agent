from __future__ import annotations

from pathlib import Path

import yaml

from multi_agent_platform.api.main import create_app


def test_runtime_openapi_paths_match_contract() -> None:
    contract = yaml.safe_load(
        Path(
            "specs/004-durable-orchestration-runtime/contracts/"
            "runtime-orchestration.openapi.yaml"
        ).read_text()
    )
    app_paths = create_app().openapi()["paths"]

    for path in contract["paths"]:
        assert path in app_paths
