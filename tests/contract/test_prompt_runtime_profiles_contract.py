from __future__ import annotations

import yaml


def test_prompt_runtime_openapi_contract_lists_prompt_and_profile_surfaces() -> None:
    with open(
        "specs/012-prompt-runtime-profiles/contracts/prompt-runtime-profiles.openapi.yaml",
        encoding="utf-8",
    ) as contract_file:
        contract = yaml.safe_load(contract_file)

    paths = contract["paths"]
    assert "/admin/prompt-runtime/api/prompts" in paths
    assert "/admin/prompt-runtime/api/profiles" in paths
