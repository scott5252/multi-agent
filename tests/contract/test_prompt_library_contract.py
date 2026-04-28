from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_prompt_library_openapi_declares_mvp_endpoints() -> None:
    paths = create_app().openapi()["paths"]

    assert "/admin/prompt-runtime/api/prompts" in paths
    assert "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/draft" in paths
    assert "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/validate" in paths
    assert "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/preview" in paths
    assert "/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish" in paths
