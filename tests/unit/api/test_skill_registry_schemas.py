from __future__ import annotations

from multi_agent_platform.api.schemas.skill_registry import (
    SkillVersionValidationResponse,
)


def test_skill_registry_schema_defaults_are_safe() -> None:
    response = SkillVersionValidationResponse(status="passed")

    assert response.findings == []
    assert response.safe_summary == {}
