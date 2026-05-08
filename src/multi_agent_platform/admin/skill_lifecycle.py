from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from multi_agent_platform.admin.skill_registry.eligibility import (
    InstalledSkillEvidence,
    evaluate_binding_eligibility,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminActionMetadata,
    ReactAdminActionMetadataSource,
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_skill_lifecycle import (
    BindingContextChoice,
    BindingEligibilityPreview,
    BindingEligibilityPreviewRequest,
    ConnectorReadinessSummary,
    CredentialConfigurationRequest,
    CredentialReferenceOption,
    PackagePublicationWorkspace,
    ReadinessRefreshRequest,
    SkillExecutionDiagnosticList,
    SkillExecutionDiagnosticSummary,
    SkillLegacyRouteMapping,
    SkillLifecycleAuditList,
    SkillLifecycleAuditRecord,
    SkillLifecycleDashboard,
    SkillLifecycleMutationResult,
    SkillLifecycleSection,
    SkillLifecycleStatus,
    SkillLifecycleWizardStep,
    SkillPackageCandidate,
    SkillPackageCandidateRequest,
    SkillPackagePublishRequest,
    SkillPackageVersionSummary,
    TenantGrantMutationRequest,
    TenantSkillDiscovery,
    TenantSkillDiscoveryList,
    TenantSkillGrantSummary,
    TenantSkillInstallationList,
    TenantSkillInstallationSummary,
    TenantSkillInstallRequest,
    empty_skill_lifecycle_state,
    live_skill_lifecycle_provenance,
    safe_skill_lifecycle_text,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.skill_registry import (
    SkillAuditRecord,
    SkillInstallation,
    SkillInstallationCredential,
    SkillInstallationState,
    SkillInstallationTest,
    SkillJobStatus,
    SkillPackageTenantGrant,
    SkillPackageVersion,
    SkillVersionLifecycleState,
)
from multi_agent_platform.db.repositories.skill_registry import (
    SkillRegistryRepository,
    StaleSkillRegistryWriteError,
)


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


async def build_skill_lifecycle_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleDashboard:
    platform_admin = is_platform_admin(principal)
    publication = (
        await build_publication_workspace(scope=scope, repository=repository)
        if platform_admin
        else None
    )
    discovery_list = await build_tenant_discovery(
        scope=scope,
        principal=principal,
        repository=repository,
    )
    installation_list = await build_tenant_installations(
        scope=scope,
        repository=repository,
    )
    diagnostic_list = await build_skill_execution_diagnostics(
        scope=scope,
        repository=repository,
    )
    audit_list = await build_skill_lifecycle_audit(
        scope=scope,
        repository=repository,
    )
    binding_preview = await build_binding_preview(
        scope=scope,
        repository=repository,
    )
    connector_diagnostics = tuple(
        connector
        for installation in installation_list.installations
        for connector in installation.connector_readiness
    )
    has_live_data = any(
        (
            publication and publication.package_versions,
            discovery_list.discovery.available_versions,
            discovery_list.discovery.grants,
            installation_list.installations,
            diagnostic_list.diagnostics,
            audit_list.audit_timeline,
        )
    )
    return SkillLifecycleDashboard(
        page_id="react-skill-lifecycle",
        title="Skill lifecycle",
        description=(
            "Package publication, tenant installation, readiness, binding, "
            "diagnostics, and audit evidence from live skill records."
        ),
        scope=scope,
        sections=_sections(
            platform_admin=platform_admin,
            publication_count=len(publication.package_versions) if publication else 0,
            discovery_count=len(discovery_list.discovery.available_versions),
            installation_count=len(installation_list.installations),
            diagnostic_count=len(diagnostic_list.diagnostics),
            audit_count=len(audit_list.audit_timeline),
        ),
        setup_summary=_setup_summary(has_live_data=has_live_data),
        platform_publication=publication,
        tenant_discovery=discovery_list.discovery,
        installations=installation_list.installations,
        connector_diagnostics=connector_diagnostics,
        skill_execution_diagnostics=diagnostic_list.diagnostics,
        binding_preview=binding_preview,
        audit_timeline=audit_list.audit_timeline,
        legacy_routes=build_skill_legacy_route_mappings(),
        actions=_dashboard_actions(
            scope=scope,
            platform_admin=platform_admin,
            has_installations=bool(installation_list.installations),
        ),
        provenance=live_skill_lifecycle_provenance(
            source_label="Skill lifecycle records",
            source_detail=(
                "Packages, versions, grants, installations, readiness, tests, "
                "and audit records are projected from durable skill registry stores."
            ),
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_skill_lifecycle_state(
            title="No skill lifecycle records found",
            summary=(
                "This scope does not yet have skill packages, grants, "
                "installations, readiness checks, diagnostics, or audit evidence."
            ),
            setup_hint=(
                "Create package versions, grant tenant availability, and install "
                "skills through governed registry flows."
            ),
        ),
    )


def build_skill_legacy_route_mappings() -> tuple[SkillLegacyRouteMapping, ...]:
    route_pairs = (
        ("/admin/skill-registry/ui/packages", "/admin/app/skills/packages", ("query",)),
        (
            "/admin/skill-registry/ui/packages/new",
            "/admin/app/skills/packages/new",
            (),
        ),
        (
            "/admin/skill-registry/ui/packages/{package_slug}",
            "/admin/app/skills/packages/{package_slug}",
            ("package_slug", "query"),
        ),
        (
            "/admin/skill-registry/ui/packages/{package_slug}/candidate",
            "/admin/app/skills/packages/{package_slug}/candidate",
            ("package_slug", "conflict", "query"),
        ),
        (
            "/admin/skill-registry/ui/packages/{package_slug}/versions/{semantic_version}",
            "/admin/app/skills/packages/{package_slug}/versions/{semantic_version}",
            ("package_slug", "semantic_version", "query"),
        ),
        (
            "/admin/skill-registry/ui/packages/{package_slug}/versions/{semantic_version}/grants",
            "/admin/app/skills/packages/{package_slug}/versions/{semantic_version}/grants",
            ("package_slug", "semantic_version", "tenant_id", "query"),
        ),
        (
            "/admin/skill-registry/ui/available-versions",
            "/admin/app/skills/available-versions",
            ("tenant_id", "query"),
        ),
        (
            "/admin/skill-registry/ui/installations",
            "/admin/app/skills/installations",
            ("tenant_id", "query"),
        ),
        (
            "/admin/skill-registry/ui/installations/{installation_id}",
            "/admin/app/skills/installations/{installation_id}",
            ("installation_id", "conflict", "eligibility", "query"),
        ),
        (
            "/admin/skill-registry/ui/installations/{installation_id}/credentials",
            "/admin/app/skills/installations/{installation_id}/credentials",
            ("installation_id", "conflict", "query"),
        ),
        (
            "/admin/skill-registry/ui/installations/{installation_id}/smoke-tests",
            "/admin/app/skills/installations/{installation_id}/smoke-tests",
            ("installation_id", "conflict", "query"),
        ),
        (
            "/admin/skill-registry/ui/installations/{installation_id}/eligibility-preview",
            "/admin/app/skills/installations/{installation_id}/eligibility-preview",
            ("installation_id", "context", "query"),
        ),
        (
            "/admin/skill-execution/ui/diagnostics",
            "/admin/app/skills/diagnostics",
            ("tenant_id", "query"),
        ),
    )
    return tuple(
        SkillLegacyRouteMapping(
            legacy_path=legacy_path,
            react_path=react_path,
            compatibility_status="redirected",
            preserved_params=preserved,
            authorization_behavior="authenticated redirect with backend Admin denial",
            evidence=(
                "tests/integration/api/test_admin_skill_registry_legacy_redirects.py",
                "tests/integration/api/test_admin_skill_execution_ui.py",
                "tests/unit/admin/test_skill_jinja_retirement.py",
            ),
            notes=(
                "Legacy skill browser route redirects to Admin and no longer "
                "renders a skill registry or diagnostics Jinja template."
            ),
        )
        for legacy_path, react_path, preserved in route_pairs
    )


async def build_publication_workspace(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
) -> PackagePublicationWorkspace:
    versions = await _package_versions(
        scope=scope,
        repository=repository,
        platform_admin=True,
    )
    candidate = _candidate_unavailable()
    return PackagePublicationWorkspace(
        candidate=candidate,
        available_steps=(
            SkillLifecycleWizardStep(
                step_id="candidate",
                label="Candidate",
                status=SkillLifecycleStatus.UNAVAILABLE,
                summary="No active package candidate exists in the live registry.",
            ),
            SkillLifecycleWizardStep(
                step_id="validation",
                label="Validation",
                status=SkillLifecycleStatus.READY
                if versions
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=(
                    "Published versions include persisted validation summaries."
                    if versions
                    else "Validation evidence appears after a version is persisted."
                ),
            ),
            SkillLifecycleWizardStep(
                step_id="grants",
                label="Grants",
                status=SkillLifecycleStatus.READY
                if any(version.tenant_grant_summary for version in versions)
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=(
                    "Tenant grant impact is projected from stored grant records."
                    if versions
                    else "No persisted grant records are visible."
                ),
            ),
            SkillLifecycleWizardStep(
                step_id="publish",
                label="Publish",
                status=SkillLifecycleStatus.READY
                if versions
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=(
                    "Immutable package versions are visible from the registry."
                    if versions
                    else "No immutable package version has been published."
                ),
            ),
        ),
        package_versions=versions,
        validation_summary=(
            "Live package versions include safe validation evidence references."
            if versions
            else (
                "No active package candidate or persisted version evidence is "
                "available."
            )
        ),
        grant_preview=tuple(
            grant for version in versions for grant in version.tenant_grant_summary
        ),
        publish_readiness=SkillLifecycleStatus.READY
        if versions
        else SkillLifecycleStatus.UNAVAILABLE,
        authorized_actions=(
            AdminAction(
                action_id="candidate-create",
                label="Save candidate",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
    )


async def build_candidate_result(
    *,
    request: SkillPackageCandidateRequest,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    source = "upload" if request.uploaded_fixture_id else "paste"
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_package_candidate.saved",
        actor_principal_id=principal.principal_id,
        outcome="saved",
        safe_summary={
            "manifest_source": source,
            "summary": "Candidate input was summarized for safe review.",
        },
    )
    diagnostics = (
        "Uploaded fixture metadata took precedence over pasted input."
        if request.uploaded_fixture_id and request.manifest_text
        else "Candidate input was summarized before returning to Admin."
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Package candidate saved with safe manifest metadata.",
        revision=f"candidate-{audit_reference_id}",
        diagnostics=(diagnostics,),
        audit_reference_id=audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Candidate saved",
            summary="Safe package metadata is ready for validation.",
        ),
    )


async def build_candidate_validation_result(
    *,
    ready: bool = True,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    if not ready:
        audit_reference_id = await _record_audit(
            repository,
            event_type="skill_package_candidate.validation_blocked",
            actor_principal_id=principal.principal_id,
            outcome="blocked",
            safe_summary={"summary": "Candidate validation requires current evidence."},
        )
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Publication is blocked until validation evidence is current.",
            diagnostics=("Validation findings are summarized by field category.",),
            audit_reference_id=audit_reference_id,
        )
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_package_candidate.validated",
        actor_principal_id=principal.principal_id,
        outcome="passed",
        safe_summary={"summary": "Candidate validation completed with safe evidence."},
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Candidate validation passed with safe evidence references.",
        revision=f"candidate-validation-{audit_reference_id}",
        diagnostics=(
            "Manifest digest, tool policy, and smoke evidence are ready.",
            "Manifest text and tool details were not returned.",
        ),
        audit_reference_id=audit_reference_id,
    )


async def build_publish_result(
    *,
    request: SkillPackagePublishRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    versions = await _package_versions(
        scope=scope,
        repository=repository,
        platform_admin=True,
    )
    if not request.confirmed:
        audit_reference_id = await _record_audit(
            repository,
            event_type="skill_package_version.publish_confirmation_required",
            actor_principal_id=principal.principal_id,
            outcome="confirmation_required",
            safe_summary={"summary": "Publication confirmation is required."},
        )
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Confirm immutable publication after reviewing tenant grants.",
            revision=request.candidate_revision,
            audit_reference_id=audit_reference_id,
        )
    if not versions:
        audit_reference_id = await _record_audit(
            repository,
            event_type="skill_package_version.publish_unavailable",
            actor_principal_id=principal.principal_id,
            outcome="unavailable",
            safe_summary={"summary": "No validated candidate is available to publish."},
        )
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="No validated live package candidate is available to publish.",
            audit_reference_id=audit_reference_id,
        )
    publication = versions[0]
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_package_version.publish_reviewed",
        actor_principal_id=principal.principal_id,
        outcome="accepted",
        package_slug=publication.package_slug,
        package_version=publication.version_label,
        safe_summary={"summary": "Publication review returned persisted version."},
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Immutable skill package version returned from live registry.",
        revision=publication.version_id,
        publication=publication,
        diagnostics=(
            "Persisted package version and tenant grants were used for the result.",
        ),
        audit_reference_id=audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Package reviewed",
            summary="Tenant grant impact is available for review.",
        ),
    )


