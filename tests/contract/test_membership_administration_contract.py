from __future__ import annotations

from pathlib import Path

import yaml


def test_membership_contract_exposes_required_operations() -> None:
    contract = yaml.safe_load(
        Path(
            "specs/018-user-tenant-membership-administration/contracts/"
            "memberships.openapi.yaml"
        ).read_text()
    )
    paths = contract["paths"]

    assert "/admin/memberships/api/users" in paths
    assert "/admin/memberships/api/invitations" in paths
    assert "/admin/memberships/api/principals/link" in paths
    assert "/admin/memberships/api/role-grants" in paths
    assert "InvitationCreateRequest" in contract["components"]["schemas"]
