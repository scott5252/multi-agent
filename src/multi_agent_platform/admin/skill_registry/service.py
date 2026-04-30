from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from multi_agent_platform.admin.skill_registry.audit import (
    SkillAuditEvent,
    build_lifecycle_audit_event,
)
from multi_agent_platform.admin.skill_registry.eligibility import (
    InstalledSkillEvidence,
    SkillEligibilityDecision,
    evaluate_binding_eligibility,
)
from multi_agent_platform.admin.skill_registry.manifest import SkillManifest
from multi_agent_platform.admin.skill_registry.readiness import (
    CredentialReferenceSummary,
    InstallationReadiness,
    evaluate_installation_readiness,
)
from multi_agent_platform.admin.skill_registry.validation import (
    SkillPackageValidationResult,
    SkillValidationFinding,
    validate_manifest_payload,
)


class SkillRegistryServiceError(RuntimeError):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


@dataclass(slots=True)
class SkillPackageRecord:
    slug: str
    display_name: str
    description: str
    owner_principal_id: str
    lifecycle_state: str = "approved"
    versions: dict[str, SkillPackageVersionRecord] = field(default_factory=dict)


@dataclass(slots=True)
class SkillPackageVersionRecord:
    package_version_id: str
    slug: str
    semantic_version: str
    manifest: SkillManifest
    manifest_digest: str
    artifact_digest: str
    validation_status: str
    lifecycle_state: str = "published"
    availability_mode: str = "selected_tenants"
    tenant_grants: set[str] = field(default_factory=set)
    validation_findings: tuple[SkillValidationFinding, ...] = ()
    runtime_blocked: bool = False
    quarantined: bool = False


@dataclass(slots=True)
class SkillInstallationRecord:
    installation_id: str
    tenant_id: str
    slug: str
    semantic_version: str
    installation_version: int
    manifest_digest: str
    artifact_digest: str
    manifest_summary: dict[str, object]
    revision_token: str
    previous_installation_id: str | None = None
    readiness: InstallationReadiness | None = None
    credentials: list[CredentialReferenceSummary] = field(default_factory=list)
    runtime_blocked: bool = False
    quarantined: bool = False