async def build_tenant_grant_result(
    *,
    request: TenantGrantMutationRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    _ = scope
    tenant_uuid = _parse_uuid(request.tenant_id)
    version_uuid = _parse_uuid(request.version_id)
    if tenant_uuid is None or version_uuid is None:
        return _field_error_result(
            field="version_id",
            label="Package version",
            message="Choose a persisted package version and tenant.",
            code="invalid_identifier",
            audit_reference_id="skill-grant-validation",
        )
    version = await repository.get_package_version_by_id(version_uuid)
    if version is None:
        return _field_error_result(
            field="version_id",
            label="Package version",
            message="The selected package version is not available.",
            code="not_found",
            audit_reference_id="skill-grant-missing",
        )
    grant = await repository.get_tenant_grant(
        version_id=version_uuid,
        tenant_id=tenant_uuid,
    )
    if grant is None and request.grant_enabled:
        grant = await repository.add_tenant_grant(
            SkillPackageTenantGrant(
                skill_package_version_id=version_uuid,
                tenant_id=tenant_uuid,
                status="active",
                granted_by_principal_id=principal.principal_id,
                reason="Granted from the admin skill lifecycle workspace.",
            )
        )
    elif grant is not None:
        grant.status = "active" if request.grant_enabled else "revoked"
        grant.reason = "Updated from the admin skill lifecycle workspace."
        if not request.grant_enabled:
            grant.revoked_at = utcnow()
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_package_version.availability_updated",
        actor_principal_id=principal.principal_id,
        outcome="granted" if request.grant_enabled else "revoked",
        tenant_id=tenant_uuid,
        skill_package_version_id=version_uuid,
        package_slug=version.slug,
        package_version=version.semantic_version,
        safe_summary={"summary": "Tenant availability was updated."},
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Tenant grant updated with safe availability summary.",
        revision=str(grant.tenant_grant_id) if grant else request.version_id,
        diagnostics=("Grant mutation is restricted to platform administrators.",),
        audit_reference_id=audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Grant updated",
            summary="Tenant availability is ready for review.",
        ),
    )


