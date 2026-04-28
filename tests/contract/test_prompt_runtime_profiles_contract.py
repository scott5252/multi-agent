from __future__ import annotations

import yaml

from multi_agent_platform.api.main import create_app


def test_prompt_runtime_openapi_contract_lists_prompt_and_profile_surfaces() -> None:
    with open(
        "specs/012-prompt-runtime-profiles/contracts/prompt-runtime-profiles.openapi.yaml",
        encoding="utf-8",
    ) as contract_file:
        contract = yaml.safe_load(contract_file)

    paths = contract["paths"]
    assert "/admin/prompt-runtime/api/prompts" in paths
    assert "/admin/prompt-runtime/api/profiles" in paths


def test_prompt_runtime_openapi_contract_methods_are_implemented() -> None:
    with open(
        "specs/012-prompt-runtime-profiles/contracts/prompt-runtime-profiles.openapi.yaml",
        encoding="utf-8",
    ) as contract_file:
        contract = yaml.safe_load(contract_file)

    app_paths = create_app().openapi()["paths"]
    missing = []
    for path, methods in contract["paths"].items():
        for method in methods:
            if method.startswith("x-"):
                continue
            if path not in app_paths or method not in app_paths[path]:
                missing.append(f"{method.upper()} {path}")

    assert missing == []
