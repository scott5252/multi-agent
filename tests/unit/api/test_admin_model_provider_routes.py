from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.api.routers import admin_model_providers
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    ProviderTestSummary,
    TestOutcome,
)


class FakeSession:
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


class FakeProviderService:
    async def test_connection(
        self,
        *,
        principal: PrincipalContext,
        connection_id,
    ) -> ProviderTestSummary:
        return ProviderTestSummary(
            outcome=TestOutcome.SUCCESS,
            normalized_reason=ErrorCategory.NONE,
            latency_ms=7,
            tested_model_id="gpt-test",
            safe_diagnostic_summary=f"safe probe for {principal.principal_id}",
        )


@pytest.mark.asyncio
async def test_provider_test_endpoint_serializes_probe_summary(monkeypatch) -> None:
    service = FakeProviderService()
    monkeypatch.setattr(
        admin_model_providers,
        "_service",
        lambda session, container: service,
    )
    session = FakeSession()

    response = await admin_model_providers.test_provider_connection(
        connection_id=uuid4(),
        principal=PrincipalContext(
            principal_id="platform-admin",
            role_codes=("platform_admin",),
        ),
        session=session,
        container=object(),
    )

    assert session.committed is True
    assert response.outcome is TestOutcome.SUCCESS
    assert response.normalized_reason is ErrorCategory.NONE
    assert response.tested_model_id == "gpt-test"
