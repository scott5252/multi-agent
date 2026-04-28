from __future__ import annotations

import re


class PromptTemplateSyntaxError(ValueError):
    pass


_PLACEHOLDER = re.compile(r"{{([A-Za-z_][A-Za-z0-9_]*)}}")
_EXECUTABLE_MARKERS = ("{%", "{#", "}}}", "{{{")
_ANY_MUSTACHE = re.compile(r"{{.*?}}", re.DOTALL)


def parse_template_variables(template_content: str) -> tuple[str, ...]:
    if any(marker in template_content for marker in _EXECUTABLE_MARKERS):
        raise PromptTemplateSyntaxError("template code is not allowed")
    if template_content.count("{{") != template_content.count("}}"):
        raise PromptTemplateSyntaxError("unbalanced placeholder braces")

    variables: list[str] = []
    for match in _ANY_MUSTACHE.finditer(template_content):
        placeholder = match.group(0)
        parsed = _PLACEHOLDER.fullmatch(placeholder)
        if parsed is None:
            raise PromptTemplateSyntaxError("invalid placeholder syntax")
        variables.append(parsed.group(1))
    return tuple(dict.fromkeys(variables))


def render_template(template_content: str, values_by_variable: dict[str, str]) -> str:
    parse_template_variables(template_content)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return values_by_variable.get(name, match.group(0))

    return _PLACEHOLDER.sub(replace, template_content)
