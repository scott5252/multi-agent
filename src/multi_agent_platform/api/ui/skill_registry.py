from __future__ import annotations

from dataclasses import dataclass, field

from multi_agent_platform.admin.skill_registry.service import (
    SkillInstallationRecord,
    SkillPackageRecord,
    SkillPackageVersionRecord,
)


@dataclass(frozen=True, slots=True)
class SkillRegistryPageModel:
    title: str
    scope_label: str
    packages: tuple[dict[str, object], ...] = ()
    versions: tuple[dict[str, object], ...] = ()
    installations: tuple[dict[str, object], ...] = ()
    audit_events: tuple[dict[str, object], ...] = ()
    findings: tuple[dict[str, object], ...] = ()
    redaction_notice: str = (
        "Raw package payloads, secrets, credential values, provider tokens, "
        "unsafe docs, and cross-tenant data are omitted."
    )
    actions: tuple[str, ...] = field(default_factory=tuple)


def build_package_list_page(
    packages: list[SkillPackageRecord],
    *,
    platform_admin: bool,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title="Skill Registry",
        scope_label="platform" if platform_admin else "tenant",
        packages=tuple(
            {
                "slug": package.slug,
                "display_name": package.display_name,
                "lifecycle_state": package.lifecycle_state,
                "latest_published_version": max(package.versions, default=None),
                "version_count": len(package.versions),
            }
            for package in packages
        ),
        actions=("create_package", "publish_version") if platform_admin else (),
    )


def build_package_detail_page(
    package: SkillPackageRecord,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title=f"Skill Package: {package.slug}",
        scope_label="platform",
        packages=(
            {
                "slug": package.slug,
                "display_name": package.display_name,
                "description": package.description,
                "lifecycle_state": package.lifecycle_state,
            },
        ),
        versions=tuple(
            _version_summary(version) for version in package.versions.values()
        ),
        actions=("validate_candidate", "grant_availability", "quarantine"),
    )


def build_version_detail_page(
    version: SkillPackageVersionRecord,
) -> SkillRegistryPageModel:
    findings = tuple(
        {
            "code": finding.code,
            "message": finding.message,
            "severity": finding.severity,
            "blocking": finding.blocking,
        }
        for finding in version.validation_findings
    )
    return SkillRegistryPageModel(
        title=f"{version.slug} {version.semantic_version}",
        scope_label="platform",
        versions=(_version_summary(version),),
        findings=findings,
        actions=("withdraw", "quarantine", "grant_availability"),
    )


def build_installation_list_page(
    installations: list[SkillInstallationRecord],
    *,
    tenant_id: str,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title="Installed Skills",
        scope_label=tenant_id,
        installations=tuple(_installation_summary(item) for item in installations),
        actions=("install", "run_smoke_tests", "promote_readiness"),
    )


def build_installation_detail_page(
    installation: SkillInstallationRecord,
) -> SkillRegistryPageModel:
    return SkillRegistryPageModel(
        title=f"Installed Skill: {installation.slug}",
        scope_label=installation.tenant_id,
        installations=(_installation_summary(installation),),
        findings=tuple(
            {
                "code": finding.code,
                "message": finding.message,
                "blocking": finding.blocking,
            }
            for finding in (
                installation.readiness.findings if installation.readiness else ()
            )
        ),
        actions=("configure_credentials", "run_smoke_tests", "preview_binding"),
    )


def _version_summary(version: SkillPackageVersionRecord) -> dict[str, object]:
    return {
        "package_version_id": version.package_version_id,
        "slug": version.slug,
        "semantic_version": version.semantic_version,
        "manifest_digest": version.manifest_digest,
        "artifact_digest": version.artifact_digest,
        "validation_status": version.validation_status,
        "lifecycle_state": version.lifecycle_state,
        "tenant_grants": sorted(version.tenant_grants),
        "quarantined": version.quarantined,
        "runtime_blocked": version.runtime_blocked,
    }


def _installation_summary(
    installation: SkillInstallationRecord,
) -> dict[str, object]:
    readiness = installation.readiness
    return {
        "installation_id": installation.installation_id,
        "tenant_id": installation.tenant_id,
        "slug": installation.slug,
        "semantic_version": installation.semantic_version,
        "installation_version": installation.installation_version,
        "manifest_digest": installation.manifest_digest,
        "artifact_digest": installation.artifact_digest,
        "revision_token": installation.revision_token,
        "readiness_state": readiness.readiness_state if readiness else "blocked",
        "credential_status": readiness.credential_status if readiness else "blocked",
        "smoke_test_status": readiness.smoke_test_status if readiness else "blocked",
        "binding_eligibility_status": (
            readiness.binding_eligibility_status if readiness else "denied"
        ),
        "quarantined": installation.quarantined,
        "runtime_blocked": installation.runtime_blocked,
    }
