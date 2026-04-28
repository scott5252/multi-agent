from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.model_providers import (
    ProviderConnectionCreateRequest,
)


def test_provider_connection_schema_accepts_secret_references_only() -> None:
    payload = ProviderConnectionCreateRequest(
        provider_type="openai",
        display_name="QA Provider",
        models=[{"model_id": "gpt-test"}],
        credential_secret_reference_ids=["qa011/openai-placeholder"],
    )

    assert payload.provider_type == "openai"
    assert payload.models[0].model_id == "gpt-test"


def test_provider_connection_schema_rejects_raw_secret_like_reference() -> None:
    with pytest.raises(ValidationError):
        ProviderConnectionCreateRequest(
            provider_type="openai",
            display_name="QA Provider",
            models=[{"model_id": "gpt-test"}],
            credential_secret_reference_ids=["sk-live-secret-value"],
        )
