from __future__ import annotations

from multi_agent_platform.api.schemas.admin_governance import (
    GovernanceDashboard,
    GovernanceMutationResult,
    GovernanceSection,
    GovernanceStatus,
    PolicyHistoryList,
    PolicyHistoryRecord,
    ProfileGovernanceList,
    ProfileResolutionPreview,
    ProfileSaveRequest,
    PromptGovernanceList,
    PromptLibrarySummary,
    PromptPreviewRequest,
    PromptSaveRequest,
    PromptVersionSummary,
    ProviderCredentialReference,
    ProviderCredentialReferenceRequest,
    ProviderGovernanceList,
    ProviderGovernanceSummary,
    ProviderHealthSummary,
    ProviderProbeDiagnostic,
    RoutingPreviewRequest,
    RoutingPreviewResult,
    RunProvenanceSummary,
    RuntimeProfileGovernanceSummary,
    SafePromptPreview,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminMutationStatus,
    ToastHint,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminNotificationTone,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import PrincipalContext

CURRENT_PROMPT_REVISION = "prompt-rev-qa031-current"
CURRENT_PROFILE_REVISION = "profile-rev-qa031-current"


def build_governance_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> GovernanceDashboard:
    platform_admin = is_platform_admin(principal)
    providers = build_provider_list(scope=scope, principal=principal).providers
    prompts = build_prompt_list(scope=scope).prompts
    profiles = build_profile_list(scope=scope).profiles
    return GovernanceDashboard(
        page_id="react-governance",
        title="Governance",
        description=(
            "Model, provider, prompt, profile, routing, policy, and provenance "
            "governance with safe diagnostics."
        ),
        scope=scope,
        sections=_sections(),
        setup_summary=(
            "Provider credentials are represented by safe references only.",
            "Prompt previews use deterministic fixtures before rendering.",
            "Routing previews are read-only policy evaluations.",
        ),
        providers=providers,
        prompts=prompts,
        profiles=profiles,
        routing_preview=build_routing_preview_result(scope=scope),
        profile_resolution=build_profile_resolution(profile_id=profiles[0].profile_id),
        prompt_preview=build_prompt_preview(
            prompt_lineage_id=prompts[0].prompt_lineage_id,
            request=PromptPreviewRequest(fixture_id="qa031-safe-preview"),
        ),
        policy_history=build_policy_history(scope=scope).history,
        run_provenance=build_run_provenance(scope=scope),
        actions=_dashboard_actions(scope=scope, platform_admin=platform_admin),
    )


def build_provider_list(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> ProviderGovernanceList:
    platform_admin = is_platform_admin(principal)
    providers = [
        ProviderGovernanceSummary(
            provider_id="openai-primary",
            provider_key="openai-primary",
            display_name="OpenAI primary",
            provider_type="OpenAI",
            status=GovernanceStatus.READY,
            tenant_availability="Granted to authorized tenants",
            model_count=3,
            health=ProviderHealthSummary(
                status=GovernanceStatus.READY,
                latency_bucket="under 300 ms",
                breaker_state="closed",
                checked_at_label="Last checked by deterministic QA031 probe",
                summary="Gateway health is ready with credential reference resolved.",
            ),
            credential_reference=ProviderCredentialReference(
                reference_id="secret-ref-openai-primary",
                label="OpenAI production reference",
                source_type="secret manager reference",
                readiness=GovernanceStatus.READY,
                fingerprint="fp_qa031_openai",
                last_resolution_status="resolved by ProviderSecretResolver",
                last_checked_label="Deterministic QA031 check",
                policy_reason="Reference is authorized for gateway use.",
                remediation="No action needed.",
            ),
            local_no_auth_status="Not applicable",
            direct_call_guardrail="ModelGateway-only execution is enforced.",
            authorized_actions=_provider_actions(
                provider_id="openai-primary",
                scope=scope,
                platform_admin=platform_admin,
            ),
            links=(
                AdminAction(
                    action_id="provider-operations",
                    label="Operations evidence",
                    method=AdminActionMethod.GET,
                    href=_with_tenant_query("/admin/app/operations", scope),
                    variant=ReactAdminPageActionVariant.SECONDARY,
                ),
            ),
        ),
        ProviderGovernanceSummary(
            provider_id="local-openai-compatible",
            provider_key="local-openai-compatible",
            display_name="Local compatible provider",
            provider_type="OpenAI-compatible local",
            status=GovernanceStatus.WARNING,
            tenant_availability="Platform diagnostics only"
            if platform_admin
            else "Read-only catalog readiness",
            model_count=1,
            health=ProviderHealthSummary(
                status=GovernanceStatus.DEGRADED,
                latency_bucket="local fixture",
                breaker_state="half open",
                checked_at_label="Last checked by deterministic QA031 probe",
                summary="Local provider is allowed only through the no-auth allowlist.",
            ),
            credential_reference=ProviderCredentialReference(
                reference_id="credential-not-required-local",
                label="No credential required",
                source_type="local allowlist",
                readiness=GovernanceStatus.WARNING,
                fingerprint="fp_qa031_local_allowlist",
                last_resolution_status="no credential resolved",
                last_checked_label="Deterministic QA031 check",
                policy_reason="No-auth is allowed only for the local provider key.",
                remediation="Use a secret reference for non-local providers.",
            ),
            local_no_auth_status="Explicit local allowlist active",
            direct_call_guardrail=(
                "Direct SDK calls are blocked outside gateway adapters."
            ),
            authorized_actions=_provider_actions(
                provider_id="local-openai-compatible",
                scope=scope,
                platform_admin=platform_admin,
            ),
        ),
    ]
    if scope.scope_type == ReactAdminScopeType.TENANT:
        providers = providers[:1]
    return ProviderGovernanceList(providers=tuple(providers))


def build_provider_probe_result(provider_id: str) -> GovernanceMutationResult:
    status = (
        GovernanceStatus.DEGRADED
        if provider_id == "local-openai-compatible"
        else GovernanceStatus.READY
    )
    probe = ProviderProbeDiagnostic(
        probe_id=f"probe-qa031-{provider_id}",
        provider_id=provider_id,
        status=status,
        summary=("Explicit mocked probe completed with safe credential diagnostics."),
        latency_bucket="under 300 ms" if status == GovernanceStatus.READY else "local",
        failure_category=None
        if status == GovernanceStatus.READY
        else "allowlisted_local_no_auth",
        retry_state="no retry needed",
        breaker_state="closed" if status == GovernanceStatus.READY else "half open",
        credential_resolution_status="safe reference selected",
        audit_reference_id=f"audit-governance-probe-qa031-{provider_id}",
        redaction_summary="Attempt evidence is summarized before leaving backend.",
    )
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Provider probe completed with redaction-safe diagnostics.",
        probe=probe,
        diagnostics=(
            "ProviderSecretResolver selected an authorized reference.",
            "Adapter attempt details stayed inside backend diagnostics.",
        ),
        audit_reference_id=probe.audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS
            if status == GovernanceStatus.READY
            else ReactAdminNotificationTone.WARNING,
            title="Provider probe complete",
            summary="Safe diagnostics are ready for review.",
        ),
    )


