from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from uuid import UUID, uuid4

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
from multi_agent_platform.db.repositories.skill_registry import SkillRegistryRepository


def valid_skill_manifest() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "slug": "calendar-assistant",
        "semantic_version": "1.2.3",
        "description": "Calendar assistant for safe scheduling operations.",
        "entrypoint": {
            "type": "approved_tool_ref",
            "approved_integration_ref": "tool:calendar:v1",
        },
        "tools": [
            {
                "tool_id": "calendar.list",
                "approved_integration_ref": "tool:calendar:v1",
                "display_name": "List calendars",
                "description": "Lists calendar metadata.",
                "action_categories": ["read"],
                "side_effect_profile": "read_only",
                "safe_usage": "Use for tenant-scoped calendar listing.",
            }
        ],
        "action_categories": ["read"],
        "network_requirements": [
            {
                "tool_id": "calendar.list",
                "action_category": "read",
                "allowed_schemes": ["https"],
                "allowed_domain_patterns": ["calendar.example.com"],
                "allowed_ports": [443],
                "required": True,
                "safe_description": "Calendar API endpoint.",
            }
        ],
        "credential_requirements": [
            {
                "requirement_key": "calendar-oauth",
                "credential_kind": "delegated_credential",
                "tool_id": "calendar.list",
                "action_category": "read",
                "required": True,
                "delegated_credential_scopes": ["calendar.readonly"],
                "safe_description": "Delegated calendar read access.",
            }
        ],
        "runtime_permissions": [
            {
                "permission_key": "calendar-read",
                "permission_type": "tool_access",
                "tool_id": "calendar.list",
                "action_category": "read",
                "side_effect_level": "read_only",
                "required": True,
                "safe_description": "Read calendar metadata.",
            }
        ],
        "test_fixtures": [
            {
                "fixture_key": "list-calendars",
                "tool_id": "calendar.list",
                "action_category": "read",
                "fixture_kind": "policy_preview",
                "safe_input_summary": "Policy-only calendar list probe.",
                "fixture_digest": "sha256:fixture",
                "requires_credentials": True,
                "expected_outcome": "passed",
                "timeout_seconds": 10,
            }
        ],
        "compatibility": {"platform_min_version": "0.1.0"},
        "safe_documentation": {
            "summary": "Safe operator documentation.",
            "documentation_digest": "sha256:docs",
            "redaction_classification": "safe",
            "support_contacts": ["ops@example.com"],
        },
        "artifact_digests": {
            "package": "sha256:artifact",
            "documentation": "sha256:docs",
        },
    }


def invalid_secret_manifest() -> dict[str, object]:
    manifest = deepcopy(valid_skill_manifest())
    manifest["support"] = {"api_token": "sk-thisshouldnotbehere123456"}
    return manifest


def invalid_entrypoint_manifest() -> dict[str, object]:
    manifest = deepcopy(valid_skill_manifest())
    manifest["entrypoint"] = {
        "type": "python",
        "approved_integration_ref": "exec:unsafe",
    }
    return manifest


