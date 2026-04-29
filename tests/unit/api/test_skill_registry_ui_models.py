from __future__ import annotations

from multi_agent_platform.admin.skill_registry.service import SkillRegistryService
from multi_agent_platform.api.ui.skill_registry import build_package_list_page


def test_skill_registry_ui_model_omits_raw_content() -> None:
    service = SkillRegistryService()
    package = service.create_package(
        slug="calendar-assistant",
        display_name="Calendar Assistant",
        description="Safe calendar skill.",
        owner_principal_id="platform-admin",
        actor_principal_id="platform-admin",
    )

    page = build_package_list_page([package], platform_admin=True)

    assert page.packages[0]["slug"] == "calendar-assistant"
    assert "Raw package payloads" in page.redaction_notice