def build_credential_reference_result(
    *,
    provider_id: str,
    request: ProviderCredentialReferenceRequest,
) -> GovernanceMutationResult:
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Credential reference updated as a safe secret reference.",
        revision=f"provider-rev-qa031-{provider_id}",
        diagnostics=(
            f"Selected reference {request.credential_reference_id} by identifier.",
            "Secret values remain outside React contracts.",
        ),
        audit_reference_id=f"audit-governance-credential-qa031-{provider_id}",
    )


def build_prompt_list(*, scope: ReactAdminScope) -> PromptGovernanceList:
    grant = (
        scope.label if scope.scope_type == ReactAdminScopeType.TENANT else "Platform"
    )
    return PromptGovernanceList(
        prompts=(
            PromptLibrarySummary(
                prompt_lineage_id="daily-briefing",
                name="Daily briefing prompt",
                status=GovernanceStatus.READY,
                draft_version="draft qa031",
                published_version="v3",
                tenant_grants=(grant,),
                render_test_status=GovernanceStatus.READY,
                safe_change_summary=(
                    "Published prompt version has current render tests."
                ),
                history=(
                    PromptVersionSummary(
                        version_id="prompt-v3",
                        label="Published v3",
                        status=GovernanceStatus.READY,
                        safe_change_summary=(
                            "Updated briefing tone and fixture coverage."
                        ),
                        audit_reference_id="audit-prompt-v3-qa031",
                    ),
                    PromptVersionSummary(
                        version_id="prompt-draft",
                        label="Draft qa031",
                        status=GovernanceStatus.WARNING,
                        safe_change_summary="Draft summary awaits review.",
                        audit_reference_id="audit-prompt-draft-qa031",
                    ),
                ),
                authorized_actions=(
                    AdminAction(
                        action_id="prompt-save",
                        label="Save prompt summary",
                        method=AdminActionMethod.POST,
                        href=_with_tenant_query(
                            "/admin/app/governance/prompts/daily-briefing/save",
                            scope,
                        ),
                        variant=ReactAdminPageActionVariant.PRIMARY,
                        requires_idempotency_key=True,
                    ),
                    AdminAction(
                        action_id="prompt-preview",
                        label="Preview prompt",
                        method=AdminActionMethod.POST,
                        href=_with_tenant_query(
                            "/admin/app/governance/prompts/daily-briefing/preview",
                            scope,
                        ),
                        variant=ReactAdminPageActionVariant.SECONDARY,
                    ),
                ),
            ),
        ),
    )