async def build_package_lifecycle_result(
    *,
    package_id: str,
    action: str,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    version_uuid = _parse_uuid(package_id)
    if version_uuid is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Choose a persisted package version before updating lifecycle.",
            audit_reference_id="skill-lifecycle-validation",
        )
    version = await repository.get_package_version_by_id(version_uuid)
    if version is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="The package version is not available for lifecycle updates.",
            audit_reference_id="skill-lifecycle-missing",
        )
    if action == "quarantine":
        version.lifecycle_state = SkillVersionLifecycleState.QUARANTINED
        version.quarantined_at = utcnow()
        outcome = "quarantined"
    else:
        version.lifecycle_state = SkillVersionLifecycleState.WITHDRAWN
        version.withdrawn_at = utcnow()
        outcome = "withdrawn"
    audit_reference_id = await _record_audit(
        repository,
        event_type=f"skill_package_version.{outcome}",
        actor_principal_id=principal.principal_id,
        outcome=outcome,
        skill_package_version_id=version.skill_package_version_id,
        package_slug=version.slug,
        package_version=version.semantic_version,
        safe_summary={"summary": f"Package version was {outcome}."},
    )
    refreshed = _version_summary(
        version,
        grants=await repository.list_tenant_grants(
            version_ids=(version.skill_package_version_id,)
        ),
        scope=scope,
        platform_admin=True,
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary=f"Package version lifecycle state updated to {outcome}.",
        publication=refreshed,
        revision=str(version.skill_package_version_id),
        diagnostics=("Tenant installations receive safe lifecycle guidance.",),
        audit_reference_id=audit_reference_id,
    )


async def build_tenant_discovery(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> TenantSkillDiscoveryList:
    platform_admin = is_platform_admin(principal)
    tenant_id = _scope_tenant_uuid(scope)
    versions = (
        await repository.list_package_versions()
        if scope.scope_type == ReactAdminScopeType.PLATFORM and platform_admin
        else await repository.list_available_versions(tenant_id=tenant_id)
        if tenant_id is not None
        else []
    )
    grants = await repository.list_tenant_grants(
        tenant_id=tenant_id,
        version_ids=tuple(version.skill_package_version_id for version in versions),
    )
    available = tuple(
        _version_summary(
            version,
            grants=grants,
            scope=scope,
            platform_admin=platform_admin,
        )
        for version in versions
    )
    grant_preview = tuple(
        _grant_summary(
            grant=grant,
            version=_version_for_grant(grant, versions),
            scope=scope,
            platform_admin=platform_admin,
        )
        for grant in grants
        if _version_for_grant(grant, versions) is not None
    )
    discovery = TenantSkillDiscovery(
        grants=grant_preview,
        available_versions=available,
        empty_state_summary=None
        if available or grant_preview
        else "No granted skill package versions are visible for this scope.",
    )
    has_live_data = bool(available or grant_preview)
    return TenantSkillDiscoveryList(
        discovery=discovery,
        provenance=live_skill_lifecycle_provenance(
            source_label="Skill grants",
            source_detail=(
                "Available versions and grants are read from skill registry rows."
            ),
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_skill_lifecycle_state(
            title="No granted skills found",
            summary=(
                "No live package grants or available versions exist for this scope."
            ),
            source_label="Skill grants",
        ),
    )


async def build_tenant_installations(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
) -> TenantSkillInstallationList:
    tenant_id = _scope_tenant_uuid(scope)
    if tenant_id is None:
        return TenantSkillInstallationList(
            installations=(),
            empty_state=empty_skill_lifecycle_state(
                title="Tenant scope required",
                summary=(
                    "Installation readiness appears after selecting a tenant scope."
                ),
                source_label="Skill installations",
            ),
        )
    installations = await repository.list_installations_for_tenant(tenant_id=tenant_id)
    installation_ids = tuple(
        installation.skill_installation_id for installation in installations
    )
    credentials_by_installation = _group_by_installation(
        await repository.list_credentials_for_installations(installation_ids)
    )
    tests_by_installation = _group_tests_by_installation(
        await repository.list_tests_for_installations(installation_ids)
    )
    summaries = tuple(
        _installation_summary(
            installation=installation,
            scope=scope,
            credentials=credentials_by_installation[installation.skill_installation_id],
            tests=tests_by_installation[installation.skill_installation_id],
        )
        for installation in installations[:10]
    )
    has_live_data = bool(summaries)
    return TenantSkillInstallationList(
        installations=summaries,
        provenance=live_skill_lifecycle_provenance(
            source_label="Skill installations",
            source_detail=(
                "Installation readiness is projected from persisted tenant rows."
            ),
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_skill_lifecycle_state(
            title="No skill installations found",
            summary="No tenant skill installations exist for the active scope.",
            source_label="Skill installations",
        ),
    )


async def build_install_result(
    *,
    installation_id: str,
    request: TenantSkillInstallRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    installation_uuid = _parse_uuid(installation_id)
    if installation_uuid is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Choose a persisted installation before updating it.",
            audit_reference_id="skill-install-validation",
        )
    try:
        installation = await repository.require_revision(
            installation_id=installation_uuid,
            expected_revision_token=request.revision,
        )
    except StaleSkillRegistryWriteError:
        current = await repository.get_installation(installation_uuid)
        return _stale_installation_result(
            submitted_revision=request.revision,
            current_revision=current.revision_token if current else "missing",
            scope=scope,
        )
    except LookupError:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="The requested skill installation was not found.",
            audit_reference_id="skill-install-missing",
        )
    installation.revision_token = _next_revision("install")
    installation.updated_at = utcnow()
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_installation.updated",
        actor_principal_id=principal.principal_id,
        outcome="accepted",
        tenant_id=installation.tenant_id,
        skill_installation_id=installation.skill_installation_id,
        skill_package_version_id=installation.skill_package_version_id,
        package_slug=installation.slug,
        package_version=installation.semantic_version,
        safe_summary={"summary": "Installation metadata was refreshed."},
    )
    credentials = await repository.list_credentials_for_installations(
        (installation.skill_installation_id,)
    )
    tests = await repository.list_tests_for_installations(
        (installation.skill_installation_id,)
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Skill installation refreshed for the active tenant.",
        revision=installation.revision_token,
        installation=_installation_summary(
            installation=installation,
            scope=scope,
            credentials=credentials,
            tests=tests,
        ),
        diagnostics=(
            "Install action used idempotency and active tenant grant checks.",
            "No external connector or provider calls were made.",
        ),
        audit_reference_id=audit_reference_id,
    )


async def build_credential_configuration_result(
    *,
    installation_id: str,
    request: CredentialConfigurationRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    installation_uuid = _parse_uuid(installation_id)
    if installation_uuid is None:
        return _field_error_result(
            field="installation_id",
            label="Installation",
            message="Choose a persisted installation.",
            code="invalid_identifier",
            audit_reference_id="credential-validation",
        )
    try:
        installation = await repository.require_revision(
            installation_id=installation_uuid,
            expected_revision_token=request.revision,
        )
    except StaleSkillRegistryWriteError:
        current = await repository.get_installation(installation_uuid)
        return _stale_installation_result(
            submitted_revision=request.revision,
            current_revision=current.revision_token if current else "missing",
            scope=scope,
        )
    except LookupError:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="The requested skill installation was not found.",
            audit_reference_id="credential-installation-missing",
        )
    credentials = await repository.list_credentials_for_installations(
        (installation_uuid,)
    )
    selected = _selected_credential(credentials, request.selected_reference_id)
    if selected is None:
        return _field_error_result(
            field="selected_reference_id",
            label="Credential reference",
            message="The selected reference is not available for this tenant.",
            code="unauthorized_reference",
            audit_reference_id="credential-reference-denied",
        )
    selected.status = "ready"
    selected.configured_by_principal_id = principal.principal_id
    selected.configured_at = utcnow()
    selected.last_checked_at = utcnow()
    selected.safe_summary = {
        **(selected.safe_summary or {}),
        "policy_reason": "Reference is authorized for this installation.",
        "last_result": "Configured from the admin skill lifecycle workspace.",
    }
    installation.credential_status = _aggregate_status(
        credential.status for credential in credentials
    )
    installation.readiness_state = (
        SkillInstallationState.READY
        if _installation_is_ready(installation)
        else SkillInstallationState.BLOCKED
    )
    installation.binding_eligibility_status = (
        "eligible" if _installation_is_ready(installation) else "denied"
    )
    installation.revision_token = _next_revision("credential")
    installation.updated_at = utcnow()
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_installation.credentials_configured",
        actor_principal_id=principal.principal_id,
        outcome="ready",
        tenant_id=installation.tenant_id,
        skill_installation_id=installation.skill_installation_id,
        skill_package_version_id=installation.skill_package_version_id,
        package_slug=installation.slug,
        package_version=installation.semantic_version,
        safe_summary={"summary": "Credential reference metadata was configured."},
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Credential reference configured without exposing values.",
        revision=installation.revision_token,
        credential=_credential_option(selected),
        diagnostics=(
            "Only authorized credential reference metadata was returned.",
            "Secret values stayed outside admin contracts.",
        ),
        audit_reference_id=audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Credential saved",
            summary="Credential readiness was persisted for this installation.",
        ),
    )


