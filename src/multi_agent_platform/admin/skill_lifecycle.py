from __future__ import annotations

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    RevisionConflict,
    ToastHint,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
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
)
from multi_agent_platform.auth.principal import PrincipalContext

CURRENT_CANDIDATE_REVISION = "candidate-rev-qa032-current"
CURRENT_INSTALLATION_REVISION = "installation-rev-qa032-current"
ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def build_skill_lifecycle_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> SkillLifecycleDashboard:
    platform_admin = is_platform_admin(principal)
    discovery = build_tenant_discovery(scope=scope, principal=principal).discovery
    installations = build_tenant_installations(scope=scope).installations
    diagnostics = build_skill_execution_diagnostics(scope=scope).diagnostics
    connectors = installations[0].connector_readiness if installations else ()
    return SkillLifecycleDashboard(
        page_id="react-skill-lifecycle",
        title="Skill lifecycle",
        description=(
            "Guided package publication, tenant installation, readiness, "
            "binding, diagnostics, and audit evidence."
        ),
        scope=scope,
        sections=_sections(platform_admin=platform_admin),
        setup_summary=(
            "Manifests are summarized after validation and never echoed raw.",
            "Credential references are selected from authorized backend options.",
            (
                "Smoke tests and connector diagnostics run only as explicit "
                "queued actions."
            ),
        ),
        platform_publication=build_publication_workspace(scope=scope)
        if platform_admin
        else None,
        tenant_discovery=discovery,
        installations=installations,
        connector_diagnostics=connectors,
        skill_execution_diagnostics=diagnostics,
        binding_preview=build_binding_preview(scope=scope),
        audit_timeline=build_skill_lifecycle_audit(scope=scope).audit_timeline,
        actions=_dashboard_actions(scope=scope, platform_admin=platform_admin),
    )


def build_publication_workspace(
    *,
    scope: ReactAdminScope,
) -> PackagePublicationWorkspace:
    candidate = _candidate(
        manifest_source="upload",
        validation_status=SkillLifecycleStatus.READY,
        publish_blockers=(),
    )
    return PackagePublicationWorkspace(
        candidate=candidate,
        available_steps=(
            SkillLifecycleWizardStep(
                step_id="candidate",
                label="Candidate",
                status=SkillLifecycleStatus.READY,
                summary="Package candidate metadata is summarized for review.",
            ),
            SkillLifecycleWizardStep(
                step_id="validation",
                label="Validation",
                status=SkillLifecycleStatus.READY,
                summary="Manifest validation and smoke evidence are current.",
            ),
            SkillLifecycleWizardStep(
                step_id="grants",
                label="Grants",
                status=SkillLifecycleStatus.WARNING,
                summary="Review tenant grant impact before publication.",
            ),
            SkillLifecycleWizardStep(
                step_id="publish",
                label="Publish",
                status=SkillLifecycleStatus.BLOCKED,
                summary="Confirmation is required for immutable publication.",
            ),
        ),
        package_versions=_package_versions(scope=scope, platform_admin=True),
        validation_summary=(
            "Candidate validation passed with safe summaries and evidence references."
        ),
        grant_preview=_grant_preview(scope=scope, platform_admin=True),
        publish_readiness=SkillLifecycleStatus.READY,
        authorized_actions=(
            AdminAction(
                action_id="candidate-create",
                label="Save candidate",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
            AdminAction(
                action_id="candidate-validate",
                label="Validate candidate",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates/qa032-candidate/validate",
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
            AdminAction(
                action_id="candidate-publish",
                label="Publish version",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates/qa032-candidate/publish",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_confirmation=True,
                requires_idempotency_key=True,
            ),
        ),
    )


def build_candidate_result(
    *,
    request: SkillPackageCandidateRequest,
) -> SkillLifecycleMutationResult:
    source = "upload" if request.uploaded_fixture_id else "paste"
    candidate = _candidate(
        manifest_source=source,
        validation_status=SkillLifecycleStatus.READY,
        publish_blockers=(),
    )
    diagnostics = (
        "Uploaded manifest fixture took precedence over pasted text."
        if request.uploaded_fixture_id and request.manifest_text
        else "Manifest input was summarized before returning to React."
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Package candidate saved with safe manifest summary.",
        revision=candidate.candidate_revision,
        diagnostics=(diagnostics,),
        audit_reference_id=candidate.audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Candidate saved",
            summary="Safe package metadata is ready for validation.",
        ),
    )


def build_candidate_validation_result(
    *,
    ready: bool = True,
) -> SkillLifecycleMutationResult:
    if not ready:
        candidate = _candidate(
            manifest_source="upload",
            validation_status=SkillLifecycleStatus.BLOCKED,
            publish_blockers=("Required smoke-test evidence is not current.",),
        )
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Publication is blocked until validation evidence is current.",
            revision=candidate.candidate_revision,
            diagnostics=("Validation findings are summarized by field category.",),
            audit_reference_id=candidate.audit_reference_id,
        )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Candidate validation passed with safe evidence references.",
        revision=CURRENT_CANDIDATE_REVISION,
        diagnostics=(
            "Manifest digest, tool policy, and smoke evidence are ready.",
            "No manifest body or connector output was returned.",
        ),
        audit_reference_id="audit-skill-candidate-validation-qa032",
    )


