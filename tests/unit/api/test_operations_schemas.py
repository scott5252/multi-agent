from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from multi_agent_platform.api.schemas.operations import (
    OperationsExportCreateRequest,
    OperationsLogResponse,
)
from multi_agent_platform.operations.models import OperationsLogFilters


def test_operations_filters_validate_time_range_and_limit() -> None:
    start = datetime(2026, 5, 3, tzinfo=UTC)

    filters = OperationsLogFilters(start=start, end=start + timedelta(minutes=5))

    assert filters.limit == 100
    assert filters.safe_snapshot()["start"].startswith("2026-05-03")
    with pytest.raises(ValueError):
        OperationsLogFilters(start=start, end=start)


def test_operations_api_schemas_default_filters() -> None:
    request = OperationsExportCreateRequest()
    response = OperationsLogResponse(items=(), filters=request.filters.safe_snapshot())

    assert request.filters.limit == 100
    assert response.items == ()