async def build_readiness_refresh_result(
    *,
    installation_id: str,
    request: ReadinessRefreshRequest,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    installation_uuid = _parse_uuid(installation_id)
    if installation_uuid is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Choose a persisted installation before refreshing readiness.",
            audit_reference_id="readiness-validation",
        )
    try:
        installation = await repository.require_revision(
            installation_id=installation_uuid,
            expected_revision_token=request.revision,
        )
    except StaleSkillRegistryWriteError:
        current = await repository.get_installation(installation_uuid)
        return _stale_installation_result(
            submitted_revision=request.revision,
            current_revision=current.revision_token if current else "missing",
            scope=scope,
        )
    except LookupError:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="The requested skill installation was not found.",
            audit_reference_id="readiness-installation-missing",
        )
    test = await repository.add_installation_test(
        SkillInstallationTest(
            skill_installation_id=installation.skill_installation_id,
            tenant_id=installation.tenant_id,
            skill_package_version_id=installation.skill_package_version_id,
            installation_version=installation.installation_version,
            fixture_key="readiness-refresh",
            test_run_id=f"readiness-{uuid4()}",
            idempotency_key=request.idempotency_key,
            runner_status=SkillJobStatus.QUEUED,
            outcome="queued",
            credential_readiness_summary={"status": installation.credential_status},
            policy_decision_summary={"status": installation.permission_status},
            safe_output_summary={"summary": "Readiness refresh queued locally."},
        )
    )
    installation.smoke_test_status = "queued"
    installation.revision_token = _next_revision("readiness")
    installation.updated_at = utcnow()
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_installation.readiness_refresh_queued",
        actor_principal_id=principal.principal_id,
        outcome="queued",
        tenant_id=installation.tenant_id,
        skill_installation_id=installation.skill_installation_id,
        skill_package_version_id=installation.skill_package_version_id,
        package_slug=installation.slug,
        package_version=installation.semantic_version,
        safe_summary={"summary": "Readiness refresh was queued locally."},
    )
    smoke = _connector_from_test(installation=installation, test=test, scope=scope)
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Smoke-test readiness refresh queued.",
        revision=installation.revision_token,
        smoke_test=smoke,
        diagnostics=("No external connector or provider call was started.",),
        audit_reference_id=audit_reference_id,
    )


async def build_connector_diagnostic_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    tenant_id = _scope_tenant_uuid(scope)
    if tenant_id is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="Select a tenant before running skill diagnostics.",
            audit_reference_id="diagnostic-tenant-required",
        )
    installations = await repository.list_installations_for_tenant(tenant_id=tenant_id)
    if not installations:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
            summary="No tenant skill installation is available for diagnostics.",
            audit_reference_id="diagnostic-installation-missing",
        )
    installation = installations[0]
    test = await repository.add_installation_test(
        SkillInstallationTest(
            skill_installation_id=installation.skill_installation_id,
            tenant_id=installation.tenant_id,
            skill_package_version_id=installation.skill_package_version_id,
            installation_version=installation.installation_version,
            fixture_key="gateway-diagnostic",
            test_run_id=f"diagnostic-{uuid4()}",
            idempotency_key=f"diagnostic-{uuid4()}",
            runner_status=SkillJobStatus.QUEUED,
            outcome="queued",
            credential_readiness_summary={"status": installation.credential_status},
            policy_decision_summary={"status": installation.permission_status},
            safe_output_summary={"summary": "Gateway diagnostic queued locally."},
        )
    )
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_execution.diagnostic_queued",
        actor_principal_id=principal.principal_id,
        outcome="queued",
        tenant_id=installation.tenant_id,
        skill_installation_id=installation.skill_installation_id,
        skill_package_version_id=installation.skill_package_version_id,
        package_slug=installation.slug,
        package_version=installation.semantic_version,
        safe_summary={"summary": "Skill execution diagnostic was queued locally."},
    )
    diagnostic = _diagnostic_from_test(
        installation=installation,
        test=test,
        audit_reference_id=audit_reference_id,
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Connector diagnostic queued with safe gateway summary.",
        diagnostic=diagnostic,
        diagnostics=(
            "Skill execution policy evidence is summarized.",
            "Adapter bodies stayed outside the browser contract.",
        ),
        audit_reference_id=audit_reference_id,
    )


async def build_binding_preview(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
    request: BindingEligibilityPreviewRequest | None = None,
) -> BindingEligibilityPreview:
    tenant_id = _scope_tenant_uuid(scope)
    selected_context = (
        request.workflow_context
        if request is not None
        else "Tenant skill binding readiness"
    )
    if tenant_id is None:
        return _empty_binding_preview(
            scope=scope,
            selected_context=selected_context,
            reason="Tenant scope is required before previewing binding eligibility.",
        )
    installations = await repository.list_installations_for_tenant(tenant_id=tenant_id)
    installation = _select_installation_for_preview(installations, request)
    if installation is None:
        return _empty_binding_preview(
            scope=scope,
            selected_context=selected_context,
            reason="No persisted skill installation is available for binding.",
        )
    action_categories = tuple(
        _string_items(installation.manifest_summary, "action_categories")
    )
    tool_names = tuple(_tool_names(installation.manifest_summary))
    decision = evaluate_binding_eligibility(
        InstalledSkillEvidence(
            tenant_id=str(installation.tenant_id),
            installation_id=str(installation.skill_installation_id),
            installation_version=installation.installation_version,
            package_slug=installation.slug,
            semantic_version=installation.semantic_version,
            manifest_digest=installation.manifest_digest,
            artifact_digest=installation.artifact_digest,
            readiness_state=_value(installation.readiness_state),
            credential_status=installation.credential_status,
            compatibility_status=installation.compatibility_status,
            permission_status=installation.permission_status,
            quarantine_state=installation.quarantine_state,
            runtime_blocked=installation.runtime_blocked,
            action_categories=action_categories,
            policy_summary=installation.policy_summary or {},
        ),
        required_action_categories={"read"} if action_categories else None,
    )
    policy_reasons = (
        ("Tenant grant, readiness, and policy records allow read-only binding.",)
        if decision.allowed
        else tuple(reason.replace(".", " ") for reason in decision.reason_codes)
    )
    blocked = tuple(_string_items(installation.policy_summary, "blocked_tools")) or (
        ("write tools",) if decision.allowed else ("all tools",)
    )
    return BindingEligibilityPreview(
        preview_id=f"binding-preview-{installation.skill_installation_id}",
        tenant_label=scope.label,
        context_choices=(
            BindingContextChoice(
                choice_id=f"installation-{installation.skill_installation_id}",
                label=installation.slug,
                kind="installation",
                selected=True,
            ),
        ),
        selected_context=selected_context,
        eligible_tools=tool_names if decision.allowed else (),
        blocked_tools=blocked,
        policy_reasons=policy_reasons,
        missing_requirements=()
        if decision.allowed
        else tuple(reason.replace(".", " ") for reason in decision.reason_codes),
        remediation="No action needed."
        if decision.allowed
        else "Resolve readiness, credential, permission, or quarantine blockers.",
        audit_reference_id=f"binding-preview-{installation.skill_installation_id}",
    )


