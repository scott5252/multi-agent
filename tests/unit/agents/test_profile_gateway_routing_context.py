from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.agents.model_skill_integration import (
    build_profile_gateway_routing_context,
)
from multi_agent_platform.config.resolver import enforce_gateway_route_authorization


def test_profile_gateway_context_preserves_profile_hints_as_advisory_metadata() -> None:
    profile_id = uuid4()
    context = build_profile_gateway_routing_context(
        agent_profile_version_id=profile_id,
        model_routing_hints={"provider_key": "openai", "model_id": "gpt-test"},
        memory_policy={"scope": "tenant"},
        tool_policy_expectations={"tools": ["search"]},
        output_contract={"type": "object"},
        source_scope="tenant",
    )

    assert context["agent_profile_version_id"] == str(profile_id)
    assert context["model_routing_hints"]["provider_key"] == "openai"
    assert context["profile_provenance"]["tenant_profile_precedence_applied"] is True


def test_profile_hints_cannot_bypass_model_skill_route_authorization() -> None:
    with pytest.raises(PermissionError, match="model_skill_config"):
        enforce_gateway_route_authorization(
            selected_provider_key="local_openai_compatible",
            selected_model_id="local-model",
            profile_model_routing_hints={
                "provider_key": "openai",
                "model_id": "gpt-4.1",
            },
            authorized_provider_keys={"openai"},
        )
