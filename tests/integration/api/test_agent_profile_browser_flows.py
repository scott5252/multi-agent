from __future__ import annotations


def test_profile_browser_flow_assets_include_expected_states() -> None:
    edit = open(
        "src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html",
        encoding="utf-8",
    ).read()
    resolve = open(
        "src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html",
        encoding="utf-8",
    ).read()
    history = open(
        "src/multi_agent_platform/web_admin/templates/agent_profiles/history.html",
        encoding="utf-8",
    ).read()

    assert "Activate" in edit
    assert "Tenant profiles win" in resolve
    assert "activations" in history
