from __future__ import annotations

from multi_agent_platform.prompts.models import PromptVariableDeclaration
from multi_agent_platform.prompts.validation import validate_prompt


def test_validate_prompt_reports_missing_unused_duplicate_and_malformed_variables() -> (
    None
):
    report = validate_prompt(
        template_content="Hello {{name}} and {{missing}}",
        variables=[
            PromptVariableDeclaration(name="name", purpose="Recipient"),
            PromptVariableDeclaration(name="name", purpose="Duplicate"),
            PromptVariableDeclaration(name="unused", purpose="Not used"),
        ],
        fixture_values={"name": "Ada"},
    )

    codes = {finding.code for finding in report.findings}
    assert report.status == "failed"
    assert {
        "duplicate_variable",
        "undeclared_placeholder",
        "unused_variable",
        "missing_fixture_value",
    } <= codes


def test_validate_prompt_passes_complete_safe_template() -> None:
    report = validate_prompt(
        template_content="Hello {{name}}",
        variables=[PromptVariableDeclaration(name="name", purpose="Recipient")],
        fixture_values={"name": "Ada"},
    )

    assert report.status == "passed"
    assert report.blocking_issue_count == 0