def seed_live_skill_lifecycle_session(
    session: Session,
    *,
    tenant_id: UUID,
    actor_principal_id: str = "tenant-admin",
) -> dict[str, UUID | str]:
    package_id = uuid4()
    version_id = uuid4()
    installation_id = uuid4()
    credential_id = uuid4()
    secret_reference_id = uuid4()
    test_id = uuid4()
    audit_id = uuid4()
    now = datetime(2026, 5, 7, 15, tzinfo=UTC)
    session.add(
        SkillPackage(
            skill_package_id=package_id,
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Calendar assistant for safe scheduling operations.",
            owner_principal_id="platform-admin",
            lifecycle_state=SkillPackageLifecycleState.APPROVED,
            safe_documentation_summary={
                "summary": "Safe operator documentation is available."
            },
            latest_published_version="1.2.3",
            created_by_principal_id="platform-admin",
        )
    )
    session.add(
        SkillPackageVersion(
            skill_package_version_id=version_id,
            skill_package_id=package_id,
            slug="calendar-assistant",
            semantic_version="1.2.3",
            manifest_digest="sha256:calendar-live-manifest",
            manifest_snapshot={"slug": "calendar-assistant"},
            safe_manifest_summary={
                "summary": "Calendar assistant exposes calendar.list as read-only.",
                "tools": [{"tool_id": "calendar.list"}],
                "action_categories": ["read"],
            },
            artifact_digest="sha256:calendar-live-artifact",
            validation_status="passed",
            validation_summary={"evidence_reference_id": "validation-calendar-live"},
            lifecycle_state=SkillVersionLifecycleState.PUBLISHED,
            availability_mode="selected_tenants",
            published_by_principal_id="platform-admin",
            published_at=now,
        )
    )
    session.add(
        SkillPackageTenantGrant(
            skill_package_version_id=version_id,
            tenant_id=tenant_id,
            status="active",
            granted_by_principal_id="platform-admin",
            granted_at=now,
            reason="Read-only calendar tools only.",
        )
    )
    session.add(
        SkillInstallation(
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            skill_package_version_id=version_id,
            slug="calendar-assistant",
            semantic_version="1.2.3",
            installation_version=1,
            manifest_digest="sha256:calendar-live-manifest",
            manifest_summary={
                "summary": "Calendar assistant installation is tenant scoped.",
                "tools": [{"tool_id": "calendar.list"}],
                "action_categories": ["read"],
                "blocked_tools": ["calendar.write"],
            },
            artifact_digest="sha256:calendar-live-artifact",
            readiness_state=SkillInstallationState.READY,
            credential_status="pending",
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="passed",
            binding_eligibility_status="denied",
            policy_summary={"blocked_tools": ["calendar.write"]},
            findings=[{"message": "Credential reference requires confirmation."}],
            installed_by_principal_id=actor_principal_id,
            installed_at=now,
            revision_token="installation-live-rev-1",
        )
    )
    session.add(
        SkillInstallationCredential(
            credential_readiness_id=credential_id,
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            requirement_key="calendar-oauth",
            credential_kind="delegated_credential",
            secret_reference_id=secret_reference_id,
            status="pending",
            safe_summary={
                "label": "Calendar OAuth reference",
                "policy_reason": (
                    "Reference is authorized for read-only calendar tools."
                ),
                "remediation": "Save the reference to mark readiness current.",
            },
        )
    )
    session.add(
        SkillInstallationTest(
            skill_installation_test_id=test_id,
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            skill_package_version_id=version_id,
            installation_version=1,
            fixture_key="calendar.list",
            test_run_id="calendar-live-diagnostic",
            idempotency_key="calendar-live-diagnostic",
            runner_status=SkillJobStatus.PASSED,
            outcome="passed",
            credential_readiness_summary={"status": "pending"},
            policy_decision_summary={"status": "ready"},
            safe_output_summary={"summary": "Calendar diagnostic completed safely."},
            started_at=now,
            completed_at=now,
        )
    )
    session.add(
        SkillAuditRecord(
            skill_audit_record_id=audit_id,
            event_type="skill_installation.created",
            actor_principal_id=actor_principal_id,
            outcome="ready",
            tenant_id=tenant_id,
            skill_package_id=package_id,
            skill_package_version_id=version_id,
            skill_installation_id=installation_id,
            package_slug="calendar-assistant",
            package_version="1.2.3",
            safe_summary={"summary": "Calendar assistant installation created."},
            redaction_metadata={"react_contract": "safe_summary_only"},
            created_at=now,
        )
    )
    session.commit()
    return {
        "package_id": package_id,
        "version_id": version_id,
        "installation_id": installation_id,
        "credential_id": credential_id,
        "secret_reference_id": secret_reference_id,
        "test_id": test_id,
        "audit_id": audit_id,
        "revision": "installation-live-rev-1",
    }