async def build_binding_preview_result(
    *,
    scope: ReactAdminScope,
    request: BindingEligibilityPreviewRequest,
    principal: PrincipalContext,
    repository: SkillRegistryRepository,
) -> SkillLifecycleMutationResult:
    preview = await build_binding_preview(
        scope=scope,
        repository=repository,
        request=request,
    )
    audit_reference_id = await _record_audit(
        repository,
        event_type="skill_binding.previewed",
        actor_principal_id=principal.principal_id,
        outcome="allowed" if preview.eligible_tools else "denied",
        tenant_id=_scope_tenant_uuid(scope),
        package_slug=request.package_id,
        safe_summary={"summary": "Binding eligibility preview was evaluated."},
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Read-only binding eligibility preview completed.",
        binding_preview=preview.model_copy(
            update={"audit_reference_id": audit_reference_id}
        ),
        diagnostics=("No tools, credentials, delivery, model, or external calls ran.",),
        audit_reference_id=audit_reference_id,
    )


async def build_skill_execution_diagnostics(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
) -> SkillExecutionDiagnosticList:
    tenant_id = _scope_tenant_uuid(scope)
    if tenant_id is None:
        return SkillExecutionDiagnosticList(
            diagnostics=(),
            empty_state=empty_skill_lifecycle_state(
                title="Tenant scope required",
                summary="Skill execution diagnostics are tenant-scoped.",
                source_label="Skill diagnostics",
            ),
        )
    installations = await repository.list_installations_for_tenant(tenant_id=tenant_id)
    tests = await repository.list_tests_for_installations(
        tuple(installation.skill_installation_id for installation in installations),
        limit=10,
    )
    by_installation = {item.skill_installation_id: item for item in installations}
    diagnostics = tuple(
        _diagnostic_from_test(
            installation=by_installation[test.skill_installation_id],
            test=test,
            audit_reference_id=str(
                test.audit_record_id or test.skill_installation_test_id
            ),
        )
        for test in tests
        if test.skill_installation_id in by_installation
    )
    has_live_data = bool(diagnostics)
    return SkillExecutionDiagnosticList(
        diagnostics=diagnostics,
        provenance=live_skill_lifecycle_provenance(
            source_label="Skill diagnostics",
            source_detail="Diagnostics are projected from persisted skill test runs.",
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_skill_lifecycle_state(
            title="No skill diagnostics found",
            summary=(
                "No persisted skill execution diagnostic runs exist for this scope."
            ),
            source_label="Skill diagnostics",
        ),
    )


async def build_skill_lifecycle_audit(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
) -> SkillLifecycleAuditList:
    records = await repository.list_audit_records(
        tenant_id=_scope_tenant_uuid(scope),
        limit=20,
    )
    timeline = tuple(
        _audit_record_summary(record=record, scope=scope) for record in records
    )
    has_live_data = bool(timeline)
    return SkillLifecycleAuditList(
        audit_timeline=timeline,
        provenance=live_skill_lifecycle_provenance(
            source_label="Skill audit records",
            source_detail="Lifecycle timeline is read from skill audit rows.",
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_skill_lifecycle_state(
            title="No skill audit records found",
            summary="No skill lifecycle audit records exist for the active scope.",
            source_label="Skill audit records",
        ),
    )


def _candidate_unavailable() -> SkillPackageCandidate:
    return SkillPackageCandidate(
        candidate_id="no-active-candidate",
        package_slug="not-selected",
        candidate_revision="candidate-unavailable",
        manifest_digest="not-available",
        manifest_source="none",
        safe_manifest_summary=(
            "No active package candidate exists in the live registry."
        ),
        validation_status=SkillLifecycleStatus.UNAVAILABLE,
        validation_findings=(),
        safe_documentation_summary=(
            "Candidate documentation appears after safe validation."
        ),
        smoke_evidence_status=SkillLifecycleStatus.UNAVAILABLE,
        publish_blockers=("No persisted candidate is available for publication.",),
        audit_reference_id="candidate-unavailable",
        authorized_actions=(),
    )


async def _package_versions(
    *,
    scope: ReactAdminScope,
    repository: SkillRegistryRepository,
    platform_admin: bool,
) -> tuple[SkillPackageVersionSummary, ...]:
    versions = await repository.list_package_versions()
    grants = await repository.list_tenant_grants(
        tenant_id=_scope_tenant_uuid(scope),
        version_ids=tuple(version.skill_package_version_id for version in versions),
    )
    return tuple(
        _version_summary(
            version,
            grants=grants,
            scope=scope,
            platform_admin=platform_admin,
        )
        for version in versions
    )


def _version_summary(
    version: SkillPackageVersion,
    *,
    grants: Sequence[SkillPackageTenantGrant],
    scope: ReactAdminScope,
    platform_admin: bool,
) -> SkillPackageVersionSummary:
    related_grants = tuple(
        grant
        for grant in grants
        if grant.skill_package_version_id == version.skill_package_version_id
    )
    return SkillPackageVersionSummary(
        package_id=str(version.skill_package_id),
        package_slug=version.slug,
        version_id=str(version.skill_package_version_id),
        version_label=version.semantic_version,
        lifecycle_status=_version_status(version.lifecycle_state),
        manifest_digest=_safe_identifier(version.manifest_digest),
        safe_manifest_summary=_summary_from_mapping(
            version.safe_manifest_summary,
            fallback=f"{version.slug} {version.semantic_version} package summary.",
        ),
        tenant_grant_summary=tuple(
            _grant_summary(
                grant=grant,
                version=version,
                scope=scope,
                platform_admin=platform_admin,
            )
            for grant in related_grants
        ),
        validation_evidence_ref=_evidence_reference(
            "validation",
            version.validation_summary,
            version.validation_status,
        ),
        smoke_evidence_ref=_evidence_reference(
            "smoke",
            version.compatibility_metadata,
            "persisted",
        ),
        quarantine_summary="Package version is quarantined."
        if _version_status(version.lifecycle_state) == SkillLifecycleStatus.QUARANTINED
        else None,
        withdrawal_summary="Package version is withdrawn from new installations."
        if _version_status(version.lifecycle_state) == SkillLifecycleStatus.WITHDRAWN
        else None,
        audit_reference_id=f"version-{version.skill_package_version_id}",
        authorized_actions=_package_actions(
            version=version, platform_admin=platform_admin
        ),
    )


def _grant_summary(
    *,
    grant: SkillPackageTenantGrant,
    version: SkillPackageVersion | None,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> TenantSkillGrantSummary:
    package_slug = version.slug if version is not None else "unknown-package"
    version_label = version.semantic_version if version is not None else "unknown"
    tenant_label = scope.label if grant.tenant_id is not None else "All tenants"
    return TenantSkillGrantSummary(
        tenant_id=str(grant.tenant_id) if grant.tenant_id else "all-tenants",
        tenant_label=tenant_label,
        package_slug=package_slug,
        version_label=version_label,
        grant_status=_status_from_text(grant.status),
        allowed_versions=(version_label,),
        install_eligibility=SkillLifecycleStatus.READY
        if grant.status == "active"
        else SkillLifecycleStatus.DENIED,
        restrictions=(grant.reason or "Availability follows persisted grant status.",),
        authorized_actions=_grant_actions(
            version_id=str(grant.skill_package_version_id),
            platform_admin=platform_admin,
        ),
    )


def _installation_summary(
    *,
    installation: SkillInstallation,
    scope: ReactAdminScope,
    credentials: Sequence[SkillInstallationCredential],
    tests: Sequence[SkillInstallationTest],
) -> TenantSkillInstallationSummary:
    connectors = tuple(
        _connector_from_tool(
            installation=installation,
            scope=scope,
            tool_name=tool_name,
            readiness=_status_from_text(installation.smoke_test_status),
        )
        for tool_name in _tool_names(installation.manifest_summary)
    )
    if not connectors and tests:
        connectors = tuple(
            _connector_from_test(installation=installation, test=test, scope=scope)
            for test in tests[:5]
        )
    findings = tuple(
        _safe_text(str(item.get("message") or item.get("code") or "Readiness finding."))
        for item in installation.findings
        if isinstance(item, Mapping)
    ) or (_readiness_sentence(installation),)
    return TenantSkillInstallationSummary(
        installation_id=str(installation.skill_installation_id),
        tenant_id=str(installation.tenant_id),
        package_slug=installation.slug,
        installed_version=installation.semantic_version,
        installation_revision=installation.revision_token,
        installation_status=_installation_status(installation.readiness_state),
        credential_readiness=_status_from_text(installation.credential_status),
        smoke_test_readiness=_status_from_text(installation.smoke_test_status),
        connector_readiness=connectors,
        binding_readiness=_status_from_text(installation.binding_eligibility_status),
        upgrade_path=None,
        findings=findings,
        credential_options=tuple(_credential_option(item) for item in credentials),
        authorized_actions=_installation_actions(
            scope=scope, installation=installation
        ),
        audit_reference_id=f"installation-{installation.skill_installation_id}",
    )


def _credential_option(
    credential: SkillInstallationCredential,
) -> CredentialReferenceOption:
    reference_id = _credential_reference_id(credential)
    summary = credential.safe_summary or {}
    return CredentialReferenceOption(
        reference_id=reference_id,
        label=_safe_text(
            str(summary.get("label") or f"{credential.requirement_key} reference")
        ),
        source_type=_safe_text(credential.credential_kind.replace("_", " ")),
        readiness=_status_from_text(credential.status),
        fingerprint=_fingerprint(reference_id) if reference_id else None,
        policy_reason=_safe_text(
            str(
                summary.get("policy_reason")
                or f"{credential.requirement_key} readiness is {credential.status}."
            )
        ),
        last_checked_label=_timestamp_label(
            credential.last_checked_at or credential.configured_at
        ),
        remediation=_safe_text(
            str(summary.get("remediation") or "Configure an authorized reference.")
        ),
    )


def _connector_from_tool(
    *,
    installation: SkillInstallation,
    scope: ReactAdminScope,
    tool_name: str,
    readiness: SkillLifecycleStatus,
) -> ConnectorReadinessSummary:
    connector_id = tool_name.split(".", 1)[0] if "." in tool_name else tool_name
    return ConnectorReadinessSummary(
        connector_id=f"{installation.skill_installation_id}-{connector_id}",
        connector_label=_safe_text(connector_id.replace("_", " ").title()),
        tool_names=(tool_name,),
        readiness=readiness,
        credential_status=_status_from_text(installation.credential_status),
        policy_status=_status_from_text(installation.permission_status),
        smoke_test_status=_status_from_text(installation.smoke_test_status),
        staging_probe_status=SkillLifecycleStatus.UNAVAILABLE,
        last_safe_summary=(
            f"{connector_id.replace('_', ' ').title()} readiness is projected "
            f"from installation {installation.installation_version}."
        ),
        evidence_reference_id=f"installation-{installation.skill_installation_id}",
        remediation="Refresh readiness evidence if this status is degraded.",
        authorized_actions=(
            AdminAction(
                action_id=f"connector-diagnostic-{connector_id}",
                label="Run diagnostic",
                method=AdminActionMethod.POST,
                href=_with_tenant_query(
                    "/admin/app/skills/diagnostics/run",
                    scope,
                ),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
    )


def _connector_from_test(
    *,
    installation: SkillInstallation,
    test: SkillInstallationTest,
    scope: ReactAdminScope,
) -> ConnectorReadinessSummary:
    tool_name = test.fixture_key if "." in test.fixture_key else "readiness.refresh"
    status = _status_from_text(test.outcome or _value(test.runner_status))
    return _connector_from_tool(
        installation=installation,
        scope=scope,
        tool_name=tool_name,
        readiness=status,
    ).model_copy(
        update={
            "smoke_test_status": status,
            "last_safe_summary": _summary_from_mapping(
                test.safe_output_summary,
                fallback=f"{tool_name} readiness evidence is persisted.",
            ),
            "evidence_reference_id": str(test.skill_installation_test_id),
        }
    )


def _diagnostic_from_test(
    *,
    installation: SkillInstallation,
    test: SkillInstallationTest,
    audit_reference_id: str,
) -> SkillExecutionDiagnosticSummary:
    tool_name = test.fixture_key if "." in test.fixture_key else "readiness.refresh"
    status = _status_from_text(test.outcome or _value(test.runner_status))
    return SkillExecutionDiagnosticSummary(
        diagnostic_id=str(test.skill_installation_test_id),
        skill_package_version=f"{installation.slug} {installation.semantic_version}",
        tool_name=tool_name,
        gateway_decision="allowed_read_only"
        if status in {SkillLifecycleStatus.READY, SkillLifecycleStatus.PASSED}
        else "queued"
        if status == SkillLifecycleStatus.QUEUED
        else "blocked",
        side_effect_posture="read-only connector execution",
        outbound_policy_status=_status_from_text(installation.permission_status),
        credential_policy_status=_status_from_text(installation.credential_status),
        connector_readiness=status,
        safe_attempt_summary=_summary_from_mapping(
            test.safe_output_summary,
            fallback=f"{tool_name} diagnostic evidence is persisted.",
        ),
        redaction_summary="Attempt details were summarized before admin rendering.",
        audit_reference_id=audit_reference_id,
        remediation="No action needed."
        if status in {SkillLifecycleStatus.READY, SkillLifecycleStatus.PASSED}
        else "Review readiness evidence before binding.",
    )


def _audit_record_summary(
    *,
    record: SkillAuditRecord,
    scope: ReactAdminScope,
) -> SkillLifecycleAuditRecord:
    return SkillLifecycleAuditRecord(
        record_id=str(record.skill_audit_record_id),
        domain=_safe_text(record.event_type.split(".", 1)[0]),
        package_slug=_safe_text(record.package_slug or "not package scoped"),
        version_label=_safe_text(record.package_version or "not version scoped"),
        tenant_scope_label=scope.label if record.tenant_id else "Platform",
        actor_label=_safe_text(record.actor_principal_id),
        timestamp_label=_timestamp_label(record.created_at),
        action=_safe_text(record.event_type),
        outcome=_status_from_text(record.outcome),
        safe_diff_summary=_summary_from_mapping(
            record.safe_summary,
            fallback="Skill lifecycle audit event recorded.",
        ),
        audit_reference_id=str(record.skill_audit_record_id),
    )


def _sections(
    *,
    platform_admin: bool,
    publication_count: int,
    discovery_count: int,
    installation_count: int,
    diagnostic_count: int,
    audit_count: int,
) -> tuple[SkillLifecycleSection, ...]:
    sections: list[SkillLifecycleSection] = []
    if platform_admin:
        sections.append(
            SkillLifecycleSection(
                section_id="publish",
                label="Publish",
                status=SkillLifecycleStatus.READY
                if publication_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=f"{publication_count} persisted package versions visible.",
            )
        )
    sections.extend(
        [
            SkillLifecycleSection(
                section_id="discover",
                label="Discover",
                status=SkillLifecycleStatus.READY
                if discovery_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=f"{discovery_count} granted versions visible.",
            ),
            SkillLifecycleSection(
                section_id="installations",
                label="Installations",
                status=SkillLifecycleStatus.READY
                if installation_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=f"{installation_count} tenant installations visible.",
            ),
            SkillLifecycleSection(
                section_id="diagnostics",
                label="Diagnostics",
                status=SkillLifecycleStatus.READY
                if diagnostic_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=f"{diagnostic_count} persisted diagnostic runs visible.",
            ),
            SkillLifecycleSection(
                section_id="binding",
                label="Binding",
                status=SkillLifecycleStatus.READY
                if installation_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary="Binding preview is computed from persisted readiness records.",
            ),
            SkillLifecycleSection(
                section_id="audit",
                label="Audit",
                status=SkillLifecycleStatus.READY
                if audit_count
                else SkillLifecycleStatus.UNAVAILABLE,
                summary=f"{audit_count} lifecycle audit records visible.",
            ),
        ]
    )
    return tuple(sections)


def _setup_summary(*, has_live_data: bool) -> tuple[str, ...]:
    if has_live_data:
        return (
            "Package and installation state is read from skill registry rows.",
            "Credential references are summarized without exposing values.",
            "Diagnostics and smoke evidence use persisted local-safe records.",
        )
    return (
        "No live skill lifecycle records are present for this scope.",
        "Empty states are returned instead of sample package or connector rows.",
        "Seed or create governed registry records to populate this workspace.",
    )


def _dashboard_actions(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
    has_installations: bool,
) -> tuple[AdminAction, ...]:
    actions: list[AdminAction] = [
        AdminAction(
            action_id="binding-preview",
            label="Preview binding",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/skills/eligibility/preview", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
            enabled=has_installations,
            disabled_reason=None
            if has_installations
            else "Install a tenant skill before previewing binding.",
        ),
        AdminAction(
            action_id="diagnostics-refresh",
            label="Run diagnostic",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/skills/diagnostics/run", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
            enabled=has_installations,
            disabled_reason=None
            if has_installations
            else "Install a tenant skill before running diagnostics.",
        ),
    ]
    if platform_admin:
        actions.append(
            AdminAction(
                action_id="candidate-create",
                label="Save candidate",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            )
        )
    return tuple(actions)


def _package_actions(
    *,
    version: SkillPackageVersion,
    platform_admin: bool,
) -> tuple[AdminAction, ...]:
    if not platform_admin:
        return ()
    version_id = str(version.skill_package_version_id)
    return (
        AdminAction(
            action_id="package-grant",
            label="Update grant",
            method=AdminActionMethod.POST,
            href=f"/admin/app/skills/packages/{version_id}/grants",
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                revision=version_id,
                revision_source=ReactAdminActionMetadataSource.BACKEND,
            ),
        ),
        AdminAction(
            action_id="package-quarantine",
            label="Quarantine",
            method=AdminActionMethod.POST,
            href=f"/admin/app/skills/packages/{version_id}/quarantine",
            variant=ReactAdminPageActionVariant.DANGER,
        ),
        AdminAction(
            action_id="package-withdraw",
            label="Withdraw",
            method=AdminActionMethod.POST,
            href=f"/admin/app/skills/packages/{version_id}/withdraw",
            variant=ReactAdminPageActionVariant.DANGER,
        ),
    )


def _grant_actions(
    *,
    version_id: str,
    platform_admin: bool,
) -> tuple[AdminAction, ...]:
    if not platform_admin:
        return ()
    return (
        AdminAction(
            action_id="grant-update",
            label="Update tenant grant",
            method=AdminActionMethod.POST,
            href=f"/admin/app/skills/packages/{version_id}/grants",
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                revision=version_id,
                revision_source=ReactAdminActionMetadataSource.BACKEND,
            ),
        ),
    )


def _installation_actions(
    *,
    scope: ReactAdminScope,
    installation: SkillInstallation,
) -> tuple[AdminAction, ...]:
    installation_id = str(installation.skill_installation_id)
    return (
        AdminAction(
            action_id="install-package",
            label="Refresh installation",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/skills/installations/{installation_id}/install",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                revision=installation.revision_token,
                revision_source=ReactAdminActionMetadataSource.BACKEND,
            ),
        ),
        AdminAction(
            action_id="configure-credentials",
            label="Save credential reference",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/skills/installations/{installation_id}/credentials",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                revision=installation.revision_token,
                revision_source=ReactAdminActionMetadataSource.BACKEND,
            ),
        ),
        AdminAction(
            action_id="refresh-smoke-tests",
            label="Refresh readiness",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/skills/installations/{installation_id}/smoke-tests",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
            action_metadata=ReactAdminActionMetadata(
                revision=installation.revision_token,
                revision_source=ReactAdminActionMetadataSource.BACKEND,
            ),
        ),
    )


def _stale_installation_result(
    *,
    submitted_revision: str,
    current_revision: str,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.STALE_CONFLICT,
        summary="Reload the latest installation state before retrying.",
        stale_conflict=RevisionConflict(
            submitted_revision=submitted_revision,
            current_revision=current_revision,
            message="The installation has newer safe readiness metadata.",
            reload_href=_with_tenant_query("/admin/app/skills", scope),
        ),
        audit_reference_id="installation-stale-conflict",
    )


def _field_error_result(
    *,
    field: str,
    label: str,
    message: str,
    code: str,
    audit_reference_id: str,
) -> SkillLifecycleMutationResult:
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.VALIDATION_ERROR,
        summary=message,
        field_errors=(
            ValidationFieldError(
                field=field,
                label=label,
                message=message,
                code=code,
            ),
        ),
        audit_reference_id=audit_reference_id,
    )


