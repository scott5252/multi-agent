from __future__ import annotations

from collections import Counter

from multi_agent_platform.prompts.fixture_safety import (
    UnsafeFixtureValueError,
    sanitize_fixture_values,
)
from multi_agent_platform.prompts.models import (
    PromptValidationReport,
    PromptVariableDeclaration,
    ValidationFinding,
)
from multi_agent_platform.prompts.template import (
    PromptTemplateSyntaxError,
    parse_template_variables,
)


def validate_prompt(
    *,
    template_content: str,
    variables: list[PromptVariableDeclaration],
    fixture_values: dict[str, str],
) -> PromptValidationReport:
    findings: list[ValidationFinding] = []
    try:
        placeholders = set(parse_template_variables(template_content))
    except PromptTemplateSyntaxError as exc:
        return PromptValidationReport(
            status="failed",
            findings=(
                ValidationFinding(
                    code="malformed_template",
                    severity="blocking",
                    message=str(exc),
                    field="template_content",
                ),
            ),
        )

    names = [variable.name for variable in variables]
    name_counts = Counter(names)
    declared = set(names)
    for name, count in name_counts.items():
        if count > 1:
            findings.append(
                ValidationFinding(
                    code="duplicate_variable",
                    severity="blocking",
                    message=f"Variable {name} is declared more than once.",
                    field=f"variables.{name}",
                )
            )
    for name in sorted(placeholders - declared):
        findings.append(
            ValidationFinding(
                code="undeclared_placeholder",
                severity="blocking",
                message=f"Placeholder {name} is not declared.",
                field="template_content",
            )
        )
    for name in sorted(declared - placeholders):
        findings.append(
            ValidationFinding(
                code="unused_variable",
                severity="blocking",
                message=f"Variable {name} is not used in the template.",
                field=f"variables.{name}",
            )
        )
    required = {variable.name for variable in variables if variable.required}
    for name in sorted(required - set(fixture_values)):
        findings.append(
            ValidationFinding(
                code="missing_fixture_value",
                severity="blocking",
                message=f"Required fixture value {name} is missing.",
                field=f"fixture_values.{name}",
            )
        )
    try:
        sanitize_fixture_values(fixture_values)
    except UnsafeFixtureValueError as exc:
        findings.append(
            ValidationFinding(
                code="unsafe_fixture_value",
                severity="blocking",
                message="Fixture value was rejected by safety policy.",
                field=f"fixture_values.{exc.variable_name}",
            )
        )
    return PromptValidationReport(
        status="failed"
        if any(f.severity == "blocking" for f in findings)
        else "passed",
        findings=tuple(findings),
    )
