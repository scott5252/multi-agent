from __future__ import annotations

import pytest

from multi_agent_platform.prompts.template import (
    PromptTemplateSyntaxError,
    parse_template_variables,
    render_template,
)


def test_parse_template_variables_accepts_literal_placeholders() -> None:
    assert parse_template_variables("Hello {{first_name}} from {{team_2}}") == (
        "first_name",
        "team_2",
    )


@pytest.mark.parametrize(
    "content",
    [
        "Hello {{ first_name }}",
        "Hello {{first-name}}",
        "{% for item in items %}",
        "{{ user.name }}",
        "{{name",
    ],
)
def test_parse_template_variables_rejects_executable_or_malformed_syntax(
    content: str,
) -> None:
    with pytest.raises(PromptTemplateSyntaxError):
        parse_template_variables(content)


def test_render_template_replaces_values_without_executing_code() -> None:
    rendered = render_template(
        "Hello {{name}}. Literal code: {{script}}",
        {"name": "Ada", "script": "{% do_not_execute %}"},
    )

    assert rendered == "Hello Ada. Literal code: {% do_not_execute %}"
