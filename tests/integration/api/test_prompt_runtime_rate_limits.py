from __future__ import annotations

import pytest
from fastapi import HTTPException

from multi_agent_platform.api.routers.admin_prompts import _assert_prompt_payload_bounds
from multi_agent_platform.api.schemas.prompts import PromptDraftSave


def test_prompt_payload_bounds_reject_oversized_prompt_content() -> None:
    payload = PromptDraftSave.model_construct(
        expected_revision_number=0,
        prompt_title="Too Large",
        purpose="QA",
        template_content="x" * (65 * 1024),
        fixture_sets=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        _assert_prompt_payload_bounds(payload)

    assert exc_info.value.status_code == 413
