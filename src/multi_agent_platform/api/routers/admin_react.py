from __future__ import annotations

import hashlib
import html
import json
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
)
from multi_agent_platform.admin.channel_telegram_briefing import (
    build_alias_action_result,
    build_alias_save_result,
    build_briefing_preferences,
    build_channel_telegram_briefing_dashboard,
    build_delivery_diagnostics,
    build_link_token_result,
    build_preference_export_result,
    build_preference_import_result,
    build_preference_save_result,
    build_run_status_summary,
    build_telegram_config_result,
    build_webhook_validation_result,
)
from multi_agent_platform.admin.governance import (
    build_credential_reference_result,
    build_governance_dashboard,
    build_governance_legacy_route_mappings,
    build_policy_history,
    build_profile_list,
    build_profile_resolution,
    build_profile_save_result,
    build_prompt_list,
    build_prompt_preview,
    build_prompt_save_result,
    build_provider_list,
    build_provider_probe_result,
    build_routing_preview_mutation,
    build_run_provenance,
    is_platform_admin,
)
from multi_agent_platform.admin.memberships.react_memberships import (
    build_grant_revoke_result,
    build_invitation_result,
    build_membership_access_history,
    build_membership_audit,
    build_membership_dashboard,
    build_membership_status_result,
    build_principal_link_result,
    build_principal_status_result,
    build_role_grant_result,
)
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
)
from multi_agent_platform.admin.migration_hardening import (
    build_decommission_inventory_dashboard,
    build_live_data_inventory_dashboard,
    build_migration_dashboard,
    build_migration_rollback_plan,
    build_migration_route_groups,
    build_transitional_label_gate,
)
from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.admin.skill_lifecycle import (
    build_binding_preview_result,
    build_candidate_result,
    build_candidate_validation_result,
    build_connector_diagnostic_result,
    build_credential_configuration_result,
    build_install_result,
    build_package_lifecycle_result,
    build_readiness_refresh_result,
    build_skill_execution_diagnostics,
    build_skill_legacy_route_mappings,
    build_skill_lifecycle_audit,
    build_skill_lifecycle_dashboard,
    build_tenant_discovery,
    build_tenant_grant_result,
    build_tenant_installations,
)
from multi_agent_platform.admin.skill_lifecycle import (
    build_publish_result as build_skill_publish_result,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
)
from multi_agent_platform.admin.usage.react_usage import (
    UsageReactExportNotFoundError,
    build_usage_dashboard,
    build_usage_events,
    build_usage_export_detail,
    build_usage_export_result,
)
from multi_agent_platform.admin.workflow_builder import (
    build_copy_result,
    build_create_result,
    build_publish_readiness,
    build_publish_result,
    build_restore_result,
    build_save_result,
    build_validation_result,
    build_workflow_builder_envelope,
    build_workflow_create_envelope,
    build_workflow_legacy_route_mappings,
    build_workflow_registry_envelope,
    build_workflow_version_detail,
)
from multi_agent_platform.admin.workflow_registry.service import (
    DraftConflictError,
    PublishConflictError,
    WorkflowAccessError,
    WorkflowNotFoundError,
    WorkflowRegistryError,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import (
    available_scope_options_for_request,
    resolve_scope_for_request,
)
from multi_agent_platform.api.schemas.admin_channel_telegram_briefing_react import (
    BriefingPreferenceExportRequest,
    BriefingPreferenceImportRequest,
    BriefingPreferenceList,
    BriefingPreferenceMutationResult,
    BriefingPreferenceSaveRequest,
    ChannelMutationResult,
    ChannelTelegramBriefingDashboard,
    DeliveryDiagnosticList,
    LinkTokenCreateRequest,
    LinkTokenResult,
    RunStatusSummary,
    TelegramAliasActionRequest,
    TelegramAliasSaveRequest,
    TelegramConfigSaveRequest,
    WebhookValidationRequest,
)
from multi_agent_platform.api.schemas.admin_governance import (
    GovernanceDashboard,
    GovernanceLegacyRouteMapping,
    GovernanceMutationResult,
    PolicyHistoryList,
    ProfileGovernanceList,
    ProfileResolutionPreview,
    ProfileSaveRequest,
    PromptGovernanceList,
    PromptPreviewRequest,
    PromptSaveRequest,
    ProviderCredentialReferenceRequest,
    ProviderGovernanceList,
    RoutingPreviewRequest,
    RunProvenanceSummary,
    SafePromptPreview,
)
from multi_agent_platform.api.schemas.admin_membership_react import (
    MembershipAccessHistoryList,
    MembershipAuditList,
    MembershipConfirmationRequest,
    MembershipDashboard,
    MembershipInvitationSaveRequest,
    MembershipMutationResult,
    PrincipalLinkRequest,
    RoleGrantSaveRequest,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    AdminMigrationHardeningDashboard,
    JinjaInventoryDashboard,
    LiveDataInventoryDashboard,
    MigrationRollbackPlan,
    MigrationRouteGroup,
    TransitionalLabelGate,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminProblemReason,
    RevisionConflict,
    SafeProblemDetail,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
    ConsoleHomeAttentionItem,
    ConsoleHomeEnvelope,
    ConsoleHomeMetric,
    ConsoleHomeQuickAction,
    ConsoleHomeWorkspace,
    ReactAdminActionTokens,
    ReactAdminAssetManifestSummary,
    ReactAdminBootstrap,
    ReactAdminBreadcrumb,
    ReactAdminCommandSearch,
    ReactAdminCommandSearchResult,
    ReactAdminConfig,
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminFallbackKind,
    ReactAdminFeatureFlags,
    ReactAdminNavigationGroup,
    ReactAdminNavigationItem,
    ReactAdminNotificationTone,
    ReactAdminPageAction,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminPrincipal,
    ReactAdminRequiredScope,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
    ReactAdminShellChrome,
    ReactAdminShellNotification,
    ReactAdminShellState,
    ReactAdminShellStateKind,
    ReactAdminSourceKind,
    ReactAdminSystemHealth,
    ReactAdminSystemHealthDependency,
    ReactAdminVersion,
)
from multi_agent_platform.api.schemas.admin_skill_lifecycle import (
    BindingEligibilityPreviewRequest,
    CredentialConfigurationRequest,
    ReadinessRefreshRequest,
    SkillExecutionDiagnosticList,
    SkillLegacyRouteMapping,
    SkillLifecycleAuditList,
    SkillLifecycleDashboard,
    SkillLifecycleMutationResult,
    SkillPackageCandidateRequest,
    SkillPackagePublishRequest,
    TenantGrantMutationRequest,
    TenantSkillDiscoveryList,
    TenantSkillInstallationList,
    TenantSkillInstallRequest,
)
from multi_agent_platform.api.schemas.admin_test_bench import (
    ArtifactReferenceSummary,
    GateEvidenceRefreshRequest,
    PublishGateEvidenceList,
    TestBenchAuditList,
    TestBenchDashboard,
    TestBenchMutationResult,
    TestCaseSaveRequest,
    TestRunDetail,
    TestRunLaunchRequest,
    TestRunList,
    TestSuiteDetail,
    TestSuiteList,
    TestSuiteSaveRequest,
)
from multi_agent_platform.api.schemas.admin_usage_react import (
    UsageReactConfidenceStatus,
    UsageReactDashboard,
    UsageReactDashboardQuery,
    UsageReactEventDrilldown,
    UsageReactEventQuery,
    UsageReactExportCreateRequest,
    UsageReactExportSummary,
    UsageReactGroupBy,
)
from multi_agent_platform.api.schemas.admin_workbench import (
    OperationsWorkbenchEnvelope,
    RunDebugEnvelope,
    WorkbenchExportRequest,
    WorkbenchExportSnapshot,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    BuilderMutationResult,
    WorkflowBuilderEnvelope,
    WorkflowCreateEnvelope,
    WorkflowDraftCopyActionRequest,
    WorkflowDraftCreateActionRequest,
    WorkflowDraftSaveRequest,
    WorkflowLegacyRouteMapping,
    WorkflowPublishReadiness,
    WorkflowPublishRequest,
    WorkflowReferenceCatalog,
    WorkflowRegistryEnvelope,
    WorkflowRevisionRestoreActionRequest,
    WorkflowVersionDetail,
)
from multi_agent_platform.api.schemas.workflow_editor import PublishGateRequest
from multi_agent_platform.api.schemas.workflow_registry import (
    CopyDraftRequest as RegistryCopyDraftRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    PublishDraftRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    RestoreRevisionRequest as RegistryRestoreRevisionRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftCreateRequest as RegistryWorkflowDraftCreateRequest,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftSaveRequest as RegistryWorkflowDraftSaveRequest,
)
from multi_agent_platform.api.ui.admin_console import (
    AdminConsoleAccessError,
    AdminScope,
    AdminScopeOption,
    AdminShellContext,
    BreadcrumbItem,
    NavigationGroup,
    NavigationItem,
    build_admin_shell_context,
    safe_redirect_target,
    sanitize_text,
)
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.db.repositories.agent_profiles import AgentProfileRepository
from multi_agent_platform.db.repositories.agent_tests import AgentTestRepository
from multi_agent_platform.db.repositories.artifact import ArtifactRepository
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.memberships import MembershipRepository
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)
from multi_agent_platform.db.repositories.prompts import PromptRepository
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.db.repositories.skill_registry import SkillRegistryRepository
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)
from multi_agent_platform.db.repositories.usage import (
    UsageAccessDeniedError,
    UsageRepository,
)
from multi_agent_platform.db.repositories.workflow_registry import (
    WorkflowRegistryRepository,
)
from multi_agent_platform.observability.metrics import (
    record_admin_shell_audit_failure,
)
from multi_agent_platform.operations.service import OperationsConsoleService
from multi_agent_platform.operations.workbench import (
    RunDebugNotFoundError,
    build_operations_workbench_envelope,
    build_run_debug_envelope,
    create_workbench_export_snapshot,
)
from multi_agent_platform.runtime.health.service import HealthService
from multi_agent_platform.testing.agent_bench.react_test_bench import (
    build_artifact_reference,
    build_case_save_result,
    build_gate_refresh_result,
    build_publish_gate_evidence,
    build_run_launch_result,
    build_suite_save_result,
    build_test_bench_audit,
    build_test_bench_dashboard,
    build_test_run_detail,
    build_test_run_list,
    build_test_suite_detail,
    build_test_suite_list,
)
from multi_agent_platform.testing.agent_bench.service import AgentTestBenchService
from multi_agent_platform.usage.service import UsageAnalyticsService