def build_publish_result(
    *,
    request: SkillPackagePublishRequest,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    if request.candidate_revision != CURRENT_CANDIDATE_REVISION:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the latest candidate before publishing.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.candidate_revision,
                current_revision=CURRENT_CANDIDATE_REVISION,
                message="The package candidate has a newer safe revision.",
                reload_href="/admin/app/skills",
            ),
            audit_reference_id="audit-skill-publish-stale-qa032",
        )
    if not request.confirmed:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Confirm immutable publication after reviewing tenant grants.",
            revision=CURRENT_CANDIDATE_REVISION,
            audit_reference_id="audit-skill-publish-confirm-qa032",
        )
    publication = _package_versions(scope=scope, platform_admin=True)[0]
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Immutable skill package version published.",
        revision="package-version-rev-qa032-v1",
        publication=publication,
        diagnostics=(
            (
                "Validation, smoke evidence, tenant grant review, revision, "
                "and audit gates passed."
            ),
            "Published package version is immutable.",
        ),
        audit_reference_id="audit-skill-publish-qa032",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Package published",
            summary="Tenant grant impact is available for review.",
        ),
    )


def build_tenant_grant_result(
    *,
    request: TenantGrantMutationRequest,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    _ = request
    grant = _grant_preview(scope=scope, platform_admin=True)[0]
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Tenant grant updated with safe availability summary.",
        revision="grant-rev-qa032-next",
        diagnostics=("Grant mutation is restricted to platform administrators.",),
        audit_reference_id="audit-skill-grant-qa032",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Grant updated",
            summary=f"{grant.tenant_label} availability is ready.",
        ),
    )


