from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.api.schemas.admin_governance import (
    GovernanceDashboard,
    GovernanceLegacyRouteMapping,
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
    empty_governance_state,
    live_governance_provenance,
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
from multi_agent_platform.db.repositories.agent_profiles import (
    AgentProfileRepository,
    StaleAgentProfileRevisionError,
)
from multi_agent_platform.db.repositories.model_providers import (
    ModelProviderRepository,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)
from multi_agent_platform.db.repositories.prompts import (
    PromptRepository,
    StalePromptRevisionError,
)
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderTestSummary,
    TestOutcome,
)


async def build_governance_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    provider_repository: ModelProviderRepository,
    prompt_repository: PromptRepository,
    profile_repository: AgentProfileRepository,
    config_repository: ModelSkillConfigRepository,
) -> GovernanceDashboard:
    provider_list = await build_provider_list(
        scope=scope,
        principal=principal,
        provider_repository=provider_repository,
    )
    prompt_list = await build_prompt_list(
        scope=scope,
        principal=principal,
        prompt_repository=prompt_repository,
    )
    profile_list = await build_profile_list(
        scope=scope,
        principal=principal,
        profile_repository=profile_repository,
    )
    policy_history = await build_policy_history(
        scope=scope,
        config_repository=config_repository,
    )
    routing_preview = await build_routing_preview_result(
        scope=scope,
        config_repository=config_repository,
    )
    prompt_preview = None
    if prompt_list.prompts:
        prompt_preview = await build_prompt_preview(
            prompt_lineage_id=prompt_list.prompts[0].prompt_lineage_id,
            request=PromptPreviewRequest(fixture_id="latest-safe-summary"),
            prompt_repository=prompt_repository,
        )
    profile_resolution = None
    if profile_list.profiles:
        profile_resolution = await build_profile_resolution(
            profile_id=profile_list.profiles[0].profile_id,
            scope=scope,
            profile_repository=profile_repository,
        )
    run_provenance = await build_run_provenance_list(
        scope=scope,
        config_repository=config_repository,
    )
    has_live_data = any(
        (
            provider_list.providers,
            prompt_list.prompts,
            profile_list.profiles,
            policy_history.history,
            run_provenance,
        )
    )
    return GovernanceDashboard(
        page_id="react-governance",
        title="Governance",
        description=(
            "Model, provider, prompt, profile, routing, policy, and provenance "
            "governance with safe diagnostics."
        ),
        scope=scope,
        sections=_sections(
            provider_count=len(provider_list.providers),
            prompt_count=len(prompt_list.prompts),
            profile_count=len(profile_list.profiles),
            policy_count=len(policy_history.history),
            provenance_count=len(run_provenance),
        ),
        setup_summary=_setup_summary(
            provider_list=provider_list,
            prompt_list=prompt_list,
            profile_list=profile_list,
        ),
        providers=provider_list.providers,
        prompts=prompt_list.prompts,
        profiles=profile_list.profiles,
        routing_preview=routing_preview,
        profile_resolution=profile_resolution,
        prompt_preview=prompt_preview,
        policy_history=policy_history.history,
        run_provenance=run_provenance,
        legacy_routes=build_governance_legacy_route_mappings(scope=scope),
        actions=_dashboard_actions(
            scope=scope,
            platform_admin=is_platform_admin(principal),
            has_routing_context=routing_preview is not None,
        ),
        provenance=live_governance_provenance(
            source_label="Governance records",
            source_detail=(
                "Providers, prompts, profiles, policy history, diagnostics, "
                "and provenance are projected from durable governance stores."
            ),
        )
        if has_live_data
        else None,
        empty_state=None
        if has_live_data
        else empty_governance_state(
            title="No governance records found",
            summary=(
                "This scope does not yet have providers, prompts, profiles, "
                "policy history, diagnostics, or provenance evidence."
            ),
            setup_hint=(
                "Create provider, prompt, profile, or routing records through "
                "governed setup flows."
            ),
            source_label="Governance records",
        ),
    )


