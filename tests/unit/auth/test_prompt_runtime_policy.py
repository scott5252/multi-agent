from __future__ import annotations

from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_prompt_runtime_surfaces_are_registered_with_scoped_actions() -> None:
    expected = {
        "GET:/admin/prompt-runtime/prompts": "render_prompt_library_ui",
        "POST:/admin/prompt-runtime/api/prompts": "create_prompt_lineage",
        (
            "POST:/admin/prompt-runtime/api/prompts/{prompt_lineage_id}/publish"
        ): "publish_prompt_version",
        "GET:/admin/prompt-runtime/profiles": "render_agent_profiles_ui",
        "POST:/admin/prompt-runtime/api/profiles": "create_agent_profile",
        (
            "POST:/admin/prompt-runtime/api/profiles/"
            "{agent_runtime_profile_id}/activate"
        ): "activate_agent_profile",
    }

    for surface, action in expected.items():
        assert SURFACE_POLICIES[surface].requested_action == action
