from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.config.model_skill import (
    ConfigKind,
    ModelProviderSummary,
    PromptReferenceCandidate,
    ScopeSelector,
)
from multi_agent_platform.config.validation import (
    ModelSkillValidationError,
    assert_no_raw_secret,
    require_reason,
    validate_model_reference,
    validate_publish_time_model_skill_config,
    validate_scope_for_kind,
)


def test_validation_rejects_tenant_global_prompt_reference() -> None:
    with pytest.raises(ModelSkillValidationError):
        validate_scope_for_kind(
            ConfigKind.PROMPT_REFERENCE,
            ScopeSelector(tenant_id=uuid4()),
        )


def test_validation_rejects_raw_secret_like_payloads() -> None:
    with pytest.raises(ModelSkillValidationError):
        assert_no_raw_secret({"api_key": "sk-test"})


def test_validation_requires_non_empty_reason() -> None:
    with pytest.raises(ModelSkillValidationError):
        require_reason(" ")

    assert require_reason(" because ") == "because"


def test_validation_resolves_known_active_model_reference() -> None:
    tenant_id = uuid4()
    provider = ModelProviderSummary(
        model_provider_entry_id=uuid4(),
        tenant_id=tenant_id,
        provider_key="openai",
        model_id="gpt-5.4",
        display_name="GPT 5.4",
    )

    assert (
        validate_model_reference(
            provider_key="openai",
            model_id="gpt-5.4",
            tenant_id=tenant_id,
            providers=[provider],
        )
        == provider
    )


def test_validation_rejects_unknown_model_reference() -> None:
    with pytest.raises(ModelSkillValidationError) as exc_info:
        validate_model_reference(
            provider_key="openai",
            model_id="missing",
            tenant_id=uuid4(),
            providers=[],
        )

    assert exc_info.value.category.value == "invalid_model_reference"


def test_publish_time_validation_collects_safe_errors() -> None:
    tenant_id = uuid4()
    prompt = PromptReferenceCandidate(
        version_id=uuid4(),
        tenant_id=tenant_id,
        scope=ScopeSelector(tenant_id=tenant_id, workflow_lineage_id=uuid4()),
        activation_reason="test",
        prompt_id=uuid4(),
        prompt_version_id=uuid4(),
        prompt_digest="digest",
    )

    errors = validate_publish_time_model_skill_config(
        has_model_backed_steps=True,
        has_global_default=False,
        prompt_references=[prompt],
        required_skills=["web"],
        bound_skills=[],
        required_tools=["http.fetch"],
        allowed_tools=[],
    )

    assert {error.category.value for error in errors} == {
        "missing_global_default",
        "skill_not_bound",
        "tool_denied",
    }
