from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import pytest

from multi_agent_platform.reliability.authorization import (
    ReliabilityAction,
    ReliabilityAuthorizationError,
    ensure_reliability_authorized,
)

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


@dataclass(slots=True, frozen=True)
class Principal:
    principal_id: str
    tenant_id: UUID | None
    role_codes: tuple[str, ...]


def test_global_admin_can_take_any_reliability_action() -> None:
    principal = Principal("admin", None, ("platform_admin",))
    ensure_reliability_authorized(
        principal=principal,
        tenant_id=TENANT_ID,
        action=ReliabilityAction.RESET_BREAKER,
    )


def test_tenant_operator_is_limited_to_same_tenant() -> None:
    principal = Principal("operator", TENANT_ID, ("operator",))
    ensure_reliability_authorized(
        principal=principal,
        tenant_id=TENANT_ID,
        action=ReliabilityAction.ACT_ON_DEAD_LETTER,
    )
    with pytest.raises(ReliabilityAuthorizationError):
        ensure_reliability_authorized(
            principal=principal,
            tenant_id=UUID("00000000-0000-0000-0000-000000000002"),
            action=ReliabilityAction.ACT_ON_DEAD_LETTER,
        )


def test_auditor_can_inspect_but_not_change_controls() -> None:
    principal = Principal("auditor", TENANT_ID, ("auditor",))
    ensure_reliability_authorized(
        principal=principal,
        tenant_id=TENANT_ID,
        action=ReliabilityAction.INSPECT,
    )
    with pytest.raises(ReliabilityAuthorizationError):
        ensure_reliability_authorized(
            principal=principal,
            tenant_id=TENANT_ID,
            action=ReliabilityAction.CHANGE_POLICY,
        )