def build_prompt_preview(
    *,
    prompt_lineage_id: str,
    request: PromptPreviewRequest,
) -> SafePromptPreview:
    unsafe_fixture = "unsafe" in request.fixture_id
    return SafePromptPreview(
        preview_id=f"preview-qa031-{request.fixture_id}",
        prompt_lineage_id=prompt_lineage_id,
        fixture_label="Unsafe fixture" if unsafe_fixture else "Safe preview fixture",
        status=GovernanceStatus.SUMMARIZED
        if unsafe_fixture
        else GovernanceStatus.READY,
        safe_output=(
            "Preview was summarized because unsafe prompt or completion text "
            "was detected."
            if unsafe_fixture
            else "Daily briefing preview uses safe fixture variables and summaries."
        ),
        redaction_findings=(
            "Prompt body summarized before rendering.",
            "Completion text blocked before rendering.",
        )
        if unsafe_fixture
        else ("No unsafe preview text returned.",),
        variable_summary="Tenant, date, and briefing scope variables are summarized.",
        artifact_reference_id=f"artifact-ref-qa031-preview-{request.fixture_id}",
        audit_reference_id=f"audit-prompt-preview-qa031-{request.fixture_id}",
    )


def build_prompt_save_result(
    *,
    prompt_lineage_id: str,
    request: PromptSaveRequest,
) -> GovernanceMutationResult:
    status = (
        AdminMutationStatus.CONFIRMATION_REQUIRED
        if request.publish
        else AdminMutationStatus.ACCEPTED
    )
    return GovernanceMutationResult(
        status=status,
        summary="Prompt draft summary saved with safe revision metadata."
        if not request.publish
        else "Confirm publish after reviewing safe prompt version summary.",
        revision=f"{prompt_lineage_id}-rev-qa031-next",
        diagnostics=(
            "Prompt body remains governed by backend prompt services.",
            "Only safe change summary was returned to React.",
        ),
        audit_reference_id=f"audit-prompt-save-qa031-{prompt_lineage_id}",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Prompt saved",
            summary="Safe prompt metadata was updated.",
        ),
    )


