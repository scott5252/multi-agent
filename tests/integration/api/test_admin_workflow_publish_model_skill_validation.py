from __future__ import annotations

from multi_agent_platform.config.validation import (
    validate_publish_time_model_skill_config,
)


def test_admin_workflow_publish_model_skill_validation_blocks_unsafe_publish() -> None:
    errors = validate_publish_time_model_skill_config(
        has_model_backed_steps=True,
        has_global_default=False,
        prompt_references=[],
        required_skills=["web"],
        bound_skills=[],
        required_tools=["http.fetch"],
        allowed_tools=[],
    )

    assert {error.category.value for error in errors} >= {
        "missing_global_default",
        "missing_prompt_version",
        "skill_not_bound",
        "tool_denied",
    }
