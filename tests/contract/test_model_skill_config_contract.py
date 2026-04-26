from __future__ import annotations

from pathlib import Path


def test_model_skill_openapi_contract_lists_required_surfaces() -> None:
    contract = Path(
        "specs/007-model-skill-routing/contracts/model-skill-routing.openapi.yaml"
    ).read_text()

    for path in (
        "/admin/config/model-routing",
        "/admin/config/prompt-references",
        "/admin/config/skill-bindings",
        "/admin/config/tool-policies",
        "/admin/config/outbound-domain-policies",
        "/admin/config/secret-references",
        "/admin/config/credential-requirements",
        "/admin/config/preview/model",
        "/admin/config/preview/tool",
        "/admin/config/history",
        "/admin/config/runs/{workflow_run_id}/provenance",
    ):
        assert path in contract