async def build_provider_list(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    provider_repository: ModelProviderRepository,
) -> ProviderGovernanceList:
    tenant_id = _scope_tenant_uuid(scope)
    platform_scope = (
        scope.scope_type == ReactAdminScopeType.PLATFORM
        and is_platform_admin(principal)
    )
    providers = await provider_repository.list_connections(
        tenant_id=tenant_id,
        platform_scope=platform_scope,
    )
    summaries: list[ProviderGovernanceSummary] = []
    for provider in providers:
        connection = await provider_repository.get_connection(
            provider.provider_connection_id
        )
        latest_test = await provider_repository.latest_test(
            provider.provider_connection_id
        )
        visible_tenants = await provider_repository.visible_tenant_ids(
            provider.provider_connection_id
        )
        credential_ids = tuple(connection.credential_secret_reference_ids or ())
        summaries.append(
            ProviderGovernanceSummary(
                provider_id=str(provider.provider_connection_id),
                provider_key=str(provider.provider_connection_id),
                display_name=provider.display_name,
                provider_type=provider.provider_type.value,
                status=_status_from_provider_health(provider.health_state),
                tenant_availability=_tenant_availability(
                    scope=scope,
                    visible_tenants=visible_tenants,
                    active=provider.active,
                ),
                model_count=provider.model_count,
                health=ProviderHealthSummary(
                    status=_status_from_provider_health(provider.health_state),
                    latency_bucket=_latency_bucket(
                        latest_test.latency_ms if latest_test else None
                    ),
                    breaker_state="closed"
                    if provider.health_state is HealthState.HEALTHY
                    else provider.health_state.value,
                    checked_at_label=_timestamp_label(
                        latest_test.completed_at if latest_test else provider.updated_at
                    ),
                    summary=latest_test.safe_diagnostic_summary
                    if latest_test
                    else "No provider health check has been recorded.",
                ),
                credential_reference=ProviderCredentialReference(
                    reference_id=credential_ids[0]
                    if credential_ids
                    else "unconfigured",
                    label="Configured secret reference"
                    if credential_ids
                    else "No credential reference configured",
                    source_type="secret reference"
                    if credential_ids
                    else "not configured",
                    readiness=GovernanceStatus.READY
                    if credential_ids
                    else GovernanceStatus.UNAVAILABLE,
                    fingerprint=_safe_fingerprint(credential_ids[0])
                    if credential_ids
                    else None,
                    last_resolution_status="Reference metadata is configured."
                    if credential_ids
                    else "No safe credential reference is configured.",
                    last_checked_label=_timestamp_label(
                        latest_test.completed_at if latest_test else provider.updated_at
                    ),
                    policy_reason="Provider calls remain gateway-controlled.",
                    remediation=(
                        "Add a credential reference before enabling live "
                        "provider calls."
                    )
                    if not credential_ids
                    else "No remediation required.",
                ),
                local_no_auth_status="Local allowlist metadata present"
                if connection.allowlist_decision_hash
                else "No local no-auth allowlist evidence",
                direct_call_guardrail="ModelGateway-only execution is enforced.",
                authorized_actions=_provider_actions(
                    provider_id=str(provider.provider_connection_id),
                    platform_admin=is_platform_admin(principal),
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
            )
        )
    return ProviderGovernanceList(
        providers=tuple(summaries),
        provenance=live_governance_provenance(
            source_label="Provider connection records",
            source_detail=(
                "Provider summaries are read from model provider connection, "
                "visibility, model, and health records."
            ),
        )
        if summaries
        else None,
        empty_state=None
        if summaries
        else empty_governance_state(
            title="No provider connections found",
            summary="No authorized live provider connections exist for this scope.",
            setup_hint=(
                "Create a provider connection through provider governance "
                "before running probes."
            ),
            source_label="Provider connection records",
        ),
    )


async def build_provider_probe_result(
    *,
    provider_id: str,
    provider_repository: ModelProviderRepository,
    principal: PrincipalContext,
) -> GovernanceMutationResult:
    provider_uuid = _parse_uuid(provider_id)
    if provider_uuid is None:
        return _unavailable_result("Provider probe unavailable for unknown provider.")
    try:
        connection = await provider_repository.get_connection(provider_uuid)
    except LookupError:
        return _unavailable_result("Provider probe unavailable for unknown provider.")
    models = await provider_repository.list_models(connection.provider_connection_id)
    tested_model = models[0].model_id if models else None
    now = datetime.now(UTC)
    result = ProviderTestSummary(
        outcome=TestOutcome.SUCCESS,
        normalized_reason=ErrorCategory.NONE,
        latency_ms=0,
        tested_model_id=tested_model,
        safe_diagnostic_summary="Local QA provider probe recorded safe metadata only.",
        safe_provider_request_id=None,
        completed_at=now,
    )
    record = await provider_repository.append_test_result(
        connection=connection,
        model_definition_id=models[0].provider_model_definition_id if models else None,
        actor_principal_id=principal.principal_id,
        started_at=now,
        result=result,
    )
    await provider_repository.update_health(
        connection=connection,
        health_state=HealthState.HEALTHY,
        reason="Local QA safe probe completed.",
        test_result_id=record.connection_test_result_id,
        selectable=connection.active,
    )
    probe = ProviderProbeDiagnostic(
        probe_id=str(record.connection_test_result_id),
        provider_id=str(connection.provider_connection_id),
        status=GovernanceStatus.READY,
        summary=record.safe_diagnostic_summary,
        latency_bucket=_latency_bucket(record.latency_ms),
        failure_category=None,
        retry_state="no retry needed",
        breaker_state="closed",
        credential_resolution_status="safe metadata only",
        audit_reference_id=f"provider-test:{record.connection_test_result_id}",
        redaction_summary="Provider attempt details stayed inside backend diagnostics.",
    )
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Provider probe completed with redaction-safe diagnostics.",
        probe=probe,
        diagnostics=("No external provider call was required for local QA.",),
        audit_reference_id=probe.audit_reference_id,
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Provider probe complete",
            summary="Safe diagnostics are ready for review.",
        ),
    )


async def build_credential_reference_result(
    *,
    provider_id: str,
    request: ProviderCredentialReferenceRequest,
    provider_repository: ModelProviderRepository,
) -> GovernanceMutationResult:
    provider_uuid = _parse_uuid(provider_id)
    if provider_uuid is None:
        return _unavailable_result(
            "Credential reference update unavailable for unknown provider."
        )
    try:
        connection = await provider_repository.get_connection(provider_uuid)
    except LookupError:
        return _unavailable_result(
            "Credential reference update unavailable for unknown provider."
        )
    connection.credential_secret_reference_ids = [request.credential_reference_id]
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Credential reference metadata saved without exposing secret values.",
        revision=f"provider:{connection.provider_connection_id}",
        diagnostics=("Secret values remain outside admin contracts.",),
        audit_reference_id=f"provider-credential:{connection.provider_connection_id}",
    )


