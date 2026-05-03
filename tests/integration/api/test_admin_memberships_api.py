from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
PLATFORM_HEADERS = {"X-Local-Principal": "platform-admin"}
ACME_HEADERS = {"X-Local-Principal": "tenant-admin-acme"}


def _configure_env(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "memberships.db"
    import_models()
    engine = create_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE IF NOT EXISTS alembic_version "
                "(version_num VARCHAR(64) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0018_membership_admin')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(
                    tenant_id=UUID(ACME_TENANT_ID),
                    slug="acme",
                    display_name="Acme",
                ),
                Tenant(
                    tenant_id=UUID(GLOBEX_TENANT_ID),
                    slug="globex",
                    display_name="Globex",
                ),
            ]
        )
        session.commit()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": [
                        "platform:admin",
                        "membership-admin:read",
                        "membership-admin:invite",
                        "membership-admin:write",
                        "membership-admin:grants",
                        "membership-admin:audit",
                    ],
                },
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Acme Tenant Admin",
                    "tenant_id": ACME_TENANT_ID,
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": [
                        "tenant:read",
                        "tenant:admin",
                        "membership-admin:read",
                        "membership-admin:invite",
                        "membership-admin:write",
                        "membership-admin:grants",
                        "membership-admin:audit",
                    ],
                },
            }
        ),
    )