router = APIRouter(tags=["admin-react"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

REACT_MOUNT_PATH = "/admin/app"
REACT_BOOTSTRAP_URL = "/admin/app/bootstrap.json"
REACT_HOME_URL = "/admin/app/home.json"
REACT_CONFIG_URL = "/admin/app/config.json"
REACT_MANIFEST_URL = "/admin/app/manifest.json"
REACT_SEARCH_URL = "/admin/app/search.json"
REACT_WORKFLOWS_PATH = "/admin/app/workflows"
REACT_WORKFLOWS_URL = "/admin/app/workflows/builder.json"
REACT_WORKFLOWS_LOOKUPS_URL = "/admin/app/workflows/lookups.json"
REACT_GOVERNANCE_PATH = "/admin/app/governance"
REACT_GOVERNANCE_URL = "/admin/app/governance/bootstrap.json"
REACT_SKILLS_PATH = "/admin/app/skills"
REACT_SKILLS_URL = "/admin/app/skills/bootstrap.json"
REACT_TEST_BENCH_PATH = "/admin/app/test-bench"
REACT_TEST_BENCH_URL = "/admin/app/test-bench/bootstrap.json"
REACT_MEMBERSHIPS_PATH = "/admin/app/memberships"
REACT_MEMBERSHIPS_URL = "/admin/app/memberships/bootstrap.json"
REACT_USAGE_PATH = "/admin/app/usage"
REACT_USAGE_URL = "/admin/app/usage/bootstrap.json"
REACT_CHANNELS_PATH = "/admin/app/channels"
REACT_CHANNELS_URL = "/admin/app/channels/bootstrap.json"
REACT_MIGRATION_PATH = "/admin/app/migration"
REACT_MIGRATION_URL = "/admin/app/migration/bootstrap.json"
REACT_OPERATIONS_PATH = "/admin/app/operations"
REACT_OPERATIONS_URL = "/admin/app/operations.json"
REACT_OPERATIONS_EXPORT_URL = "/admin/app/operations/export"
VITE_ENTRY_KEY = "src/main.tsx"
DESIGN_TOKEN_VERSION = "admin-shell-2026-05"
DISABLED_REACT_FALLBACKS: dict[str, str] = {
    "operations": "/admin/operations",
}


def _build_workflow_admin_service(
    session: AsyncSession,
    container: ContainerDep,
) -> AdminService:
    return AdminService(
        workflow_repository=WorkflowRegistryRepository(session),
        artifact_repository=ArtifactRepository(session),
        audit_service=AuditService(AuditRepository(session)),
        storage_provider=container.storage_provider,
        workflow_registry_artifact_prefix=container.settings.workflow_registry_artifact_prefix,
        logger=container.logger,
    )


@router.get("/admin/app", response_class=HTMLResponse)
async def react_admin_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="admin app is disabled")
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc

    return render_react_admin_host(
        asset_manifest=react_admin_manifest(container),
        bootstrap_url=_with_tenant_query(REACT_BOOTSTRAP_URL, shell.active_scope),
        config_url=REACT_CONFIG_URL,
        mount_path=REACT_MOUNT_PATH,
    )


@router.get("/admin/app/bootstrap.json", response_model=ReactAdminBootstrap)
async def react_admin_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ReactAdminBootstrap:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="admin app is disabled")
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await react_admin_bootstrap_from_shell(
        shell=shell,
        principal=principal,
        container=container,
    )


@router.get(
    "/admin/app/home.json",
    response_model=ConsoleHomeEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_home(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ConsoleHomeEnvelope:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="admin app is disabled")
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return _console_home_from_shell(shell=shell)


@router.get("/admin/app/migration", response_class=HTMLResponse)
async def react_admin_migration_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="admin app is disabled")
    await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    bootstrap_url = (
        f"/admin/app/migration/shell.json?tenant_id={tenant_id}"
        if tenant_id
        else "/admin/app/migration/shell.json"
    )
    return render_react_admin_host(
        asset_manifest=react_admin_manifest(container),
        bootstrap_url=bootstrap_url,
        config_url=REACT_CONFIG_URL,
        mount_path=REACT_MOUNT_PATH,
    )


