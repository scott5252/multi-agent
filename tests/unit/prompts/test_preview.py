from __future__ import annotations

import pytest

from multi_agent_platform.prompts.preview import PromptPreviewError, render_safe_preview


def test_render_safe_preview_uses_fixture_values_and_returns_redaction_metadata() -> (
    None
):
    preview = render_safe_preview(
        "Hello {{name}}",
        {"name": "Ada"},
        required_variables=("name",),
    )

    assert preview.rendered_preview == "Hello Ada"
    assert preview.redaction_categories == ()


def test_render_safe_preview_blocks_missing_required_fixture() -> None:
    with pytest.raises(PromptPreviewError) as exc:
        render_safe_preview("Hello {{name}}", {}, required_variables=("name",))

    assert exc.value.missing_variables == ("name",)
