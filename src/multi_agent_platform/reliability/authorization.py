from __future__ import annotations

from enum import StrEnum
from typing import Protocol
from uuid import UUID


class ReliabilityAction(StrEnum):
    INSPECT = "inspect"
    CHANGE_POLICY = "change_policy"
    RESET_BREAKER = "reset_breaker"
    ACT_ON_DEAD_LETTER = "act_on_dead_letter"
    RETRY_COMPENSATION = "retry_compensation"


class PrincipalLike(Protocol):
    principal_id: str
    tenant_id: UUID | None
    role_codes: tuple[str, ...]


class ReliabilityAuthorizationError(PermissionError):
    pass


GLOBAL_ADMIN_ROLES = {"platform_admin", "admin"}
TENANT_OPERATOR_ROLES = {"tenant_admin", "operator"}
AUDITOR_ROLES = {"auditor"}


def ensure_reliability_authorized(
    *,
    principal: PrincipalLike,
    tenant_id: UUID | None,
    action: ReliabilityAction,
) -> None:
    roles = set(principal.role_codes)
    if roles & GLOBAL_ADMIN_ROLES:
        return
    same_tenant = tenant_id is not None and principal.tenant_id == tenant_id
    if action is ReliabilityAction.INSPECT and roles & AUDITOR_ROLES and same_tenant:
        return
    if roles & TENANT_OPERATOR_ROLES and same_tenant:
        if action is not ReliabilityAction.CHANGE_POLICY or tenant_id is not None:
            return
    raise ReliabilityAuthorizationError("reliability action denied")