async def build_prompt_list(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    prompt_repository: PromptRepository,
) -> PromptGovernanceList:
    tenant_id = _scope_tenant_uuid(scope) or principal.tenant_id
    lineages = await prompt_repository.list_visible_lineages(
        principal_tenant_id=tenant_id,
        include_platform_admin=scope.scope_type == ReactAdminScopeType.PLATFORM
        and is_platform_admin(principal),
    )
    prompts: list[PromptLibrarySummary] = []
    for lineage in lineages:
        draft = await prompt_repository.get_active_draft(lineage.prompt_lineage_id)
        latest_revision = (
            await prompt_repository.get_latest_revision(draft) if draft else None
        )
        validation = (
            await prompt_repository.get_validation_result(
                draft.last_validation_result_id
            )
            if draft
            else None
        )
        versions = await prompt_repository.list_versions_for_lineage(
            lineage.prompt_lineage_id
        )
        active_versions = [
            version for version in versions if version.status == "active"
        ]
        published = active_versions[0] if active_versions else None
        grant_labels: tuple[str, ...] = ()
        if published is not None:
            grants = await prompt_repository.list_grants_for_version(
                published.prompt_version_id
            )
            grant_labels = tuple(str(grant.grantee_tenant_id) for grant in grants)
        prompts.append(
            PromptLibrarySummary(
                prompt_lineage_id=str(lineage.prompt_lineage_id),
                name=lineage.display_name,
                status=_status_from_record_status(lineage.status),
                draft_version=f"draft r{draft.current_revision_number}"
                if draft
                else None,
                published_version=published.display_version if published else None,
                tenant_grants=grant_labels,
                render_test_status=_status_from_validation(validation.status)
                if validation
                else GovernanceStatus.UNAVAILABLE,
                safe_change_summary=_summary_from_mapping(
                    latest_revision.safe_summary_json
                    if latest_revision
                    else (published.safe_summary_json if published else {}),
                    fallback="No safe prompt summary has been recorded.",
                ),
                history=tuple(
                    PromptVersionSummary(
                        version_id=str(version.prompt_version_id),
                        label=version.display_version,
                        status=_status_from_record_status(version.status),
                        safe_change_summary=_summary_from_mapping(
                            version.safe_summary_json,
                            fallback=version.publication_reason,
                        ),
                        audit_reference_id=f"prompt-version:{version.prompt_version_id}",
                    )
                    for version in versions[:5]
                ),
                authorized_actions=_prompt_actions(
                    prompt_lineage_id=str(lineage.prompt_lineage_id),
                    scope=scope,
                    draft=draft is not None,
                ),
            )
        )
    return PromptGovernanceList(
        prompts=tuple(prompts),
        provenance=live_governance_provenance(
            source_label="Prompt library records",
            source_detail=(
                "Prompt summaries are read from prompt lineages, drafts, "
                "versions, validations, and grants."
            ),
        )
        if prompts
        else None,
        empty_state=None
        if prompts
        else empty_governance_state(
            title="No prompts found",
            summary="No authorized live prompt records exist for this scope.",
            setup_hint="Create a prompt draft before previewing governance evidence.",
            source_label="Prompt library records",
        ),
    )


async def build_prompt_preview(
    *,
    prompt_lineage_id: str,
    request: PromptPreviewRequest,
    prompt_repository: PromptRepository,
) -> SafePromptPreview:
    lineage_id = _parse_uuid(prompt_lineage_id)
    if lineage_id is None:
        return _unavailable_prompt_preview(prompt_lineage_id, request.fixture_id)
    draft = await prompt_repository.get_active_draft(lineage_id)
    latest_revision = (
        await prompt_repository.get_latest_revision(draft) if draft else None
    )
    if latest_revision is None:
        return _unavailable_prompt_preview(prompt_lineage_id, request.fixture_id)
    return SafePromptPreview(
        preview_id=f"prompt-preview:{latest_revision.prompt_draft_revision_id}",
        prompt_lineage_id=prompt_lineage_id,
        fixture_label=request.fixture_id,
        status=GovernanceStatus.SUMMARIZED,
        safe_output=_summary_from_mapping(
            latest_revision.safe_summary_json,
            fallback="Prompt preview is summarized before rendering.",
        ),
        redaction_findings=("Protected prompt content is summarized.",),
        variable_summary=_variable_summary(latest_revision.variable_declarations_json),
        artifact_reference_id=None,
        audit_reference_id=f"prompt-revision:{latest_revision.prompt_draft_revision_id}",
    )