@router.get(
    "/admin/app/migration/shell.json",
    response_model=ReactAdminBootstrap,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_shell_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ReactAdminBootstrap:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return await react_admin_bootstrap_from_shell(
        shell=shell,
        principal=principal,
        container=container,
    )


@router.get(
    "/admin/app/migration/bootstrap.json",
    response_model=AdminMigrationHardeningDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> AdminMigrationHardeningDashboard:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_migration_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get(
    "/admin/app/migration/routes.json",
    response_model=tuple[MigrationRouteGroup, ...],
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_routes(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> tuple[MigrationRouteGroup, ...]:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_migration_route_groups(
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get(
    "/admin/app/migration/decommission-inventory.json",
    response_model=JinjaInventoryDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_decommission_inventory(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> JinjaInventoryDashboard:
    await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_decommission_inventory_dashboard()


@router.get(
    "/admin/app/migration/live-data-inventory.json",
    response_model=LiveDataInventoryDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_live_data_inventory(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
    ci_mode: Annotated[bool, Query()] = False,
    source_scan: Annotated[bool, Query()] = True,
) -> LiveDataInventoryDashboard:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_live_data_inventory_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        ci_mode=ci_mode,
        source_scan=source_scan,
    )


@router.get(
    "/admin/app/migration/transitional-labels.json",
    response_model=TransitionalLabelGate,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_transitional_labels(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
    ci_mode: Annotated[bool, Query()] = False,
    source_scan: Annotated[bool, Query()] = True,
) -> TransitionalLabelGate:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_transitional_label_gate(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        ci_mode=ci_mode,
        source_scan=source_scan,
    )


@router.get(
    "/admin/app/migration/jinja-inventory.json",
    response_model=JinjaInventoryDashboard,
    include_in_schema=False,
)
async def react_admin_migration_legacy_inventory_alias(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> JinjaInventoryDashboard:
    return await react_admin_migration_decommission_inventory(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/migration/rollback.json",
    response_model=MigrationRollbackPlan,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_rollback(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MigrationRollbackPlan:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_migration_rollback_plan(
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get("/admin/app/config.json", response_model=ReactAdminConfig)
async def react_admin_config(
    _principal: PrincipalDep,
    container: ContainerDep,
) -> ReactAdminConfig:
    return ReactAdminConfig(
        mount_path=REACT_MOUNT_PATH,
        asset_base_path=container.settings.react_admin_asset_base_path,
        bootstrap_url=REACT_BOOTSTRAP_URL,
        config_url=REACT_CONFIG_URL,
        manifest_url=REACT_MANIFEST_URL,
    )


@router.get(
    "/admin/app/manifest.json",
    response_model=ReactAdminAssetManifestSummary,
)
async def react_admin_manifest_endpoint(
    _principal: PrincipalDep,
    container: ContainerDep,
) -> ReactAdminAssetManifestSummary:
    return react_admin_manifest(container)


@router.get("/admin/app/search.json", response_model=ReactAdminCommandSearch)
async def react_admin_search(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    query: Annotated[str, Query(alias="q", max_length=80)] = "",
    tenant_id: Annotated[str | None, Query()] = None,
) -> ReactAdminCommandSearch:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return react_admin_command_search_from_shell(shell=shell, query=query)


@router.get("/admin/app/workflows", response_class=HTMLResponse)
async def react_admin_workflows_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get("/admin/app/workflows/new", response_class=HTMLResponse)
async def react_admin_workflows_new_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


async def _react_workflow_scope(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> ReactAdminScope:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return _scope_response(shell.active_scope)


def _uuid_or_404(value: str, label: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"{label} not found") from exc


async def _workflow_builder_payload(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    service: AdminService,
    workflow_draft_id: UUID | None = None,
) -> WorkflowBuilderEnvelope:
    try:
        registry_items = await service.list_workflows(principal=principal)
        selected_draft_id = workflow_draft_id
        if selected_draft_id is None:
            selected_draft_id = next(
                (
                    item.workflow_draft_id
                    for item in registry_items
                    if item.workflow_draft_id is not None
                ),
                None,
            )
        if selected_draft_id is None:
            return build_workflow_builder_envelope(
                scope=scope,
                principal=principal,
                registry_items=registry_items,
            )
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=selected_draft_id,
        )
        lookups = await service.get_workflow_editor_lookups(
            principal=principal,
            workflow_draft_id=selected_draft_id,
        )
        graph = await service.get_workflow_graph_preview(
            principal=principal,
            workflow_draft_id=selected_draft_id,
        )
        revisions = await service.list_workflow_draft_revisions(
            principal=principal,
            workflow_draft_id=selected_draft_id,
        )
        gate = await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=selected_draft_id,
            payload=PublishGateRequest(),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return build_workflow_builder_envelope(
        scope=scope,
        principal=principal,
        registry_items=registry_items,
        draft=draft,
        lookups=lookups,
        graph_preview=graph,
        revisions=revisions,
        publish_gate=gate,
    )


@router.get(
    "/admin/app/workflows/registry.json",
    response_model=WorkflowRegistryEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_registry(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
    scope_filter: Annotated[str, Query()] = "all",
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    search_query: Annotated[str | None, Query(alias="q")] = None,
) -> WorkflowRegistryEnvelope:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    try:
        items = await service.list_workflows(
            principal=principal,
            scope_filter=scope_filter,
            status=status_filter,
            search_query=search_query,
        )
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return build_workflow_registry_envelope(
        scope=scope,
        items=items,
        filters={
            "status": status_filter or "all",
            "scope_filter": scope_filter,
            "sort": "updated_desc",
        },
    )


@router.get(
    "/admin/app/workflows/create.json",
    response_model=WorkflowCreateEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_create_state(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkflowCreateEnvelope:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_workflow_create_envelope(scope=scope)


@router.get(
    "/admin/app/workflows/legacy-routes.json",
    response_model=tuple[WorkflowLegacyRouteMapping, ...],
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_legacy_routes(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> tuple[WorkflowLegacyRouteMapping, ...]:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_workflow_legacy_route_mappings(
        scope=scope,
    )


@router.get(
    "/admin/app/workflows/builder.json",
    response_model=WorkflowBuilderEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
    workflow_draft_id: Annotated[str | None, Query()] = None,
) -> WorkflowBuilderEnvelope:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return await _workflow_builder_payload(
        scope=scope,
        principal=principal,
        service=_build_workflow_admin_service(session, container),
        workflow_draft_id=_uuid_or_404(workflow_draft_id, "workflow draft")
        if workflow_draft_id
        else None,
    )


@router.get(
    "/admin/app/workflows/drafts/{workflow_draft_id}/detail.json",
    response_model=WorkflowBuilderEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_draft_detail(
    workflow_draft_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkflowBuilderEnvelope:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return await _workflow_builder_payload(
        scope=scope,
        principal=principal,
        service=_build_workflow_admin_service(session, container),
        workflow_draft_id=_uuid_or_404(workflow_draft_id, "workflow draft"),
    )


@router.get(
    "/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate.json",
    response_model=WorkflowPublishReadiness,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_publish_gate_detail(
    workflow_draft_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkflowPublishReadiness:
    await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        gate = await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=PublishGateRequest(),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return build_publish_readiness(draft=draft, gate=gate)


@router.get(
    "/admin/app/workflows/versions/{workflow_version_bundle_id}/detail.json",
    response_model=WorkflowVersionDetail,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_version_detail(
    workflow_version_bundle_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkflowVersionDetail:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    try:
        version = await service.get_workflow_version(
            principal=principal,
            workflow_version_bundle_id=_uuid_or_404(
                workflow_version_bundle_id,
                "workflow version",
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    detail = build_workflow_version_detail(scope=scope, version=version)
    if detail is None:
        raise HTTPException(status_code=404, detail="workflow version not found")
    return detail


@router.get(
    "/admin/app/workflows/lookups.json",
    response_model=WorkflowReferenceCatalog,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_lookups(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
    workflow_draft_id: Annotated[str | None, Query()] = None,
) -> WorkflowReferenceCatalog:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    try:
        lookups = await service.get_workflow_editor_lookups(
            principal=principal,
            workflow_draft_id=_uuid_or_404(workflow_draft_id, "workflow draft")
            if workflow_draft_id
            else None,
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return build_workflow_builder_envelope(
        scope=scope,
        principal=principal,
        lookups=lookups,
    ).reference_catalog


@router.post(
    "/admin/app/workflows",
    response_model=BuilderMutationResult,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        409: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_create(
    payload: WorkflowDraftCreateActionRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    try:
        draft = await service.create_workflow_draft(
            principal=principal,
            payload=RegistryWorkflowDraftCreateRequest(
                scope_type=payload.scope_type,
                tenant_id=payload.tenant_id,
                workflow_kind=payload.workflow_kind,
                slug=payload.slug,
                display_name=payload.display_name,
                description=payload.description,
                created_from_version_id=payload.created_from_version_id,
                document=payload.document,
            ),
        )
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except WorkflowRegistryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return build_create_result(draft=draft, scope=scope)


@router.post(
    "/admin/app/workflows/drafts/{workflow_draft_id}/save",
    response_model=BuilderMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_save(
    workflow_draft_id: str,
    payload: WorkflowDraftSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _ = scope
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        current = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        document = current.document.model_copy(
            update={
                "display_name": payload.name,
                "description": payload.description,
            }
        )
        base_revision = int(payload.revision)
        if payload.force_stale:
            base_revision = max(base_revision - 1, -1)
        saved = await service.save_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=RegistryWorkflowDraftSaveRequest(
                base_revision_number=base_revision,
                display_name=payload.name,
                description=payload.description,
                document=document,
                change_summary="Admin workflow draft save",
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409, detail="workflow draft revision is stale"
        ) from exc
    except DraftConflictError:
        current = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        return build_save_result(
            conflict=RevisionConflict(
                submitted_revision=payload.revision,
                current_revision=str(current.current_revision_number),
                message="Reload the current draft revision before saving again.",
                reload_href=(
                    f"/admin/app/workflows?tenant_id={scope.tenant_id}"
                    if scope.scope_type == ReactAdminScopeType.TENANT
                    and scope.tenant_id is not None
                    else "/admin/app/workflows"
                ),
            )
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return build_save_result(draft=saved)


@router.post(
    "/admin/app/workflows/drafts/{workflow_draft_id}/validate",
    response_model=BuilderMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_validate(
    workflow_draft_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    ready: Annotated[bool, Query()] = False,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    _ = ready
    await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        validation = await service.validate_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        gate = await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=PublishGateRequest(
                validation_result_id=str(validation.validation_result_id),
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except DraftConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return build_validation_result(
        draft=draft, validation=validation, publish_gate=gate
    )


@router.post(
    "/admin/app/workflows/drafts/{workflow_draft_id}/publish",
    response_model=BuilderMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_publish(
    workflow_draft_id: str,
    payload: WorkflowPublishRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        draft = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        gate = await service.evaluate_workflow_publish_gate(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=PublishGateRequest(),
        )
        if gate.status != "ready" or gate.validation_result_id is None:
            return build_publish_result(draft=draft, gate=gate)
        if not payload.confirmed:
            return build_publish_result(
                draft=draft,
                gate=gate,
                confirmation_required=True,
            )
        version = await service.publish_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=PublishDraftRequest(
                validation_result_id=UUID(gate.validation_result_id),
                publish_gate_id=gate.publish_gate_id,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (DraftConflictError, PublishConflictError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return build_publish_result(draft=draft, version=version, gate=gate)


@router.post(
    "/admin/app/workflows/drafts/{workflow_draft_id}/restore",
    response_model=BuilderMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_restore(
    workflow_draft_id: str,
    payload: WorkflowRevisionRestoreActionRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        draft = await service.restore_workflow_revision(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=RegistryRestoreRevisionRequest(
                revision_number=payload.revision_number,
                base_revision_number=payload.base_revision_number,
                change_summary=payload.change_summary,
            ),
        )
    except DraftConflictError:
        current = await service.get_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
        )
        return build_restore_result(
            conflict=RevisionConflict(
                submitted_revision=str(payload.base_revision_number),
                current_revision=str(current.current_revision_number),
                message="Reload the current draft revision before restoring.",
                reload_href=(
                    f"/admin/app/workflows?tenant_id={scope.tenant_id}"
                    if scope.scope_type == ReactAdminScopeType.TENANT
                    and scope.tenant_id is not None
                    else "/admin/app/workflows"
                ),
            )
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return build_restore_result(draft=draft)


@router.post(
    "/admin/app/workflows/drafts/{workflow_draft_id}/copy",
    response_model=BuilderMutationResult,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_workflow_builder_copy(
    workflow_draft_id: str,
    payload: WorkflowDraftCopyActionRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    scope = await _react_workflow_scope(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    service = _build_workflow_admin_service(session, container)
    draft_id = _uuid_or_404(workflow_draft_id, "workflow draft")
    try:
        draft = await service.copy_workflow_draft(
            principal=principal,
            workflow_draft_id=draft_id,
            payload=RegistryCopyDraftRequest(
                source_revision_number=payload.source_revision_number,
                new_slug=payload.new_slug,
                display_name=payload.display_name,
                description=payload.description,
                scope_type=payload.scope_type,
                tenant_id=payload.tenant_id,
                change_summary=payload.change_summary,
            ),
        )
    except WorkflowNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkflowAccessError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except WorkflowRegistryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return build_copy_result(draft=draft, scope=scope)


@router.get("/admin/app/governance", response_class=HTMLResponse)
async def react_admin_governance_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/governance/bootstrap.json",
    response_model=GovernanceDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> GovernanceDashboard:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    scope = _scope_response(shell.active_scope)
    return await build_governance_dashboard(
        scope=scope,
        principal=principal,
        provider_repository=ModelProviderRepository(session),
        prompt_repository=PromptRepository(session),
        profile_repository=AgentProfileRepository(session),
        config_repository=ModelSkillConfigRepository(session),
    )


@router.get(
    "/admin/app/governance/providers.json",
    response_model=ProviderGovernanceList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_providers(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ProviderGovernanceList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_provider_list(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        provider_repository=ModelProviderRepository(session),
    )


@router.get(
    "/admin/app/governance/legacy-routes.json",
    response_model=tuple[GovernanceLegacyRouteMapping, ...],
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_legacy_routes(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> tuple[GovernanceLegacyRouteMapping, ...]:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return build_governance_legacy_route_mappings(
        scope=_scope_response(shell.active_scope),
    )


@router.post(
    "/admin/app/governance/providers/{provider_id}/probe",
    response_model=GovernanceMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_provider_probe(
    provider_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> GovernanceMutationResult:
    await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return await build_provider_probe_result(
        provider_id=provider_id,
        provider_repository=ModelProviderRepository(session),
        principal=principal,
    )


@router.post(
    "/admin/app/governance/providers/{provider_id}/credential-reference",
    response_model=GovernanceMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_provider_credential_reference(
    provider_id: str,
    payload: ProviderCredentialReferenceRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> GovernanceMutationResult:
    await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return await build_credential_reference_result(
        provider_id=provider_id,
        request=payload,
        provider_repository=ModelProviderRepository(session),
    )


@router.get(
    "/admin/app/governance/prompts.json",
    response_model=PromptGovernanceList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_prompts(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> PromptGovernanceList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_prompt_list(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        prompt_repository=PromptRepository(session),
    )


@router.post(
    "/admin/app/governance/prompts/{prompt_lineage_id}/save",
    response_model=GovernanceMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_prompt_save(
    prompt_lineage_id: str,
    payload: PromptSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> GovernanceMutationResult:
    try:
        await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_prompt_save_result(
        prompt_lineage_id=prompt_lineage_id,
        request=payload,
        prompt_repository=PromptRepository(session),
        principal=principal,
    )


@router.post(
    "/admin/app/governance/prompts/{prompt_lineage_id}/preview",
    response_model=SafePromptPreview,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_prompt_preview(
    prompt_lineage_id: str,
    payload: PromptPreviewRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SafePromptPreview:
    try:
        await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_prompt_preview(
        prompt_lineage_id=prompt_lineage_id,
        request=payload,
        prompt_repository=PromptRepository(session),
    )


@router.get(
    "/admin/app/governance/profiles.json",
    response_model=ProfileGovernanceList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_profiles(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ProfileGovernanceList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_profile_list(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        profile_repository=AgentProfileRepository(session),
    )


@router.post(
    "/admin/app/governance/profiles/{profile_id}/save",
    response_model=GovernanceMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_profile_save(
    profile_id: str,
    payload: ProfileSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> GovernanceMutationResult:
    try:
        await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_profile_save_result(
        profile_id=profile_id,
        request=payload,
        profile_repository=AgentProfileRepository(session),
        principal=principal,
    )


@router.post(
    "/admin/app/governance/profiles/{profile_id}/resolve",
    response_model=ProfileResolutionPreview,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_profile_resolve(
    profile_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ProfileResolutionPreview:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_profile_resolution(
        profile_id=profile_id,
        scope=_scope_response(shell.active_scope),
        profile_repository=AgentProfileRepository(session),
    )


@router.post(
    "/admin/app/governance/routing/preview",
    response_model=GovernanceMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_routing_preview(
    payload: RoutingPreviewRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> GovernanceMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_routing_preview_mutation(
        scope=_scope_response(shell.active_scope),
        request=payload,
        config_repository=ModelSkillConfigRepository(session),
    )


@router.get(
    "/admin/app/governance/history.json",
    response_model=PolicyHistoryList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_history(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> PolicyHistoryList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_policy_history(
        scope=_scope_response(shell.active_scope),
        config_repository=ModelSkillConfigRepository(session),
    )


@router.get(
    "/admin/app/governance/provenance/{run_id}.json",
    response_model=RunProvenanceSummary,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_governance_provenance(
    run_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> RunProvenanceSummary:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_run_provenance(
        scope=_scope_response(shell.active_scope),
        run_id=run_id,
        config_repository=ModelSkillConfigRepository(session),
    )


@router.get("/admin/app/skills", response_class=HTMLResponse)
async def react_admin_skills_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/skills/bootstrap.json",
    response_model=SkillLifecycleDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleDashboard:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_skill_lifecycle_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.get(
    "/admin/app/skills/legacy-routes.json",
    response_model=tuple[SkillLegacyRouteMapping, ...],
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_legacy_routes(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> tuple[SkillLegacyRouteMapping, ...]:
    try:
        await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return build_skill_legacy_route_mappings()


@router.post(
    "/admin/app/skills/packages/candidates",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_candidate_create(
    payload: SkillPackageCandidateRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> SkillLifecycleMutationResult:
    await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return await build_candidate_result(
        request=payload,
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/packages/candidates/{candidate_id}/validate",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_candidate_validate(
    candidate_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    ready: Annotated[bool, Query()] = True,
) -> SkillLifecycleMutationResult:
    await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    _ = candidate_id
    return await build_candidate_validation_result(
        ready=ready,
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/packages/candidates/{candidate_id}/publish",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_candidate_publish(
    candidate_id: str,
    payload: SkillPackagePublishRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> SkillLifecycleMutationResult:
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    _ = candidate_id
    return await build_skill_publish_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/packages/{package_id}/grants",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_package_grants(
    package_id: str,
    payload: TenantGrantMutationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> SkillLifecycleMutationResult:
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    _ = package_id
    return await build_tenant_grant_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/packages/{package_id}/quarantine",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_package_quarantine(
    package_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> SkillLifecycleMutationResult:
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return await build_package_lifecycle_result(
        package_id=package_id,
        action="quarantine",
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/packages/{package_id}/withdraw",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_package_withdraw(
    package_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
) -> SkillLifecycleMutationResult:
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return await build_package_lifecycle_result(
        package_id=package_id,
        action="withdraw",
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.get(
    "/admin/app/skills/discovery.json",
    response_model=TenantSkillDiscoveryList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_discovery(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TenantSkillDiscoveryList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_tenant_discovery(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.get(
    "/admin/app/skills/installations.json",
    response_model=TenantSkillInstallationList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_installations(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TenantSkillInstallationList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_tenant_installations(
        scope=_scope_response(shell.active_scope),
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/installations/{installation_id}/install",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_install(
    installation_id: str,
    payload: TenantSkillInstallRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_install_result(
        installation_id=installation_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/installations/{installation_id}/credentials",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_credentials(
    installation_id: str,
    payload: CredentialConfigurationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_credential_configuration_result(
        installation_id=installation_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/installations/{installation_id}/smoke-tests",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_smoke_tests(
    installation_id: str,
    payload: ReadinessRefreshRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_readiness_refresh_result(
        installation_id=installation_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.get(
    "/admin/app/skills/diagnostics.json",
    response_model=SkillExecutionDiagnosticList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_diagnostics(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillExecutionDiagnosticList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_skill_execution_diagnostics(
        scope=_scope_response(shell.active_scope),
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/diagnostics/run",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_diagnostics_run(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_connector_diagnostic_result(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.post(
    "/admin/app/skills/eligibility/preview",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
@router.post(
    "/admin/app/skills/installations/{installation_id}/eligibility/preview",
    response_model=SkillLifecycleMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_eligibility_preview(
    payload: BindingEligibilityPreviewRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
    installation_id: str | None = None,
) -> SkillLifecycleMutationResult:
    _ = installation_id
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_binding_preview_result(
        scope=_scope_response(shell.active_scope),
        request=payload,
        principal=principal,
        repository=SkillRegistryRepository(session),
    )


@router.get(
    "/admin/app/skills/audit.json",
    response_model=SkillLifecycleAuditList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_skills_audit(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> SkillLifecycleAuditList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_skill_lifecycle_audit(
        scope=_scope_response(shell.active_scope),
        repository=SkillRegistryRepository(session),
    )


@router.get("/admin/app/test-bench", response_class=HTMLResponse)
async def react_admin_test_bench_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/test-bench/bootstrap.json",
    response_model=TestBenchDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchDashboard:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_test_bench_dashboard(
        repository=AgentTestRepository(session),
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get(
    "/admin/app/test-bench/suites",
    response_model=TestSuiteList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_suites(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestSuiteList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_test_suite_list(
        repository=AgentTestRepository(session),
        scope=_scope_response(shell.active_scope),
    )


@router.post(
    "/admin/app/test-bench/suites",
    response_model=TestBenchMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_suite_save(
    payload: TestSuiteSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    repository = AgentTestRepository(session)
    return await build_suite_save_result(
        repository=repository,
        service=AgentTestBenchService(repository),
        request=payload,
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get(
    "/admin/app/test-bench/suites/{suite_id}",
    response_model=TestSuiteDetail,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_suite_detail(
    suite_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestSuiteDetail:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    try:
        return await build_test_suite_detail(
            repository=AgentTestRepository(session),
            suite_id=suite_id,
            scope=_scope_response(shell.active_scope),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not_found"
        ) from exc


@router.post(
    "/admin/app/test-bench/suites/{suite_id}/cases",
    response_model=TestBenchMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_case_save(
    suite_id: str,
    payload: TestCaseSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    repository = AgentTestRepository(session)
    try:
        return await build_case_save_result(
            repository=repository,
            service=AgentTestBenchService(repository),
            suite_id=suite_id,
            request=payload,
            scope=_scope_response(shell.active_scope),
            principal=principal,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not_found"
        ) from exc


@router.post(
    "/admin/app/test-bench/suites/{suite_id}/runs",
    response_model=TestBenchMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_run_launch(
    suite_id: str,
    payload: TestRunLaunchRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    repository = AgentTestRepository(session)
    try:
        return await build_run_launch_result(
            repository=repository,
            service=AgentTestBenchService(repository),
            suite_id=suite_id,
            request=payload,
            scope=_scope_response(shell.active_scope),
            principal=principal,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not_found"
        ) from exc


@router.get(
    "/admin/app/test-bench/runs.json",
    response_model=TestRunList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_runs(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestRunList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_test_run_list(
        repository=AgentTestRepository(session),
        scope=_scope_response(shell.active_scope),
    )


@router.get(
    "/admin/app/test-bench/runs/{run_id}.json",
    response_model=TestRunDetail,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_run_detail(
    run_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestRunDetail:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    try:
        return await build_test_run_detail(
            repository=AgentTestRepository(session),
            run_id=run_id,
            scope=_scope_response(shell.active_scope),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not_found"
        ) from exc


@router.get(
    "/admin/app/test-bench/gates.json",
    response_model=PublishGateEvidenceList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_gates(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> PublishGateEvidenceList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_publish_gate_evidence(
        repository=AgentTestRepository(session),
        scope=_scope_response(shell.active_scope),
    )


@router.post(
    "/admin/app/test-bench/gates/{gate_id}/refresh",
    response_model=TestBenchMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_gate_refresh(
    gate_id: str,
    payload: GateEvidenceRefreshRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchMutationResult:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_gate_refresh_result(
        repository=AgentTestRepository(session),
        gate_id=gate_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
    )


@router.get(
    "/admin/app/test-bench/artifacts/{artifact_reference_id}.json",
    response_model=ArtifactReferenceSummary,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_artifact(
    artifact_reference_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ArtifactReferenceSummary:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    try:
        return await build_artifact_reference(
            repository=AgentTestRepository(session),
            artifact_reference_id=artifact_reference_id,
            scope=_scope_response(shell.active_scope),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not_found"
        ) from exc


@router.get(
    "/admin/app/test-bench/audit.json",
    response_model=TestBenchAuditList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_test_bench_audit(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> TestBenchAuditList:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_test_bench_audit(
        repository=AgentTestRepository(session),
        scope=_scope_response(shell.active_scope),
    )


@router.get("/admin/app/memberships", response_class=HTMLResponse)
async def react_admin_memberships_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/memberships/bootstrap.json",
    response_model=MembershipDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=120)] = None,
) -> MembershipDashboard:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    membership_repository, membership_service = _membership_service(session)
    return await build_membership_dashboard(
        repository=membership_repository,
        service=membership_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
        query=q,
    )


@router.post(
    "/admin/app/memberships/invitations",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_invitation(
    payload: MembershipInvitationSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_invitation_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/memberships/principals/link",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_principal_link(
    payload: PrincipalLinkRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_principal_link_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/memberships/role-grants",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_role_grant(
    payload: RoleGrantSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_role_grant_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/memberships/role-grants/{role_grant_id}/revoke",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_role_grant_revoke(
    role_grant_id: str,
    payload: MembershipConfirmationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_grant_revoke_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        role_grant_id=role_grant_id,
        request=payload,
    )


@router.post(
    "/admin/app/memberships/principals/{principal_identity_id}/{status_action}",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_principal_status(
    principal_identity_id: str,
    status_action: str,
    payload: MembershipConfirmationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    if status_action not in {"suspend", "reactivate"}:
        raise HTTPException(status_code=404, detail="membership action unavailable")
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_principal_status_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        principal_identity_id=principal_identity_id,
        status_action=status_action,
        request=payload,
    )


@router.post(
    "/admin/app/memberships/memberships/{tenant_membership_id}/{membership_status}",
    response_model=MembershipMutationResult,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_membership_status(
    tenant_membership_id: str,
    membership_status: str,
    payload: MembershipConfirmationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipMutationResult:
    if membership_status not in {"active", "suspended", "removed"}:
        raise HTTPException(status_code=404, detail="membership status unavailable")
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    membership_repository, membership_service = _membership_service(session)
    return await build_membership_status_result(
        service=membership_service,
        repository=membership_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        tenant_membership_id=tenant_membership_id,
        membership_status=membership_status,
        request=payload,
    )


@router.get(
    "/admin/app/memberships/access-history.json",
    response_model=MembershipAccessHistoryList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_access_history(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipAccessHistoryList:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _, membership_service = _membership_service(session)
    return await build_membership_access_history(
        service=membership_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get(
    "/admin/app/memberships/audit.json",
    response_model=MembershipAuditList,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_memberships_audit(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MembershipAuditList:
    shell = await _membership_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _, membership_service = _membership_service(session)
    return await build_membership_audit(
        service=membership_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


@router.get("/admin/app/channels", response_class=HTMLResponse)
async def react_admin_channels_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="admin app is disabled")
    await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    bootstrap_url = (
        f"/admin/app/channels/shell.json?tenant_id={tenant_id}"
        if tenant_id
        else "/admin/app/channels/shell.json"
    )
    return render_react_admin_host(
        asset_manifest=react_admin_manifest(container),
        bootstrap_url=bootstrap_url,
        config_url=REACT_CONFIG_URL,
        mount_path=REACT_MOUNT_PATH,
    )


@router.get("/admin/app/channels/runs", response_class=HTMLResponse)
async def react_admin_channels_runs_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_channels_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get("/admin/app/channels/runs/{workflow_run_id}", response_class=HTMLResponse)
async def react_admin_channels_run_app(
    workflow_run_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    _ = workflow_run_id
    return await react_admin_channels_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/channels/shell.json",
    response_model=ReactAdminBootstrap,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_channels_shell_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ReactAdminBootstrap:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return await react_admin_bootstrap_from_shell(
        shell=shell,
        principal=principal,
        container=container,
    )


@router.get(
    "/admin/app/channels/bootstrap.json",
    response_model=ChannelTelegramBriefingDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_channels_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelTelegramBriefingDashboard:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        telegram_repository,
        telegram_service,
        briefing_repository,
        briefing_service,
        channel_repository,
        runtime_repository,
    ) = _channel_telegram_briefing_services(session=session, container=container)
    return await build_channel_telegram_briefing_dashboard(
        telegram_service=telegram_service,
        telegram_repository=telegram_repository,
        briefing_service=briefing_service,
        briefing_repository=briefing_repository,
        channel_repository=channel_repository,
        runtime_repository=runtime_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
    )


@router.post(
    "/admin/app/channels/telegram/config",
    response_model=ChannelMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_telegram_config(
    payload: TelegramConfigSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _repository, telegram_service, *_rest = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_telegram_config_result(
        telegram_service=telegram_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/channels/telegram/webhook/validate",
    response_model=ChannelMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_webhook_validate(
    payload: WebhookValidationRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _repository, telegram_service, *_rest = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_webhook_validation_result(
        telegram_service=telegram_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/channels/telegram/aliases",
    response_model=ChannelMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_alias_save(
    payload: TelegramAliasSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _repository, telegram_service, *_rest = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_alias_save_result(
        telegram_service=telegram_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/channels/telegram/aliases/{alias_id}/{action}",
    response_model=ChannelMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_alias_action(
    alias_id: str,
    action: str,
    payload: TelegramAliasActionRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    telegram_repository, telegram_service, *_rest = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_alias_action_result(
        telegram_service=telegram_service,
        telegram_repository=telegram_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        alias_id=alias_id,
        action=action,
        request=payload,
    )


@router.post(
    "/admin/app/channels/telegram/link-tokens",
    response_model=LinkTokenResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_link_token(
    payload: LinkTokenCreateRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> LinkTokenResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _repository, telegram_service, *_rest = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_link_token_result(
        telegram_service=telegram_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.get(
    "/admin/app/channels/telegram/deliveries.json",
    response_model=DeliveryDiagnosticList,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_deliveries(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> DeliveryDiagnosticList:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        telegram_repository,
        _telegram_service,
        _briefing_repository,
        _briefing_service,
        channel_repository,
        _runtime_repository,
    ) = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_delivery_diagnostics(
        telegram_repository=telegram_repository,
        channel_repository=channel_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
    )


@router.get(
    "/admin/app/channels/runs/{workflow_run_id}/status.json",
    response_model=RunStatusSummary,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_channels_run_status(
    workflow_run_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> RunStatusSummary:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    *_rest, runtime_repository = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_run_status_summary(
        runtime_repository=runtime_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        workflow_run_id=workflow_run_id,
    )


@router.get(
    "/admin/app/channels/briefing/preferences.json",
    response_model=BriefingPreferenceList,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_briefing_preferences(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceList:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        _telegram_repository,
        _telegram_service,
        briefing_repository,
        briefing_service,
        *_rest,
    ) = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_briefing_preferences(
        briefing_service=briefing_service,
        briefing_repository=briefing_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
    )


@router.post(
    "/admin/app/channels/briefing/preferences",
    response_model=BriefingPreferenceMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_briefing_preference_save(
    payload: BriefingPreferenceSaveRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        _telegram_repository,
        _telegram_service,
        _briefing_repository,
        briefing_service,
        *_rest,
    ) = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_preference_save_result(
        briefing_service=briefing_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/channels/briefing/preferences/import",
    response_model=BriefingPreferenceMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_briefing_preference_import(
    payload: BriefingPreferenceImportRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        _telegram_repository,
        _telegram_service,
        briefing_repository,
        _briefing_service,
        *_rest,
    ) = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_preference_import_result(
        briefing_repository=briefing_repository,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.post(
    "/admin/app/channels/briefing/preferences/export",
    response_model=BriefingPreferenceMutationResult,
    responses={401: {"model": SafeProblemDetail}, 403: {"model": SafeProblemDetail}},
)
async def react_admin_channels_briefing_preference_export(
    payload: BriefingPreferenceExportRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    (
        _telegram_repository,
        _telegram_service,
        _briefing_repository,
        briefing_service,
        *_rest,
    ) = _channel_telegram_briefing_services(
        session=session,
        container=container,
    )
    return await build_preference_export_result(
        briefing_service=briefing_service,
        scope=_scope_response(shell.active_scope),
        principal=principal,
        request=payload,
    )


@router.get("/admin/app/usage", response_class=HTMLResponse)
async def react_admin_usage_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/usage/bootstrap.json",
    response_model=UsageReactDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_usage_bootstrap(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
    start: Annotated[datetime | None, Query()] = None,
    end: Annotated[datetime | None, Query()] = None,
    group_by: Annotated[UsageReactGroupBy, Query()] = UsageReactGroupBy.DAY,
    provider_key: Annotated[str | None, Query(max_length=128)] = None,
    model_id: Annotated[str | None, Query(max_length=128)] = None,
    usage_status: Annotated[UsageReactConfidenceStatus | None, Query()] = None,
) -> UsageReactDashboard:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    query = UsageReactDashboardQuery(
        tenant_id=tenant_id,
        start=start,
        end=end,
        group_by=group_by,
        provider_key=provider_key,
        model_id=model_id,
        usage_status=usage_status,
    )
    repository = UsageRepository(session)
    return await build_usage_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
        repository=repository,
        service=UsageAnalyticsService(repository),
        query=query,
    )


@router.get(
    "/admin/app/usage/events.json",
    response_model=UsageReactEventDrilldown,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_usage_events(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
    start: Annotated[datetime | None, Query()] = None,
    end: Annotated[datetime | None, Query()] = None,
    group_by: Annotated[UsageReactGroupBy, Query()] = UsageReactGroupBy.DAY,
    rollup_key: Annotated[str | None, Query(max_length=255)] = None,
    provider_key: Annotated[str | None, Query(max_length=128)] = None,
    model_id: Annotated[str | None, Query(max_length=128)] = None,
    usage_status: Annotated[UsageReactConfidenceStatus | None, Query()] = None,
) -> UsageReactEventDrilldown:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    query = UsageReactEventQuery(
        tenant_id=tenant_id,
        start=start,
        end=end,
        group_by=group_by,
        rollup_key=rollup_key,
        provider_key=provider_key,
        model_id=model_id,
        usage_status=usage_status,
    )
    _ = container
    repository = UsageRepository(session)
    return await build_usage_events(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=repository,
        query=query,
    )


@router.post(
    "/admin/app/usage/exports",
    response_model=UsageReactExportSummary,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_usage_export(
    payload: UsageReactExportCreateRequest,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> UsageReactExportSummary:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    repository = UsageRepository(session)
    return await build_usage_export_result(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        repository=repository,
        service=UsageAnalyticsService(repository),
        storage_provider=container.storage_provider,
        request=payload,
    )


@router.get(
    "/admin/app/usage/exports/{usage_export_request_id}.json",
    response_model=UsageReactExportSummary,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_usage_export_detail(
    usage_export_request_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> UsageReactExportSummary:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    _ = container
    try:
        return await build_usage_export_detail(
            scope=_scope_response(shell.active_scope),
            principal=principal,
            repository=UsageRepository(session),
            usage_export_request_id=usage_export_request_id,
        )
    except UsageReactExportNotFoundError as exc:
        raise HTTPException(status_code=404, detail="usage export not found") from exc
    except UsageAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="usage export denied") from exc


@router.get("/admin/app/operations", response_class=HTMLResponse)
async def react_admin_operations_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    return await react_admin_app(
        request=request,
        principal=principal,
        session=session,
        container=container,
        tenant_id=tenant_id,
    )


@router.get(
    "/admin/app/operations.json",
    response_model=OperationsWorkbenchEnvelope,
    responses={
        400: {"model": SafeProblemDetail},
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_operations_workbench(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    range_preset: Annotated[str, Query(alias="range", max_length=20)] = "60m",
    severity: Annotated[str | None, Query(max_length=40)] = None,
    subsystem: Annotated[str | None, Query(max_length=40)] = None,
    tenant_id: Annotated[str | None, Query()] = None,
) -> OperationsWorkbenchEnvelope:
    if range_preset != "60m":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_problem_detail(
                reason=AdminProblemReason.VALIDATION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Time range unavailable",
                detail="Choose an allowed workbench time range.",
                trace_id=principal.trace_id,
                field_errors=(
                    ValidationFieldError(
                        field="range",
                        label="Time range",
                        message="Use the last 60 minutes range.",
                        code="unsupported_range",
                    ),
                ),
            ).model_dump(mode="json"),
        )
    if severity is not None and severity not in {"info", "warning", "critical"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_problem_detail(
                reason=AdminProblemReason.VALIDATION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Severity unavailable",
                detail="Choose an allowed severity filter.",
                trace_id=principal.trace_id,
                field_errors=(
                    ValidationFieldError(
                        field="severity",
                        label="Severity",
                        message="Use warning or critical severity.",
                        code="unsupported_severity",
                    ),
                ),
            ).model_dump(mode="json"),
        )
    if subsystem is not None and subsystem not in {
        "audit",
        "channel",
        "gateway",
        "reliability",
        "runtime",
        "telegram",
        "tool",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_problem_detail(
                reason=AdminProblemReason.VALIDATION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Subsystem unavailable",
                detail="Choose an allowed subsystem filter.",
                trace_id=principal.trace_id,
                field_errors=(
                    ValidationFieldError(
                        field="subsystem",
                        label="Subsystem",
                        message="Use an allowed subsystem.",
                        code="unsupported_subsystem",
                    ),
                ),
            ).model_dump(mode="json"),
        )
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await build_operations_workbench_envelope(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        service=OperationsConsoleService(session=session, container=container),
        range_preset=range_preset,
        severity=severity,
        subsystem=subsystem,
    )


@router.get(
    "/admin/app/operations/runs/{workflow_run_id}.json",
    response_model=RunDebugEnvelope,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
        404: {"model": SafeProblemDetail},
    },
)
async def react_admin_operations_run_debug(
    workflow_run_id: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> RunDebugEnvelope:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    try:
        return await build_run_debug_envelope(
            scope=_scope_response(shell.active_scope),
            principal=principal,
            service=OperationsConsoleService(session=session, container=container),
            workflow_run_id=workflow_run_id,
        )
    except RunDebugNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run debug not found") from exc


@router.post(
    "/admin/app/operations/export",
    response_model=WorkbenchExportSnapshot,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_operations_export(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    payload: WorkbenchExportRequest | None = None,
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkbenchExportSnapshot:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    return await create_workbench_export_snapshot(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        service=OperationsConsoleService(session=session, container=container),
        storage_provider=container.storage_provider,
        request=payload,
    )


@router.get("/admin/app/{react_path:path}", response_class=HTMLResponse)
async def react_admin_spa_fallback(
    react_path: str,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if (
        react_path in DISABLED_REACT_FALLBACKS
        or react_path.startswith("workflows/")
        or react_path.startswith("governance/")
        or react_path.startswith("skills/")
        or react_path.startswith("saved-filters/")
        or react_path.startswith("usage/exports/")
        or react_path.startswith("channels/runs/")
    ):
        return await react_admin_app(
            request=request,
            principal=principal,
            session=session,
            container=container,
            tenant_id=tenant_id,
        )
    raise HTTPException(status_code=404, detail="admin route is unavailable")


async def build_react_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
    allow_tenant_user: bool = False,
    current_path: str = REACT_MOUNT_PATH,
    tenant_user_label: str = "Admin",
) -> AdminShellContext:
    if allow_tenant_user and not set(principal.role_codes) & {
        "tenant_admin",
        "platform_admin",
        "auditor",
    }:
        return await _tenant_user_react_shell(
            principal=principal,
            session=session,
            tenant_id=tenant_id,
            current_path=current_path,
            label=tenant_user_label,
        )
    scope_request = request
    if tenant_id is not None:
        request.scope.setdefault("query_string", b"")
    active_scope = await resolve_scope_for_request(
        request=scope_request,
        principal=principal,
        session=session,
    )
    if tenant_id:
        active_scope = await _scope_for_tenant_id(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    shell = build_admin_shell_context(
        principal=principal,
        active_scope=active_scope,
        current_path=current_path,
        title="Admin",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Admin", href=current_path, active=True),
        ),
        available_scopes=await available_scope_options_for_request(
            principal=principal,
            active_scope=active_scope,
            current_path=current_path,
            session=session,
        ),
    )
    try:
        await AuditService(AuditRepository(session)).record_admin_navigation_visibility(
            principal=principal,
            active_scope=shell.active_scope,
            request_path=current_path,
            outcomes=shell.navigation_outcomes,
        )
    except Exception as exc:
        record_admin_shell_audit_failure(
            action="react_navigation_visibility",
            reason=exc.__class__.__name__,
        )
        raise AdminConsoleAccessError(
            "admin audit persistence is unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            reason_category="audit_unavailable",
        ) from exc
    return shell


async def _require_platform_admin(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> AdminShellContext:
    try:
        shell = await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc
    if not is_platform_admin(principal):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="platform_admin_required",
        )
    return shell


async def _membership_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> AdminShellContext:
    try:
        return await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc


def _membership_service(
    session: AsyncSession,
) -> tuple[MembershipRepository, MembershipAdministrationService]:
    repository = MembershipRepository(session)
    return repository, MembershipAdministrationService(repository)


async def _usage_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> AdminShellContext:
    try:
        return await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc


async def _channel_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> AdminShellContext:
    try:
        return await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
            allow_tenant_user=True,
            current_path=REACT_CHANNELS_PATH,
            tenant_user_label="Channel Preferences",
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc


def _channel_service(container: ContainerDep) -> ChannelService:
    service = container.state.get("channel_service")
    if isinstance(service, ChannelService):
        return service
    service = ChannelService(settings=container.settings)
    container.state["channel_service"] = service
    return service


def _channel_telegram_briefing_services(
    *,
    session: AsyncSession,
    container: ContainerDep,
) -> tuple[
    TelegramConfigRepository,
    TelegramConfigurationService,
    BriefingPreferenceRepository,
    BriefingPreferenceService,
    ChannelRepository,
    RuntimeOrchestrationRepository,
]:
    telegram_repository = TelegramConfigRepository(session)
    briefing_repository = BriefingPreferenceRepository(session)
    channel_repository = ChannelRepository(session)
    return (
        telegram_repository,
        TelegramConfigurationService(
            repository=telegram_repository,
            settings=container.settings,
            channel_service=_channel_service(container),
        ),
        briefing_repository,
        BriefingPreferenceService(briefing_repository),
        channel_repository,
        RuntimeOrchestrationRepository(session),
    )


async def _migration_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
) -> AdminShellContext:
    try:
        return await build_react_shell(
            request=request,
            principal=principal,
            session=session,
            tenant_id=tenant_id,
            allow_tenant_user=True,
            current_path=REACT_MIGRATION_PATH,
            tenant_user_label="Migration Hardening",
        )
    except AdminConsoleAccessError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.reason_category,
        ) from exc


async def _tenant_user_react_shell(
    *,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
    current_path: str,
    label: str,
) -> AdminShellContext:
    if "tenant_user" not in principal.role_codes or principal.tenant_id is None:
        raise AdminConsoleAccessError(
            "tenant user scope is unavailable",
            status_code=status.HTTP_403_FORBIDDEN,
            reason_category="insufficient_role",
        )
    try:
        selected_tenant_id = UUID(str(tenant_id)) if tenant_id else principal.tenant_id
    except ValueError as exc:
        raise AdminConsoleAccessError(
            "tenant scope is invalid",
            status_code=status.HTTP_403_FORBIDDEN,
            reason_category="invalid_scope",
        ) from exc
    if selected_tenant_id != principal.tenant_id:
        raise AdminConsoleAccessError(
            "tenant scope is not authorized",
            status_code=status.HTTP_403_FORBIDDEN,
            reason_category="cross_tenant_scope",
        )
    active_scope = AdminScope.tenant(selected_tenant_id)
    scope_option = AdminScopeOption(
        scope=active_scope,
        label=active_scope.label or "Tenant",
        href=f"{current_path}?tenant_id={selected_tenant_id}",
        selected=True,
    )
    shell = AdminShellContext(
        title="Admin",
        active_scope=active_scope,
        available_scopes=(scope_option,),
        navigation_groups=(),
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label=label,
                href=current_path,
                active=True,
            ),
        ),
        trace_id=principal.trace_id,
        navigation_outcomes=(),
    )
    try:
        await AuditService(AuditRepository(session)).record_admin_navigation_visibility(
            principal=principal,
            active_scope=shell.active_scope,
            request_path=current_path,
            outcomes=shell.navigation_outcomes,
        )
    except Exception as exc:
        record_admin_shell_audit_failure(
            action="react_tenant_user_visibility",
            reason=exc.__class__.__name__,
        )
        raise AdminConsoleAccessError(
            "admin tenant user audit persistence is unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            reason_category="audit_unavailable",
        ) from exc
    return shell


async def _scope_for_tenant_id(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str,
) -> AdminScope:
    original = request.scope.get("query_string", b"")
    request.scope["query_string"] = f"tenant_id={tenant_id}".encode()
    try:
        return await resolve_scope_for_request(
            request=request,
            principal=principal,
            session=session,
        )
    finally:
        request.scope["query_string"] = original


async def react_admin_bootstrap_from_shell(
    *,
    shell: AdminShellContext,
    principal: PrincipalContext,
    container: ContainerDep,
) -> ReactAdminBootstrap:
    system_health = await _system_health_summary(container)
    return ReactAdminBootstrap(
        principal=ReactAdminPrincipal.from_context(principal),
        active_scope=_scope_response(shell.active_scope),
        available_scopes=tuple(
            ReactAdminScopeOption(
                scope=_scope_response(option.scope),
                label=sanitize_text(option.label, fallback="Scope", max_length=100),
                href=safe_redirect_target(option.href, fallback=REACT_MOUNT_PATH),
                selected=option.selected,
            )
            for option in shell.available_scopes
        ),
        navigation=tuple(
            _navigation_group_response(group, shell.active_scope)
            for group in shell.navigation_groups
        ),
        feature_flags=ReactAdminFeatureFlags(
            react_admin_enabled=container.settings.react_admin_enabled,
            react_domain_routes=dict(container.settings.react_admin_domain_routes_json),
            source="settings",
        ),
        version=ReactAdminVersion(
            app_name=container.settings.app_name,
            app_version=container.settings.app_version,
            api_version=DESIGN_TOKEN_VERSION,
            commit_sha=container.settings.commit_sha,
            build_time=container.settings.build_time,
        ),
        asset_manifest=react_admin_manifest(container),
        action_tokens=ReactAdminActionTokens(
            csrf_token=None,
            issued_at=datetime.now(UTC),
        ),
        system_health=system_health,
        shell=_shell_chrome_response(shell, system_health=system_health),
    )


async def _system_health_summary(container: ContainerDep) -> ReactAdminSystemHealth:
    report = await HealthService(container).dependency_status()
    dependencies = tuple(
        ReactAdminSystemHealthDependency(
            name=dependency.name,
            required=dependency.required,
            status=dependency.status.value,
        )
        for dependency in report.dependencies
    )
    unavailable_required = sum(
        1
        for dependency in dependencies
        if dependency.required and dependency.status == "unavailable"
    )
    degraded_dependencies = sum(
        1 for dependency in dependencies if dependency.status == "degraded"
    )
    if report.status == "ready":
        health_status: Literal["ready", "degraded", "not_ready"] = "ready"
        label = "Ready"
        summary = "All required platform dependencies are reporting ready."
    elif report.status == "degraded":
        health_status = "degraded"
        label = "Degraded"
        dependency_label = (
            "dependency" if degraded_dependencies == 1 else "dependencies"
        )
        summary = (
            f"{degraded_dependencies} platform {dependency_label} degraded."
        )
    else:
        health_status = "not_ready"
        label = "Not ready"
        dependency_label = (
            "dependency" if unavailable_required == 1 else "dependencies"
        )
        summary = (
            f"{unavailable_required} required platform {dependency_label} unavailable."
        )
    return ReactAdminSystemHealth(
        status=health_status,
        label=label,
        summary=summary,
        checked_at=report.checked_at,
        dependencies=dependencies,
    )


def react_admin_command_search_from_shell(
    *,
    shell: AdminShellContext,
    query: str,
) -> ReactAdminCommandSearch:
    normalized_query = " ".join(query.strip().lower().split())
    results = _command_results(shell)
    if normalized_query:
        results = tuple(
            result
            for result in results
            if normalized_query in result.label.lower()
            or normalized_query in result.group.lower()
            or (
                result.description is not None
                and normalized_query in result.description.lower()
            )
        )
    return ReactAdminCommandSearch(query=query[:80], results=results[:12])


_HOME_QUICK_ACTION_IDS = (
    "workflow_registry",
    "operations_console",
    "run_search",
    "model_skill_config",
    "model_providers",
    "skill_registry_packages",
    "agent_tests",
    "membership_administration",
    "usage_analytics",
    "telegram_configuration",
)

_HOME_WORKSPACE_IDS = (
    "workflow_registry",
    "operations_console",
    "run_search",
    "reliability_dashboard",
    "model_skill_config",
    "model_providers",
    "prompt_library",
    "agent_profiles",
    "skill_registry_packages",
    "skill_registry_installations",
    "skill_tool_diagnostics",
    "agent_tests",
    "membership_administration",
    "usage_analytics",
    "telegram_configuration",
    "briefing_preferences",
)

_HOME_ACTION_COPY: dict[str, tuple[str, str]] = {
    "workflow_registry": (
        "Review workflows",
        "Open drafts, validation results, publishing readiness, and sharing.",
    ),
    "operations_console": (
        "Open operations",
        "Inspect queues, reliability signals, delivery status, and run health.",
    ),
    "run_search": (
        "Search runs",
        "Find recent workflow runs, timelines, failures, and artifacts.",
    ),
    "model_skill_config": (
        "Check routing",
        "Review model routing, policy controls, and active configuration.",
    ),
    "model_providers": (
        "Review providers",
        "Check provider setup, health, credentials, and safe diagnostics.",
    ),
    "skill_registry_packages": (
        "Manage skills",
        "Review available tools, tenant installation state, and readiness.",
    ),
    "agent_tests": (
        "Open test bench",
        "Launch safe workflow tests and review current evidence.",
    ),
    "membership_administration": (
        "Manage access",
        "Review tenant members, invitations, roles, and audit history.",
    ),
    "usage_analytics": (
        "Review usage",
        "Inspect usage, cost attribution, exports, and drilldowns.",
    ),
    "telegram_configuration": (
        "Open channels",
        "Manage Telegram configuration, aliases, delivery, and briefing settings.",
    ),
}

_HOME_WORKSPACE_COPY: dict[str, str] = {
    "workflow_registry": "Draft, validate, publish, and share workflow versions.",
    "operations_console": "Track platform health, queues, delivery, and exports.",
    "run_search": "Inspect run timelines, failures, artifacts, and recovery signals.",
    "reliability_dashboard": (
        "Review quotas, leases, breakers, retries, and dead letters."
    ),
    "model_skill_config": "Manage routing policy and model-skill configuration.",
    "model_providers": "Review provider catalog entries, health, and credentials.",
    "prompt_library": "Manage prompts, safe previews, and version history.",
    "agent_profiles": "Review runtime profiles, grants, and resolution evidence.",
    "skill_registry_packages": "Publish, grant, install, and validate skills.",
    "skill_registry_installations": "Review tenant skill installation and readiness.",
    "skill_tool_diagnostics": (
        "Run governed connector diagnostics and binding previews."
    ),
    "agent_tests": "Author suites and inspect test runs for workflow quality.",
    "membership_administration": (
        "Manage memberships, invitations, roles, and audit history."
    ),
    "usage_analytics": "Review usage, cost attribution, exports, and trends.",
    "telegram_configuration": (
        "Configure Telegram readiness, webhooks, aliases, and delivery."
    ),
    "briefing_preferences": (
        "Manage briefing preferences, imports, exports, and revisions."
    ),
}


def _console_home_from_shell(*, shell: AdminShellContext) -> ConsoleHomeEnvelope:
    nav_items = _console_home_navigation_items(shell)
    quick_actions = _console_home_quick_actions(nav_items)
    attention_items = _console_home_attention(shell)
    return ConsoleHomeEnvelope(
        page_id="console-home",
        title="Console Home",
        description=(
            "A scope-aware starting point for workflows, operations, governance, "
            "skills, access, usage, and channels."
        ),
        scope=_scope_response(shell.active_scope),
        updated_at=datetime.now(UTC),
        metrics=(
            ConsoleHomeMetric(
                metric_id="workspace-count",
                label="Workspaces",
                value=str(len(nav_items)),
                summary="Authorized destinations available in this scope.",
                tone="success" if nav_items else "warning",
            ),
            ConsoleHomeMetric(
                metric_id="attention-count",
                label="Needs attention",
                value=str(len(attention_items)),
                summary="Current admin notices for the active scope.",
                tone="warning" if attention_items else "success",
            ),
            ConsoleHomeMetric(
                metric_id="scope-mode",
                label="Scope mode",
                value=shell.active_scope.scope_type.title(),
                summary="Actions and data are constrained by the selected scope.",
                tone="info",
            ),
        ),
        attention_items=attention_items
        or (
            ConsoleHomeAttentionItem(
                item_id="no-active-notices",
                title="No active notices",
                summary="No admin notices are active for this scope.",
                tone="success",
            ),
        ),
        quick_actions=quick_actions,
        workspaces=_console_home_workspaces(nav_items),
        provenance=_provenance(
            source_kind=ReactAdminSourceKind.COMPUTED_METADATA,
            source_label="Authorized admin navigation",
            source_detail=(
                "Console Home is assembled from the current principal, scope, "
                "and route visibility decisions."
            ),
        ),
    )


def _console_home_navigation_items(
    shell: AdminShellContext,
) -> tuple[ReactAdminNavigationItem, ...]:
    by_id: dict[str, ReactAdminNavigationItem] = {}
    for group in shell.navigation_groups:
        response_group = _navigation_group_response(group, shell.active_scope)
        for item in response_group.items:
            if item.item_id == "home" or item.item_id not in _HOME_WORKSPACE_IDS:
                continue
            by_id.setdefault(item.item_id, item)
    return tuple(by_id[item_id] for item_id in _HOME_WORKSPACE_IDS if item_id in by_id)


def _console_home_quick_actions(
    nav_items: tuple[ReactAdminNavigationItem, ...],
) -> tuple[ConsoleHomeQuickAction, ...]:
    by_id = {item.item_id: item for item in nav_items}
    actions: list[ConsoleHomeQuickAction] = []
    for item_id in _HOME_QUICK_ACTION_IDS:
        item = by_id.get(item_id)
        if item is None:
            continue
        label, summary = _HOME_ACTION_COPY.get(item.item_id, (item.label, item.group))
        actions.append(
            ConsoleHomeQuickAction(
                action_id=item.item_id,
                label=label,
                summary=summary,
                href=item.href,
                group=item.group,
            )
        )
    return tuple(actions[:8])


def _console_home_workspaces(
    nav_items: tuple[ReactAdminNavigationItem, ...],
) -> tuple[ConsoleHomeWorkspace, ...]:
    return tuple(
        ConsoleHomeWorkspace(
            workspace_id=item.item_id,
            label=item.label,
            summary=_HOME_WORKSPACE_COPY.get(
                item.item_id,
                f"Open {item.label} for the selected scope.",
            ),
            href=item.href,
            group=item.group,
            status_label=_home_status_label(item),
            status_tone=_home_status_tone(item),
        )
        for item in nav_items
    )


def _console_home_attention(
    shell: AdminShellContext,
) -> tuple[ConsoleHomeAttentionItem, ...]:
    chrome = _shell_chrome_response(shell)
    return tuple(
        ConsoleHomeAttentionItem(
            item_id=notification.notification_id,
            title=notification.title,
            summary=notification.summary,
            href=notification.href,
            tone=notification.tone.value,
        )
        for notification in chrome.notifications
        if notification.tone
        in {
            ReactAdminNotificationTone.WARNING,
            ReactAdminNotificationTone.CRITICAL,
        }
    )


def _home_status_label(item: ReactAdminNavigationItem) -> str:
    if item.fallback_kind == ReactAdminFallbackKind.DISABLED:
        return "Unavailable"
    return "Available"


def _home_status_tone(
    item: ReactAdminNavigationItem,
) -> Literal["neutral", "info", "success", "warning", "critical"]:
    if item.fallback_kind == ReactAdminFallbackKind.DISABLED:
        return "warning"
    return "success"


def _problem_detail(
    *,
    reason: AdminProblemReason,
    status_code: int,
    title: str,
    detail: str,
    trace_id: str | None,
    field_errors: tuple[ValidationFieldError, ...] = (),
) -> SafeProblemDetail:
    return SafeProblemDetail(
        title=title,
        status=status_code,
        detail=detail,
        reason_category=reason,
        field_errors=field_errors,
        audit_reference_id=trace_id,
    )


def react_admin_manifest(container: ContainerDep) -> ReactAdminAssetManifestSummary:
    settings = container.settings
    manifest_path = settings.react_admin_manifest_file
    if not manifest_path.exists():
        return ReactAdminAssetManifestSummary(
            available=False,
            base_path=settings.react_admin_asset_base_path,
            unavailable_reason="manifest_missing",
        )
    try:
        raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ReactAdminAssetManifestSummary(
            available=False,
            base_path=settings.react_admin_asset_base_path,
            unavailable_reason="manifest_unreadable",
        )
    if not isinstance(raw_manifest, dict):
        return ReactAdminAssetManifestSummary(
            available=False,
            base_path=settings.react_admin_asset_base_path,
            unavailable_reason="manifest_invalid",
        )
    entry = _entry_manifest(raw_manifest)
    if entry is None:
        return ReactAdminAssetManifestSummary(
            available=False,
            base_path=settings.react_admin_asset_base_path,
            unavailable_reason="entry_missing",
        )
    file_name = _safe_asset_value(entry.get("file"))
    if file_name is None:
        return ReactAdminAssetManifestSummary(
            available=False,
            base_path=settings.react_admin_asset_base_path,
            unavailable_reason="entry_file_missing",
        )
    stylesheets = tuple(
        _asset_url(settings.react_admin_asset_base_path, stylesheet)
        for stylesheet in _safe_asset_list(entry.get("css"))
    )
    entrypoints = (_asset_url(settings.react_admin_asset_base_path, file_name),)
    manifest_hash = hashlib.sha256(
        json.dumps(raw_manifest, sort_keys=True).encode()
    ).hexdigest()[:12]
    return ReactAdminAssetManifestSummary(
        available=True,
        base_path=settings.react_admin_asset_base_path,
        entrypoints=entrypoints,
        stylesheets=stylesheets,
        version=manifest_hash,
    )


def _entry_manifest(raw_manifest: dict[str, Any]) -> dict[str, Any] | None:
    entry = raw_manifest.get(VITE_ENTRY_KEY)
    if isinstance(entry, dict):
        return entry
    for value in raw_manifest.values():
        if isinstance(value, dict) and value.get("isEntry") is True:
            return value
    return None


def _safe_asset_value(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if value.startswith(("/", "http://", "https://")) or ".." in value:
        return None
    return value


def _safe_asset_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(
        asset
        for asset in (_safe_asset_value(candidate) for candidate in value)
        if asset is not None
    )


def _asset_url(base_path: str, asset: str) -> str:
    return f"{base_path.rstrip('/')}/{asset.lstrip('/')}"


def render_react_admin_host(
    *,
    asset_manifest: ReactAdminAssetManifestSummary,
    bootstrap_url: str,
    config_url: str,
    mount_path: str,
) -> HTMLResponse:
    stylesheet_links = "\n".join(
        f'    <link rel="stylesheet" href="{html.escape(stylesheet, quote=True)}">'
        for stylesheet in asset_manifest.stylesheets
    )
    script_tags = "\n".join(
        (
            '    <script type="module" '
            f'src="{html.escape(entrypoint, quote=True)}"></script>'
        )
        for entrypoint in asset_manifest.entrypoints
    )
    if asset_manifest.available:
        fallback_body = "<p>Loading the authenticated admin shell.</p>"
    else:
        reason = html.escape(asset_manifest.unavailable_reason or "unavailable")
        fallback_body = (
            "<p>Admin built assets are unavailable: "
            f"{reason}.</p>"
            '<p><a href="/auth/local-login?redirect_to=/admin/app">'
            "Open local login</a></p>"
        )
    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin</title>
{stylesheet_links}
  </head>
  <body>
    <a
      href="#admin-main-content"
      style="position:absolute;left:-999px;top:auto;width:1px;height:1px;overflow:hidden;"
    >
      Skip to content
    </a>
    <div
      id="root"
      data-bootstrap-url="{html.escape(bootstrap_url, quote=True)}"
      data-config-url="{html.escape(config_url, quote=True)}"
      data-mount-path="{html.escape(mount_path, quote=True)}"
    >
      <main
        id="admin-main-content"
        aria-label="Admin"
        style="font-family: system-ui, sans-serif; padding: 2rem;"
      >
        <p style="font-weight: 700; text-transform: uppercase;">
          Admin
        </p>
        <h1 style="font-size: 2rem; margin: 0 0 0.75rem;">Admin</h1>
        {fallback_body}
      </main>
    </div>
{script_tags}
  </body>
</html>
"""
    csp = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return HTMLResponse(
        document,
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": csp,
            "X-React-Admin-Host": "non-jinja",
        },
    )


def _scope_response(scope: AdminScope) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType(scope.scope_type),
        tenant_id=scope.tenant_id,
        label=sanitize_text(scope.label, fallback="Scope", max_length=80),
    )


def _scope_option_response(option: Any) -> ReactAdminScopeOption:
    return ReactAdminScopeOption(
        scope=_scope_response(option.scope),
        label=sanitize_text(option.label, fallback="Scope", max_length=80),
        href=safe_redirect_target(option.href, fallback="/admin/app/memberships"),
        selected=option.selected,
    )


def _navigation_group_response(
    group: NavigationGroup,
    active_scope: AdminScope,
) -> ReactAdminNavigationGroup:
    return ReactAdminNavigationGroup(
        label=_static_navigation_text(
            group.label,
            fallback="Navigation",
            max_length=80,
        ),
        items=tuple(
            _navigation_item_response(item, active_scope) for item in group.items
        ),
    )


def _navigation_item_response(
    item: NavigationItem,
    active_scope: AdminScope | None = None,
) -> ReactAdminNavigationItem:
    href = safe_redirect_target(item.href, fallback="/admin")
    route_surface_key = item.route_surface_key
    fallback_kind = ReactAdminFallbackKind.REACT
    if item.admin_area == "home":
        href = _with_optional_tenant_query(REACT_MOUNT_PATH, active_scope)
        route_surface_key = "GET:/admin/app"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "workflows":
        href = _with_optional_tenant_query(REACT_WORKFLOWS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/workflows"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "governance":
        href = _with_optional_tenant_query(REACT_GOVERNANCE_PATH, active_scope)
        route_surface_key = "GET:/admin/app/governance"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area in {
        "skill_registry",
        "skill_registry_installations",
        "skill_execution",
    }:
        href = _with_optional_tenant_query(href, active_scope)
        route_surface_key = "GET:/admin/app/skills"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "operations":
        href = _with_optional_tenant_query(REACT_OPERATIONS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/operations"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "agent_tests":
        href = _with_optional_tenant_query(REACT_TEST_BENCH_PATH, active_scope)
        route_surface_key = "GET:/admin/app/test-bench"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area in {"memberships", "membership_administration"}:
        href = _with_optional_tenant_query(REACT_MEMBERSHIPS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/memberships"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "usage_analytics":
        href = _with_optional_tenant_query(REACT_USAGE_PATH, active_scope)
        route_surface_key = "GET:/admin/app/usage"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area in {"telegram_configuration", "briefing_preferences"}:
        href = _with_optional_tenant_query(href, active_scope)
        route_surface_key = "GET:/admin/app/channels"
        fallback_kind = ReactAdminFallbackKind.REACT
    return ReactAdminNavigationItem(
        item_id=item.item_id,
        label=_static_navigation_text(
            item.label,
            fallback="Destination",
            max_length=80,
        ),
        group=_static_navigation_text(
            item.group,
            fallback="Navigation",
            max_length=80,
        ),
        href=href,
        route_surface_key=route_surface_key,
        required_scope=ReactAdminRequiredScope(item.required_scope),
        admin_area=item.admin_area,
        preserve_tenant_scope=item.preserve_tenant_scope,
        active=item.active,
        fallback_kind=fallback_kind,
    )


def _static_navigation_text(
    value: object,
    *,
    fallback: str,
    max_length: int,
) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    if len(text) > max_length:
        return f"{text[: max_length - 1].rstrip()}..."
    return text


def _shell_chrome_response(
    shell: AdminShellContext,
    *,
    system_health: ReactAdminSystemHealth | None = None,
) -> ReactAdminShellChrome:
    return ReactAdminShellChrome(
        product_name="Multi-Agent Admin",
        active_area="home",
        breadcrumbs=tuple(
            ReactAdminBreadcrumb(
                label=sanitize_text(crumb.label, fallback="Admin", max_length=80),
                href=safe_redirect_target(crumb.href, fallback="/admin")
                if crumb.href
                else None,
                active=crumb.active,
            )
            for crumb in shell.breadcrumbs
        ),
        page_actions=(
            ReactAdminPageAction(
                action_id="log-off",
                label="Log off",
                href="/auth/local-logout?redirect_to=/auth/local-login",
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
        notifications=_system_health_notifications(system_health),
        states=_common_shell_states(),
        command_results=_command_results(shell),
        design_token_version=DESIGN_TOKEN_VERSION,
        search_url=_with_tenant_query(REACT_SEARCH_URL, shell.active_scope),
    )


def _system_health_notifications(
    system_health: ReactAdminSystemHealth | None,
) -> tuple[ReactAdminShellNotification, ...]:
    if system_health is None or system_health.status == "ready":
        return ()
    return (
        ReactAdminShellNotification(
            notification_id="system-health-status",
            tone=(
                ReactAdminNotificationTone.CRITICAL
                if system_health.status == "not_ready"
                else ReactAdminNotificationTone.WARNING
            ),
            title=f"System health {system_health.label.lower()}",
            summary=system_health.summary,
            href="/dependencies",
        ),
    )


def _provenance(
    *,
    source_kind: ReactAdminSourceKind,
    source_label: str,
    source_detail: str | None = None,
) -> ReactAdminPageProvenance:
    return ReactAdminPageProvenance(
        source_kind=source_kind,
        source_label=source_label,
        source_detail=source_detail,
        last_verified_at=datetime.now(UTC),
    )


def _empty_metadata(
    *,
    reason: ReactAdminEmptyStateReason,
    title: str,
    summary: str,
    setup_hint: str | None,
    provenance: ReactAdminPageProvenance,
) -> ReactAdminEmptyStateMetadata:
    return ReactAdminEmptyStateMetadata(
        reason=reason,
        title=title,
        summary=summary,
        setup_hint=setup_hint,
        provenance=provenance,
    )


def _common_shell_states() -> tuple[ReactAdminShellState, ...]:
    computed_shell = _provenance(
        source_kind=ReactAdminSourceKind.COMPUTED_METADATA,
        source_label="Admin shell",
        source_detail=(
            "Derived from authorized navigation, scope, settings, and asset "
            "manifest metadata."
        ),
    )
    empty_scope = _provenance(
        source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
        source_label="Authorized live data scope",
        source_detail=(
            "No persisted rows are available for this authorized admin scope."
        ),
    )
    denied_scope = _provenance(
        source_kind=ReactAdminSourceKind.DENIED,
        source_label="Backend authorization decision",
        source_detail="The backend denied access before returning tenant-scoped data.",
    )
    dependency_unavailable = _provenance(
        source_kind=ReactAdminSourceKind.DEPENDENCY_UNAVAILABLE,
        source_label="Backend dependency state",
        source_detail=(
            "A required dependency is unavailable and no substitute rows were "
            "generated."
        ),
    )
    return (
        ReactAdminShellState(
            state=ReactAdminShellStateKind.LOADING,
            title="Loading admin workspace",
            summary="Checking your signed-in principal and active scope.",
            provenance=computed_shell,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.EMPTY,
            title="No records yet",
            summary="This area has no records available for your current scope.",
            provenance=empty_scope,
            empty_state=_empty_metadata(
                reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
                title="No records yet",
                summary=(
                    "No persisted rows are available for your current authorized scope."
                ),
                setup_hint=(
                    "Create or seed live records through the documented admin "
                    "setup flow."
                ),
                provenance=empty_scope,
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.FILTERED_EMPTY,
            title="No matching results",
            summary=(
                "Adjust filters or clear the search to review all authorized records."
            ),
            provenance=empty_scope,
            empty_state=_empty_metadata(
                reason=ReactAdminEmptyStateReason.FILTERED_EMPTY,
                title="No matching results",
                summary=(
                    "Filters returned no persisted rows for the current "
                    "authorized scope."
                ),
                setup_hint="Clear filters to review all authorized live records.",
                provenance=empty_scope,
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DENIED,
            title="Access denied",
            summary="Your current principal is not authorized for this admin area.",
            provenance=denied_scope,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.NOT_FOUND,
            title="Page not found",
            summary="The requested admin destination is unavailable for this route.",
            provenance=computed_shell,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.VALIDATION_ERROR,
            title="Review required fields",
            summary="Fix the highlighted values and try again.",
            provenance=computed_shell,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DEPENDENCY_UNAVAILABLE,
            title="Dependency unavailable",
            summary=(
                "A required admin dependency is not ready. Try again after it recovers."
            ),
            provenance=dependency_unavailable,
            empty_state=_empty_metadata(
                reason=ReactAdminEmptyStateReason.DEPENDENCY_UNAVAILABLE,
                title="Dependency unavailable",
                summary=(
                    "A required dependency is unavailable, so no fallback "
                    "records were generated."
                ),
                setup_hint="Retry after the dependency reports healthy readiness.",
                provenance=dependency_unavailable,
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.PARTIAL_DATA,
            title="Partial data",
            summary=(
                "Some optional summaries are unavailable, but authorized "
                "navigation is ready."
            ),
            provenance=computed_shell,
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.UNEXPECTED_ERROR,
            title="Unexpected error",
            summary="The admin shell could not complete this request safely.",
            provenance=dependency_unavailable,
        ),
    )


def _command_results(
    shell: AdminShellContext,
) -> tuple[ReactAdminCommandSearchResult, ...]:
    results: list[ReactAdminCommandSearchResult] = []
    for group in shell.navigation_groups:
        for item in group.items:
            response = _navigation_item_response(item, shell.active_scope)
            results.append(
                ReactAdminCommandSearchResult(
                    result_id=response.item_id,
                    label=response.label,
                    description=f"Open {response.group}",
                    group=response.group,
                    href=response.href,
                    required_scope=response.required_scope,
                    fallback_kind=response.fallback_kind,
                )
            )
    return tuple(results)


def _with_tenant_query(path: str, scope: AdminScope) -> str:
    if scope.scope_type != "tenant" or scope.tenant_id is None:
        return path
    parsed = urlsplit(path)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["tenant_id"] = str(scope.tenant_id)
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )


def _with_optional_tenant_query(path: str, scope: AdminScope | None) -> str:
    if scope is None:
        return path
    return _with_tenant_query(path, scope)
