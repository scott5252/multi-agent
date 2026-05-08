from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.skill_registry import (
    SkillAuditRecord,
    SkillInstallation,
    SkillInstallationCredential,
)

INSTALLATION_ID = UUID("52000000-0000-0000-0000-000000000003")
CREDENTIAL_ID = UUID("52000000-0000-0000-0000-000000000004")


def main() -> int:
    engine = create_engine(_database_url())
    with Session(engine) as session:
        installation = session.get(SkillInstallation, INSTALLATION_ID)
        credential = session.get(SkillInstallationCredential, CREDENTIAL_ID)
        audit_count = session.scalar(
            select(func.count())
            .select_from(SkillAuditRecord)
            .where(SkillAuditRecord.skill_installation_id == INSTALLATION_ID)
        )
        if installation is None:
            raise RuntimeError("QA052 installation is missing")
        if credential is None:
            raise RuntimeError("QA052 credential readiness row is missing")
        if credential.status != "ready":
            raise RuntimeError(
                "Expected credential status ready after UI action, "
                f"got {credential.status}"
            )
        if installation.credential_status != "ready":
            raise RuntimeError(
                "Expected installation credential_status ready after UI action, "
                f"got {installation.credential_status}"
            )
        if credential.configured_by_principal_id != "tenant-admin-acme":
            raise RuntimeError(
                "Expected credential configured_by_principal_id tenant-admin-acme, "
                f"got {credential.configured_by_principal_id}"
            )
    print("Verified QA052 skill lifecycle credential persistence")
    print(f"installation_revision={installation.revision_token}")
    print(f"credential_status={credential.status}")
    print(f"audit_records={audit_count}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