async def build_prompt_save_result(
    *,
    prompt_lineage_id: str,
    request: PromptSaveRequest,
    prompt_repository: PromptRepository,
    principal: PrincipalContext,
) -> GovernanceMutationResult:
    lineage_id = _parse_uuid(prompt_lineage_id)
    if lineage_id is None:
        return _unavailable_result("Prompt save unavailable for unknown prompt.")
    lineage = await prompt_repository.get_lineage(lineage_id)
    draft = await prompt_repository.get_active_draft(lineage_id)
    latest_revision = (
        await prompt_repository.get_latest_revision(draft) if draft else None
    )
    if lineage is None or draft is None or latest_revision is None:
        return _unavailable_result("Prompt save unavailable until a live draft exists.")
    try:
        revision = await prompt_repository.save_draft_revision(
            draft=draft,
            expected_revision_number=draft.current_revision_number,
            prompt_title=latest_revision.prompt_title,
            purpose=lineage.purpose,
            usage_notes=latest_revision.usage_notes,
            template_content=latest_revision.template_content,
            variable_declarations=latest_revision.variable_declarations_json,
            fixture_value_sets=latest_revision.fixture_value_sets_json,
            safe_summary={
                **latest_revision.safe_summary_json,
                "summary": request.safe_summary,
                "saved_via": "governance_react_live_data",
            },
            principal_id=principal.principal_id,
        )
    except StalePromptRevisionError:
        return GovernanceMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Prompt draft revision is stale; refresh before saving.",
        )
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Prompt draft summary saved with durable revision metadata.",
        revision=f"draft r{revision.revision_number}",
        diagnostics=("Only safe prompt metadata was returned to Admin.",),
        audit_reference_id=f"prompt-revision:{revision.prompt_draft_revision_id}",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Prompt saved",
            summary="Safe prompt metadata was updated.",
        ),
    )


async def build_profile_list(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    profile_repository: AgentProfileRepository,
) -> ProfileGovernanceList:
    tenant_id = _scope_tenant_uuid(scope) or principal.tenant_id
    profiles = await profile_repository.list_visible_profiles(
        principal_tenant_id=tenant_id,
        include_platform_admin=scope.scope_type == ReactAdminScopeType.PLATFORM
        and is_platform_admin(principal),
    )
    summaries: list[RuntimeProfileGovernanceSummary] = []
    for profile in profiles:
        draft = await profile_repository.get_active_draft(
            profile.agent_runtime_profile_id
        )
        latest_revision = (
            await profile_repository.get_latest_revision(draft) if draft else None
        )
        active_version = (
            await profile_repository.get_profile_version(
                profile.active_profile_version_id
            )
            if profile.active_profile_version_id
            else None
        )
        prompt_binding = _prompt_binding_label(
            latest_revision.prompt_references_json
            if latest_revision
            else (active_version.prompt_references_json if active_version else [])
        )
        routing_hints = (
            latest_revision.model_routing_hints_json
            if latest_revision
            else (active_version.model_routing_hints_json if active_version else {})
        )
        summaries.append(
            RuntimeProfileGovernanceSummary(
                profile_id=str(profile.agent_runtime_profile_id),
                profile_lineage_id=str(profile.agent_runtime_profile_id),
                name=profile.display_name,
                status=_status_from_record_status(profile.status),
                draft_version=f"draft r{draft.current_revision_number}"
                if draft
                else None,
                published_version=active_version.display_version
                if active_version
                else "unavailable",
                model_binding=str(routing_hints.get("model_id", "unavailable")),
                provider_binding=str(routing_hints.get("provider_key", "unavailable")),
                prompt_binding=prompt_binding,
                skill_requirements=_skill_labels(
                    latest_revision.skill_requirements_json
                    if latest_revision
                    else (
                        active_version.skill_requirements_json if active_version else []
                    )
                ),
                tenant_grants=await _profile_grant_labels(
                    profile_repository=profile_repository,
                    active_version_id=profile.active_profile_version_id,
                ),
                resolver_status=GovernanceStatus.READY
                if active_version or draft
                else GovernanceStatus.UNAVAILABLE,
                authorized_actions=_profile_actions(
                    profile_id=str(profile.agent_runtime_profile_id),
                    scope=scope,
                    draft=draft is not None,
                ),
            )
        )
    return ProfileGovernanceList(
        profiles=tuple(summaries),
        provenance=live_governance_provenance(
            source_label="Runtime profile records",
            source_detail=(
                "Profile summaries are read from runtime profile drafts, "
                "versions, validations, pointers, and grants."
            ),
        )
        if summaries
        else None,
        empty_state=None
        if summaries
        else empty_governance_state(
            title="No runtime profiles found",
            summary="No authorized live runtime profile records exist for this scope.",
            setup_hint=(
                "Create a runtime profile draft before resolving profile governance."
            ),
            source_label="Runtime profile records",
        ),
    )


async def build_profile_resolution(
    *,
    profile_id: str,
    scope: ReactAdminScope,
    profile_repository: AgentProfileRepository,
) -> ProfileResolutionPreview:
    profile_uuid = _parse_uuid(profile_id)
    if profile_uuid is None:
        return _unavailable_profile_resolution(profile_id)
    profile = await profile_repository.get_profile(profile_uuid)
    if profile is None:
        return _unavailable_profile_resolution(profile_id)
    tenant_id = _scope_tenant_uuid(scope)
    pointer = None
    if tenant_id is not None:
        pointer = await profile_repository.resolve_active_pointer(
            scope_type=profile.scope_type,
            tenant_id=profile.tenant_id,
            agent_kind=profile.agent_kind,
            agent_key=profile.agent_key,
        )
    active_version_id = (
        pointer.active_profile_version_id
        if pointer is not None
        else profile.active_profile_version_id
    )
    active_version = (
        await profile_repository.get_profile_version(active_version_id)
        if active_version_id
        else None
    )
    return ProfileResolutionPreview(
        preview_id=f"profile-resolution:{profile.agent_runtime_profile_id}",
        profile_id=profile_id,
        status=GovernanceStatus.READY
        if active_version
        else GovernanceStatus.UNAVAILABLE,
        selected_profile_version=active_version.display_version
        if active_version
        else "unavailable",
        model_route=str(
            (active_version.model_routing_hints_json if active_version else {}).get(
                "model_id", "unavailable"
            )
        ),
        provider_route=str(
            (active_version.model_routing_hints_json if active_version else {}).get(
                "provider_key", "unavailable"
            )
        ),
        prompt_route=_prompt_binding_label(
            active_version.prompt_references_json if active_version else []
        ),
        skill_route=", ".join(
            _skill_labels(active_version.skill_requirements_json)
            if active_version
            else ("unavailable",)
        ),
        policy_reasons=(
            "Profile resolution used authorized live profile records.",
            "Protected prompt content remains summarized.",
        )
        if active_version
        else ("No active profile version is available for this scope.",),
        remediation="No action needed."
        if active_version
        else "Activate a profile version before relying on resolution.",
        audit_reference_id=f"profile:{profile.agent_runtime_profile_id}",
    )


