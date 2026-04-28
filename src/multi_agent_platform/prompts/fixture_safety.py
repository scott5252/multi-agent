from __future__ import annotations

import re

from multi_agent_platform.prompts.models import SanitizedFixtureValues


class UnsafeFixtureValueError(ValueError):
    def __init__(self, variable_name: str, category: str) -> None:
        super().__init__("fixture value is unsafe")
        self.variable_name = variable_name
        self.category = category


_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("credential", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")),
    ("credential", re.compile(r"(?i)\b(password|secret|api[_-]?key)\s*=")),
    ("credential", re.compile(r"(?i)\bauthorization:\s*bearer\b")),
    ("credential", re.compile(r"(?i)\bprovider[_-]?token\b")),
)


def sanitize_fixture_values(
    values_by_variable: dict[str, str],
    *,
    max_value_length: int = 2_000,
) -> SanitizedFixtureValues:
    sanitized: dict[str, str] = {}
    redaction_categories: set[str] = set()
    for variable_name, value in values_by_variable.items():
        if len(value) > max_value_length:
            raise UnsafeFixtureValueError(variable_name, "oversized")
        for category, pattern in _SECRET_PATTERNS:
            if pattern.search(value):
                redaction_categories.add(category)
                raise UnsafeFixtureValueError(variable_name, category)
        sanitized[variable_name] = value
    return SanitizedFixtureValues(
        values_by_variable=sanitized,
        redaction_categories=tuple(sorted(redaction_categories)),
    )
