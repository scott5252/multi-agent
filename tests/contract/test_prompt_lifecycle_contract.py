from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_prompt_lifecycle_openapi_declares_retire_and_grant_endpoints() -> None:
    paths = create_app().openapi()["paths"]

    assert (
        "/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/retire" in paths
    )
    assert (
        "/admin/prompt-runtime/api/prompts/versions/{prompt_version_id}/grants" in paths
    )
