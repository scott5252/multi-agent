from __future__ import annotations

from multi_agent_platform.admin.memberships.models import (
    MembershipAccessScope,
    MembershipPermissionError,
    MembershipScopeType,
    role_scope_type,
)
from multi_agent_platform.admin.memberships.redaction import (
    email_fingerprint,
    mask_email,
    mask_identifier,
    normalize_email,
    sanitize_metadata,
    sanitize_text,
)
from multi_agent_platform.db.models.access_control import RoleScopeType


def test_email_normalization_hashing_and_masking_are_stable() -> None:
    assert normalize_email(" Reviewer@Example.COM ") == "reviewer@example.com"
    assert email_fingerprint("Reviewer@Example.com") == email_fingerprint(
        " reviewer@example.COM "
    )
    assert mask_email("reviewer@example.com") == "re***r@e***.com"


def test_identifier_and_metadata_redaction_remove_sensitive_values() -> None:
    assert mask_identifier("auth0|abcdef123456") == "auth***3456"
    redacted = sanitize_metadata(
        {
            "token": "secret-token",
            "role_code": "tenant_admin",
            "raw_email": "reviewer@example.com",
        }
    )

    assert redacted["token"] == "[redacted]"
    assert redacted["raw_email"] == "[redacted]"
    assert redacted["role_code"] == "tenant_admin"


def test_redaction_handles_short_or_missing_values() -> None:
    assert mask_email("nobody") == "no***"
    assert mask_email("a@example") == "a***@ex***"
    assert mask_email("ab@example.test") == "a***@e***.test"
    assert mask_identifier(None) == "unavailable"
    assert mask_identifier("short") == "sh***"
    assert sanitize_text(None) is None
    assert sanitize_text(" \x00  ") is None
    assert sanitize_text(" a \n b ", max_length=3) == "a b"


def test_metadata_sanitizer_keeps_safe_scalar_and_list_values() -> None:
    redacted = sanitize_metadata(
        {
            "\x00count": 3,
            "enabled": True,
            "empty": None,
            "roles": ("tenant_user", "tenant_admin"),
            "object": {"nested": "value"},
        }
    )

    assert redacted["count"] == 3
    assert redacted["enabled"] is True
    assert redacted["empty"] is None
    assert redacted["roles"] == ["tenant_user", "tenant_admin"]
    assert redacted["object"] == "{'nested': 'value'}"
    assert sanitize_metadata(None) == {}


def test_membership_access_scope_and_role_scope_helpers() -> None:
    tenant_scope = MembershipAccessScope(
        scope_type=MembershipScopeType.TENANT,
        principal_id="tenant-admin",
        tenant_id="11111111-1111-1111-1111-111111111111",
    )
    platform_scope = MembershipAccessScope(
        scope_type=MembershipScopeType.PLATFORM,
        principal_id="platform-admin",
    )

    assert str(tenant_scope.require_tenant()) == "11111111-1111-1111-1111-111111111111"
    assert role_scope_type(MembershipScopeType.PLATFORM) is RoleScopeType.PLATFORM
    assert role_scope_type(MembershipScopeType.TENANT) is RoleScopeType.TENANT

    try:
        platform_scope.require_tenant()
    except MembershipPermissionError as exc:
        assert "tenant membership scope required" in str(exc)
    else:  # pragma: no cover - defensive assertion guard
        raise AssertionError("platform scope should require an explicit tenant")
