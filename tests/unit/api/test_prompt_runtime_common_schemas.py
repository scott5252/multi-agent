from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.agent_profiles import ProfileCreate
from multi_agent_platform.api.schemas.prompts import PromptLineageCreate


def test_prompt_schema_enforces_scope_rules() -> None:
    payload = PromptLineageCreate(
        scope_type="platform",
        tenant_id=None,
        slug="triage",
        display_name="Triage",
        purpose="Summarize",
    )

    assert payload.scope_type == "platform"


def test_profile_schema_rejects_tenant_scope_without_tenant_id() -> None:
    with pytest.raises(ValidationError):
        ProfileCreate(
            scope_type="tenant",
            tenant_id=None,
            agent_key="planner",
            agent_kind="agent",
            display_name="Planner",
            purpose="Plan",
        )
