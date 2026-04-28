from __future__ import annotations

from multi_agent_platform.api.ui.agent_profiles import build_agent_profile_ui_model
from multi_agent_platform.api.ui.prompts import build_prompt_ui_model


def test_prompt_and_profile_ui_models_disable_unsafe_actions() -> None:
    prompt = build_prompt_ui_model(
        title="Prompt",
        scope_type="tenant",
        required_fixture_missing=True,
        validation_status="passed",
    )
    profile = build_agent_profile_ui_model(
        title="Profile",
        scope_type="tenant",
        validation_status="passed",
    )

    assert prompt.can_publish
    assert not prompt.can_preview
    assert profile.can_activate