def build_package_lifecycle_result(
    *,
    package_id: str,
    action: str,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    version = _package_versions(scope=scope, platform_admin=True)[0].model_copy(
        update={
            "lifecycle_status": SkillLifecycleStatus.QUARANTINED
            if action == "quarantine"
            else SkillLifecycleStatus.WITHDRAWN,
            "quarantine_summary": "Package is temporarily blocked for tenant installs."
            if action == "quarantine"
            else None,
            "withdrawal_summary": "Package is withdrawn from new installations."
            if action == "withdraw"
            else None,
        }
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary=f"Package {package_id} lifecycle state updated.",
        publication=version,
        revision=f"{package_id}-{action}-rev-qa032",
        diagnostics=("Tenant installations receive safe lifecycle guidance.",),
        audit_reference_id=f"audit-skill-{action}-qa032",
    )


def build_tenant_discovery(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> TenantSkillDiscoveryList:
    platform_admin = is_platform_admin(principal)
    return TenantSkillDiscoveryList(
        discovery=TenantSkillDiscovery(
            grants=_grant_preview(scope=scope, platform_admin=platform_admin),
            available_versions=_package_versions(
                scope=scope,
                platform_admin=platform_admin,
            ),
            empty_state_summary=None,
        )
    )


def build_tenant_installations(
    *,
    scope: ReactAdminScope,
) -> TenantSkillInstallationList:
    tenant_id = str(scope.tenant_id or ACME_TENANT_ID)
    connectors = _connectors(scope=scope)
    return TenantSkillInstallationList(
        installations=(
            TenantSkillInstallationSummary(
                installation_id="install-qa032-daily-briefing",
                tenant_id=tenant_id,
                package_slug="daily-briefing-connectors",
                installed_version="1.4.0",
                installation_revision=CURRENT_INSTALLATION_REVISION,
                installation_status=SkillLifecycleStatus.READY,
                credential_readiness=SkillLifecycleStatus.READY,
                smoke_test_readiness=SkillLifecycleStatus.PASSED,
                connector_readiness=connectors,
                binding_readiness=SkillLifecycleStatus.READY,
                upgrade_path="1.5.0 available after smoke evidence refresh",
                findings=("Connector readiness is fixture-backed and current.",),
                credential_options=_credential_options(),
                authorized_actions=_installation_actions(scope=scope),
                audit_reference_id="audit-installation-qa032",
            ),
        )
    )


def build_install_result(
    *,
    request: TenantSkillInstallRequest,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    if request.revision == "stale-revision":
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the latest installation state before retrying.",
            stale_conflict=RevisionConflict(
                submitted_revision=request.revision,
                current_revision=CURRENT_INSTALLATION_REVISION,
                message="The installation has newer safe readiness metadata.",
                reload_href=_with_tenant_query("/admin/app/skills", scope),
            ),
            audit_reference_id="audit-installation-stale-qa032",
        )
    installation = build_tenant_installations(scope=scope).installations[0]
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Skill package installed for the active tenant.",
        revision="installation-rev-qa032-next",
        installation=installation,
        diagnostics=(
            "Install action used idempotency and active tenant grant checks.",
            "No external connector calls were made.",
        ),
        audit_reference_id="audit-installation-qa032",
    )


def build_credential_configuration_result(
    *,
    request: CredentialConfigurationRequest,
) -> SkillLifecycleMutationResult:
    options = _credential_options()
    selected = next(
        (
            option
            for option in options
            if option.reference_id == request.selected_reference_id
        ),
        None,
    )
    if selected is None:
        return SkillLifecycleMutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Choose an authorized credential reference.",
            field_errors=(
                ValidationFieldError(
                    field="selected_reference_id",
                    label="Credential reference",
                    message="The selected reference is not available for this tenant.",
                    code="unauthorized_reference",
                ),
            ),
            audit_reference_id="audit-credential-denied-qa032",
        )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Credential reference configured without exposing resolved values.",
        revision="credential-rev-qa032-next",
        credential=selected,
        diagnostics=(
            "Only authorized credential reference metadata was returned.",
            "Secret values stayed outside React contracts.",
        ),
        audit_reference_id="audit-credential-configured-qa032",
    )


def build_readiness_refresh_result(
    *,
    request: ReadinessRefreshRequest,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    _ = request
    smoke = _connectors(scope=scope)[0].model_copy(
        update={
            "readiness": SkillLifecycleStatus.QUEUED,
            "smoke_test_status": SkillLifecycleStatus.QUEUED,
            "last_safe_summary": (
                "Readiness refresh is queued with deterministic evidence."
            ),
        }
    )
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Smoke-test readiness refresh queued.",
        revision="readiness-rev-qa032-next",
        smoke_test=smoke,
        diagnostics=(
            "No unbounded polling or live connector side effect was started.",
        ),
        audit_reference_id="audit-readiness-refresh-qa032",
    )


