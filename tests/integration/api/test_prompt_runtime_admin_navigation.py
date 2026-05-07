from __future__ import annotations

from multi_agent_platform.api.ui.admin_console import navigation_registry


def test_prompt_runtime_navigation_entries_are_authorization_aware() -> None:
    items = {item.item_id: item for item in navigation_registry()}

    assert items["prompt_library"].href == "/admin/app/governance/prompts"
    assert items["prompt_library"].route_surface_key == "GET:/admin/app/governance"
    assert items["agent_profiles"].href == "/admin/app/governance/profiles"
    assert items["agent_profiles"].route_surface_key == "GET:/admin/app/governance"
    assert items["prompt_library"].preserve_tenant_scope
    assert items["agent_profiles"].required_scope == "either"
