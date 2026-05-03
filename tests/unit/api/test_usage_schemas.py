from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.usage import UsageFilterParams


def test_usage_filter_params_validate_time_range() -> None:
    params = UsageFilterParams(group_by="provider")

    assert params.to_filters().group_by == "provider"


def test_usage_filter_params_reject_invalid_time_range() -> None:
    with pytest.raises(ValidationError):
        UsageFilterParams(
            start="2026-05-03T12:00:00Z",
            end="2026-05-03T11:00:00Z",
        ).to_filters()