async def seed_live_skill_lifecycle_repository(
    repository: SkillRegistryRepository,
    *,
    tenant_id: UUID,
    actor_principal_id: str = "tenant-admin",
) -> dict[str, UUID | str]:
    package_id = uuid4()
    version_id = uuid4()
    installation_id = uuid4()
    credential_id = uuid4()
    secret_reference_id = uuid4()
    test_id = uuid4()
    audit_id = uuid4()
    now = datetime(2026, 5, 7, 15, tzinfo=UTC)
    await repository.add_package(
        SkillPackage(
            skill_package_id=package_id,
            slug="calendar-assistant",
            display_name="Calendar Assistant",
            description="Calendar assistant for safe scheduling operations.",
            owner_principal_id="platform-admin",
            lifecycle_state=SkillPackageLifecycleState.APPROVED,
            safe_documentation_summary={
                "summary": "Safe operator documentation is available."
            },
            latest_published_version="1.2.3",
            created_by_principal_id="platform-admin",
        )
    )
    await repository.add_package_version(
        SkillPackageVersion(
            skill_package_version_id=version_id,
            skill_package_id=package_id,
            slug="calendar-assistant",
            semantic_version="1.2.3",
            manifest_digest="sha256:calendar-live-manifest",
            manifest_snapshot={"slug": "calendar-assistant"},
            safe_manifest_summary={
                "summary": "Calendar assistant exposes calendar.list as read-only.",
                "tools": [{"tool_id": "calendar.list"}],
                "action_categories": ["read"],
            },
            artifact_digest="sha256:calendar-live-artifact",
            validation_status="passed",
            validation_summary={"evidence_reference_id": "validation-calendar-live"},
            lifecycle_state=SkillVersionLifecycleState.PUBLISHED,
            availability_mode="selected_tenants",
            published_by_principal_id="platform-admin",
            published_at=now,
        )
    )
    await repository.add_tenant_grant(
        SkillPackageTenantGrant(
            skill_package_version_id=version_id,
            tenant_id=tenant_id,
            status="active",
            granted_by_principal_id="platform-admin",
            granted_at=now,
            reason="Read-only calendar tools only.",
        )
    )
    await repository.add_installation(
        SkillInstallation(
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            skill_package_version_id=version_id,
            slug="calendar-assistant",
            semantic_version="1.2.3",
            installation_version=1,
            manifest_digest="sha256:calendar-live-manifest",
            manifest_summary={
                "summary": "Calendar assistant installation is tenant scoped.",
                "tools": [{"tool_id": "calendar.list"}],
                "action_categories": ["read"],
                "blocked_tools": ["calendar.write"],
            },
            artifact_digest="sha256:calendar-live-artifact",
            readiness_state=SkillInstallationState.READY,
            credential_status="pending",
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="passed",
            binding_eligibility_status="denied",
            policy_summary={"blocked_tools": ["calendar.write"]},
            findings=[{"message": "Credential reference requires confirmation."}],
            installed_by_principal_id=actor_principal_id,
            installed_at=now,
            revision_token="installation-live-rev-1",
        )
    )
    await repository.add_installation_credential(
        SkillInstallationCredential(
            credential_readiness_id=credential_id,
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            requirement_key="calendar-oauth",
            credential_kind="delegated_credential",
            secret_reference_id=secret_reference_id,
            status="pending",
            safe_summary={
                "label": "Calendar OAuth reference",
                "policy_reason": (
                    "Reference is authorized for read-only calendar tools."
                ),
                "remediation": "Save the reference to mark readiness current.",
            },
        )
    )
    await repository.add_installation_test(
        SkillInstallationTest(
            skill_installation_test_id=test_id,
            skill_installation_id=installation_id,
            tenant_id=tenant_id,
            skill_package_version_id=version_id,
            installation_version=1,
            fixture_key="calendar.list",
            test_run_id="calendar-live-diagnostic",
            idempotency_key="calendar-live-diagnostic",
            runner_status=SkillJobStatus.PASSED,
            outcome="passed",
            credential_readiness_summary={"status": "pending"},
            policy_decision_summary={"status": "ready"},
            safe_output_summary={"summary": "Calendar diagnostic completed safely."},
            started_at=now,
            completed_at=now,
        )
    )
    await repository.add_audit_record(
        SkillAuditRecord(
            skill_audit_record_id=audit_id,
            event_type="skill_installation.created",
            actor_principal_id=actor_principal_id,
            outcome="ready",
            tenant_id=tenant_id,
            skill_package_id=package_id,
            skill_package_version_id=version_id,
            skill_installation_id=installation_id,
            package_slug="calendar-assistant",
            package_version="1.2.3",
            safe_summary={"summary": "Calendar assistant installation created."},
            redaction_metadata={"react_contract": "safe_summary_only"},
            created_at=now,
        )
    )
    return {
        "package_id": package_id,
        "version_id": version_id,
        "installation_id": installation_id,
        "credential_id": credential_id,
        "secret_reference_id": secret_reference_id,
        "test_id": test_id,
        "audit_id": audit_id,
        "revision": "installation-live-rev-1",
    }
