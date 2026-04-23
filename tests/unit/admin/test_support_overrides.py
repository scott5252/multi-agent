from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.db.repositories.access_control import AccessControlRepository


async def test_admin_service_requires_access_repository_for_override_actions() -> None:
    service = AdminService()
    with pytest.raises(RuntimeError):
        await service.create_support_override(
            requester_principal_id=uuid4(),
            target_tenant_id=uuid4(),
            justification="Investigate issue",
            trace_id="trace-1",
            idempotency_key="override-1",
        )


async def test_admin_service_returns_none_for_unknown_support_override(session) -> None:
    service = AdminService(access_repository=AccessControlRepository(session))
    assert (
        await service.approve_support_override(
            support_override_request_id=uuid4(),
            approver_principal_id=uuid4(),
        )
        is None
    )
