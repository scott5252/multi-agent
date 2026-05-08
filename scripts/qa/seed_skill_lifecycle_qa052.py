from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.skill_registry import (
    SkillAuditRecord,
    SkillInstallation,
    SkillInstallationCredential,
    SkillInstallationState,
    SkillInstallationTest,
    SkillJobStatus,
    SkillPackage,
    SkillPackageLifecycleState,
    SkillPackageTenantGrant,
    SkillPackageVersion,
    SkillVersionLifecycleState,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
PACKAGE_ID = UUID("52000000-0000-0000-0000-000000000001")
VERSION_ID = UUID("52000000-0000-0000-0000-000000000002")
INSTALLATION_ID = UUID("52000000-0000-0000-0000-000000000003")
CREDENTIAL_ID = UUID("52000000-0000-0000-0000-000000000004")
SECRET_REFERENCE_ID = UUID("52000000-0000-0000-0000-000000000005")
TEST_ID = UUID("52000000-0000-0000-0000-000000000006")
AUDIT_ID = UUID("52000000-0000-0000-0000-000000000007")
REVISION = "qa052-installation-rev-1"


def main() -> int:
    database_url = _database_url()
    engine = create_engine(database_url)
    now = datetime(2026, 5, 7, 16, tzinfo=UTC)
    with Session(engine) as session:
        package = session.get(SkillPackage, PACKAGE_ID)
        if package is None:
            session.add(
                SkillPackage(
                    skill_package_id=PACKAGE_ID,
                    slug="qa052-calendar-assistant",
                    display_name="QA052 Calendar Assistant",
                    description="Calendar assistant for safe read-only scheduling.",
                    owner_principal_id="platform-admin",
                    lifecycle_state=SkillPackageLifecycleState.APPROVED,
                    safe_documentation_summary={
                        "summary": "Safe operator documentation is available."
                    },
                    latest_published_version="1.0.0",
                    created_by_principal_id="qa052-seed",
                )
            )
        version = session.get(SkillPackageVersion, VERSION_ID)
        if version is None:
            session.add(
                SkillPackageVersion(
                    skill_package_version_id=VERSION_ID,
                    skill_package_id=PACKAGE_ID,
                    slug="qa052-calendar-assistant",
                    semantic_version="1.0.0",
                    manifest_digest="sha256:qa052-calendar-manifest",
                    manifest_snapshot={"slug": "qa052-calendar-assistant"},
                    safe_manifest_summary={
                        "summary": (
                            "QA052 calendar assistant exposes calendar.list "
                            "as a read-only tool."
                        ),
                        "tools": [{"tool_id": "calendar.list"}],
                        "action_categories": ["read"],
                    },
                    artifact_digest="sha256:qa052-calendar-artifact",
                    validation_status="passed",
                    validation_summary={
                        "evidence_reference_id": "validation-qa052-calendar"
                    },
                    lifecycle_state=SkillVersionLifecycleState.PUBLISHED,
                    availability_mode="selected_tenants",
                    published_by_principal_id="qa052-seed",
                    published_at=now,
                )
            )
        grant = session.scalar(
            select(SkillPackageTenantGrant).where(
                SkillPackageTenantGrant.skill_package_version_id == VERSION_ID,
                SkillPackageTenantGrant.tenant_id == ACME_TENANT_ID,
            )
        )
        if grant is None:
            session.add(
                SkillPackageTenantGrant(
                    skill_package_version_id=VERSION_ID,
                    tenant_id=ACME_TENANT_ID,
                    status="active",
                    granted_by_principal_id="qa052-seed",
                    granted_at=now,
                    reason="Read-only calendar tools only.",
                )
            )
        installation = session.get(SkillInstallation, INSTALLATION_ID)
        if installation is None:
            session.add(
                SkillInstallation(
                    skill_installation_id=INSTALLATION_ID,
                    tenant_id=ACME_TENANT_ID,
                    skill_package_version_id=VERSION_ID,
                    slug="qa052-calendar-assistant",
                    semantic_version="1.0.0",
                    installation_version=1,
                    manifest_digest="sha256:qa052-calendar-manifest",
                    manifest_summary={
                        "summary": (
                            "QA052 calendar assistant installation is tenant scoped."
                        ),
                        "tools": [{"tool_id": "calendar.list"}],
                        "action_categories": ["read"],
                        "blocked_tools": ["calendar.write"],
                    },
                    artifact_digest="sha256:qa052-calendar-artifact",
                    readiness_state=SkillInstallationState.READY,
                    credential_status="pending",
                    compatibility_status="ready",
                    permission_status="ready",
                    smoke_test_status="passed",
                    binding_eligibility_status="denied",
                    policy_summary={"blocked_tools": ["calendar.write"]},
                    findings=[
                        {"message": "Credential reference requires confirmation."}
                    ],
                    installed_by_principal_id="tenant-admin-acme",
                    installed_at=now,
                    revision_token=REVISION,
                )
            )
        else:
            installation.credential_status = "pending"
            installation.binding_eligibility_status = "denied"
            installation.revision_token = REVISION
        credential = session.get(SkillInstallationCredential, CREDENTIAL_ID)
        if credential is None:
            session.add(
                SkillInstallationCredential(
                    credential_readiness_id=CREDENTIAL_ID,
                    skill_installation_id=INSTALLATION_ID,
                    tenant_id=ACME_TENANT_ID,
                    requirement_key="calendar-oauth",
                    credential_kind="delegated_credential",
                    secret_reference_id=SECRET_REFERENCE_ID,
                    status="pending",
                    safe_summary={
                        "label": "QA052 Calendar OAuth reference",
                        "policy_reason": (
                            "Reference is authorized for read-only calendar tools."
                        ),
                        "remediation": "Save the reference to mark readiness current.",
                    },
                )
            )
        else:
            credential.status = "pending"
            credential.configured_by_principal_id = None
            credential.configured_at = None
        if session.get(SkillInstallationTest, TEST_ID) is None:
            session.add(
                SkillInstallationTest(
                    skill_installation_test_id=TEST_ID,
                    skill_installation_id=INSTALLATION_ID,
                    tenant_id=ACME_TENANT_ID,
                    skill_package_version_id=VERSION_ID,
                    installation_version=1,
                    fixture_key="calendar.list",
                    test_run_id="qa052-calendar-diagnostic",
                    idempotency_key="qa052-calendar-diagnostic",
                    runner_status=SkillJobStatus.PASSED,
                    outcome="passed",
                    credential_readiness_summary={"status": "pending"},
                    policy_decision_summary={"status": "ready"},
                    safe_output_summary={
                        "summary": "QA052 calendar diagnostic completed safely."
                    },
                    started_at=now,
                    completed_at=now,
                )
            )
        if session.get(SkillAuditRecord, AUDIT_ID) is None:
            session.add(
                SkillAuditRecord(
                    skill_audit_record_id=AUDIT_ID,
                    event_type="skill_installation.created",
                    actor_principal_id="qa052-seed",
                    outcome="ready",
                    tenant_id=ACME_TENANT_ID,
                    skill_package_id=PACKAGE_ID,
                    skill_package_version_id=VERSION_ID,
                    skill_installation_id=INSTALLATION_ID,
                    package_slug="qa052-calendar-assistant",
                    package_version="1.0.0",
                    safe_summary={
                        "summary": "QA052 calendar assistant installation created."
                    },
                    redaction_metadata={"react_contract": "safe_summary_only"},
                    created_at=now,
                )
            )
        session.commit()
    print("Seeded QA052 skill lifecycle records")
    print(f"installation_id={INSTALLATION_ID}")
    print(f"credential_reference_id={SECRET_REFERENCE_ID}")
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
