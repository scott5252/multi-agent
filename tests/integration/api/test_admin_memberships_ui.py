from __future__ import annotations

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from tests.integration.api.test_admin_memberships_api import (
    ACME_TENANT_ID,
    PLATFORM_HEADERS,
    _configure_env,
)


def test_membership_admin_page_renders_safe_scoped_forms(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        page = client.get(
            f"/admin/memberships?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )
        posted = client.post(
            "/admin/memberships/invitations",
            headers=PLATFORM_HEADERS,
            data={
                "tenant_id": ACME_TENANT_ID,
                "email": "Reviewer@Example.com",
                "requested_roles": "tenant_user",
                "idempotency_key": "ui-reviewer",
            },
            follow_redirects=False,
        )
        updated = client.get(
            f"/admin/memberships?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )

    assert page.status_code == 200
    assert "Membership Administration" in page.text
    assert "Create Invitation" in page.text
    assert posted.status_code == 303
    assert "re***r@e***.com" in updated.text
    assert "Reviewer@Example.com" not in updated.text


def test_membership_admin_page_post_actions_and_errors(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()
    missing_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    with TestClient(app) as client:
        linked = client.post(
            "/admin/memberships/api/principals/link",
            headers=PLATFORM_HEADERS,
            json={"auth0_subject": "auth0|ui-actions"},
        )
        principal_id = linked.json()["principal_identity_id"]
        role_post = client.post(
            "/admin/memberships/role-grants",
            headers=PLATFORM_HEADERS,
            data={
                "principal_identity_id": principal_id,
                "scope_type": "tenant",
                "tenant_id": ACME_TENANT_ID,
                "role_code": "tenant_user",
            },
            follow_redirects=False,
        )
        snapshot = client.get(
            f"/admin/memberships/api/users?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )
        grant_id = snapshot.json()["role_grants"][0]["role_grant_id"]
        membership_id = snapshot.json()["memberships"][0]["tenant_membership_id"]
        role_revoke = client.post(
            f"/admin/memberships/role-grants/{grant_id}/revoke",
            headers=PLATFORM_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
            follow_redirects=False,
        )
        role_revoke_missing = client.post(
            f"/admin/memberships/role-grants/{missing_id}/revoke",
            headers=PLATFORM_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
        )
        suspend = client.post(
            f"/admin/memberships/principals/{principal_id}/suspend",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        reactivate = client.post(
            f"/admin/memberships/principals/{principal_id}/reactivate",
            headers=PLATFORM_HEADERS,
            follow_redirects=False,
        )
        unknown_principal_action = client.post(
            f"/admin/memberships/principals/{principal_id}/unknown",
            headers=PLATFORM_HEADERS,
        )
        missing_principal = client.post(
            f"/admin/memberships/principals/{missing_id}/suspend",
            headers=PLATFORM_HEADERS,
        )
        membership_suspend = client.post(
            f"/admin/memberships/memberships/{membership_id}/suspended",
            headers=PLATFORM_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
            follow_redirects=False,
        )
        membership_restore = client.post(
            f"/admin/memberships/memberships/{membership_id}/active",
            headers=PLATFORM_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
            follow_redirects=False,
        )
        missing_membership = client.post(
            f"/admin/memberships/memberships/{missing_id}/removed",
            headers=PLATFORM_HEADERS,
            data={"tenant_id": ACME_TENANT_ID},
        )

    assert role_post.status_code == 303
    assert role_revoke.status_code == 303
    assert role_revoke_missing.status_code == 404
    assert suspend.status_code == 303
    assert reactivate.status_code == 303
    assert unknown_principal_action.status_code == 404
    assert missing_principal.status_code == 404
    assert membership_suspend.status_code == 303
    assert membership_restore.status_code == 303
    assert missing_membership.status_code == 404
