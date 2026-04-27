from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.reliability import (
    BreakerResetRequest,
    ListResponse,
    ReliabilityDashboard,
)
from multi_agent_platform.reliability.models import BreakerState


def test_reliability_dashboard_redaction_flags_default_false() -> None:
    dashboard = ReliabilityDashboard(tenant_id=uuid4())
    assert not dashboard.partial
    assert not dashboard.redacted


def test_reliability_schema_generics_and_breaker_reset() -> None:
    assert ListResponse[ReliabilityDashboard]().items == []
    request = BreakerResetRequest(reason="healthy", target_state=BreakerState.CLOSED)
    assert request.target_state is BreakerState.CLOSED
