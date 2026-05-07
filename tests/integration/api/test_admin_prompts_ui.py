from __future__ import annotations

from pathlib import Path
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


def test_prompt_templates_removed_after_react_redirect_parity() -> None:
    paths = [
        "src/multi_agent_platform/web_admin/templates/prompts/index.html",
        "src/multi_agent_platform/web_admin/templates/prompts/edit.html",
        "src/multi_agent_platform/web_admin/templates/prompts/detail.html",
        "src/multi_agent_platform/web_admin/templates/prompts/history.html",
        "src/multi_agent_platform/web_admin/templates/prompts/preview.html",
    ]

    for path in paths:
        assert not Path(path).exists()
