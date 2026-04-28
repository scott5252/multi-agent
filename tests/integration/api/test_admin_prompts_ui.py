from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.ui.prompts import build_prompt_ui_model


def test_prompt_ui_model_disables_publish_and_preserves_fields() -> None:
    model = build_prompt_ui_model(
        title="Edit Prompt",
        scope_type="tenant",
        tenant_id=uuid4(),
        validation_status="failed",
        submitted_fields={"display_name": "Draft"},
    )

    assert not model.can_publish
    assert model.can_preview
    assert model.submitted_fields["display_name"] == "Draft"


def test_prompt_templates_cover_list_edit_detail_history_and_preview() -> None:
    paths = [
        "src/multi_agent_platform/web_admin/templates/prompts/index.html",
        "src/multi_agent_platform/web_admin/templates/prompts/edit.html",
        "src/multi_agent_platform/web_admin/templates/prompts/detail.html",
        "src/multi_agent_platform/web_admin/templates/prompts/history.html",
        "src/multi_agent_platform/web_admin/templates/prompts/preview.html",
    ]

    for path in paths:
        text = open(path, encoding="utf-8").read()
        assert "admin_shell/base.html" in text
