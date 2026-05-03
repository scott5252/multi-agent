from __future__ import annotations

from uuid import uuid4

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.memberships import (
    MembershipInvitationCreateRequest,
    MembershipRoleGrantCreateRequest,
)


def test_invitation_request_defaults_to_tenant_user() -> None:
    payload = MembershipInvitationCreateRequest(email="Reviewer@Example.com")

    assert payload.requested_roles[0].value == "tenant_user"


def test_invitation_request_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        MembershipInvitationCreateRequest(email="not-an-email")


def test_role_grant_request_accepts_tenant_scope() -> None:
    payload = MembershipRoleGrantCreateRequest(
        principal_identity_id=uuid4(),
        scope_type="tenant",
        tenant_id=uuid4(),
        role_code="tenant_admin",
    )

    assert payload.scope_type.value == "tenant"
    assert payload.role_code.value == "tenant_admin"