def test_platform_membership_api_invite_link_grant_suspend_and_replay(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        linked = client.post(
            "/admin/memberships/api/principals/link",
            headers=PLATFORM_HEADERS,
            json={
                "auth0_subject": "auth0|reviewer",
                "email": "Reviewer@Example.com",
                "display_name": "Reviewer",
            },
        )
        principal_id = linked.json()["principal_identity_id"]
        invite = client.post(
            "/admin/memberships/api/invitations",
            headers=PLATFORM_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "email": "Reviewer@Example.com",
                "requested_roles": ["tenant_user"],
                "idempotency_key": "invite-reviewer",
            },
        )
        replay = client.post(
            "/admin/memberships/api/invitations",
            headers=PLATFORM_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "email": " reviewer@example.COM ",
                "requested_roles": ["tenant_user"],
                "idempotency_key": "invite-reviewer",
            },
        )
        grant = client.post(
            "/admin/memberships/api/role-grants",
            headers=PLATFORM_HEADERS,
            json={
                "principal_identity_id": principal_id,
                "scope_type": "tenant",
                "tenant_id": ACME_TENANT_ID,
                "role_code": "tenant_admin",
            },
        )
        suspended = client.post(
            f"/admin/memberships/api/principals/{principal_id}/suspend",
            headers=PLATFORM_HEADERS,
        )
        snapshot = client.get(
            f"/admin/memberships/api/users?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )

    assert linked.status_code == 200
    assert invite.status_code == 201
    assert replay.json()["replayed"] is True
    assert replay.json()["user_invitation_id"] == invite.json()["user_invitation_id"]
    assert "Reviewer@Example.com" not in invite.text
    assert grant.status_code == 201
    assert suspended.json()["status"] == "suspended"
    assert snapshot.json()["role_grants"][0]["role_code"] == "tenant_admin"


def test_tenant_admin_boundaries_for_cross_tenant_and_platform_roles(
    tmp_path,
    monkeypatch,
) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    with TestClient(app) as client:
        linked = client.post(
            "/admin/memberships/api/principals/link",
            headers=PLATFORM_HEADERS,
            json={"auth0_subject": "auth0|tenant-reviewer"},
        )
        principal_id = linked.json()["principal_identity_id"]
        tenant_invite = client.post(
            "/admin/memberships/api/invitations",
            headers=ACME_HEADERS,
            json={
                "tenant_id": ACME_TENANT_ID,
                "email": "tenant@example.com",
                "requested_roles": ["tenant_user"],
            },
        )
        cross_tenant = client.post(
            "/admin/memberships/api/invitations",
            headers=ACME_HEADERS,
            json={
                "tenant_id": GLOBEX_TENANT_ID,
                "email": "globex@example.com",
                "requested_roles": ["tenant_user"],
            },
        )
        platform_role = client.post(
            "/admin/memberships/api/role-grants",
            headers=ACME_HEADERS,
            json={
                "principal_identity_id": principal_id,
                "scope_type": "platform",
                "role_code": "platform_admin",
            },
        )

    assert tenant_invite.status_code == 201
    assert cross_tenant.status_code == 403
    assert platform_role.status_code == 403


def test_membership_api_error_and_status_paths(tmp_path, monkeypatch) -> None:
    _configure_env(monkeypatch, tmp_path)
    app = create_app()

    missing_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

    with TestClient(app) as client:
        linked = client.post(
            "/admin/memberships/api/principals/link",
            headers=PLATFORM_HEADERS,
            json={
                "auth0_subject": "auth0|api-status",
                "email": "api.status@example.com",
            },
        )
        principal_id = linked.json()["principal_identity_id"]
        conflict = client.post(
            "/admin/memberships/api/principals/link",
            headers=PLATFORM_HEADERS,
            json={"auth0_subject": "auth0|api-status"},
        )
        tenant_link = client.post(
            "/admin/memberships/api/principals/link",
            headers=ACME_HEADERS,
            json={"auth0_subject": "auth0|tenant-denied"},
        )
        missing_grant_principal = client.post(
            "/admin/memberships/api/role-grants",
            headers=PLATFORM_HEADERS,
            json={
                "principal_identity_id": missing_id,
                "scope_type": "tenant",
                "tenant_id": ACME_TENANT_ID,
                "role_code": "tenant_user",
            },
        )
        grant = client.post(
            "/admin/memberships/api/role-grants",
            headers=PLATFORM_HEADERS,
            json={
                "principal_identity_id": principal_id,
                "scope_type": "tenant",
                "tenant_id": ACME_TENANT_ID,
                "role_code": "tenant_user",
            },
        )
        missing_revoke = client.post(
            f"/admin/memberships/api/role-grants/{missing_id}/revoke",
            headers=PLATFORM_HEADERS,
        )
        revoked = client.post(
            f"/admin/memberships/api/role-grants/{grant.json()['role_grant_id']}/revoke",
            headers=PLATFORM_HEADERS,
        )
        missing_suspend = client.post(
            f"/admin/memberships/api/principals/{missing_id}/suspend",
            headers=PLATFORM_HEADERS,
        )
        suspended = client.post(
            f"/admin/memberships/api/principals/{principal_id}/suspend",
            headers=PLATFORM_HEADERS,
        )
        missing_reactivate = client.post(
            f"/admin/memberships/api/principals/{missing_id}/reactivate",
            headers=PLATFORM_HEADERS,
        )
        reactivated = client.post(
            f"/admin/memberships/api/principals/{principal_id}/reactivate",
            headers=PLATFORM_HEADERS,
        )
        snapshot = client.get(
            f"/admin/memberships/api/users?tenant_id={ACME_TENANT_ID}&q=api.status",
            headers=PLATFORM_HEADERS,
        )
        membership_id = snapshot.json()["memberships"][0]["tenant_membership_id"]
        membership_no_tenant = client.post(
            f"/admin/memberships/api/memberships/{membership_id}/suspended",
            headers=PLATFORM_HEADERS,
        )
        membership_updated = client.post(
            f"/admin/memberships/api/memberships/{membership_id}/suspended?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )
        missing_membership = client.post(
            f"/admin/memberships/api/memberships/{missing_id}/removed?tenant_id={ACME_TENANT_ID}",
            headers=PLATFORM_HEADERS,
        )

    assert linked.status_code == 200
    assert conflict.status_code == 409
    assert tenant_link.status_code == 403
    assert missing_grant_principal.status_code == 404
    assert missing_revoke.status_code == 404
    assert revoked.json()["status"] == "revoked"
    assert missing_suspend.status_code == 404
    assert suspended.json()["status"] == "suspended"
    assert missing_reactivate.status_code == 404
    assert reactivated.json()["status"] == "active"
    assert membership_no_tenant.status_code == 403
    assert membership_updated.json()["status"] == "suspended"
    assert missing_membership.status_code == 404
