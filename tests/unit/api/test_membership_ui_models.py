from __future__ import annotations

from multi_agent_platform.api.ui.memberships import (
    MembershipAdministrationPage,
    redaction_notice,
)


def test_membership_page_summary_properties() -> None:
    page = MembershipAdministrationPage(
        platform_scope=True,
        principals=(),
        invitations=(),
        memberships=(),
        role_grants=(),
        access_history=(),
        audit_records=(),
    )

    assert page.scope_label == "Platform scope"
    assert page.active_principal_count == 0
    assert "Passwords" in redaction_notice()
