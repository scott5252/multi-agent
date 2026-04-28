from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.tenant import Tenant


def prepare_prompt_runtime_database(
    database_path: Path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
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
        connection.execute(text("DELETE FROM alembic_version"))
        connection.execute(
            text(
                "INSERT INTO alembic_version(version_num) "
                "VALUES ('0012_prompt_runtime_profiles')"
            )
        )
    with Session(engine) as session:
        session.add_all(
            [
                Tenant(
                    tenant_id=tenant_id,
                    slug="acme",
                    display_name="Acme",
                ),
                Tenant(
                    tenant_id=other_tenant_id,
                    slug="beta",
                    display_name="Beta",
                ),
            ]
        )
        session.commit()


def configure_prompt_runtime_env(
    monkeypatch,
    tmp_path,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> None:
    database_path = tmp_path / "prompt-runtime-browser.db"
    prepare_prompt_runtime_database(database_path, tenant_id, other_tenant_id)
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "artifacts"))
    monkeypatch.setenv("AUTH_MODE", "local_principal")
    monkeypatch.setenv(
        "LOCAL_PRINCIPAL_CATALOG_JSON",
        json.dumps(
            {
                "tenant-admin-acme": {
                    "catalog_key": "tenant-admin-acme",
                    "display_name": "Tenant Admin",
                    "tenant_id": str(tenant_id),
                    "org_id": "org-acme",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "tenant-admin-beta": {
                    "catalog_key": "tenant-admin-beta",
                    "display_name": "Beta Tenant Admin",
                    "tenant_id": str(other_tenant_id),
                    "org_id": "org-beta",
                    "role_codes": ["tenant_user", "tenant_admin"],
                    "permission_codes": ["tenant:read", "tenant:admin"],
                },
                "platform-admin": {
                    "catalog_key": "platform-admin",
                    "display_name": "Platform Admin",
                    "role_codes": ["platform_admin"],
                    "permission_codes": ["platform:admin"],
                },
            }
        ),
    )