async def build_profile_save_result(
    *,
    profile_id: str,
    request: ProfileSaveRequest,
    profile_repository: AgentProfileRepository,
    principal: PrincipalContext,
) -> GovernanceMutationResult:
    profile_uuid = _parse_uuid(profile_id)
    if profile_uuid is None:
        return _unavailable_result("Profile save unavailable for unknown profile.")
    profile = await profile_repository.get_profile(profile_uuid)
    draft = (
        await profile_repository.get_active_draft(profile.agent_runtime_profile_id)
        if profile
        else None
    )
    latest_revision = (
        await profile_repository.get_latest_revision(draft) if draft else None
    )
    if profile is None or draft is None or latest_revision is None:
        return _unavailable_result(
            "Profile save unavailable until a live draft exists."
        )
    routing_hints = dict(latest_revision.model_routing_hints_json)
    routing_hints["model_id"] = request.model_binding
    routing_hints["provider_key"] = request.provider_binding
    try:
        revision = await profile_repository.save_draft_revision(
            draft=draft,
            expected_revision_number=draft.current_revision_number,
            purpose=latest_revision.purpose,
            prompt_references=latest_revision.prompt_references_json,
            model_routing_hints=routing_hints,
            memory_scope_policy=latest_revision.memory_scope_policy_json,
            skill_requirements=latest_revision.skill_requirements_json,
            tool_policy_expectations=latest_revision.tool_policy_expectations_json,
            output_contract_expectations=latest_revision.output_contract_expectations_json,
            test_suite_requirements=latest_revision.test_suite_requirements_json,
            safe_summary={
                **latest_revision.safe_summary_json,
                "saved_via": "governance_react_live_data",
            },
            principal_id=principal.principal_id,
        )
    except StaleAgentProfileRevisionError:
        return GovernanceMutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Runtime profile draft revision is stale; refresh before saving.",
        )
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Runtime profile draft saved with safe binding summaries.",
        revision=f"draft r{revision.revision_number}",
        diagnostics=("Provider and model bindings remain gateway-controlled.",),
        audit_reference_id=f"profile-revision:{revision.agent_profile_draft_revision_id}",
    )


async def build_routing_preview_result(
    *,
    scope: ReactAdminScope,
    config_repository: ModelSkillConfigRepository,
    request: RoutingPreviewRequest | None = None,
) -> RoutingPreviewResult | None:
    tenant_id = _scope_tenant_uuid(scope)
    if tenant_id is None:
        return None
    routes = await config_repository.list_active_model_routes(tenant_id)
    prompt_refs = await config_repository.list_active_prompt_references(tenant_id)
    skills = await config_repository.list_active_skill_bindings(tenant_id)
    policies = await config_repository.list_active_tool_policies(tenant_id)
    if not any((routes, prompt_refs, skills, policies)):
        return None
    context = request.workflow_context if request else "Active governance scope"
    return RoutingPreviewResult(
        preview_id=f"routing-preview:{tenant_id}",
        tenant_label=scope.label,
        workflow_context_label=context,
        status=GovernanceStatus.READY,
        model_decision=f"{len(routes)} active model route(s)",
        provider_decision="Provider selection remains gateway-controlled.",
        skill_decision=f"{len(skills)} active skill binding(s)",
        policy_reasons=(
            f"{len(prompt_refs)} prompt reference(s) active.",
            f"{len(policies)} tool policy record(s) active.",
        ),
        direct_call_guardrail="ModelGateway-only execution preserved.",
        credential_reference_status=(
            "Credential policy is evaluated by backend configuration."
        ),
        audit_reference_id=f"routing-preview:{tenant_id}",
        remediation="No action needed.",
    )


async def build_routing_preview_mutation(
    *,
    scope: ReactAdminScope,
    request: RoutingPreviewRequest,
    config_repository: ModelSkillConfigRepository,
) -> GovernanceMutationResult:
    preview = await build_routing_preview_result(
        scope=scope,
        config_repository=config_repository,
        request=request,
    )
    if preview is None:
        return _unavailable_result(
            "Routing preview unavailable until policy records exist."
        )
    return GovernanceMutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Read-only routing preview completed without runtime side effects.",
        routing_preview=preview,
        diagnostics=("No live providers were invoked.",),
        audit_reference_id=preview.audit_reference_id,
    )


