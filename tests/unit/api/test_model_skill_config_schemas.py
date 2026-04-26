from __future__ import annotations

from uuid import uuid4

from pydantic import ValidationError

from multi_agent_platform.api.schemas.model_skill_config import (
    ActivationRequest,
    ModelRoutingCreateRequest,
    ModelSkillErrorResponse,
    SecretReferenceCreateRequest,
)
from multi_agent_platform.config.model_skill import (
    ModelSkillErrorCategory,
    ScopeSelector,
)
from multi_agent_platform.config.validation import assert_no_raw_secret, require_reason


def test_model_skill_schemas_use_stable_error_categories_and_safe_ids() -> None:
    response = ModelSkillErrorResponse(
        category=ModelSkillErrorCategory.SECRET_REFERENCE_INVALID,
        message="secret reference unavailable",
        safe_identifiers={"secret_reference_id": "ref"},
    )

    assert response.category.value == "secret_reference_invalid"
    assert response.safe_identifiers == {"secret_reference_id": "ref"}


def test_model_skill_requests_require_reasons_at_validation_boundary() -> None:
    request = ModelRoutingCreateRequest(
        scope=ScopeSelector(tenant_id=uuid4()),
        provider_key="openai",
        model_id="gpt-5.4",
        reason="Set tenant default",
    )
    activation = ActivationRequest(reason="Activate reviewed default")

    assert require_reason(request.reason) == "Set tenant default"
    assert require_reason(activation.reason) == "Activate reviewed default"


def test_secret_reference_payloads_reject_raw_secret_like_values() -> None:
    request = SecretReferenceCreateRequest(
        scope=ScopeSelector(tenant_id=uuid4()),
        secret_reference_id="ref",
        provider_key="static",
        external_reference="example/api-key",
        allowed_scopes={"host": "docs.example.com"},
        reason="Safe reference only",
    )

    assert_no_raw_secret(request.model_dump(mode="json"))
    try:
        assert_no_raw_secret({"token": "sk-secret"})
    except ValueError as exc:
        assert "raw credential field" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("raw token should be rejected")


def test_pydantic_schema_rejects_missing_required_reason() -> None:
    try:
        ModelRoutingCreateRequest(
            scope=ScopeSelector(tenant_id=uuid4()),
            provider_key="openai",
            model_id="gpt-5.4",
        )
    except ValidationError:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("reason is required")