def build_profile_list(*, scope: ReactAdminScope) -> ProfileGovernanceList:
    grant = (
        scope.label if scope.scope_type == ReactAdminScopeType.TENANT else "Platform"
    )
    return ProfileGovernanceList(
        profiles=(
            RuntimeProfileGovernanceSummary(
                profile_id="briefing-runtime",
                profile_lineage_id="profile-briefing",
                name="Briefing runtime profile",
                status=GovernanceStatus.READY,
                draft_version="draft qa031",
                published_version="v2",
                model_binding="gpt-qa031-safe-route",
                provider_binding="openai-primary",
                prompt_binding="daily-briefing v3",
                skill_requirements=("weather-readonly", "calendar-readonly"),
                tenant_grants=(grant,),
                resolver_status=GovernanceStatus.READY,
                authorized_actions=(
                    AdminAction(
                        action_id="profile-save",
                        label="Save profile",
                        method=AdminActionMethod.POST,
                        href=_with_tenant_query(
                            "/admin/app/governance/profiles/briefing-runtime/save",
                            scope,
                        ),
                        variant=ReactAdminPageActionVariant.PRIMARY,
                        requires_idempotency_key=True,
                    ),
                    AdminAction(
                        action_id="profile-resolve",
                        label="Resolve profile",
                        method=AdminActionMethod.POST,
                        href=_with_tenant_query(
                            "/admin/app/governance/profiles/briefing-runtime/resolve",
                            scope,
                        ),
                        variant=ReactAdminPageActionVariant.SECONDARY,
                    ),
                ),
            ),
        ),
    )


def build_profile_resolution(profile_id: str) -> ProfileResolutionPreview:
    return ProfileResolutionPreview(
        preview_id=f"profile-resolution-qa031-{profile_id}",
        profile_id=profile_id,
        status=GovernanceStatus.READY,
        selected_profile_version="v2",
        model_route="gpt-qa031-safe-route",
        provider_route="openai-primary through ModelGateway",
        prompt_route="daily-briefing v3",
        skill_route="read-only briefing connectors",
        policy_reasons=(
            "Tenant grant is active.",
            "Provider credential reference is ready.",
            "Skill policy is read-only.",
        ),
        remediation="No action needed.",
        audit_reference_id=f"audit-profile-resolution-qa031-{profile_id}",
    )


def build_profile_save_result(
    *,
    profile_id: str,
    request: ProfileSaveRequest,
) -> GovernanceMutationResult:
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Runtime profile draft saved with safe binding summaries.",
        revision=f"{profile_id}-rev-qa031-next",
        profile_resolution=build_profile_resolution(profile_id),
        diagnostics=(
            f"Model binding {request.model_binding} stored as safe metadata.",
            f"Provider binding {request.provider_binding} remains gateway-controlled.",
        ),
        audit_reference_id=f"audit-profile-save-qa031-{profile_id}",
    )


def build_routing_preview_result(
    *,
    scope: ReactAdminScope,
    request: RoutingPreviewRequest | None = None,
) -> RoutingPreviewResult:
    context = request.workflow_context if request else "Daily briefing workflow"
    return RoutingPreviewResult(
        preview_id="routing-preview-qa031",
        tenant_label=scope.label,
        workflow_context_label=context,
        status=GovernanceStatus.READY,
        model_decision="Use gpt-qa031-safe-route through ModelGateway.",
        provider_decision="OpenAI primary provider selected by policy.",
        skill_decision="Read-only briefing skills are eligible.",
        policy_reasons=(
            "Tenant grant allows prompt and profile.",
            "Provider credential reference is ready.",
            "Direct SDK calls are blocked by policy.",
        ),
        direct_call_guardrail="ModelGateway-only execution preserved.",
        credential_reference_status="Safe reference fingerprint is ready.",
        audit_reference_id="audit-routing-preview-qa031",
        remediation="No routing changes required.",
    )


def build_routing_preview_mutation(
    *,
    scope: ReactAdminScope,
    request: RoutingPreviewRequest,
) -> GovernanceMutationResult:
    preview = build_routing_preview_result(scope=scope, request=request)
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Read-only routing preview completed without runtime side effects.",
        routing_preview=preview,
        diagnostics=(
            "No live providers were invoked.",
            "No direct SDK calls were permitted.",
        ),
        audit_reference_id=preview.audit_reference_id,
    )