class SkillRegistryService:
    def __init__(self) -> None:
        self.packages: dict[str, SkillPackageRecord] = {}
        self.installations: dict[str, SkillInstallationRecord] = {}
        self.audit_events: list[SkillAuditEvent] = []

    def create_package(
        self,
        *,
        slug: str,
        display_name: str,
        description: str,
        owner_principal_id: str,
        actor_principal_id: str,
    ) -> SkillPackageRecord:
        if slug in self.packages:
            raise SkillRegistryServiceError("duplicate_package", "package exists")
        package = SkillPackageRecord(
            slug=slug,
            display_name=display_name,
            description=description,
            owner_principal_id=owner_principal_id,
        )
        self.packages[slug] = package
        self._audit(
            "skill_package.created",
            actor_principal_id=actor_principal_id,
            outcome="created",
            package_slug=slug,
            summary={"slug": slug, "display_name": display_name},
        )
        return package

    def validate_candidate(
        self,
        *,
        manifest_payload: dict[str, object],
        approved_integration_refs: set[str] | None = None,
    ) -> SkillPackageValidationResult:
        return validate_manifest_payload(
            manifest_payload,
            approved_integration_refs=approved_integration_refs,
        )

    def publish_version(
        self,
        *,
        slug: str,
        manifest_payload: dict[str, object],
        artifact_digest: str,
        actor_principal_id: str,
        approved_integration_refs: set[str] | None = None,
    ) -> SkillPackageVersionRecord:
        package = self.packages.get(slug)
        if package is None:
            raise SkillRegistryServiceError("not_found", "package not found")
        validation = self.validate_candidate(
            manifest_payload=manifest_payload,
            approved_integration_refs=approved_integration_refs,
        )
        if validation.status != "passed" or validation.manifest_digest is None:
            raise SkillRegistryServiceError("validation_blocked", "validation failed")
        manifest = SkillManifest.model_validate(manifest_payload)
        if manifest.slug != slug:
            raise SkillRegistryServiceError("manifest_mismatch", "slug mismatch")
        if manifest.semantic_version in package.versions:
            raise SkillRegistryServiceError("duplicate_version", "version exists")
        record = SkillPackageVersionRecord(
            package_version_id=str(uuid4()),
            slug=slug,
            semantic_version=manifest.semantic_version,
            manifest=manifest,
            manifest_digest=validation.manifest_digest,
            artifact_digest=artifact_digest,
            validation_status=validation.status,
            validation_findings=validation.findings,
        )
        package.versions[manifest.semantic_version] = record
        self._audit(
            "skill_package_version.published",
            actor_principal_id=actor_principal_id,
            outcome="published",
            package_slug=slug,
            package_version=manifest.semantic_version,
            summary={"manifest_digest": validation.manifest_digest},
        )
        return record

    def grant_tenant_availability(
        self,
        *,
        slug: str,
        semantic_version: str,
        tenant_id: str,
        actor_principal_id: str,
    ) -> None:
        version = self._version(slug, semantic_version)
        version.tenant_grants.add(tenant_id)
        self._audit(
            "skill_package_version.availability_granted",
            actor_principal_id=actor_principal_id,
            outcome="granted",
            tenant_id=tenant_id,
            package_slug=slug,
            package_version=semantic_version,
            summary={"tenant_id": tenant_id},
        )

    def list_available_versions(
        self, *, tenant_id: str
    ) -> list[SkillPackageVersionRecord]:
        visible: list[SkillPackageVersionRecord] = []
        for package in self.packages.values():
            for version in package.versions.values():
                if (
                    not version.quarantined
                    and version.lifecycle_state == "published"
                    and (
                        version.availability_mode == "all_tenants"
                        or tenant_id in version.tenant_grants
                    )
                ):
                    visible.append(version)
        return visible

    def install_version(
        self,
        *,
        tenant_id: str,
        slug: str,
        semantic_version: str,
        actor_principal_id: str,
        previous_installation_id: str | None = None,
    ) -> SkillInstallationRecord:
        version = self._version(slug, semantic_version)
        if version.quarantined or version.runtime_blocked:
            raise SkillRegistryServiceError("quarantined", "package version blocked")
        if (
            version.availability_mode != "all_tenants"
            and tenant_id not in version.tenant_grants
        ):
            self._audit(
                "skill_installation.denied",
                actor_principal_id=actor_principal_id,
                outcome="denied",
                tenant_id=tenant_id,
                package_slug=slug,
                package_version=semantic_version,
                summary={"reason": "tenant_not_granted"},
            )
            raise SkillRegistryServiceError("unauthorized", "tenant not granted")
        installation_version = 1 + max(
            (
                installation.installation_version
                for installation in self.installations.values()
                if installation.tenant_id == tenant_id and installation.slug == slug
            ),
            default=0,
        )
        required_credentials = [
            requirement.requirement_key
            for requirement in version.manifest.credential_requirements
            if requirement.required
        ]
        readiness = evaluate_installation_readiness(
            required_credential_keys=required_credentials,
            configured_credentials=[],
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="not_required"
            if not version.manifest.test_fixtures
            else "pending",
        )
        installation = SkillInstallationRecord(
            installation_id=str(uuid4()),
            tenant_id=tenant_id,
            slug=slug,
            semantic_version=semantic_version,
            installation_version=installation_version,
            manifest_digest=version.manifest_digest,
            artifact_digest=version.artifact_digest,
            manifest_summary={
                "tools": [tool.tool_id for tool in version.manifest.tools],
                "action_categories": list(version.manifest.action_categories),
                "credential_requirements": required_credentials,
            },
            revision_token=str(uuid4()),
            previous_installation_id=previous_installation_id,
            readiness=readiness,
        )
        self.installations[installation.installation_id] = installation
        self._audit(
            "skill_installation.created",
            actor_principal_id=actor_principal_id,
            outcome="installed",
            tenant_id=tenant_id,
            package_slug=slug,
            package_version=semantic_version,
            installation_id=installation.installation_id,
            summary={"installation_version": installation_version},
        )
        return installation

    def configure_credentials(
        self,
        *,
        installation_id: str,
        revision_token: str,
        credentials: list[CredentialReferenceSummary],
    ) -> SkillInstallationRecord:
        installation = self.installations[installation_id]
        self._check_revision(installation, revision_token)
        installation.credentials = credentials
        installation.revision_token = str(uuid4())
        return self.recompute_readiness(installation_id=installation_id)

    def recompute_readiness(self, *, installation_id: str) -> SkillInstallationRecord:
        installation = self.installations[installation_id]
        version = self._version(installation.slug, installation.semantic_version)
        required_credentials = [
            requirement.requirement_key
            for requirement in version.manifest.credential_requirements
            if requirement.required
        ]
        installation.readiness = evaluate_installation_readiness(
            required_credential_keys=required_credentials,
            configured_credentials=installation.credentials,
            compatibility_status="ready",
            permission_status="ready",
            smoke_test_status="not_required"
            if not version.manifest.test_fixtures
            else "passed",
            quarantine_state="quarantined" if installation.quarantined else "clear",
        )
        return installation

    def binding_eligibility(
        self,
        *,
        installation_id: str,
        required_action_categories: set[str] | None = None,
    ) -> SkillEligibilityDecision:
        installation = self.installations[installation_id]
        readiness = installation.readiness
        raw_action_categories = installation.manifest_summary.get(
            "action_categories",
            (),
        )
        action_categories = (
            raw_action_categories
            if isinstance(raw_action_categories, list | tuple | set)
            else ()
        )
        evidence = InstalledSkillEvidence(
            tenant_id=installation.tenant_id,
            installation_id=installation.installation_id,
            installation_version=installation.installation_version,
            package_slug=installation.slug,
            semantic_version=installation.semantic_version,
            manifest_digest=installation.manifest_digest,
            artifact_digest=installation.artifact_digest,
            readiness_state=readiness.readiness_state if readiness else "blocked",
            credential_status=readiness.credential_status if readiness else "blocked",
            compatibility_status=readiness.compatibility_status
            if readiness
            else "blocked",
            permission_status=readiness.permission_status if readiness else "blocked",
            quarantine_state="quarantined" if installation.quarantined else "clear",
            runtime_blocked=installation.runtime_blocked,
            action_categories=tuple(str(item) for item in action_categories),
        )
        return evaluate_binding_eligibility(
            evidence,
            required_action_categories=required_action_categories,
        )

    def quarantine_installation(self, *, installation_id: str) -> None:
        installation = self.installations[installation_id]
        installation.quarantined = True
        installation.runtime_blocked = True
        self.recompute_readiness(installation_id=installation_id)

    def _version(self, slug: str, semantic_version: str) -> SkillPackageVersionRecord:
        package = self.packages.get(slug)
        if package is None or semantic_version not in package.versions:
            raise SkillRegistryServiceError("not_found", "package version not found")
        return package.versions[semantic_version]

    def _check_revision(
        self,
        installation: SkillInstallationRecord,
        expected_revision_token: str,
    ) -> None:
        if installation.revision_token != expected_revision_token:
            self._audit(
                "skill_installation.stale_revision_rejected",
                actor_principal_id="system",
                outcome="rejected",
                tenant_id=installation.tenant_id,
                package_slug=installation.slug,
                package_version=installation.semantic_version,
                installation_id=installation.installation_id,
                summary={"reason": "stale_revision_token"},
            )
            raise SkillRegistryServiceError("stale_revision", "stale revision token")

    def _audit(
        self,
        event_type: str,
        *,
        actor_principal_id: str,
        outcome: str,
        summary: dict[str, object],
        tenant_id: str | None = None,
        package_slug: str | None = None,
        package_version: str | None = None,
        installation_id: str | None = None,
    ) -> None:
        self.audit_events.append(
            build_lifecycle_audit_event(
                event_type=event_type,
                actor_principal_id=actor_principal_id,
                outcome=outcome,
                summary=summary,
                tenant_id=tenant_id,
                package_slug=package_slug,
                package_version=package_version,
                installation_id=installation_id,
            )
        )
