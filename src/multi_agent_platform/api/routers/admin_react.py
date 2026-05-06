from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
from multi_agent_platform.admin.migration_hardening import (
    build_jinja_inventory_dashboard,
    build_migration_dashboard,
    build_migration_rollback_plan,
    build_migration_route_groups,
)
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
    build_skill_lifecycle_audit,
    build_skill_lifecycle_dashboard,
    build_tenant_discovery,
    build_tenant_grant_result,
    build_tenant_installations,
)
from multi_agent_platform.admin.skill_lifecycle import (
    build_publish_result as build_skill_publish_result,
)
from multi_agent_platform.admin.usage.react_usage import (
    build_usage_dashboard,
    build_usage_events,
    build_usage_export_detail,
    build_usage_export_result,
)
from multi_agent_platform.admin.workflow_builder import (
    build_publish_result,
    build_reference_catalog,
    build_save_result,
    build_validation_result,
    build_workflow_builder_envelope,
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
    MigrationRollbackPlan,
    MigrationRouteGroup,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminExportStatus,
    AdminMutationStatus,
    AdminPageEnvelope,
    AdminProblemReason,
    AdminSortDirection,
    ConfirmationRequirement,
    EvidenceReferenceType,
    EvidenceSummary,
    ExportSnapshot,
    FilterChip,
    FilterCriterion,
    FilterOption,
    FilterProfile,
    FormFieldDescriptor,
    IdempotencyReplay,
    MutationResult,
    PaginationState,
    PatternsSampleData,
    RefreshHint,
    RevisionConflict,
    SafeProblemDetail,
    SampleActionRequest,
    SampleFormDescriptor,
    SampleRecord,
    SavedFilterSummary,
    SortField,
    SortingState,
    ToastHint,
    ValidationFieldError,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminActionTokens,
    ReactAdminAssetManifestSummary,
    ReactAdminBootstrap,
    ReactAdminBreadcrumb,
    ReactAdminCommandSearch,
    ReactAdminCommandSearchResult,
    ReactAdminConfig,
    ReactAdminFallbackKind,
    ReactAdminFeatureFlags,
    ReactAdminNavigationGroup,
    ReactAdminNavigationItem,
    ReactAdminNotificationTone,
    ReactAdminPageAction,
    ReactAdminPageActionVariant,
    ReactAdminPrincipal,
    ReactAdminRequiredScope,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
    ReactAdminShellChrome,
    ReactAdminShellNotification,
    ReactAdminShellState,
    ReactAdminShellStateKind,
    ReactAdminVersion,
)
from multi_agent_platform.api.schemas.admin_skill_lifecycle import (
    BindingEligibilityPreviewRequest,
    CredentialConfigurationRequest,
    ReadinessRefreshRequest,
    SkillExecutionDiagnosticList,
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
    WorkflowDraftSaveRequest,
    WorkflowPublishRequest,
    WorkflowReferenceCatalog,
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
from multi_agent_platform.db.repositories.audit import AuditRepository
from multi_agent_platform.observability.metrics import (
    record_admin_shell_audit_failure,
)
from multi_agent_platform.operations.workbench import (
    build_operations_workbench_envelope,
    build_run_debug_envelope,
    build_workbench_export_snapshot,
)
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

router = APIRouter(tags=["admin-react"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

REACT_MOUNT_PATH = "/admin/app"
REACT_BOOTSTRAP_URL = "/admin/app/bootstrap.json"
REACT_CONFIG_URL = "/admin/app/config.json"
REACT_MANIFEST_URL = "/admin/app/manifest.json"
REACT_SEARCH_URL = "/admin/app/search.json"
REACT_PATTERNS_PATH = "/admin/app/patterns"
REACT_PATTERNS_URL = "/admin/app/patterns.json"
REACT_PATTERNS_ACTION_URL = "/admin/app/patterns/actions/sample"
REACT_PATTERNS_EXPORT_URL = "/admin/app/patterns/export"
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
DESIGN_TOKEN_VERSION = "qa034"
DISABLED_REACT_FALLBACKS: dict[str, str] = {
    "workflows": "/admin/workflows/ui",
    "operations": "/admin/operations",
}


@router.get("/admin/app", response_class=HTMLResponse)
async def react_admin_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="react admin is disabled")
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

    bootstrap_url = _with_tenant_query(REACT_BOOTSTRAP_URL, shell.active_scope)
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "admin_react/app.html",
            {
                "asset_manifest": react_admin_manifest(container),
                "bootstrap_url": bootstrap_url,
                "config_url": REACT_CONFIG_URL,
                "mount_path": REACT_MOUNT_PATH,
                "shell": shell,
            },
        ),
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
        raise HTTPException(status_code=404, detail="react admin is disabled")
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
    return react_admin_bootstrap_from_shell(
        shell=shell,
        principal=principal,
        container=container,
    )


@router.get("/admin/app/migration", response_class=HTMLResponse)
async def react_admin_migration_app(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> HTMLResponse:
    if not container.settings.react_admin_enabled:
        raise HTTPException(status_code=404, detail="react admin is disabled")
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
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "admin_react/app.html",
            {
                "asset_manifest": react_admin_manifest(container),
                "bootstrap_url": bootstrap_url,
                "config_url": REACT_CONFIG_URL,
                "mount_path": REACT_MOUNT_PATH,
            },
        ),
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
    return react_admin_bootstrap_from_shell(
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
    "/admin/app/migration/jinja-inventory.json",
    response_model=JinjaInventoryDashboard,
    responses={
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_migration_jinja_inventory(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> JinjaInventoryDashboard:
    shell = await _migration_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_jinja_inventory_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        item_limit_per_group=None,
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


@router.get("/admin/app/patterns", response_class=HTMLResponse)
async def react_admin_patterns_app(
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
    "/admin/app/patterns.json",
    response_model=AdminPageEnvelope,
    responses={
        400: {"model": SafeProblemDetail},
        401: {"model": SafeProblemDetail},
        403: {"model": SafeProblemDetail},
    },
)
async def react_admin_patterns_envelope(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    sort: Annotated[str, Query(max_length=40)] = "name",
    page_size: Annotated[int, Query(ge=1, le=50)] = 10,
    tenant_id: Annotated[str | None, Query()] = None,
) -> AdminPageEnvelope:
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
            detail=_problem_detail(
                reason=AdminProblemReason.TENANT_SCOPE_DENIED
                if exc.status_code == status.HTTP_403_FORBIDDEN
                else AdminProblemReason.AUTH_REQUIRED,
                status_code=exc.status_code,
                title="Patterns unavailable",
                detail=exc.reason_category,
                trace_id=principal.trace_id,
            ).model_dump(mode="json"),
        ) from exc
    return _patterns_envelope(
        shell=shell,
        status_filter=status_filter,
        sort=sort,
        page_size=page_size,
    )


@router.post(
    "/admin/app/patterns/actions/sample",
    response_model=MutationResult,
)
async def react_admin_patterns_sample_action(
    request: Request,
    payload: SampleActionRequest,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> MutationResult:
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
    return _sample_mutation_result(shell=shell, payload=payload)


@router.post("/admin/app/patterns/export", response_model=ExportSnapshot)
async def react_admin_patterns_export(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[str | None, Query()] = None,
) -> ExportSnapshot:
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
    return _export_snapshot(shell)


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
    tenant_id: Annotated[str | None, Query()] = None,
    workflow_draft_id: Annotated[str | None, Query()] = None,
    large: Annotated[bool, Query()] = False,
) -> WorkflowBuilderEnvelope:
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
    return build_workflow_builder_envelope(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        workflow_draft_id=workflow_draft_id,
        large=large,
    )


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
    tenant_id: Annotated[str | None, Query()] = None,
) -> WorkflowReferenceCatalog:
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
    return build_reference_catalog(scope=_scope_response(shell.active_scope))


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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    _ = workflow_draft_id
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
    return build_save_result(scope=_scope_response(shell.active_scope), request=payload)


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
    ready: Annotated[bool, Query()] = False,
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    _ = workflow_draft_id
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
    return build_validation_result(ready=ready)


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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BuilderMutationResult:
    _ = workflow_draft_id
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
    return build_publish_result(request=payload)


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
    return build_governance_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    return build_provider_list(
        scope=_scope_response(shell.active_scope), principal=principal
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
    return build_provider_probe_result(provider_id)


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
    return build_credential_reference_result(provider_id=provider_id, request=payload)


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
    return build_prompt_list(scope=_scope_response(shell.active_scope))


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
    return build_prompt_save_result(
        prompt_lineage_id=prompt_lineage_id, request=payload
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
    return build_prompt_preview(prompt_lineage_id=prompt_lineage_id, request=payload)


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
    return build_profile_list(scope=_scope_response(shell.active_scope))


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
    return build_profile_save_result(profile_id=profile_id, request=payload)


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
    return build_profile_resolution(profile_id)


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
    return build_routing_preview_mutation(
        scope=_scope_response(shell.active_scope),
        request=payload,
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
    return build_policy_history(scope=_scope_response(shell.active_scope))


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
    for provenance in build_run_provenance(scope=_scope_response(shell.active_scope)):
        if provenance.run_id == run_id:
            return provenance
    raise HTTPException(status_code=404, detail="run_provenance_not_found")


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
    return build_skill_lifecycle_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
    )


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
    return build_candidate_result(request=payload)


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
    _ = candidate_id
    await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return build_candidate_validation_result(ready=ready)


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
    _ = candidate_id
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return build_skill_publish_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
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
    _ = package_id
    shell = await _require_platform_admin(
        request=request,
        principal=principal,
        session=session,
        tenant_id=None,
    )
    return build_tenant_grant_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
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
    return build_package_lifecycle_result(
        package_id=package_id,
        action="quarantine",
        scope=_scope_response(shell.active_scope),
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
    return build_package_lifecycle_result(
        package_id=package_id,
        action="withdraw",
        scope=_scope_response(shell.active_scope),
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
    return build_tenant_discovery(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    return build_tenant_installations(scope=_scope_response(shell.active_scope))


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
    return build_install_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
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
    _ = installation_id
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
    return build_credential_configuration_result(request=payload)


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
    return build_readiness_refresh_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
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
    return build_skill_execution_diagnostics(scope=_scope_response(shell.active_scope))


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
    return build_connector_diagnostic_result(scope=_scope_response(shell.active_scope))


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
    return build_binding_preview_result(
        scope=_scope_response(shell.active_scope),
        request=payload,
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
    return build_skill_lifecycle_audit(scope=_scope_response(shell.active_scope))


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
    return build_test_bench_dashboard(
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
    return build_test_suite_list(scope=_scope_response(shell.active_scope))


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
    return build_suite_save_result(
        request=payload,
        scope=_scope_response(shell.active_scope),
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
    return build_test_suite_detail(
        suite_id=suite_id,
        scope=_scope_response(shell.active_scope),
    )


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
    return build_case_save_result(
        suite_id=suite_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
    )


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
    return build_run_launch_result(
        suite_id=suite_id,
        request=payload,
        scope=_scope_response(shell.active_scope),
    )


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
    return build_test_run_list(scope=_scope_response(shell.active_scope))


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
    return build_test_run_detail(
        run_id=run_id,
        scope=_scope_response(shell.active_scope),
    )


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
    return build_publish_gate_evidence(scope=_scope_response(shell.active_scope))


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
    _ = gate_id
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
    return build_gate_refresh_result(request=payload)


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
    return build_artifact_reference(artifact_reference_id=artifact_reference_id)


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
    return build_test_bench_audit(scope=_scope_response(shell.active_scope))


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
    return build_membership_dashboard(
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
    return build_invitation_result(
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
    return build_principal_link_result(
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
    return build_role_grant_result(
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
    return build_grant_revoke_result(
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
    return build_principal_status_result(
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
    return build_membership_status_result(
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
    return build_membership_access_history(
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
    return build_membership_audit(
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
        raise HTTPException(status_code=404, detail="react admin is disabled")
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
    return cast(
        HTMLResponse,
        container.workflow_ui_templates.TemplateResponse(
            request,
            "admin_react/app.html",
            {
                "asset_manifest": react_admin_manifest(container),
                "bootstrap_url": bootstrap_url,
                "config_url": REACT_CONFIG_URL,
                "mount_path": REACT_MOUNT_PATH,
            },
        ),
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
    return react_admin_bootstrap_from_shell(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelTelegramBriefingDashboard:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_channel_telegram_briefing_dashboard(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_telegram_config_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_webhook_validation_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_alias_save_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> ChannelMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_alias_action_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> LinkTokenResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_link_token_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> DeliveryDiagnosticList:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_delivery_diagnostics(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> RunStatusSummary:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_run_status_summary(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceList:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_briefing_preferences(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_preference_save_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_preference_import_result(
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> BriefingPreferenceMutationResult:
    shell = await _channel_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_preference_export_result(
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
    return build_usage_dashboard(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        allowed_scope_options=tuple(
            _scope_option_response(option) for option in shell.available_scopes
        ),
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
    return build_usage_events(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> UsageReactExportSummary:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_usage_export_result(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    tenant_id: Annotated[str | None, Query()] = None,
) -> UsageReactExportSummary:
    shell = await _usage_shell(
        request=request,
        principal=principal,
        session=session,
        tenant_id=tenant_id,
    )
    return build_usage_export_detail(
        scope=_scope_response(shell.active_scope),
        principal=principal,
        usage_export_request_id=usage_export_request_id,
    )


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
        "gateway",
        "telegram",
        "reliability",
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
    return build_operations_workbench_envelope(
        scope=_scope_response(shell.active_scope),
        principal=principal,
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
    return build_run_debug_envelope(
        scope=_scope_response(shell.active_scope),
        workflow_run_id=workflow_run_id,
    )


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
    return build_workbench_export_snapshot(
        scope=_scope_response(shell.active_scope),
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
    raise HTTPException(status_code=404, detail="react admin route is unavailable")


async def build_react_shell(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    tenant_id: str | None,
    allow_tenant_user: bool = False,
    current_path: str = REACT_MOUNT_PATH,
    tenant_user_label: str = "React Admin",
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
        title="React Admin",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="React Admin", href=current_path, active=True),
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
            "react admin audit persistence is unavailable",
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
        title="React Admin",
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
            "react tenant user audit persistence is unavailable",
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


def react_admin_bootstrap_from_shell(
    *,
    shell: AdminShellContext,
    principal: PrincipalContext,
    container: ContainerDep,
) -> ReactAdminBootstrap:
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
        shell=_shell_chrome_response(shell),
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


def _patterns_envelope(
    *,
    shell: AdminShellContext,
    status_filter: str | None,
    sort: str,
    page_size: int,
) -> AdminPageEnvelope:
    allowed_statuses = {"ready", "needs_review", "paused"}
    if status_filter is not None and status_filter not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_problem_detail(
                reason=AdminProblemReason.VALIDATION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Filter unavailable",
                detail="This filter is not available for the current admin page.",
                trace_id=None,
                field_errors=(
                    ValidationFieldError(
                        field="status",
                        label="Status",
                        message="Choose an allowed status filter.",
                        code="unsupported_filter",
                    ),
                ),
            ).model_dump(mode="json"),
        )
    allowed_sorts = {"name", "status", "-updated"}
    if sort not in allowed_sorts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_problem_detail(
                reason=AdminProblemReason.VALIDATION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Sort unavailable",
                detail="This sort order is not available for the current admin page.",
                trace_id=None,
                field_errors=(
                    ValidationFieldError(
                        field="sort",
                        label="Sort",
                        message="Choose an allowed sort option.",
                        code="unsupported_sort",
                    ),
                ),
            ).model_dump(mode="json"),
        )
    records = _sample_records(shell)
    if status_filter:
        records = tuple(record for record in records if record.status == status_filter)
    records = _sort_records(records, sort)
    page_size = min(page_size, 50)
    visible_records = records[:page_size]
    return AdminPageEnvelope(
        page_id="react-admin-patterns",
        title="Forms and data patterns",
        description=(
            "Harmless sample contracts for future React admin forms, tables, "
            "filters, exports, and safe mutation feedback."
        ),
        scope=_scope_response(shell.active_scope),
        state=None if visible_records else _empty_patterns_state(),
        data=PatternsSampleData(
            records=visible_records,
            form=SampleFormDescriptor(
                fields=(
                    FormFieldDescriptor(
                        field="sample_name",
                        label="Sample name",
                        required=True,
                        help_text="Use a harmless label for the sample action.",
                    ),
                    FormFieldDescriptor(
                        field="outcome",
                        label="Outcome",
                        required=True,
                        help_text=(
                            "Choose accepted, validation, stale, replay, or "
                            "confirmation to preview safe feedback."
                        ),
                    ),
                ),
                default_values={
                    "sample_name": "",
                    "outcome": "accepted",
                    "confirmed": False,
                },
                revision="sample-revision-current",
                idempotency_key="sample-idempotency-key",
            ),
            export_snapshot=_export_snapshot(shell),
            details=(
                EvidenceSummary(
                    evidence_id="patterns-audit-sample",
                    label="Audit reference",
                    summary="Sample actions return safe audit reference ids.",
                    reference_type=EvidenceReferenceType.AUDIT,
                ),
            ),
        ),
        filters=_filter_profile(shell=shell, status_filter=status_filter),
        pagination=PaginationState(
            page_size=page_size,
            next_cursor="next-sample-cursor" if len(records) > page_size else None,
            total_items=len(records),
        ),
        sorting=SortingState(
            active=_sort_field(sort),
            allowed=(
                SortField(key="name", label="Name", direction=AdminSortDirection.ASC),
                SortField(
                    key="status",
                    label="Status",
                    direction=AdminSortDirection.ASC,
                ),
                SortField(
                    key="-updated",
                    label="Recently updated",
                    direction=AdminSortDirection.DESC,
                ),
            ),
        ),
        actions=(
            AdminAction(
                action_id="sample-submit",
                label="Preview form result",
                method=AdminActionMethod.POST,
                href=_with_tenant_query(
                    REACT_PATTERNS_ACTION_URL,
                    shell.active_scope,
                ),
                variant=ReactAdminPageActionVariant.PRIMARY,
                requires_idempotency_key=True,
            ),
            AdminAction(
                action_id="sample-export",
                label="Preview export",
                method=AdminActionMethod.POST,
                href=_with_tenant_query(REACT_PATTERNS_EXPORT_URL, shell.active_scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
        evidence=(
            EvidenceSummary(
                evidence_id="patterns-validation",
                label="Validation evidence",
                summary="Contracts are generated from backend schemas.",
                reference_type=EvidenceReferenceType.VALIDATION,
            ),
        ),
        refresh=RefreshHint(mode="manual"),
    )


def _sample_records(shell: AdminShellContext) -> tuple[SampleRecord, ...]:
    scope_label = shell.active_scope.label or "Current scope"
    return (
        SampleRecord(
            record_id="sample-ready",
            name="Workflow readiness review",
            status="ready",
            owner_scope=scope_label,
            updated_label="Updated today",
            revision="sample-revision-current",
        ),
        SampleRecord(
            record_id="sample-review",
            name="Credential policy review",
            status="needs_review",
            owner_scope=scope_label,
            updated_label="Updated yesterday",
            revision="sample-revision-review",
        ),
        SampleRecord(
            record_id="sample-paused",
            name="Export safety preview",
            status="paused",
            owner_scope=scope_label,
            updated_label="Updated last week",
            revision="sample-revision-paused",
        ),
    )


def _sort_records(
    records: tuple[SampleRecord, ...],
    sort: str,
) -> tuple[SampleRecord, ...]:
    if sort == "status":
        return tuple(sorted(records, key=lambda record: record.status))
    if sort == "-updated":
        return tuple(reversed(records))
    return tuple(sorted(records, key=lambda record: record.name))


def _sort_field(sort: str) -> SortField:
    if sort == "status":
        return SortField(key="status", label="Status", direction=AdminSortDirection.ASC)
    if sort == "-updated":
        return SortField(
            key="-updated",
            label="Recently updated",
            direction=AdminSortDirection.DESC,
        )
    return SortField(key="name", label="Name", direction=AdminSortDirection.ASC)


def _filter_profile(
    *,
    shell: AdminShellContext,
    status_filter: str | None,
) -> FilterProfile:
    base_href = _with_tenant_query(REACT_PATTERNS_PATH, shell.active_scope)
    chips: tuple[FilterChip, ...] = ()
    if status_filter:
        chips = (
            FilterChip(
                key="status",
                label=f"Status: {status_filter.replace('_', ' ')}",
                value=status_filter,
                href=base_href,
            ),
        )
    return FilterProfile(
        profile_id="patterns-sample-filters",
        criteria=(
            FilterCriterion(
                key="status",
                label="Status",
                options=(
                    FilterOption(value="ready", label="Ready"),
                    FilterOption(value="needs_review", label="Needs review"),
                    FilterOption(value="paused", label="Paused"),
                ),
            ),
        ),
        active_chips=chips,
        saved_filters=(
            SavedFilterSummary(
                filter_id="patterns-ready",
                label="Ready samples",
                href=f"{base_href}{'&' if '?' in base_href else '?'}status=ready",
            ),
        ),
    )


def _sample_mutation_result(
    *,
    shell: AdminShellContext,
    payload: SampleActionRequest,
) -> MutationResult:
    audit_reference = f"audit-react-patterns-{shell.active_scope.scope_type}"
    if not payload.sample_name.strip():
        return MutationResult(
            status=AdminMutationStatus.VALIDATION_ERROR,
            summary="Review the highlighted fields before submitting again.",
            toast=ToastHint(
                tone=ReactAdminNotificationTone.WARNING,
                title="Validation needed",
                summary="Sample name is required.",
            ),
            field_errors=(
                ValidationFieldError(
                    field="sample_name",
                    label="Sample name",
                    message="Enter a sample name.",
                    code="required",
                ),
            ),
            audit_reference_id=audit_reference,
        )
    if payload.outcome == "stale" or payload.revision == "stale-revision":
        return MutationResult(
            status=AdminMutationStatus.STALE_CONFLICT,
            summary="Reload the latest sample state before submitting again.",
            stale_conflict=RevisionConflict(
                submitted_revision=payload.revision or "stale-revision",
                current_revision="sample-revision-current",
                message="The sample has a newer safe revision.",
                reload_href=_with_tenant_query(REACT_PATTERNS_PATH, shell.active_scope),
            ),
            audit_reference_id=audit_reference,
        )
    if payload.outcome == "replay" or payload.idempotency_key == "replay-key":
        return MutationResult(
            status=AdminMutationStatus.REPLAYED,
            summary="This idempotency key already has a recorded sample result.",
            idempotency=IdempotencyReplay(
                idempotency_key=payload.idempotency_key or "replay-key",
                replayed=True,
                original_result_reference="sample-result-previous",
                summary="No duplicate side effect was applied.",
            ),
            audit_reference_id=audit_reference,
        )
    if payload.outcome == "confirmation" and not payload.confirmed:
        return MutationResult(
            status=AdminMutationStatus.CONFIRMATION_REQUIRED,
            summary="Confirm the sample action before previewing the result.",
            confirmation=ConfirmationRequirement(
                title="Confirm sample action",
                summary="This preview uses a safe confirmation pattern.",
                confirm_label="Confirm preview",
            ),
            audit_reference_id=audit_reference,
        )
    return MutationResult(
        status=AdminMutationStatus.ACCEPTED,
        summary="Sample form result accepted without applying domain side effects.",
        toast=ToastHint(
            tone=ReactAdminNotificationTone.SUCCESS,
            title="Sample accepted",
            summary="The pattern returned a safe audit-aware result.",
        ),
        audit_reference_id=audit_reference,
    )


def _export_snapshot(shell: AdminShellContext) -> ExportSnapshot:
    return ExportSnapshot(
        export_id=f"sample-export-{shell.active_scope.scope_type}",
        status=AdminExportStatus.COMPLETE,
        summary="Sample export snapshot is ready as a safe artifact reference.",
        artifact_reference_id=f"artifact-ref-qa028-{shell.active_scope.scope_type}",
        progress_label="Complete",
        audit_reference_id=f"audit-export-qa028-{shell.active_scope.scope_type}",
    )


def _empty_patterns_state() -> ReactAdminShellState:
    return ReactAdminShellState(
        state=ReactAdminShellStateKind.FILTERED_EMPTY,
        title="No matching sample records",
        summary="Clear filters to review all authorized sample records.",
    )


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
        label=sanitize_text(group.label, fallback="Navigation", max_length=80),
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
    fallback_kind = ReactAdminFallbackKind.JINJA
    if item.admin_area == "workflows":
        href = _with_optional_tenant_query(REACT_WORKFLOWS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/workflows"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "governance":
        href = _with_optional_tenant_query(REACT_GOVERNANCE_PATH, active_scope)
        route_surface_key = "GET:/admin/app/governance"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "operations":
        href = _with_optional_tenant_query(REACT_OPERATIONS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/operations"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "agent_tests":
        href = _with_optional_tenant_query(REACT_TEST_BENCH_PATH, active_scope)
        route_surface_key = "GET:/admin/app/test-bench"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "memberships":
        href = _with_optional_tenant_query(REACT_MEMBERSHIPS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/memberships"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area == "usage_analytics":
        href = _with_optional_tenant_query(REACT_USAGE_PATH, active_scope)
        route_surface_key = "GET:/admin/app/usage"
        fallback_kind = ReactAdminFallbackKind.REACT
    elif item.admin_area in {"telegram_configuration", "briefing_preferences"}:
        href = _with_optional_tenant_query(REACT_CHANNELS_PATH, active_scope)
        route_surface_key = "GET:/admin/app/channels"
        fallback_kind = ReactAdminFallbackKind.REACT
    return ReactAdminNavigationItem(
        item_id=item.item_id,
        label=sanitize_text(item.label, fallback="Destination", max_length=80),
        group=sanitize_text(item.group, fallback="Navigation", max_length=80),
        href=href,
        route_surface_key=route_surface_key,
        required_scope=ReactAdminRequiredScope(item.required_scope),
        admin_area=item.admin_area,
        preserve_tenant_scope=item.preserve_tenant_scope,
        active=item.active,
        fallback_kind=fallback_kind,
    )


def _shell_chrome_response(shell: AdminShellContext) -> ReactAdminShellChrome:
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
                action_id="open-existing-console",
                label="Existing console",
                href="/admin",
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
            ReactAdminPageAction(
                action_id="open-workflows",
                label="Workflows",
                href=_with_tenant_query(REACT_WORKFLOWS_PATH, shell.active_scope),
                variant=ReactAdminPageActionVariant.PRIMARY,
            ),
        ),
        notifications=(
            ReactAdminShellNotification(
                notification_id="jinja-fallbacks-active",
                tone=ReactAdminNotificationTone.INFO,
                title="Existing pages remain active",
                summary=(
                    "Domain pages still open through the authorized console "
                    "until their React migration specs pass."
                ),
                href="/admin",
            ),
        ),
        states=_common_shell_states(),
        command_results=_command_results(shell),
        design_token_version=DESIGN_TOKEN_VERSION,
        search_url=_with_tenant_query(REACT_SEARCH_URL, shell.active_scope),
    )


def _common_shell_states() -> tuple[ReactAdminShellState, ...]:
    return (
        ReactAdminShellState(
            state=ReactAdminShellStateKind.LOADING,
            title="Loading admin workspace",
            summary="Checking your signed-in principal and active scope.",
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.EMPTY,
            title="No records yet",
            summary="This area has no records available for your current scope.",
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.FILTERED_EMPTY,
            title="No matching results",
            summary=(
                "Adjust filters or clear the search to review all authorized records."
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DENIED,
            title="Access denied",
            summary="Your current principal is not authorized for this admin area.",
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.NOT_FOUND,
            title="Page not found",
            summary="The requested admin destination is unavailable for this route.",
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.VALIDATION_ERROR,
            title="Review required fields",
            summary="Fix the highlighted values and try again.",
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.DEPENDENCY_UNAVAILABLE,
            title="Dependency unavailable",
            summary=(
                "A required admin dependency is not ready. Try again after it recovers."
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.PARTIAL_DATA,
            title="Partial data",
            summary=(
                "Some optional summaries are unavailable, but authorized "
                "navigation is ready."
            ),
        ),
        ReactAdminShellState(
            state=ReactAdminShellStateKind.UNEXPECTED_ERROR,
            title="Unexpected error",
            summary="The admin shell could not complete this request safely.",
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
    return f"{path}?tenant_id={scope.tenant_id}"


def _with_optional_tenant_query(path: str, scope: AdminScope | None) -> str:
    if scope is None:
        return path
    return _with_tenant_query(path, scope)
