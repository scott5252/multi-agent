from __future__ import annotations

from multi_agent_platform.prompts.fixture_safety import sanitize_fixture_values
from multi_agent_platform.prompts.models import PromptPreview
from multi_agent_platform.prompts.template import render_template


class PromptPreviewError(ValueError):
    def __init__(self, missing_variables: tuple[str, ...]) -> None:
        super().__init__("required fixture values are missing")
        self.missing_variables = missing_variables


def render_safe_preview(
    template_content: str,
    fixture_values: dict[str, str],
    *,
    required_variables: tuple[str, ...],
) -> PromptPreview:
    missing = tuple(name for name in required_variables if name not in fixture_values)
    if missing:
        raise PromptPreviewError(missing)
    sanitized = sanitize_fixture_values(fixture_values)
    rendered = render_template(template_content, sanitized.values_by_variable)
    return PromptPreview(
        rendered_preview=rendered,
        redaction_categories=sanitized.redaction_categories,
    )
