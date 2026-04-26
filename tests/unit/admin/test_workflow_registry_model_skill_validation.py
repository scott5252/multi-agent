from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.config.model_skill import (
    ModelProviderSummary,
    ProviderStatus,
)
from multi_agent_platform.config.validation import (
    validate_model_reference,
    validate_publish_time_model_skill_config,
)


def test_publish_time_model_skill_validation_reports_safe_categories() -> None:
    errors = validate_publish_time_model_skill_config(
        has_model_backed_steps=True,
        has_global_default=False,
        prompt_references=[],
        required_skills=["web"],
        bound_skills=[],
        required_tools=["http.fetch"],
        allowed_tools=[],
    )

    assert [error.category.value for error in errors] == [
        "missing_global_default",
        "missing_prompt_version",
        "skill_not_bound",
        "tool_denied",
    ]


def test_publish_time_model_reference_rejects_inactive_or_wrong_tenant() -> None:
    tenant_id = uuid4()
    provider = ModelProviderSummary(
        model_provider_entry_id=uuid4(),
        tenant_id=uuid4(),
        provider_key="openai",
        model_id="gpt-5.4",
        display_name="OpenAI GPT",
        status=ProviderStatus.INACTIVE,
    )

    try:
        validate_model_reference(
            provider_key="openai",
            model_id="gpt-5.4",
            tenant_id=tenant_id,
            providers=[provider],
        )
    except ValueError as exc:
        assert "inactive" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("inactive cross-tenant provider should fail")
