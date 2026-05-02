from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.agent_tests import (
    AgentTestRunCreateRequest,
    AgentTestSuiteCreateRequest,
)


def test_agent_test_suite_schema_validates_threshold_and_target() -> None:
    request = AgentTestSuiteCreateRequest(
        tenant_id=uuid4(),
        name="Draft guard",
        target_type="workflow_draft",
        target_id="draft-1",
        pass_threshold=0.75,
    )

    assert request.default_safe_mode == "mock_model"
    with pytest.raises(ValidationError):
        AgentTestSuiteCreateRequest(
            tenant_id=uuid4(),
            name="Bad",
            target_type="workflow_draft",
            target_id="draft-1",
            pass_threshold=2.0,
        )


def test_run_schema_rejects_secret_like_probe_references() -> None:
    assert (
        AgentTestRunCreateRequest(
            safe_mode="real_model_side_effects_disabled"
        ).safe_mode
        == "real_model_side_effects_disabled"
    )
    with pytest.raises(ValidationError):
        AgentTestRunCreateRequest(
            safe_mode="approved_real_probe",
            approved_probe_reference="secret-token-value",
        )