def build_connector_diagnostic_result(
    *,
    scope: ReactAdminScope,
) -> SkillLifecycleMutationResult:
    diagnostic = build_skill_execution_diagnostics(scope=scope).diagnostics[0]
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Connector diagnostic queued with safe gateway summary.",
        diagnostic=diagnostic,
        diagnostics=(
            "SkillExecutionGateway policy evidence is summarized.",
            "Connector attempt payloads stayed outside the browser contract.",
        ),
        audit_reference_id=diagnostic.audit_reference_id,
    )


def build_binding_preview(
    *,
    scope: ReactAdminScope,
    request: BindingEligibilityPreviewRequest | None = None,
) -> BindingEligibilityPreview:
    selected_context = (
        request.workflow_context
        if request is not None
        else "Daily briefing workflow with briefing runtime profile"
    )
    return BindingEligibilityPreview(
        preview_id="binding-preview-qa032",
        tenant_label=scope.label,
        context_choices=(
            BindingContextChoice(
                choice_id="workflow-daily-briefing",
                label="Daily briefing workflow",
                kind="workflow",
                selected=True,
            ),
            BindingContextChoice(
                choice_id="profile-briefing-runtime",
                label="Briefing runtime profile",
                kind="profile",
            ),
            BindingContextChoice(
                choice_id="package-daily-briefing-connectors",
                label="Daily briefing connectors",
                kind="package",
            ),
        ),
        selected_context=selected_context,
        eligible_tools=(
            "calendar.read",
            "gmail.search",
            "news.lookup",
            "weather.forecast",
            "commute.estimate",
        ),
        blocked_tools=("email.send",),
        policy_reasons=(
            "Tenant grant and credential references are ready.",
            "Only read-only connector bindings are eligible.",
            "Preview did not execute tools or resolve live credentials.",
        ),
        missing_requirements=("Side-effectful email sending remains blocked.",),
        remediation="Publish a new approved skill version before enabling write tools.",
        audit_reference_id="audit-binding-preview-qa032",
    )


def build_binding_preview_result(
    *,
    scope: ReactAdminScope,
    request: BindingEligibilityPreviewRequest,
) -> SkillLifecycleMutationResult:
    preview = build_binding_preview(scope=scope, request=request)
    return SkillLifecycleMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Read-only binding eligibility preview completed.",
        binding_preview=preview,
        diagnostics=(
            (
                "No live tools, credentials, Telegram delivery, model calls, "
                "or connector side effects were invoked."
            ),
        ),
        audit_reference_id=preview.audit_reference_id,
    )


def build_skill_execution_diagnostics(
    *,
    scope: ReactAdminScope,
) -> SkillExecutionDiagnosticList:
    _ = scope
    return SkillExecutionDiagnosticList(
        diagnostics=(
            SkillExecutionDiagnosticSummary(
                diagnostic_id="diagnostic-qa032-calendar",
                skill_package_version="daily-briefing-connectors 1.4.0",
                tool_name="calendar.read",
                gateway_decision="allowed_read_only",
                side_effect_posture="read-only connector execution",
                outbound_policy_status=SkillLifecycleStatus.READY,
                credential_policy_status=SkillLifecycleStatus.READY,
                connector_readiness=SkillLifecycleStatus.READY,
                safe_attempt_summary=(
                    "Deterministic gateway fixture verified calendar readiness."
                ),
                redaction_summary=(
                    "Attempt details were summarized before React rendering."
                ),
                audit_reference_id="audit-gateway-diagnostic-qa032-calendar",
                remediation="No action needed.",
            ),
            SkillExecutionDiagnosticSummary(
                diagnostic_id="diagnostic-qa032-gmail",
                skill_package_version="daily-briefing-connectors 1.4.0",
                tool_name="gmail.search",
                gateway_decision="allowed_read_only",
                side_effect_posture="read-only connector execution",
                outbound_policy_status=SkillLifecycleStatus.READY,
                credential_policy_status=SkillLifecycleStatus.WARNING,
                connector_readiness=SkillLifecycleStatus.DEGRADED,
                safe_attempt_summary=(
                    "Mocked Gmail diagnostic reported degraded scope readiness."
                ),
                redaction_summary="Message content and connector outputs are absent.",
                audit_reference_id="audit-gateway-diagnostic-qa032-gmail",
                remediation="Refresh tenant credential reference before binding.",
            ),
        )
    )