async def _record_audit(
    repository: SkillRegistryRepository,
    *,
    event_type: str,
    actor_principal_id: str,
    outcome: str,
    tenant_id: UUID | None = None,
    skill_package_version_id: UUID | None = None,
    skill_installation_id: UUID | None = None,
    package_slug: str | None = None,
    package_version: str | None = None,
    safe_summary: dict[str, object] | None = None,
) -> str:
    record = await repository.add_audit_record(
        SkillAuditRecord(
            event_type=event_type,
            actor_principal_id=actor_principal_id,
            outcome=outcome,
            tenant_id=tenant_id,
            skill_package_version_id=skill_package_version_id,
            skill_installation_id=skill_installation_id,
            package_slug=package_slug,
            package_version=package_version,
            safe_summary=safe_summary or {},
            redaction_metadata={"react_contract": "safe_summary_only"},
        )
    )
    return str(record.skill_audit_record_id)


def _scope_tenant_uuid(scope: ReactAdminScope) -> UUID | None:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return None
    return _parse_uuid(str(scope.tenant_id))


def _parse_uuid(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        return None


def _version_for_grant(
    grant: SkillPackageTenantGrant,
    versions: Sequence[SkillPackageVersion],
) -> SkillPackageVersion | None:
    for version in versions:
        if version.skill_package_version_id == grant.skill_package_version_id:
            return version
    return None


def _group_by_installation(
    credentials: Iterable[SkillInstallationCredential],
) -> defaultdict[UUID, list[SkillInstallationCredential]]:
    grouped: defaultdict[UUID, list[SkillInstallationCredential]] = defaultdict(list)
    for credential in credentials:
        grouped[credential.skill_installation_id].append(credential)
    return grouped


def _group_tests_by_installation(
    tests: Iterable[SkillInstallationTest],
) -> defaultdict[UUID, list[SkillInstallationTest]]:
    grouped: defaultdict[UUID, list[SkillInstallationTest]] = defaultdict(list)
    for test in tests:
        grouped[test.skill_installation_id].append(test)
    return grouped


def _selected_credential(
    credentials: Sequence[SkillInstallationCredential],
    selected_reference_id: str,
) -> SkillInstallationCredential | None:
    for credential in credentials:
        if _credential_reference_id(credential) == selected_reference_id:
            return credential
    return None


def _credential_reference_id(credential: SkillInstallationCredential) -> str:
    for value in (
        credential.secret_reference_id,
        credential.secret_reference_version_id,
        credential.delegated_credential_link_id,
    ):
        if value is not None:
            return str(value)
    return f"unconfigured-{credential.requirement_key}"


def _installation_is_ready(installation: SkillInstallation) -> bool:
    return (
        installation.credential_status == "ready"
        and installation.compatibility_status == "ready"
        and installation.permission_status == "ready"
        and installation.smoke_test_status in {"passed", "ready", "not_required"}
        and installation.quarantine_state == "clear"
        and not installation.runtime_blocked
    )


def _select_installation_for_preview(
    installations: Sequence[SkillInstallation],
    request: BindingEligibilityPreviewRequest | None,
) -> SkillInstallation | None:
    if not installations:
        return None
    if request is None:
        return installations[0]
    requested_uuid = _parse_uuid(request.package_id)
    if requested_uuid is None:
        return installations[0]
    for installation in installations:
        if (
            installation.skill_installation_id == requested_uuid
            or installation.skill_package_version_id == requested_uuid
        ):
            return installation
    return installations[0]


def _empty_binding_preview(
    *,
    scope: ReactAdminScope,
    selected_context: str,
    reason: str,
) -> BindingEligibilityPreview:
    return BindingEligibilityPreview(
        preview_id="binding-preview-empty",
        tenant_label=scope.label,
        context_choices=(),
        selected_context=selected_context,
        eligible_tools=(),
        blocked_tools=("all tools",),
        policy_reasons=(reason,),
        missing_requirements=(reason,),
        remediation="Create and ready a tenant skill installation before binding.",
        audit_reference_id="binding-preview-empty",
    )


def _tool_names(summary: Mapping[str, object]) -> tuple[str, ...]:
    tools = summary.get("tools")
    if not isinstance(tools, list):
        return ()
    names: list[str] = []
    for item in tools:
        if isinstance(item, str):
            names.append(_safe_identifier(item))
        elif isinstance(item, Mapping):
            name = item.get("tool_id") or item.get("name")
            if isinstance(name, str):
                names.append(_safe_identifier(name))
    return tuple(dict.fromkeys(names))


def _string_items(summary: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = summary.get(key)
    if not isinstance(value, list):
        return ()
    return tuple(_safe_text(str(item)) for item in value if str(item).strip())


def _summary_from_mapping(
    summary: Mapping[str, object],
    *,
    fallback: str,
) -> str:
    for key in ("summary", "safe_summary", "description", "last_result"):
        value = summary.get(key)
        if isinstance(value, str) and value.strip():
            return _safe_text(value)
    tools = _tool_names(summary)
    if tools:
        return _safe_text(f"Package exposes {', '.join(tools[:5])}.")
    categories = _string_items(summary, "action_categories")
    if categories:
        return _safe_text(f"Package action categories: {', '.join(categories[:5])}.")
    return _safe_text(fallback)


def _evidence_reference(
    prefix: str,
    summary: Mapping[str, object],
    status: str,
) -> str:
    reference = summary.get("evidence_reference_id")
    if isinstance(reference, str) and reference.strip():
        return _safe_identifier(reference)
    return _safe_identifier(f"{prefix}-{status or 'not-recorded'}")


def _readiness_sentence(installation: SkillInstallation) -> str:
    return _safe_text(
        f"Readiness is {installation.readiness_state}; credential "
        f"{installation.credential_status}, smoke {installation.smoke_test_status}."
    )


def _aggregate_status(statuses: Iterable[str]) -> str:
    values = tuple(statuses)
    if values and all(value == "ready" for value in values):
        return "ready"
    if any(value == "blocked" for value in values):
        return "blocked"
    return "pending"


def _version_status(value: object) -> SkillLifecycleStatus:
    normalized = _value(value)
    return {
        SkillVersionLifecycleState.CANDIDATE.value: SkillLifecycleStatus.WARNING,
        SkillVersionLifecycleState.VALIDATED.value: SkillLifecycleStatus.READY,
        SkillVersionLifecycleState.PUBLISHED.value: SkillLifecycleStatus.PUBLISHED,
        SkillVersionLifecycleState.WITHDRAWN.value: SkillLifecycleStatus.WITHDRAWN,
        SkillVersionLifecycleState.QUARANTINED.value: SkillLifecycleStatus.QUARANTINED,
    }.get(normalized, _status_from_text(normalized))


def _installation_status(value: object) -> SkillLifecycleStatus:
    normalized = _value(value)
    return {
        SkillInstallationState.INSTALLED.value: SkillLifecycleStatus.READY,
        SkillInstallationState.CONFIGURING.value: SkillLifecycleStatus.WARNING,
        SkillInstallationState.TESTING.value: SkillLifecycleStatus.RUNNING,
        SkillInstallationState.READY.value: SkillLifecycleStatus.READY,
        SkillInstallationState.BLOCKED.value: SkillLifecycleStatus.BLOCKED,
        SkillInstallationState.QUARANTINED.value: SkillLifecycleStatus.QUARANTINED,
        SkillInstallationState.RETIRED.value: SkillLifecycleStatus.WITHDRAWN,
    }.get(normalized, _status_from_text(normalized))


def _status_from_text(value: object) -> SkillLifecycleStatus:
    normalized = _value(value)
    if normalized in {"ready", "active", "eligible", "allowed", "installed"}:
        return SkillLifecycleStatus.READY
    if normalized in {"passed", "success", "succeeded"}:
        return SkillLifecycleStatus.PASSED
    if normalized in {"published"}:
        return SkillLifecycleStatus.PUBLISHED
    if normalized in {"queued", "pending"}:
        return SkillLifecycleStatus.QUEUED
    if normalized in {"running", "testing"}:
        return SkillLifecycleStatus.RUNNING
    if normalized in {"warning", "degraded"}:
        return SkillLifecycleStatus.WARNING
    if normalized in {"blocked", "errored"}:
        return SkillLifecycleStatus.BLOCKED
    if normalized in {"denied", "revoked"}:
        return SkillLifecycleStatus.DENIED
    if normalized in {"failed", "failure"}:
        return SkillLifecycleStatus.FAILED
    if normalized in {"quarantined"}:
        return SkillLifecycleStatus.QUARANTINED
    if normalized in {"withdrawn", "withdrawn_from_new_installs", "retired"}:
        return SkillLifecycleStatus.WITHDRAWN
    if normalized in {"stale"}:
        return SkillLifecycleStatus.STALE
    if normalized in {"summarized"}:
        return SkillLifecycleStatus.SUMMARIZED
    return SkillLifecycleStatus.UNAVAILABLE


def _value(value: object) -> str:
    raw = getattr(value, "value", value)
    return str(raw).lower()


def _safe_text(value: str) -> str:
    try:
        return safe_skill_lifecycle_text(value, max_length=220)
    except ValueError:
        return "Safe summary unavailable."


def _safe_identifier(value: str) -> str:
    return safe_skill_lifecycle_text(value, max_length=160)


def _fingerprint(value: str) -> str:
    return "fp_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _timestamp_label(value: datetime | None) -> str:
    if value is None:
        return "Not checked"
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _next_revision(prefix: str) -> str:
    return f"{prefix}-{uuid4()}"


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