async def build_policy_history(
    *,
    scope: ReactAdminScope,
    config_repository: ModelSkillConfigRepository,
) -> PolicyHistoryList:
    tenant_id = _scope_tenant_uuid(scope)
    if tenant_id is None:
        return PolicyHistoryList(
            empty_state=empty_governance_state(
                title="No tenant policy history selected",
                summary="Select a tenant scope to inspect tenant policy history.",
                source_label="Policy history records",
            )
        )
    records = await config_repository.list_history(tenant_id=tenant_id, limit=25)
    history = tuple(
        PolicyHistoryRecord(
            history_id=str(record.configuration_audit_record_id),
            domain=record.config_kind.value,
            actor_label=record.actor_role or "system",
            tenant_scope_label=scope.label,
            timestamp_label=_timestamp_label(record.created_at),
            change_category=record.action,
            outcome=GovernanceStatus.READY,
            safe_diff_summary=_summary_from_mapping(
                record.redacted_diff_summary,
                fallback=record.reason,
            ),
            audit_reference_id=f"configuration-audit:{record.configuration_audit_record_id}",
        )
        for record in records
    )
    return PolicyHistoryList(
        history=history,
        provenance=live_governance_provenance(
            source_label="Policy history records",
            source_detail="Policy history is read from configuration audit records.",
        )
        if history
        else None,
        empty_state=None
        if history
        else empty_governance_state(
            title="No policy history found",
            summary="No policy or routing history exists for this tenant scope.",
            source_label="Policy history records",
        ),
    )


async def build_run_provenance_list(
    *,
    scope: ReactAdminScope,
    config_repository: ModelSkillConfigRepository,
) -> tuple[RunProvenanceSummary, ...]:
    _ = scope
    _ = config_repository
    return ()


async def build_run_provenance(
    *,
    scope: ReactAdminScope,
    run_id: str,
    config_repository: ModelSkillConfigRepository,
) -> RunProvenanceSummary:
    tenant_id = _scope_tenant_uuid(scope)
    run_uuid = _parse_uuid(run_id)
    resolved = None
    decisions = []
    if tenant_id is not None and run_uuid is not None:
        resolved = await config_repository.get_resolved_configuration_for_run(
            tenant_id=tenant_id,
            workflow_run_id=run_uuid,
        )
        decisions = await config_repository.list_run_decisions(
            tenant_id=tenant_id,
            workflow_run_id=run_uuid,
        )
    if resolved is None:
        return RunProvenanceSummary(
            run_id=run_id,
            tenant_label=scope.label,
            workflow_label="Unavailable",
            started_at_label="Unavailable",
            provider_evidence="No redaction-safe provider evidence is available.",
            model_evidence="No redaction-safe model route evidence is available.",
            prompt_evidence="No redaction-safe prompt reference evidence is available.",
            profile_evidence="No redaction-safe runtime profile evidence is available.",
            routing_evidence="No redaction-safe routing evidence is available.",
            credential_reference_evidence=(
                "No redaction-safe credential evidence is available."
            ),
            usage_evidence="No redaction-safe usage evidence is available.",
            audit_reference_id=f"run-provenance:{run_id}",
        )
    return RunProvenanceSummary(
        run_id=run_id,
        tenant_label=scope.label,
        workflow_label=str(resolved.workflow_version_bundle_id),
        started_at_label=_timestamp_label(resolved.accepted_at),
        provider_evidence=(
            f"{len(resolved.model_routing_version_ids)} model route reference(s)"
        ),
        model_evidence=f"Resolution digest {resolved.resolution_digest[:12]}",
        prompt_evidence=(
            f"{len(resolved.prompt_reference_version_ids)} prompt reference(s)"
        ),
        profile_evidence="Runtime profile evidence is summarized in the run bundle.",
        routing_evidence=f"{len(decisions)} runtime policy decision(s)",
        credential_reference_evidence=(
            f"{len(resolved.secret_reference_version_ids)} secret reference(s)"
        ),
        usage_evidence="Usage is available through usage analytics when recorded.",
        audit_reference_id=f"resolved-configuration:{resolved.resolved_execution_configuration_id}",
    )


