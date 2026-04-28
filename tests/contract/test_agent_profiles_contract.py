from __future__ import annotations

from multi_agent_platform.api.main import create_app


def test_agent_profiles_openapi_declares_mvp_endpoints() -> None:
    paths = create_app().openapi()["paths"]

    assert "/admin/prompt-runtime/api/profiles" in paths
    assert (
        "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/draft" in paths
    )
    assert (
        "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/validate"
        in paths
    )
    assert (
        "/admin/prompt-runtime/api/profiles/{agent_runtime_profile_id}/activate"
        in paths
    )