def build_skill_lifecycle_audit(*, scope: ReactAdminScope) -> SkillLifecycleAuditList:
    return SkillLifecycleAuditList(
        audit_timeline=(
            SkillLifecycleAuditRecord(
                record_id="audit-record-publish-qa032",
                domain="package",
                package_slug="daily-briefing-connectors",
                version_label="1.4.0",
                tenant_scope_label="Platform",
                actor_label="Platform Admin",
                timestamp_label="Today",
                action="published_version",
                outcome=SkillLifecycleStatus.PUBLISHED,
                safe_diff_summary="Immutable version published after validation gates.",
                audit_reference_id="audit-skill-publish-qa032",
            ),
            SkillLifecycleAuditRecord(
                record_id="audit-record-install-qa032",
                domain="installation",
                package_slug="daily-briefing-connectors",
                version_label="1.4.0",
                tenant_scope_label=scope.label,
                actor_label="Tenant Admin",
                timestamp_label="Today",
                action="configured_credentials",
                outcome=SkillLifecycleStatus.READY,
                safe_diff_summary="Credential reference fingerprint changed.",
                audit_reference_id="audit-credential-configured-qa032",
            ),
            SkillLifecycleAuditRecord(
                record_id="audit-record-diagnostic-qa032",
                domain="diagnostic",
                package_slug="daily-briefing-connectors",
                version_label="1.4.0",
                tenant_scope_label=scope.label,
                actor_label="SkillExecutionGateway",
                timestamp_label="Today",
                action="diagnostic_refreshed",
                outcome=SkillLifecycleStatus.DEGRADED,
                safe_diff_summary=(
                    "Gateway readiness summarized without adapter bodies."
                ),
                audit_reference_id="audit-gateway-diagnostic-qa032-gmail",
            ),
        )
    )