def build_governance_legacy_route_mappings(
    *,
    scope: ReactAdminScope,
) -> tuple[GovernanceLegacyRouteMapping, ...]:
    _ = scope
    mappings = (
        ("/admin/model-providers", "/admin/app/governance/providers"),
        ("/admin/model-providers/new", "/admin/app/governance/providers/new"),
        ("/admin/model-providers/catalog", "/admin/app/governance/providers"),
        (
            "/admin/model-providers/{connection_id}",
            "/admin/app/governance/providers/{connection_id}",
        ),
        (
            "/admin/model-providers/{connection_id}/edit",
            "/admin/app/governance/providers/{connection_id}/edit",
        ),
        ("/admin/prompt-runtime/prompts", "/admin/app/governance/prompts"),
        ("/admin/prompt-runtime/prompts/new", "/admin/app/governance/prompts/new"),
        (
            "/admin/prompt-runtime/prompts/{prompt_lineage_id}/edit",
            "/admin/app/governance/prompts/{prompt_lineage_id}/edit",
        ),
        (
            "/admin/prompt-runtime/prompts/{prompt_lineage_id}/history",
            "/admin/app/governance/prompts/{prompt_lineage_id}/history",
        ),
        (
            "/admin/prompt-runtime/prompts/{prompt_lineage_id}/preview",
            "/admin/app/governance/prompts/{prompt_lineage_id}/preview",
        ),
        ("/admin/prompt-runtime/profiles", "/admin/app/governance/profiles"),
        ("/admin/prompt-runtime/profiles/new", "/admin/app/governance/profiles/new"),
        (
            "/admin/prompt-runtime/profiles/{profile_id}/edit",
            "/admin/app/governance/profiles/{profile_id}/edit",
        ),
        (
            "/admin/prompt-runtime/profiles/{profile_id}/history",
            "/admin/app/governance/profiles/{profile_id}/history",
        ),
        (
            "/admin/prompt-runtime/profiles/resolve",
            "/admin/app/governance/profiles/resolve",
        ),
        ("/admin/config/ui", "/admin/app/governance/routing"),
        ("/admin/config/ui/history", "/admin/app/governance/history"),
        (
            "/admin/config/ui/runs/{workflow_run_id}/provenance",
            "/admin/app/governance/provenance/{workflow_run_id}",
        ),
    )
    return tuple(
        GovernanceLegacyRouteMapping(
            legacy_path=legacy_path,
            react_path=react_path,
            preserved_params=(
                "tenant_id",
                "q",
                "status",
                "revision",
                "agent_key",
                "agent_kind",
                "config_kind",
                "workflow_run_id",
            ),
            compatibility_status="redirected",
            authorization_behavior="authenticated redirect with backend JSON denial",
            evidence_summary=(
                "Legacy governance browser route redirects to Admin and no "
                "longer renders a governance template."
            ),
        )
        for legacy_path, react_path in mappings
    )


def is_platform_admin(principal: PrincipalContext) -> bool:
    return "platform_admin" in principal.role_codes


def _sections(
    *,
    provider_count: int,
    prompt_count: int,
    profile_count: int,
    policy_count: int,
    provenance_count: int,
) -> tuple[GovernanceSection, ...]:
    return (
        _section("setup", "Setup", provider_count + prompt_count + profile_count),
        _section("providers", "Providers", provider_count),
        _section("prompts", "Prompts", prompt_count),
        _section("profiles", "Profiles", profile_count),
        _section("routing", "Routing", policy_count),
        _section("provenance", "Provenance", provenance_count),
    )


def _section(section_id: str, label: str, count: int) -> GovernanceSection:
    return GovernanceSection(
        section_id=section_id,
        label=label,
        status=GovernanceStatus.READY if count else GovernanceStatus.UNAVAILABLE,
        summary=f"{count} live governance record(s) available."
        if count
        else "No live governance records are available.",
    )


def _setup_summary(
    *,
    provider_list: ProviderGovernanceList,
    prompt_list: PromptGovernanceList,
    profile_list: ProfileGovernanceList,
) -> tuple[str, ...]:
    return (
        f"{len(provider_list.providers)} provider connection(s) visible.",
        f"{len(prompt_list.prompts)} prompt lineage(s) visible.",
        f"{len(profile_list.profiles)} runtime profile(s) visible.",
    )


def _dashboard_actions(
    *,
    scope: ReactAdminScope,
    platform_admin: bool,
    has_routing_context: bool,
) -> tuple[AdminAction, ...]:
    actions: list[AdminAction] = []
    if has_routing_context:
        actions.append(
            AdminAction(
                action_id="routing-preview",
                label="Preview routing",
                method=AdminActionMethod.POST,
                href=_with_tenant_query("/admin/app/governance/routing/preview", scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
            )
        )
    if platform_admin:
        actions.append(
            AdminAction(
                action_id="provider-setup",
                label="Manage providers",
                method=AdminActionMethod.GET,
                href="/admin/app/governance/providers",
                variant=ReactAdminPageActionVariant.SECONDARY,
            )
        )
    return tuple(actions)


def _provider_actions(
    *,
    provider_id: str,
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
            href=f"/admin/app/governance/providers/{provider_id}/credential-reference",
            variant=ReactAdminPageActionVariant.SECONDARY,
            requires_idempotency_key=True,
        ),
    )


def _prompt_actions(
    *,
    prompt_lineage_id: str,
    scope: ReactAdminScope,
    draft: bool,
) -> tuple[AdminAction, ...]:
    if not draft:
        return ()
    return (
        AdminAction(
            action_id=f"prompt-save-{prompt_lineage_id}",
            label="Save prompt summary",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/governance/prompts/{prompt_lineage_id}/save",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
        ),
        AdminAction(
            action_id=f"prompt-preview-{prompt_lineage_id}",
            label="Preview prompt",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/governance/prompts/{prompt_lineage_id}/preview",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
        ),
    )


def _profile_actions(
    *,
    profile_id: str,
    scope: ReactAdminScope,
    draft: bool,
) -> tuple[AdminAction, ...]:
    if not draft:
        return ()
    return (
        AdminAction(
            action_id=f"profile-save-{profile_id}",
            label="Save profile",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/governance/profiles/{profile_id}/save",
                scope,
            ),
            variant=ReactAdminPageActionVariant.PRIMARY,
            requires_idempotency_key=True,
        ),
        AdminAction(
            action_id=f"profile-resolve-{profile_id}",
            label="Resolve profile",
            method=AdminActionMethod.POST,
            href=_with_tenant_query(
                f"/admin/app/governance/profiles/{profile_id}/resolve",
                scope,
            ),
            variant=ReactAdminPageActionVariant.SECONDARY,
        ),
    )


