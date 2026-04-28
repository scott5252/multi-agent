from __future__ import annotations


def test_prompt_browser_flow_assets_include_expected_states() -> None:
    edit = open(
        "src/multi_agent_platform/web_admin/templates/prompts/edit.html",
        encoding="utf-8",
    ).read()
    history = open(
        "src/multi_agent_platform/web_admin/templates/prompts/history.html",
        encoding="utf-8",
    ).read()
    script = open(
        "src/multi_agent_platform/web_admin/static/prompt_runtime.js",
        encoding="utf-8",
    ).read()

    assert "Validation" in edit
    assert "Preview" in edit
    assert "publications" in history
    assert "beforeunload" in script