def _candidate(
    *,
    manifest_source: str,
    validation_status: SkillLifecycleStatus,
    publish_blockers: tuple[str, ...],
) -> SkillPackageCandidate:
    findings = (
        (
            ValidationFieldError(
                field="smoke_evidence",
                label="Smoke evidence",
                message="Refresh smoke-test evidence before publication.",
                code="stale_evidence",
            ),
        )
        if publish_blockers
        else ()
    )
    return SkillPackageCandidate(
        candidate_id="qa032-candidate",
        package_slug="daily-briefing-connectors",
        candidate_revision=CURRENT_CANDIDATE_REVISION,
        manifest_digest="sha256:qa032dailybriefing",
        manifest_source=manifest_source,
        safe_manifest_summary=(
            "Daily briefing connector package with read-only calendar, Gmail, "
            "news, weather, and commute tools."
        ),
        validation_status=validation_status,
        validation_findings=findings,
        safe_documentation_summary=(
            "Documentation summary is stored as safe package metadata."
        ),
        smoke_evidence_status=SkillLifecycleStatus.PASSED
        if not publish_blockers
        else SkillLifecycleStatus.STALE,
        publish_blockers=publish_blockers,
        audit_reference_id="audit-skill-candidate-qa032",
        authorized_actions=(
            AdminAction(
                action_id="candidate-validate",
                label="Validate candidate",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates/qa032-candidate/validate",
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
            AdminAction(
                action_id="candidate-publish",
                label="Publish version",
                method=AdminActionMethod.POST,
                href="/admin/app/skills/packages/candidates/qa032-candidate/publish",
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
        ),
    )


def _package_versions(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> tuple[SkillPackageVersionSummary, ...]:
    return (
        SkillPackageVersionSummary(
            package_id="package-daily-briefing-connectors",
            package_slug="daily-briefing-connectors",
            version_id="package-version-daily-briefing-1-4-0",
            version_label="1.4.0",
            lifecycle_status=SkillLifecycleStatus.PUBLISHED,
            manifest_digest="sha256:qa032dailybriefing",
            safe_manifest_summary=(
                "Read-only briefing connector bundle for calendar, Gmail, "
                "news, weather, and commute evidence."
            ),
            tenant_grant_summary=_grant_preview(
                scope=scope,
                platform_admin=platform_admin,
            ),
            validation_evidence_ref="validation-evidence-qa032",
            smoke_evidence_ref="smoke-evidence-qa032",
            quarantine_summary=None,
            withdrawal_summary=None,
            audit_reference_id="audit-skill-version-qa032",
            authorized_actions=_package_actions(platform_admin=platform_admin),
        ),
    )


def _grant_preview(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> tuple[TenantSkillGrantSummary, ...]:
    tenant_id = str(scope.tenant_id or ACME_TENANT_ID)
    tenant_label = (
        scope.label if scope.scope_type == ReactAdminScopeType.TENANT else "Acme"
    )
    return (
        TenantSkillGrantSummary(
            tenant_id=tenant_id,
            tenant_label=tenant_label,
            package_slug="daily-briefing-connectors",
            version_label="1.4.0",
            grant_status=SkillLifecycleStatus.READY,
            allowed_versions=("1.4.0", "1.5.0 candidate"),
            install_eligibility=SkillLifecycleStatus.READY,
            restrictions=("Read-only tools only.",),
            authorized_actions=_grant_actions(platform_admin=platform_admin),
        ),
    )


def _credential_options() -> tuple[CredentialReferenceOption, ...]:
    return (
        CredentialReferenceOption(
            reference_id="cred-ref-acme-briefing",
            label="Acme briefing connector reference",
            source_type="tenant secret reference",
            readiness=SkillLifecycleStatus.READY,
            fingerprint="fp_qa032_acme_briefing",
            policy_reason="Reference is authorized for read-only briefing tools.",
            last_checked_label="Deterministic QA032 check",
            remediation="No action needed.",
        ),
        CredentialReferenceOption(
            reference_id="cred-ref-acme-weather",
            label="Acme weather fixture reference",
            source_type="tenant fixture reference",
            readiness=SkillLifecycleStatus.WARNING,
            fingerprint="fp_qa032_weather",
            policy_reason="Allowed for mocked local readiness only.",
            last_checked_label="Deterministic QA032 check",
            remediation="Use production reference before live probes.",
        ),
    )


def _connectors(*, scope: ReactAdminScope) -> tuple[ConnectorReadinessSummary, ...]:
    connectors = [
        ("calendar", "Calendar", ("calendar.read",), SkillLifecycleStatus.READY),
        ("gmail", "Gmail", ("gmail.search",), SkillLifecycleStatus.DEGRADED),
        ("news", "News", ("news.lookup",), SkillLifecycleStatus.READY),
        ("weather", "Weather", ("weather.forecast",), SkillLifecycleStatus.READY),
        ("commute", "Commute", ("commute.estimate",), SkillLifecycleStatus.WARNING),
    ]
    return tuple(
        ConnectorReadinessSummary(
            connector_id=f"connector-{connector_id}",
            connector_label=label,
            tool_names=tools,
            readiness=readiness,
            credential_status=SkillLifecycleStatus.READY
            if readiness != SkillLifecycleStatus.DEGRADED
            else SkillLifecycleStatus.WARNING,
            policy_status=SkillLifecycleStatus.READY,
            smoke_test_status=SkillLifecycleStatus.PASSED,
            staging_probe_status=SkillLifecycleStatus.UNAVAILABLE,
            last_safe_summary=(
                f"{label} readiness uses deterministic QA032 evidence for "
                f"{scope.label}."
            ),
            evidence_reference_id=f"evidence-qa032-{connector_id}",
            remediation="Refresh readiness evidence if the status is degraded.",
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
        for connector_id, label, tools, readiness in connectors
    )


def _sections(*, platform_admin: bool) -> tuple[SkillLifecycleSection, ...]:
    sections = []
    if platform_admin:
        sections.append(
            SkillLifecycleSection(
                section_id="publish",
                label="Publish",
                status=SkillLifecycleStatus.READY,
                summary=(
                    "Guided package candidate, validation, grants, and publication."
                ),
            )
        )
    sections.extend(
        [
            SkillLifecycleSection(
                section_id="discover",
                label="Discover",
                status=SkillLifecycleStatus.READY,
                summary="Granted packages and install readiness for the active scope.",
            ),
            SkillLifecycleSection(
                section_id="installations",
                label="Installations",
                status=SkillLifecycleStatus.READY,
                summary="Tenant installation, credential, and smoke-test state.",
            ),
            SkillLifecycleSection(
                section_id="diagnostics",
                label="Diagnostics",
                status=SkillLifecycleStatus.DEGRADED,
                summary="Connector readiness and SkillExecutionGateway decisions.",
            ),
            SkillLifecycleSection(
                section_id="binding",
                label="Binding",
                status=SkillLifecycleStatus.READY,
                summary="Read-only workflow and profile eligibility preview.",
            ),
            SkillLifecycleSection(
                section_id="audit",
                label="Audit",
                status=SkillLifecycleStatus.READY,
                summary="Bounded lifecycle timeline with safe diff summaries.",
            ),
        ]
    )
    return tuple(sections)


def _dashboard_actions(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> tuple[AdminAction, ...]:
    actions = [
        AdminAction(
            action_id="binding-preview",
            label="Preview binding",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/skills/eligibility/preview", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
        ),
        AdminAction(
            action_id="diagnostics-refresh",
            label="Run diagnostic",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/skills/diagnostics/run", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
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


def _package_actions(*, platform_admin: bool) -> tuple[AdminAction, ...]:
    if not platform_admin:
        return ()
    return (
        AdminAction(
            action_id="package-grant",
            label="Update grant",
            method=AdminActionMethod.POST,
            href="/admin/app/skills/packages/package-daily-briefing-connectors/grants",
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
        ),
        AdminAction(
            action_id="package-quarantine",
            label="Quarantine",
            method=AdminActionMethod.POST,
            href="/admin/app/skills/packages/package-daily-briefing-connectors/quarantine",
            variant=ReactAdminPageActionVariant.DANGER,
        ),
        AdminAction(
            action_id="package-withdraw",
            label="Withdraw",
            method=AdminActionMethod.POST,
            href="/admin/app/skills/packages/package-daily-briefing-connectors/withdraw",
            variant=ReactAdminPageActionVariant.DANGER,
        ),
    )


def _grant_actions(*, platform_admin: bool) -> tuple[AdminAction, ...]:
    if not platform_admin:
        return ()
    return (
        AdminAction(
            action_id="grant-update-acme",
            label="Update tenant grant",
            method=AdminActionMethod.POST,
            href="/admin/app/skills/packages/package-daily-briefing-connectors/grants",
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
        ),
    )


def _installation_actions(scope: ReactAdminScope) -> tuple[AdminAction, ...]:
    return (
        AdminAction(
            action_id="install-package",
            label="Install package",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                "/admin/app/skills/installations/install-qa032-daily-briefing/install",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
        ),
        AdminAction(
            action_id="configure-credentials",
            label="Save credential reference",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                "/admin/app/skills/installations/install-qa032-daily-briefing/credentials",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
        ),
        AdminAction(
            action_id="refresh-smoke-tests",
            label="Refresh readiness",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                "/admin/app/skills/installations/install-qa032-daily-briefing/smoke-tests",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
        ),
    )


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