def _scope_tenant_uuid(scope: ReactAdminScope) -> UUID | None:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return None
    return _parse_uuid(scope.tenant_id)


def _parse_uuid(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except ValueError:
        return None


def _status_from_provider_health(health: HealthState) -> GovernanceStatus:
    if health is HealthState.HEALTHY:
        return GovernanceStatus.READY
    if health in {HealthState.DEGRADED, HealthState.FAILING}:
        return GovernanceStatus.DEGRADED
    if health is HealthState.DISABLED:
        return GovernanceStatus.BLOCKED
    return GovernanceStatus.UNAVAILABLE


def _status_from_record_status(status: str) -> GovernanceStatus:
    normalized = status.lower()
    if normalized in {"active", "ready", "published", "healthy"}:
        return GovernanceStatus.READY
    if normalized in {"retired", "revoked", "inactive", "disabled"}:
        return GovernanceStatus.BLOCKED
    if normalized in {"draft", "pending", "untested"}:
        return GovernanceStatus.WARNING
    return GovernanceStatus.UNAVAILABLE


def _status_from_validation(status: str) -> GovernanceStatus:
    normalized = status.lower()
    if normalized in {"passed", "valid", "ready", "success"}:
        return GovernanceStatus.READY
    if normalized in {"failed", "blocking"}:
        return GovernanceStatus.BLOCKED
    return GovernanceStatus.WARNING


def _tenant_availability(
    *,
    scope: ReactAdminScope,
    visible_tenants: Iterable[UUID],
    active: bool,
) -> str:
    if not active:
        return "Provider connection is inactive."
    tenant_ids = tuple(visible_tenants)
    if scope.scope_type == ReactAdminScopeType.PLATFORM:
        return (
            "Platform visible"
            if not tenant_ids
            else f"{len(tenant_ids)} tenant grant(s)"
        )
    return (
        "Visible to this tenant"
        if _scope_tenant_uuid(scope) in tenant_ids or not tenant_ids
        else "Not visible"
    )


def _latency_bucket(latency_ms: int | None) -> str:
    if latency_ms is None:
        return "not tested"
    if latency_ms < 300:
        return "under 300 ms"
    if latency_ms < 1000:
        return "under 1 s"
    return "over 1 s"


def _timestamp_label(value: datetime | None) -> str:
    if value is None:
        return "Not yet recorded"
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M UTC")


def _safe_fingerprint(value: str) -> str:
    return f"ref-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]}"


def _summary_from_mapping(mapping: dict[str, object], *, fallback: str) -> str:
    for key in ("summary", "safe_summary", "change_summary", "description"):
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return fallback


def _variable_summary(values: list[dict[str, object]]) -> str:
    if not values:
        return "No prompt variables declared."
    return f"{len(values)} prompt variable(s) summarized."


def _prompt_binding_label(values: list[dict[str, object]]) -> str:
    if not values:
        return "unavailable"
    labels = [
        str(value.get("prompt_version_id") or value.get("prompt_id") or "prompt")
        for value in values[:3]
    ]
    return ", ".join(labels)


def _skill_labels(values: list[dict[str, object]]) -> tuple[str, ...]:
    labels = []
    for value in values[:5]:
        labels.append(str(value.get("skill_slug") or value.get("skill_id") or "skill"))
    return tuple(labels)


async def _profile_grant_labels(
    *,
    profile_repository: AgentProfileRepository,
    active_version_id: UUID | None,
) -> tuple[str, ...]:
    if active_version_id is None:
        return ()
    grants = await profile_repository.list_grants_for_version(active_version_id)
    return tuple(str(grant.grantee_tenant_id) for grant in grants)


def _unavailable_prompt_preview(
    prompt_lineage_id: str,
    fixture_id: str,
) -> SafePromptPreview:
    return SafePromptPreview(
        preview_id=f"prompt-preview-unavailable:{prompt_lineage_id}",
        prompt_lineage_id=prompt_lineage_id,
        fixture_label=fixture_id,
        status=GovernanceStatus.UNAVAILABLE,
        safe_output="Prompt preview is unavailable until a live draft revision exists.",
        redaction_findings=("No protected prompt content was rendered.",),
        variable_summary="No prompt variables available.",
        audit_reference_id=f"prompt-preview-unavailable:{prompt_lineage_id}",
    )


def _unavailable_profile_resolution(profile_id: str) -> ProfileResolutionPreview:
    return ProfileResolutionPreview(
        preview_id=f"profile-resolution-unavailable:{profile_id}",
        profile_id=profile_id,
        status=GovernanceStatus.UNAVAILABLE,
        selected_profile_version="unavailable",
        model_route="unavailable",
        provider_route="unavailable",
        prompt_route="unavailable",
        skill_route="unavailable",
        policy_reasons=("No live profile resolution evidence is available.",),
        remediation="Create and activate a runtime profile version.",
        audit_reference_id=f"profile-resolution-unavailable:{profile_id}",
    )


def _unavailable_result(summary: str) -> GovernanceMutationResult:
    return GovernanceMutationResult(
        status=AdminMutationStatus.DEPENDENCY_UNAVAILABLE,
        summary=summary,
        diagnostics=("No fake mutation success was returned.",),
    )


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
