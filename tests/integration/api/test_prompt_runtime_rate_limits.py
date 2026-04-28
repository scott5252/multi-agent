from __future__ import annotations

import pytest
from fastapi import HTTPException

from multi_agent_platform.api.routers.admin_prompts import _assert_prompt_payload_bounds
from multi_agent_platform.api.schemas.prompts import PromptDraftSave


def test_prompt_payload_bounds_reject_oversized_prompt_content() -> None:
    template_content = "\u0100" * 32769
    payload = PromptDraftSave(
        expected_revision_number=0,
        prompt_title="Too Large",
        purpose="QA",
        template_content=template_content,
        fixture_sets=[],
    )
    assert len(template_content) <= 65536
    assert len(template_content.encode("utf-8")) > 64 * 1024

    with pytest.raises(HTTPException) as exc_info:
        _assert_prompt_payload_bounds(payload)

    assert exc_info.value.status_code == 413
    assert exc_info.value.detail == {"code": "prompt_too_large"}
