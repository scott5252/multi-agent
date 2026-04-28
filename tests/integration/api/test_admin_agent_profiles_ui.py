from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.ui.agent_profiles import build_agent_profile_ui_model


def test_agent_profile_ui_sections_surface_blocking_counts() -> None:
    model = build_agent_profile_ui_model(
        title="Edit Profile",
        scope_type="tenant",
        tenant_id=uuid4(),
        validation_status="failed",
        findings=[
            {
                "severity": "blocking",
                "section": "prompt_references",
                "message": "Missing prompt",
            }
        ],
    )

    prompt_section = next(
        section for section in model.sections if section.key == "prompt_references"
    )
    assert prompt_section.blocking_count == 1
    assert not model.can_activate