def build_policy_history(*, scope: ReactAdminScope) -> PolicyHistoryList:
    return PolicyHistoryList(
        history=(
            PolicyHistoryRecord(
                history_id="history-provider-qa031",
                domain="provider",
                actor_label="Platform Admin",
                tenant_scope_label="Platform",
                timestamp_label="Today",
                change_category="credential_reference_reviewed",
                outcome=GovernanceStatus.READY,
                safe_diff_summary="Credential reference metadata was reviewed.",
                audit_reference_id="audit-history-provider-qa031",
            ),
            PolicyHistoryRecord(
                history_id="history-routing-qa031",
                domain="routing",
                actor_label="Policy Resolver",
                tenant_scope_label=scope.label,
                timestamp_label="Today",
                change_category="routing_preview",
                outcome=GovernanceStatus.READY,
                safe_diff_summary=(
                    "Model and skill routing evaluated without side effects."
                ),
                audit_reference_id="audit-history-routing-qa031",
            ),
        ),
    )


def build_run_provenance(*, scope: ReactAdminScope) -> tuple[RunProvenanceSummary, ...]:
    return (
        RunProvenanceSummary(
            run_id="run-qa031-briefing",
            tenant_label=scope.label,
            workflow_label="Daily briefing workflow",
            started_at_label="Deterministic QA031 run",
            provider_evidence="OpenAI primary provider via gateway attempt summary.",
            model_evidence="gpt-qa031-safe-route pinned in runtime bundle.",
            prompt_evidence="daily-briefing prompt v3 safe version reference.",
            profile_evidence="Briefing runtime profile v2 selected.",
            routing_evidence="Routing preview policy reasons match runtime provenance.",
            credential_reference_evidence="Credential reference fingerprint was ready.",
            usage_evidence="Usage summary is available as token and cost metadata.",
            audit_reference_id="audit-run-provenance-qa031",
        ),
    )


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def _sections() -> tuple[GovernanceSection, ...]:
    return (
        GovernanceSection(
            section_id="setup",
            label="Setup",
            status=GovernanceStatus.WARNING,
            summary=(
                "Readiness across providers, prompts, profiles, routing, and "
                "provenance."
            ),
        ),
        GovernanceSection(
            section_id="providers",
            label="Providers",
            status=GovernanceStatus.READY,
            summary="Credential references, health, probes, and guardrail evidence.",
        ),
        GovernanceSection(
            section_id="prompts",
            label="Prompts",
            status=GovernanceStatus.READY,
            summary="Prompt versions, safe summaries, and fixture-backed previews.",
        ),
        GovernanceSection(
            section_id="profiles",
            label="Profiles",
            status=GovernanceStatus.READY,
            summary="Runtime profile bindings, grants, and resolution previews.",
        ),
        GovernanceSection(
            section_id="routing",
            label="Routing",
            status=GovernanceStatus.READY,
            summary="Read-only model and skill policy evaluation.",
        ),
        GovernanceSection(
            section_id="provenance",
            label="Provenance",
            status=GovernanceStatus.READY,
            summary="Policy history and run evidence without raw payloads.",
        ),
    )


def _dashboard_actions(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> tuple[AdminAction, ...]:
    actions = [
        AdminAction(
            action_id="routing-preview",
            label="Preview routing",
            method=AdminActionMethod.POST,
            href=_with_tenant_query("/admin/app/governance/routing/preview", scope),
            variant=ReactAdminPageActionVariant.SECONDARY,
        ),
    ]
    if platform_admin:
        actions.append(
            AdminAction(
                action_id="provider-probe-openai-primary",
                label="Probe OpenAI primary",
                method=AdminActionMethod.POST,
                href="/admin/app/governance/providers/openai-primary/probe",
                variant=ReactAdminPageActionVariant.PRIMARY,
            )
        )
    return tuple(actions)


def _provider_actions(
    *,
    provider_id: str,
    scope: ReactAdminScope,
    platform_admin: bool,
) -> tuple[AdminAction, ...]:
    if not platform_admin:
        return ()
    return (
        AdminAction(
            action_id=f"provider-probe-{provider_id}",
            label="Run probe",
            method=AdminActionMethod.POST,
            href=f"/admin/app/governance/providers/{provider_id}/probe",
            variant=ReactAdminPageActionVariant.PRIMARY,
        ),
        AdminAction(
            action_id=f"credential-reference-{provider_id}",
            label="Save credential reference",
            method=AdminActionMethod.POST,
            href=(
                f"/admin/app/governance/providers/{provider_id}/credential-reference"
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
