#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

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
    PromptGovernanceList,
    ProviderGovernanceList,
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
    MigrationRollbackPlan,
    MigrationRouteGroup,
)
from multi_agent_platform.api.schemas.admin_patterns import (
    AdminPageEnvelope,
    ExportSnapshot,
    MutationResult,
    SafeProblemDetail,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminAssetManifestSummary,
    ReactAdminBootstrap,
    ReactAdminCommandSearch,
    ReactAdminConfig,
    SafeProblem,
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
    UsageReactDashboard,
    UsageReactEventDrilldown,
    UsageReactExportCreateRequest,
    UsageReactExportSummary,
)
from multi_agent_platform.api.schemas.admin_workbench import (
    OperationsWorkbenchEnvelope,
    RunDebugEnvelope,
    WorkbenchExportSnapshot,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    BuilderMutationResult,
    WorkflowBuilderEnvelope,
    WorkflowReferenceCatalog,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "frontend/admin/src/api/generated/reactAdminApi.ts"


def schema_payload() -> dict[str, Any]:
    return {
        "ReactAdminBootstrap": ReactAdminBootstrap.model_json_schema(),
        "ReactAdminConfig": ReactAdminConfig.model_json_schema(),
        "ReactAdminCommandSearch": ReactAdminCommandSearch.model_json_schema(),
        "AdminPageEnvelope": AdminPageEnvelope.model_json_schema(),
        "MutationResult": MutationResult.model_json_schema(),
        "ExportSnapshot": ExportSnapshot.model_json_schema(),
        "SafeProblemDetail": SafeProblemDetail.model_json_schema(),
        "OperationsWorkbenchEnvelope": (
            OperationsWorkbenchEnvelope.model_json_schema()
        ),
        "RunDebugEnvelope": RunDebugEnvelope.model_json_schema(),
        "WorkbenchExportSnapshot": WorkbenchExportSnapshot.model_json_schema(),
        "WorkflowBuilderEnvelope": WorkflowBuilderEnvelope.model_json_schema(),
        "WorkflowReferenceCatalog": WorkflowReferenceCatalog.model_json_schema(),
        "BuilderMutationResult": BuilderMutationResult.model_json_schema(),
        "GovernanceDashboard": GovernanceDashboard.model_json_schema(),
        "ProviderGovernanceList": ProviderGovernanceList.model_json_schema(),
        "PromptGovernanceList": PromptGovernanceList.model_json_schema(),
        "ProfileGovernanceList": ProfileGovernanceList.model_json_schema(),
        "PolicyHistoryList": PolicyHistoryList.model_json_schema(),
        "GovernanceMutationResult": GovernanceMutationResult.model_json_schema(),
        "SafePromptPreview": SafePromptPreview.model_json_schema(),
        "ProfileResolutionPreview": ProfileResolutionPreview.model_json_schema(),
        "SkillLifecycleDashboard": SkillLifecycleDashboard.model_json_schema(),
        "TenantSkillDiscoveryList": TenantSkillDiscoveryList.model_json_schema(),
        "TenantSkillInstallationList": (
            TenantSkillInstallationList.model_json_schema()
        ),
        "SkillExecutionDiagnosticList": (
            SkillExecutionDiagnosticList.model_json_schema()
        ),
        "SkillLifecycleAuditList": SkillLifecycleAuditList.model_json_schema(),
        "SkillLifecycleMutationResult": (
            SkillLifecycleMutationResult.model_json_schema()
        ),
        "SkillPackageCandidateRequest": (
            SkillPackageCandidateRequest.model_json_schema()
        ),
        "SkillPackagePublishRequest": SkillPackagePublishRequest.model_json_schema(),
        "TenantGrantMutationRequest": TenantGrantMutationRequest.model_json_schema(),
        "TenantSkillInstallRequest": TenantSkillInstallRequest.model_json_schema(),
        "CredentialConfigurationRequest": (
            CredentialConfigurationRequest.model_json_schema()
        ),
        "ReadinessRefreshRequest": ReadinessRefreshRequest.model_json_schema(),
        "BindingEligibilityPreviewRequest": (
            BindingEligibilityPreviewRequest.model_json_schema()
        ),
        "TestBenchDashboard": TestBenchDashboard.model_json_schema(),
        "TestSuiteList": TestSuiteList.model_json_schema(),
        "TestSuiteDetail": TestSuiteDetail.model_json_schema(),
        "TestRunList": TestRunList.model_json_schema(),
        "TestRunDetail": TestRunDetail.model_json_schema(),
        "PublishGateEvidenceList": PublishGateEvidenceList.model_json_schema(),
        "ArtifactReferenceSummary": ArtifactReferenceSummary.model_json_schema(),
        "TestBenchAuditList": TestBenchAuditList.model_json_schema(),
        "TestBenchMutationResult": TestBenchMutationResult.model_json_schema(),
        "TestSuiteSaveRequest": TestSuiteSaveRequest.model_json_schema(),
        "TestCaseSaveRequest": TestCaseSaveRequest.model_json_schema(),
        "TestRunLaunchRequest": TestRunLaunchRequest.model_json_schema(),
        "GateEvidenceRefreshRequest": GateEvidenceRefreshRequest.model_json_schema(),
        "MembershipDashboard": MembershipDashboard.model_json_schema(),
        "MembershipAccessHistoryList": (
            MembershipAccessHistoryList.model_json_schema()
        ),
        "MembershipAuditList": MembershipAuditList.model_json_schema(),
        "MembershipMutationResult": MembershipMutationResult.model_json_schema(),
        "MembershipInvitationSaveRequest": (
            MembershipInvitationSaveRequest.model_json_schema()
        ),
        "PrincipalLinkRequest": PrincipalLinkRequest.model_json_schema(),
        "RoleGrantSaveRequest": RoleGrantSaveRequest.model_json_schema(),
        "MembershipConfirmationRequest": (
            MembershipConfirmationRequest.model_json_schema()
        ),
        "UsageReactDashboard": UsageReactDashboard.model_json_schema(),
        "UsageReactEventDrilldown": UsageReactEventDrilldown.model_json_schema(),
        "UsageReactExportSummary": UsageReactExportSummary.model_json_schema(),
        "UsageReactExportCreateRequest": (
            UsageReactExportCreateRequest.model_json_schema()
        ),
        "ChannelTelegramBriefingDashboard": (
            ChannelTelegramBriefingDashboard.model_json_schema()
        ),
        "ChannelMutationResult": ChannelMutationResult.model_json_schema(),
        "LinkTokenResult": LinkTokenResult.model_json_schema(),
        "DeliveryDiagnosticList": DeliveryDiagnosticList.model_json_schema(),
        "RunStatusSummary": RunStatusSummary.model_json_schema(),
        "BriefingPreferenceList": BriefingPreferenceList.model_json_schema(),
        "BriefingPreferenceMutationResult": (
            BriefingPreferenceMutationResult.model_json_schema()
        ),
        "TelegramConfigSaveRequest": TelegramConfigSaveRequest.model_json_schema(),
        "WebhookValidationRequest": WebhookValidationRequest.model_json_schema(),
        "TelegramAliasSaveRequest": TelegramAliasSaveRequest.model_json_schema(),
        "TelegramAliasActionRequest": TelegramAliasActionRequest.model_json_schema(),
        "LinkTokenCreateRequest": LinkTokenCreateRequest.model_json_schema(),
        "BriefingPreferenceSaveRequest": (
            BriefingPreferenceSaveRequest.model_json_schema()
        ),
        "BriefingPreferenceImportRequest": (
            BriefingPreferenceImportRequest.model_json_schema()
        ),
        "BriefingPreferenceExportRequest": (
            BriefingPreferenceExportRequest.model_json_schema()
        ),
        "AdminMigrationHardeningDashboard": (
            AdminMigrationHardeningDashboard.model_json_schema()
        ),
        "MigrationRouteGroup": MigrationRouteGroup.model_json_schema(),
        "MigrationRollbackPlan": MigrationRollbackPlan.model_json_schema(),
        "ReactAdminAssetManifestSummary": (
            ReactAdminAssetManifestSummary.model_json_schema()
        ),
        "SafeProblem": SafeProblem.model_json_schema(),
    }


def render_types() -> str:
    schema_json = json.dumps(schema_payload(), sort_keys=True, separators=(",", ":"))
    schema_hash = hashlib.sha256(schema_json.encode("utf-8")).hexdigest()
    return f"""/* eslint-disable */
// Generated by scripts/frontend/generate_admin_react_types.py.
// Do not edit by hand.

export const REACT_ADMIN_SCHEMA_HASH = "{schema_hash}";

export type ReactAdminAuthMode = "auth0" | "local_principal";
export type ReactAdminScopeType = "platform" | "tenant";
export type ReactAdminRequiredScope = "platform" | "tenant" | "either";
export type ReactAdminFallbackKind = "jinja" | "react" | "disabled";
export type ReactAdminPageActionMethod = "get";
export type ReactAdminPageActionVariant = "primary" | "secondary" | "danger" | "ghost";
export type AdminActionMethod = "get" | "post" | "put" | "patch" | "delete";
export type AdminProblemReason =
  | "auth_required"
  | "insufficient_role"
  | "tenant_scope_denied"
  | "validation_error"
  | "stale_conflict"
  | "confirmation_required"
  | "dependency_unavailable"
  | "unexpected_error";
export type AdminMutationStatus =
  | "accepted"
  | "validation_error"
  | "stale_conflict"
  | "replayed"
  | "confirmation_required"
  | "dependency_unavailable"
  | "unexpected_error";
export type AdminSortDirection = "asc" | "desc";
export type AdminExportStatus =
  | "queued"
  | "running"
  | "complete"
  | "failed"
  | "expired";
export type EvidenceReferenceType =
  | "audit"
  | "export"
  | "delivery"
  | "runtime"
  | "gateway"
  | "validation";
export type ReactAdminShellStateKind =
  | "loading"
  | "empty"
  | "filtered_empty"
  | "denied"
  | "not_found"
  | "validation_error"
  | "dependency_unavailable"
  | "partial_data"
  | "unexpected_error";
export type ReactAdminNotificationTone = "info" | "success" | "warning" | "critical";
export type WorkbenchStatus =
  | "ready"
  | "degraded"
  | "warning"
  | "critical"
  | "unavailable";
export type WorkbenchSeverity = "info" | "warning" | "critical";
export type WorkflowBuilderStatus =
  | "ready"
  | "dirty"
  | "validating"
  | "blocked"
  | "warning"
  | "stale"
  | "published"
  | "unavailable";
export type WorkflowBuilderSeverity =
  | "info"
  | "warning"
  | "blocking"
  | "critical";
export type GovernanceStatus =
  | "ready"
  | "degraded"
  | "warning"
  | "blocked"
  | "denied"
  | "unavailable"
  | "running"
  | "summarized";
export type SkillLifecycleStatus =
  | "ready"
  | "degraded"
  | "warning"
  | "blocked"
  | "denied"
  | "unavailable"
  | "queued"
  | "running"
  | "passed"
  | "failed"
  | "stale"
  | "published"
  | "quarantined"
  | "withdrawn"
  | "summarized";
export type TestBenchStatus =
  | "ready"
  | "warning"
  | "blocked"
  | "denied"
  | "unavailable"
  | "missing"
  | "stale"
  | "queued"
  | "running"
  | "passed"
  | "failed"
  | "failed_assertion"
  | "contract_failure"
  | "evaluator_failure"
  | "safe_mode_block"
  | "runtime_error"
  | "canceled"
  | "timed_out"
  | "partial"
  | "summarized";
export type MembershipLifecycleStatus =
  | "ready"
  | "active"
  | "pending"
  | "accepted"
  | "expired"
  | "revoked"
  | "suspended"
  | "removed"
  | "denied"
  | "unavailable"
  | "stale"
  | "partial"
  | "replayed";
export type MembershipScopeType = "platform" | "tenant";
export type UsageReactConfidenceStatus =
  | "confirmed"
  | "estimated"
  | "partial"
  | "unavailable";
export type UsageReactTone = "neutral" | "success" | "warning" | "danger";
export type UsageReactGroupBy =
  | "day"
  | "tenant"
  | "provider"
  | "model"
  | "workflow"
  | "agent"
  | "sub_agent"
  | "prompt"
  | "execution_mode"
  | "principal"
  | "graph_node"
  | "gateway_operation"
  | "physical_attempt"
  | "governed_tool";
export type UsageReactProblemReason =
  | "denied"
  | "empty"
  | "partial"
  | "unavailable"
  | "stale_pricing"
  | "export_pending"
  | "audit_unavailable"
  | "unsupported_filter"
  | "invalid_range";
export type UsageReactExportStatus = "pending" | "completed" | "failed" | "denied";
export type ChannelReadinessStatus =
  | "ready"
  | "partial"
  | "disabled"
  | "stale"
  | "failed"
  | "unavailable";
export type ChannelActionMethod = "get" | "post";
export type ChannelMutationStatus =
  | "accepted"
  | "replayed"
  | "validation_error"
  | "conflict"
  | "denied"
  | "audit_unavailable"
  | "dependency_unavailable";
export type AliasLifecycleStatus =
  | "active"
  | "disabled"
  | "pending_validation"
  | "deleted";
export type AliasProtectedReadiness =
  | "ready"
  | "blocked"
  | "missing_identity"
  | "missing_config"
  | "validation_error";
export type LinkedIdentityStatus = "linked" | "pending" | "revoked" | "stale";
export type DeliveryAttemptStatus =
  | "delivered"
  | "retrying"
  | "failed"
  | "skipped"
  | "unavailable";
export type DeliveryRetryCategory =
  | "none"
  | "retryable"
  | "permanent"
  | "throttled"
  | "policy_denied"
  | "dependency_unavailable";
export type BotBoundaryStatus =
  | "mocked"
  | "skipped"
  | "delivered"
  | "failed"
  | "unavailable";
export type WebhookDiagnosticStatus =
  | "valid"
  | "stale"
  | "failed"
  | "unavailable"
  | "pending";
export type RunStatusCategory =
  | "queued"
  | "running"
  | "waiting"
  | "completed"
  | "failed"
  | "cancelled"
  | "unavailable";
export type CommuteMode = "none" | "car" | "transit" | "walk" | "bike" | "remote";
export type BriefingOutputStyle =
  | "concise"
  | "executive"
  | "detailed"
  | "action_first";
export type MigrationOverallStatus = "ready" | "partial" | "blocked" | "rollback";
export type MigrationRouteDecision =
  | "react_primary"
  | "redirect"
  | "alias"
  | "retained_fallback"
  | "retirement_candidate"
  | "blocked";
export type MigrationScopeRequirement =
  | "platform"
  | "tenant_admin"
  | "tenant_user"
  | "auditor"
  | "mixed";
export type MigrationEvidenceStatus = "pass" | "warning" | "fail";
export type MigrationProblemSeverity = "info" | "warning" | "blocking";

export interface ReactAdminPrincipal {{
  principal_id: string;
  display_name: string | null;
  role_codes: string[];
  auth_mode: ReactAdminAuthMode;
  trace_id: string;
}}

export interface ReactAdminScope {{
  scope_type: ReactAdminScopeType;
  tenant_id: string | null;
  label: string;
}}

export interface ReactAdminScopeOption {{
  scope: ReactAdminScope;
  label: string;
  href: string;
  selected: boolean;
}}

export interface ReactAdminNavigationItem {{
  item_id: string;
  label: string;
  group: string;
  href: string;
  route_surface_key: string;
  required_scope: ReactAdminRequiredScope;
  admin_area: string | null;
  preserve_tenant_scope: boolean;
  active: boolean;
  fallback_kind: ReactAdminFallbackKind;
}}

export interface ReactAdminNavigationGroup {{
  label: string;
  items: ReactAdminNavigationItem[];
}}

export interface ReactAdminBreadcrumb {{
  label: string;
  href: string | null;
  active: boolean;
}}

export interface ReactAdminPageAction {{
  action_id: string;
  label: string;
  href: string | null;
  method: ReactAdminPageActionMethod;
  variant: ReactAdminPageActionVariant;
  disabled_reason: string | null;
}}

export interface ReactAdminShellState {{
  state: ReactAdminShellStateKind;
  title: string;
  summary: string;
  action: ReactAdminPageAction | null;
  trace_id: string | null;
}}

export interface ReactAdminSavedFilterChip {{
  filter_id: string;
  label: string;
  admin_area: string;
  href: string;
  scope_type: ReactAdminScopeType;
  tenant_id: string | null;
}}

export interface ReactAdminShellNotification {{
  notification_id: string;
  tone: ReactAdminNotificationTone;
  title: string;
  summary: string;
  href: string | null;
}}

export interface ReactAdminCommandSearchResult {{
  result_id: string;
  label: string;
  description: string | null;
  group: string;
  href: string;
  required_scope: ReactAdminRequiredScope;
  fallback_kind: ReactAdminFallbackKind;
}}

export interface ReactAdminCommandSearch {{
  query: string;
  results: ReactAdminCommandSearchResult[];
}}

export interface ReactAdminShellChrome {{
  product_name: string;
  active_area: string;
  breadcrumbs: ReactAdminBreadcrumb[];
  page_actions: ReactAdminPageAction[];
  saved_filters: ReactAdminSavedFilterChip[];
  notifications: ReactAdminShellNotification[];
  states: ReactAdminShellState[];
  command_results: ReactAdminCommandSearchResult[];
  design_token_version: string;
  search_url: string;
}}

export interface ValidationFieldError {{
  field: string;
  label: string;
  message: string;
  code: string;
}}

export interface SafeProblemDetail {{
  type: string;
  title: string;
  status: number;
  detail: string;
  reason_category: AdminProblemReason;
  field_errors: ValidationFieldError[];
  retry_after_seconds: number | null;
  audit_reference_id: string | null;
}}

export interface ConfirmationRequirement {{
  title: string;
  summary: string;
  confirm_label: string;
}}

export interface AdminAction {{
  action_id: string;
  label: string;
  method: AdminActionMethod;
  href: string;
  variant: ReactAdminPageActionVariant;
  requires_confirmation: boolean;
  confirmation: ConfirmationRequirement | null;
  requires_idempotency_key: boolean;
  action_token: string | null;
  enabled: boolean;
  disabled_reason: string | null;
}}

export interface ToastHint {{
  tone: ReactAdminNotificationTone;
  title: string;
  summary: string;
}}

export interface RevisionConflict {{
  submitted_revision: string;
  current_revision: string;
  message: string;
  reload_href: string;
}}

export interface IdempotencyReplay {{
  idempotency_key: string;
  replayed: boolean;
  original_result_reference: string | null;
  summary: string;
}}

export interface MutationResult {{
  status: AdminMutationStatus;
  summary: string;
  toast: ToastHint | null;
  field_errors: ValidationFieldError[];
  stale_conflict: RevisionConflict | null;
  idempotency: IdempotencyReplay | null;
  confirmation: ConfirmationRequirement | null;
  audit_reference_id: string | null;
  next_action: AdminAction | null;
}}

export interface FilterOption {{
  value: string;
  label: string;
}}

export interface FilterCriterion {{
  key: string;
  label: string;
  operator: "equals" | "in";
  options: FilterOption[];
}}

export interface FilterChip {{
  key: string;
  label: string;
  value: string;
  href: string;
}}

export interface SavedFilterSummary {{
  filter_id: string;
  label: string;
  href: string;
}}

export interface FilterProfile {{
  profile_id: string;
  criteria: FilterCriterion[];
  active_chips: FilterChip[];
  saved_filters: SavedFilterSummary[];
}}

export interface PaginationState {{
  page_size: number;
  page_size_options: number[];
  next_cursor: string | null;
  previous_cursor: string | null;
  total_known: boolean;
  total_items: number | null;
}}

export interface SortField {{
  key: string;
  label: string;
  direction: AdminSortDirection;
}}

export interface SortingState {{
  active: SortField;
  allowed: SortField[];
}}

export interface ExportSnapshot {{
  export_id: string;
  status: AdminExportStatus;
  summary: string;
  artifact_reference_id: string | null;
  progress_label: string | null;
  expires_at: string | null;
  audit_reference_id: string | null;
}}

export interface EvidenceSummary {{
  evidence_id: string;
  label: string;
  summary: string;
  reference_type: EvidenceReferenceType;
  href: string | null;
}}

export interface RefreshHint {{
  mode: string;
  interval_seconds: number | null;
}}

export interface WorkbenchTimeRange {{
  preset: string;
  label: string;
  start: string | null;
  end: string | null;
}}

export interface WorkbenchLink {{
  label: string;
  href: string;
}}

export interface WorkbenchMetric {{
  label: string;
  value: string;
  status: WorkbenchStatus;
  summary: string | null;
}}

export interface WorkbenchSummaryCard {{
  card_id: string;
  label: string;
  value: string;
  status: WorkbenchStatus;
  severity: WorkbenchSeverity;
  summary: string;
  freshness_label: string;
  trend: string | null;
  href: string | null;
  evidence_reference_id: string | null;
}}

export interface LikelyCauseSummary {{
  cause_id: string;
  severity: WorkbenchSeverity;
  affected_subsystem: string;
  symptom: string;
  likely_cause_category: string;
  recommended_next_step: string;
  href: string | null;
  confidence_label: string;
  evidence_reference_id: string | null;
}}

export interface HealthPressurePanel {{
  panel_id: string;
  title: string;
  status: WorkbenchStatus;
  metrics: WorkbenchMetric[];
  dependencies: WorkbenchMetric[];
  freshness_label: string;
  polling_allowed: boolean;
  partial_reason: string | null;
  links: WorkbenchLink[];
}}

export interface TimelineEventSummary {{
  event_id: string;
  occurred_at_label: string;
  sequence: number | null;
  category: string;
  severity: WorkbenchSeverity;
  status: WorkbenchStatus;
  summary: string;
  details: Record<string, string>;
  trace_id: string | null;
  audit_reference_id: string | null;
  links: WorkbenchLink[];
}}

export interface GraphBranchSummary {{
  branch_id: string;
  label: string;
  status: WorkbenchStatus;
  node_count: number;
  completed_count: number;
  failed_count: number;
  waiting_count: number;
  join_policy: string | null;
  join_decision: string | null;
  manual_resolution_required: boolean;
  summary: string;
}}

export interface GatewayAttemptSummary {{
  attempt_id: string;
  provider_label: string;
  model_label: string;
  status: WorkbenchStatus;
  latency_ms: number | null;
  retry_category: string | null;
  breaker_category: string | null;
  credential_diagnostic_category: string | null;
  usage_reference_id: string | null;
  safe_summary: string;
  evidence_reference_id: string | null;
}}

export interface ToolCallSummary {{
  tool_call_id: string;
  tool_label: string;
  connector_label: string;
  readiness_status: WorkbenchStatus;
  policy_outcome: string;
  side_effect_classification: string;
  result_category: string;
  safe_summary: string;
  evidence_reference_id: string | null;
}}

export interface ChannelDeliverySummary {{
  delivery_id: string;
  channel: string;
  alias_label: string;
  identity_status: WorkbenchStatus;
  receipt_status: WorkbenchStatus;
  notification_status: WorkbenchStatus;
  delivery_status: WorkbenchStatus;
  failure_category: string | null;
  safe_summary: string;
  evidence_reference_id: string | null;
}}

export interface ReliabilityRecoveryItem {{
  item_id: string;
  label: string;
  status: WorkbenchStatus;
  severity: WorkbenchSeverity;
  summary: string;
  href: string | null;
  confirmation: string | null;
}}

export interface ReliabilityRecoverySummary {{
  breakers: ReliabilityRecoveryItem[];
  retries: ReliabilityRecoveryItem[];
  dead_letters: ReliabilityRecoveryItem[];
  confirmations: ReliabilityRecoveryItem[];
  partial_reason: string | null;
}}

export interface WorkbenchLogSummary {{
  log_id: string;
  occurred_at_label: string;
  source: string;
  severity: WorkbenchSeverity;
  status: WorkbenchStatus;
  subsystem: string;
  tenant_scope: string | null;
  run_reference: string | null;
  correlation_reference: string | null;
  summary: string;
  safe_details: Record<string, string>;
  links: WorkbenchLink[];
}}

export interface WorkbenchExportSnapshot extends ExportSnapshot {{
  scope_label: string;
  redaction_summary: string;
  row_count: number;
}}

export interface RunDebugEnvelope {{
  workflow_run_id: string;
  tenant_scope: ReactAdminScope | null;
  run_status: WorkbenchStatus;
  safe_title: string;
  timeline: TimelineEventSummary[];
  branches: GraphBranchSummary[];
  gateway_attempts: GatewayAttemptSummary[];
  tool_calls: ToolCallSummary[];
  deliveries: ChannelDeliverySummary[];
  lineage: WorkbenchLink[];
  replay_links: WorkbenchLink[];
  bundle_summary: string;
  fallback_links: WorkbenchLink[];
  state: ReactAdminShellState | null;
}}

export interface OperationsWorkbenchEnvelope {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  generated_at_label: string;
  time_range: WorkbenchTimeRange;
  summary_cards: WorkbenchSummaryCard[];
  likely_causes: LikelyCauseSummary[];
  health_panels: HealthPressurePanel[];
  run_debug: RunDebugEnvelope | null;
  reliability: ReliabilityRecoverySummary;
  logs: WorkbenchLogSummary[];
  filters: FilterProfile;
  actions: AdminAction[];
  exports: WorkbenchExportSnapshot;
  fallback_links: WorkbenchLink[];
  evidence: EvidenceSummary[];
  state: ReactAdminShellState | null;
  refresh: RefreshHint | null;
}}

export interface BuilderSection {{
  section_id: string;
  label: string;
  status: WorkflowBuilderStatus;
  summary: string;
  href: string | null;
}}

export interface WorkflowReferenceOption {{
  reference_id: string;
  label: string;
  kind: string;
  readiness_status: WorkflowBuilderStatus;
  tenant_eligible: boolean;
  version_label: string | null;
  safe_summary: string;
  href: string | null;
}}

export interface WorkflowReferenceCatalog {{
  prompt_options: WorkflowReferenceOption[];
  profile_options: WorkflowReferenceOption[];
  provider_options: WorkflowReferenceOption[];
  skill_options: WorkflowReferenceOption[];
  test_suite_options: WorkflowReferenceOption[];
  subworkflow_options: WorkflowReferenceOption[];
}}

export interface WorkflowGraphNode {{
  node_id: string;
  label: string;
  node_type: string;
  status: WorkflowBuilderStatus;
  role_label: string | null;
  summary: string;
  x: number;
  y: number;
}}

export interface WorkflowGraphEdge {{
  edge_id: string;
  source: string;
  target: string;
  label: string | null;
  condition_category: string | null;
}}

export interface WorkflowJoinPolicySummary {{
  policy_id: string;
  label: string;
  summary: string;
  required_branch_count: number;
}}

export interface WorkflowGraphPreview {{
  layout_revision: string;
  layout_is_authoritative: boolean;
  nodes: WorkflowGraphNode[];
  edges: WorkflowGraphEdge[];
  join_policies: WorkflowJoinPolicySummary[];
  accessibility_summary: string;
}}

export interface ValidationFinding {{
  finding_id: string;
  severity: WorkflowBuilderSeverity;
  category: string;
  section: string;
  message: string;
  recommended_action: string;
  href: string | null;
  evidence_reference_id: string | null;
}}

export interface WorkflowValidationSummary {{
  validation_id: string;
  status: WorkflowBuilderStatus;
  revision: string;
  generated_at_label: string;
  summary: string;
  findings: ValidationFinding[];
  artifact_reference_ids: string[];
}}

export interface WorkflowEvidenceSummary {{
  evidence_id: string;
  label: string;
  status: WorkflowBuilderStatus;
  summary: string;
  artifact_reference_id: string | null;
  href: string | null;
}}

export interface WorkflowPublishReadiness {{
  decision: AdminMutationStatus;
  revision: string;
  summary: string;
  blockers: string[];
  warnings: string[];
  required_evidence: WorkflowEvidenceSummary[];
  confirmation: ConfirmationRequirement | null;
  published_bundle_summary: string | null;
}}

export interface WorkflowRevisionSummary {{
  revision: string;
  created_at_label: string;
  actor_label: string;
  change_category: string;
  summary: string;
  audit_reference_id: string | null;
  compare_href: string | null;
  current: boolean;
}}

export interface WorkflowJsonInspector {{
  collapsed_by_default: boolean;
  summary: string;
  redaction_summary: string;
  safe_document_preview: Record<string, string>;
  artifact_reference_id: string | null;
}}

export interface WorkflowDraftDocument {{
  workflow_draft_id: string;
  workflow_lineage_id: string;
  revision: string;
  name: string;
  description: string;
  status: WorkflowBuilderStatus;
  tenant_label: string | null;
  metadata_summary: string;
  roles_summary: string;
  references_summary: string;
  graph: WorkflowGraphPreview;
}}

export interface WorkflowDraftSaveRequest {{
  revision: string;
  idempotency_key: string;
  name: string;
  description: string;
  selected_prompt_ref: string | null;
  selected_profile_ref: string | null;
  join_policy: string;
  force_stale: boolean;
}}

export interface WorkflowPublishRequest {{
  revision: string;
  confirmed: boolean;
  idempotency_key: string;
  ready_fixture: boolean;
}}

export interface BuilderMutationResult extends MutationResult {{
  revision: string | null;
  validation: WorkflowValidationSummary | null;
  publish_readiness: WorkflowPublishReadiness | null;
}}

export interface WorkflowBuilderEnvelope {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  draft: WorkflowDraftDocument;
  sections: BuilderSection[];
  reference_catalog: WorkflowReferenceCatalog;
  validation: WorkflowValidationSummary;
  publish_readiness: WorkflowPublishReadiness;
  revisions: WorkflowRevisionSummary[];
  json_inspector: WorkflowJsonInspector;
  actions: AdminAction[];
  state: ReactAdminShellState | null;
  refresh: RefreshHint | null;
}}

export interface GovernanceSection {{
  section_id: string;
  label: string;
  status: GovernanceStatus;
  summary: string;
  href: string | null;
}}

export interface ProviderCredentialReference {{
  reference_id: string;
  label: string;
  source_type: string;
  readiness: GovernanceStatus;
  fingerprint: string | null;
  last_resolution_status: string;
  last_checked_label: string;
  policy_reason: string;
  remediation: string;
}}

export interface ProviderHealthSummary {{
  status: GovernanceStatus;
  latency_bucket: string;
  breaker_state: string;
  checked_at_label: string;
  summary: string;
}}

export interface ProviderProbeDiagnostic {{
  probe_id: string;
  provider_id: string;
  status: GovernanceStatus;
  summary: string;
  latency_bucket: string;
  failure_category: string | null;
  retry_state: string;
  breaker_state: string;
  credential_resolution_status: string;
  audit_reference_id: string;
  redaction_summary: string;
}}

export interface ProviderGovernanceSummary {{
  provider_id: string;
  provider_key: string;
  display_name: string;
  provider_type: string;
  status: GovernanceStatus;
  tenant_availability: string;
  model_count: number;
  health: ProviderHealthSummary;
  credential_reference: ProviderCredentialReference;
  local_no_auth_status: string;
  direct_call_guardrail: string;
  authorized_actions: AdminAction[];
  links: AdminAction[];
}}

export interface PromptVersionSummary {{
  version_id: string;
  label: string;
  status: GovernanceStatus;
  safe_change_summary: string;
  audit_reference_id: string;
}}

export interface PromptLibrarySummary {{
  prompt_lineage_id: string;
  name: string;
  status: GovernanceStatus;
  draft_version: string | null;
  published_version: string | null;
  tenant_grants: string[];
  render_test_status: GovernanceStatus;
  safe_change_summary: string;
  history: PromptVersionSummary[];
  authorized_actions: AdminAction[];
  links: AdminAction[];
}}

export interface SafePromptPreview {{
  preview_id: string;
  prompt_lineage_id: string;
  fixture_label: string;
  status: GovernanceStatus;
  safe_output: string;
  redaction_findings: string[];
  variable_summary: string;
  artifact_reference_id: string | null;
  audit_reference_id: string;
}}

export interface RuntimeProfileGovernanceSummary {{
  profile_id: string;
  profile_lineage_id: string;
  name: string;
  status: GovernanceStatus;
  draft_version: string | null;
  published_version: string;
  model_binding: string;
  provider_binding: string;
  prompt_binding: string;
  skill_requirements: string[];
  tenant_grants: string[];
  resolver_status: GovernanceStatus;
  authorized_actions: AdminAction[];
  links: AdminAction[];
}}

export interface ProfileResolutionPreview {{
  preview_id: string;
  profile_id: string;
  status: GovernanceStatus;
  selected_profile_version: string;
  model_route: string;
  provider_route: string;
  prompt_route: string;
  skill_route: string;
  fallback_reason: string | null;
  policy_reasons: string[];
  remediation: string;
  audit_reference_id: string;
}}

export interface RoutingPreviewResult {{
  preview_id: string;
  tenant_label: string;
  workflow_context_label: string;
  status: GovernanceStatus;
  model_decision: string;
  provider_decision: string;
  skill_decision: string;
  policy_reasons: string[];
  direct_call_guardrail: string;
  credential_reference_status: string;
  audit_reference_id: string;
  remediation: string;
}}

export interface PolicyHistoryRecord {{
  history_id: string;
  domain: string;
  actor_label: string;
  tenant_scope_label: string;
  timestamp_label: string;
  change_category: string;
  outcome: GovernanceStatus;
  safe_diff_summary: string;
  audit_reference_id: string;
  links: AdminAction[];
}}

export interface RunProvenanceSummary {{
  run_id: string;
  tenant_label: string;
  workflow_label: string;
  started_at_label: string;
  provider_evidence: string;
  model_evidence: string;
  prompt_evidence: string;
  profile_evidence: string;
  routing_evidence: string;
  credential_reference_evidence: string;
  usage_evidence: string;
  audit_reference_id: string;
  links: AdminAction[];
}}

export interface GovernanceDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  sections: GovernanceSection[];
  setup_summary: string[];
  providers: ProviderGovernanceSummary[];
  prompts: PromptLibrarySummary[];
  profiles: RuntimeProfileGovernanceSummary[];
  routing_preview: RoutingPreviewResult;
  profile_resolution: ProfileResolutionPreview;
  prompt_preview: SafePromptPreview;
  policy_history: PolicyHistoryRecord[];
  run_provenance: RunProvenanceSummary[];
  actions: AdminAction[];
  state: ReactAdminShellState | null;
  refresh: RefreshHint | null;
}}

export interface ProviderGovernanceList {{
  providers: ProviderGovernanceSummary[];
}}

export interface PromptGovernanceList {{
  prompts: PromptLibrarySummary[];
}}

export interface ProfileGovernanceList {{
  profiles: RuntimeProfileGovernanceSummary[];
}}

export interface PolicyHistoryList {{
  history: PolicyHistoryRecord[];
}}

export interface ProviderCredentialReferenceRequest {{
  credential_reference_id: string;
  revision: string;
}}

export interface PromptPreviewRequest {{
  fixture_id: string;
}}

export interface PromptSaveRequest {{
  revision: string;
  idempotency_key: string;
  safe_summary: string;
  publish: boolean;
}}

export interface ProfileSaveRequest {{
  revision: string;
  idempotency_key: string;
  model_binding: string;
  provider_binding: string;
}}

export interface RoutingPreviewRequest {{
  workflow_context: string;
  profile_id: string | null;
  skill_id: string | null;
}}

export interface GovernanceMutationResult extends MutationResult {{
  revision: string | null;
  probe: ProviderProbeDiagnostic | null;
  prompt_preview: SafePromptPreview | null;
  profile_resolution: ProfileResolutionPreview | null;
  routing_preview: RoutingPreviewResult | null;
  diagnostics: string[];
}}

export interface SkillLifecycleSection {{
  section_id: string;
  label: string;
  status: SkillLifecycleStatus;
  summary: string;
  href: string | null;
}}

export interface SkillLifecycleWizardStep {{
  step_id: string;
  label: string;
  status: SkillLifecycleStatus;
  summary: string;
}}

export interface SkillPackageCandidate {{
  candidate_id: string;
  package_slug: string;
  candidate_revision: string;
  manifest_digest: string;
  manifest_source: string;
  safe_manifest_summary: string;
  validation_status: SkillLifecycleStatus;
  validation_findings: ValidationFieldError[];
  safe_documentation_summary: string;
  smoke_evidence_status: SkillLifecycleStatus;
  publish_blockers: string[];
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface TenantSkillGrantSummary {{
  tenant_id: string;
  tenant_label: string;
  package_slug: string;
  version_label: string;
  grant_status: SkillLifecycleStatus;
  allowed_versions: string[];
  install_eligibility: SkillLifecycleStatus;
  restrictions: string[];
  authorized_actions: AdminAction[];
}}

export interface SkillPackageVersionSummary {{
  package_id: string;
  package_slug: string;
  version_id: string;
  version_label: string;
  lifecycle_status: SkillLifecycleStatus;
  manifest_digest: string;
  safe_manifest_summary: string;
  tenant_grant_summary: TenantSkillGrantSummary[];
  validation_evidence_ref: string;
  smoke_evidence_ref: string;
  quarantine_summary: string | null;
  withdrawal_summary: string | null;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface PackagePublicationWorkspace {{
  candidate: SkillPackageCandidate;
  available_steps: SkillLifecycleWizardStep[];
  package_versions: SkillPackageVersionSummary[];
  validation_summary: string;
  grant_preview: TenantSkillGrantSummary[];
  publish_readiness: SkillLifecycleStatus;
  authorized_actions: AdminAction[];
}}

export interface CredentialReferenceOption {{
  reference_id: string;
  label: string;
  source_type: string;
  readiness: SkillLifecycleStatus;
  fingerprint: string | null;
  policy_reason: string;
  last_checked_label: string;
  remediation: string;
}}

export interface ConnectorReadinessSummary {{
  connector_id: string;
  connector_label: string;
  tool_names: string[];
  readiness: SkillLifecycleStatus;
  credential_status: SkillLifecycleStatus;
  policy_status: SkillLifecycleStatus;
  smoke_test_status: SkillLifecycleStatus;
  staging_probe_status: SkillLifecycleStatus;
  last_safe_summary: string;
  evidence_reference_id: string;
  remediation: string;
  authorized_actions: AdminAction[];
}}

export interface TenantSkillInstallationSummary {{
  installation_id: string;
  tenant_id: string;
  package_slug: string;
  installed_version: string;
  installation_revision: string;
  installation_status: SkillLifecycleStatus;
  credential_readiness: SkillLifecycleStatus;
  smoke_test_readiness: SkillLifecycleStatus;
  connector_readiness: ConnectorReadinessSummary[];
  binding_readiness: SkillLifecycleStatus;
  upgrade_path: string | null;
  findings: string[];
  credential_options: CredentialReferenceOption[];
  authorized_actions: AdminAction[];
  audit_reference_id: string;
}}

export interface TenantSkillDiscovery {{
  grants: TenantSkillGrantSummary[];
  available_versions: SkillPackageVersionSummary[];
  empty_state_summary: string | null;
}}

export interface SkillExecutionDiagnosticSummary {{
  diagnostic_id: string;
  skill_package_version: string;
  tool_name: string;
  gateway_decision: string;
  side_effect_posture: string;
  outbound_policy_status: SkillLifecycleStatus;
  credential_policy_status: SkillLifecycleStatus;
  connector_readiness: SkillLifecycleStatus;
  safe_attempt_summary: string;
  redaction_summary: string;
  audit_reference_id: string;
  remediation: string;
}}

export interface BindingContextChoice {{
  choice_id: string;
  label: string;
  kind: string;
  selected: boolean;
}}

export interface BindingEligibilityPreview {{
  preview_id: string;
  tenant_label: string;
  context_choices: BindingContextChoice[];
  selected_context: string;
  eligible_tools: string[];
  blocked_tools: string[];
  policy_reasons: string[];
  missing_requirements: string[];
  remediation: string;
  audit_reference_id: string;
}}

export interface SkillLifecycleAuditRecord {{
  record_id: string;
  domain: string;
  package_slug: string;
  version_label: string;
  tenant_scope_label: string;
  actor_label: string;
  timestamp_label: string;
  action: string;
  outcome: SkillLifecycleStatus;
  safe_diff_summary: string;
  audit_reference_id: string;
  links: AdminAction[];
}}

export interface SkillLifecycleDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  sections: SkillLifecycleSection[];
  setup_summary: string[];
  platform_publication: PackagePublicationWorkspace | null;
  tenant_discovery: TenantSkillDiscovery | null;
  installations: TenantSkillInstallationSummary[];
  connector_diagnostics: ConnectorReadinessSummary[];
  skill_execution_diagnostics: SkillExecutionDiagnosticSummary[];
  binding_preview: BindingEligibilityPreview;
  audit_timeline: SkillLifecycleAuditRecord[];
  actions: AdminAction[];
  state: ReactAdminShellState | null;
  refresh: RefreshHint | null;
}}

export interface SkillPackageCandidateRequest {{
  manifest_text: string | null;
  uploaded_fixture_id: string | null;
  candidate_revision: string | null;
  idempotency_key: string;
}}

export interface SkillPackagePublishRequest {{
  candidate_revision: string;
  confirmed: boolean;
  idempotency_key: string;
}}

export interface TenantGrantMutationRequest {{
  tenant_id: string;
  version_id: string;
  grant_enabled: boolean;
  revision: string;
  idempotency_key: string;
}}

export interface TenantSkillInstallRequest {{
  package_id: string;
  version_id: string;
  revision: string;
  idempotency_key: string;
  upgrade: boolean;
}}

export interface CredentialConfigurationRequest {{
  selected_reference_id: string;
  revision: string;
  idempotency_key: string;
}}

export interface ReadinessRefreshRequest {{
  revision: string;
  idempotency_key: string;
}}

export interface BindingEligibilityPreviewRequest {{
  workflow_context: string;
  profile_id: string;
  package_id: string;
}}

export interface SkillLifecycleMutationResult extends MutationResult {{
  revision: string | null;
  publication: SkillPackageVersionSummary | null;
  installation: TenantSkillInstallationSummary | null;
  credential: CredentialReferenceOption | null;
  smoke_test: ConnectorReadinessSummary | null;
  diagnostic: SkillExecutionDiagnosticSummary | null;
  binding_preview: BindingEligibilityPreview | null;
  diagnostics: string[];
}}

export interface TenantSkillDiscoveryList {{
  discovery: TenantSkillDiscovery;
}}

export interface TenantSkillInstallationList {{
  installations: TenantSkillInstallationSummary[];
}}

export interface SkillExecutionDiagnosticList {{
  diagnostics: SkillExecutionDiagnosticSummary[];
}}

export interface SkillLifecycleAuditList {{
  audit_timeline: SkillLifecycleAuditRecord[];
}}

export interface TestBenchSection {{
  section_id: string;
  label: string;
  status: TestBenchStatus;
  summary: string;
  href: string | null;
}}

export interface TestBenchSummaryMetric {{
  metric_id: string;
  label: string;
  value: string;
  status: TestBenchStatus;
  summary: string;
}}

export interface TargetOption {{
  target_type: string;
  target_id: string;
  label: string;
  current_revision: string;
  revision_status: TestBenchStatus;
  safe_summary: string;
  authorized: boolean;
}}

export interface AssertionDefinition {{
  assertion_id: string;
  label: string;
  kind: string;
  path_summary: string;
  comparator: string;
  expected_summary: string;
  severity: string;
  threshold_weight: number;
  validation_status: TestBenchStatus;
  field_errors: ValidationFieldError[];
}}

export interface TestCaseSummary {{
  case_id: string;
  case_name: string;
  case_status: TestBenchStatus;
  case_revision: string;
  fixture_summary: string;
  expected_contract_summary: string;
  assertions: AssertionDefinition[];
  evaluator_summary: string;
  threshold_contribution: number;
  order: number;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface TargetRevisionBinding {{
  target_type: string;
  target_id: string;
  target_label: string;
  current_revision: string;
  selected_revision: string;
  revision_status: TestBenchStatus;
  source_links: AdminAction[];
  stale_reason: string | null;
  remediation: string;
}}

export interface SafeExecutionModeOption {{
  mode_id: string;
  label: string;
  side_effect_posture: string;
  model_behavior: string;
  tool_behavior: string;
  credential_behavior: string;
  allowed_status: TestBenchStatus;
  policy_reason: string;
  requires_approval: boolean;
  approval_reference_id: string | null;
  audit_reference_id: string | null;
}}

export interface TestBenchFormMetadata {{
  target_options: TargetOption[];
  safe_modes: SafeExecutionModeOption[];
  assertion_templates: AssertionDefinition[];
  run_reason_options: string[];
  default_safe_mode: string;
  default_pass_threshold: number;
}}

export interface TestRunProgressSnapshot {{
  status: TestBenchStatus;
  summary: string;
  completed_cases: number;
  total_cases: number;
  next_poll_seconds: number;
  sse_href: string | null;
  audit_reference_id: string;
}}

export interface TestRunSummary {{
  run_id: string;
  suite_id: string;
  suite_name: string;
  target_revision: string;
  safe_mode: string;
  status: TestBenchStatus;
  pass_rate: number;
  failure_category: TestBenchStatus | null;
  started_label: string;
  finished_label: string | null;
  actor_label: string;
  case_total: number;
  case_passed: number;
  case_failed: number;
  usage_summary: string;
  latency_summary: string;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface DiagnosticFinding {{
  finding_id: string;
  category: TestBenchStatus;
  label: string;
  expected_summary: string;
  actual_summary: string;
  comparator: string;
  path_summary: string;
  severity: string;
  remediation: string;
}}

export interface TraceStepSummary {{
  step_id: string;
  case_id: string;
  step_label: string;
  runtime_role: string;
  status: TestBenchStatus;
  latency_ms: number;
  token_usage: string;
  model_label: string;
  provider_label: string;
  prompt_version_label: string;
  profile_version_label: string;
  skill_version_labels: string[];
  safe_transcript_excerpt: string;
  blocked_side_effects: string[];
  gateway_decision: string;
  redaction_class: string;
  artifact_reference_ids: string[];
}}

export interface ArtifactReferenceSummary {{
  artifact_reference_id: string;
  label: string;
  content_class: string;
  checksum: string;
  size_label: string;
  retention_state: TestBenchStatus;
  redaction_class: string;
  access_status: TestBenchStatus;
  safe_summary: string;
  authorized_href: string | null;
  audit_reference_id: string;
}}

export interface PublishGateEvidence {{
  gate_id: string;
  target_type: string;
  target_label: string;
  target_revision: string;
  required_suite_id: string;
  required_suite_label: string;
  evidence_status: TestBenchStatus;
  latest_run_id: string | null;
  latest_run_revision: string | null;
  latest_run_status: TestBenchStatus | null;
  reason: string;
  remediation: string;
  audit_reference_id: string;
  artifact_references: ArtifactReferenceSummary[];
  authorized_actions: AdminAction[];
}}

export interface TestSuiteSummary {{
  suite_id: string;
  suite_slug: string;
  suite_name: string;
  tenant_id: string;
  tenant_label: string;
  target_type: string;
  target_label: string;
  target_revision: string;
  target_status: TestBenchStatus;
  default_safe_mode: string;
  pass_threshold: number;
  required_for_publish: boolean;
  case_count: number;
  latest_run_status: TestBenchStatus;
  latest_run_id: string | null;
  publish_gate_status: TestBenchStatus;
  suite_revision: string;
  archive_status: TestBenchStatus;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface TestSuiteDetail {{
  summary: TestSuiteSummary;
  cases: TestCaseSummary[];
  target_binding: TargetRevisionBinding;
  run_launcher: TestBenchFormMetadata;
  recent_runs: TestRunSummary[];
  publish_gate: PublishGateEvidence;
  audit_reference_id: string;
}}

export interface TestRunDetail {{
  summary: TestRunSummary;
  progress: TestRunProgressSnapshot;
  case_results: TestCaseSummary[];
  trace_steps: TraceStepSummary[];
  assertion_diagnostics: DiagnosticFinding[];
  artifacts: ArtifactReferenceSummary[];
  publish_gate: PublishGateEvidence;
  redaction_summary: string;
  blocked_side_effects: string[];
  audit_reference_id: string;
}}

export interface TestBenchAuditRecord {{
  record_id: string;
  domain: string;
  tenant_scope_label: string;
  actor_label: string;
  target_label: string;
  timestamp_label: string;
  action: string;
  outcome: TestBenchStatus;
  safe_diff_summary: string;
  redaction_class: string;
  audit_reference_id: string;
  links: AdminAction[];
}}

export interface TestBenchDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  sections: TestBenchSection[];
  summary_cards: TestBenchSummaryMetric[];
  gate_alerts: PublishGateEvidence[];
  suites: TestSuiteSummary[];
  selected_suite: TestSuiteDetail | null;
  recent_runs: TestRunSummary[];
  audit_timeline: TestBenchAuditRecord[];
  refresh: RefreshHint | null;
  actions: AdminAction[];
}}

export interface TestSuiteList {{
  scope: ReactAdminScope;
  suites: TestSuiteSummary[];
  form_metadata: TestBenchFormMetadata;
}}

export interface TestRunList {{
  scope: ReactAdminScope;
  runs: TestRunSummary[];
}}

export interface PublishGateEvidenceList {{
  scope: ReactAdminScope;
  gates: PublishGateEvidence[];
}}

export interface TestBenchAuditList {{
  scope: ReactAdminScope;
  audit_timeline: TestBenchAuditRecord[];
}}

export interface TestBenchMutationResult extends MutationResult {{
  revision: string | null;
  suite: TestSuiteDetail | null;
  case: TestCaseSummary | null;
  run: TestRunDetail | null;
  gate: PublishGateEvidence | null;
  artifact: ArtifactReferenceSummary | null;
  diagnostics: string[];
}}

export interface TestSuiteSaveRequest {{
  name: string;
  description: string | null;
  target_type: string;
  target_id: string;
  target_revision: string;
  default_safe_mode: string;
  pass_threshold: number;
  required_for_publish: boolean;
  revision: string | null;
  idempotency_key: string;
}}

export interface TestCaseSaveRequest {{
  name: string;
  fixture_summary: string;
  expected_contract_summary: string;
  assertions: AssertionDefinition[];
  evaluator_reference_id: string | null;
  revision: string | null;
  idempotency_key: string;
}}

export interface TestRunLaunchRequest {{
  target_revision: string;
  safe_mode: string;
  run_reason: string;
  idempotency_key: string;
}}

export interface GateEvidenceRefreshRequest {{
  target_revision: string;
  idempotency_key: string;
}}

export interface MembershipSection {{
  section_id: string;
  label: string;
  status: MembershipLifecycleStatus;
  summary: string;
}}

export interface MembershipSummaryCard {{
  card_id: string;
  label: string;
  value: string;
  status: MembershipLifecycleStatus;
  summary: string;
}}

export interface MembershipFilterOption {{
  option_id: string;
  label: string;
  value: string;
  selected: boolean;
}}

export interface MembershipDirectoryFilters {{
  query: string | null;
  tenant_options: MembershipFilterOption[];
  role_options: MembershipFilterOption[];
  status_options: MembershipFilterOption[];
  invitation_state_options: MembershipFilterOption[];
  access_decision_options: MembershipFilterOption[];
}}

export interface RoleChoice {{
  role_code: string;
  role_label: string;
  scope_type: MembershipScopeType;
  tenant_id: string | null;
  tenant_label: string | null;
  eligible: boolean;
  disabled_reason: string | null;
}}

export interface RawIdentifierDetail {{
  authorized: boolean;
  principal_identity_id: string | null;
  external_subject: string | null;
  invitation_id: string | null;
  copy_label: string;
  reason: string;
}}

export interface TenantMembershipSummary {{
  tenant_membership_id: string;
  tenant_id: string;
  tenant_label: string;
  membership_status: MembershipLifecycleStatus;
  revision: string;
  membership_source: string;
  status_reason: string;
  authorized_actions: AdminAction[];
}}

export interface RoleGrantSummary {{
  role_grant_id: string;
  principal_identity_id: string;
  principal_label: string;
  scope_type: MembershipScopeType;
  tenant_id: string | null;
  tenant_label: string | null;
  role_code: string;
  role_label: string;
  grant_status: MembershipLifecycleStatus;
  effective_label: string;
  revoked_label: string | null;
  next_request_effect: string;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface UserDirectoryEntry {{
  principal_identity_id: string;
  display_name: string;
  masked_email: string;
  safe_subject_suffix: string;
  principal_status: MembershipLifecycleStatus;
  tenant_memberships: TenantMembershipSummary[];
  role_summaries: RoleGrantSummary[];
  last_access_summary: string;
  raw_identifier_detail: RawIdentifierDetail | null;
  authorized_actions: AdminAction[];
}}

export interface InvitationSummary {{
  invitation_id: string;
  tenant_id: string | null;
  tenant_label: string | null;
  masked_email: string;
  email_hash_label: string;
  requested_roles: string[];
  status: MembershipLifecycleStatus;
  expires_label: string;
  replayed: boolean;
  next_request_effect: string;
  audit_reference_id: string;
  authorized_actions: AdminAction[];
}}

export interface PrincipalLinkSummary {{
  principal_identity_id: string;
  display_name: string;
  masked_email: string | null;
  safe_subject_suffix: string;
  link_status: MembershipLifecycleStatus;
  conflict_summary: string | null;
  audit_reference_id: string;
}}

export interface MembershipStatusSummary {{
  tenant_membership_id: string;
  principal_identity_id: string;
  tenant_id: string;
  tenant_label: string;
  membership_status: MembershipLifecycleStatus;
  revision: string;
  membership_source: string;
  status_reason: string;
  authorized_actions: AdminAction[];
}}

export interface AccessHistoryRecord {{
  access_history_id: string;
  principal_label: string;
  tenant_label: string;
  surface_key: string;
  requested_action: string;
  decision: string;
  reason_category: string;
  role_source_summary: string;
  timestamp_label: string;
  trace_id: string;
  audit_reference_id: string;
}}

export interface MembershipAuditRecord {{
  audit_reference_id: string;
  domain: string;
  actor_label: string;
  target_label: string;
  tenant_scope_label: string;
  action: string;
  outcome: string;
  safe_diff_summary: string;
  timestamp_label: string;
  redaction_class: string;
}}

export interface InvitationFormMetadata {{
  default_tenant_id: string | null;
  tenant_options: MembershipFilterOption[];
  role_choices: RoleChoice[];
  default_expiry_label: string;
  idempotency_hint: string;
}}

export interface RoleGrantFormMetadata {{
  role_choices: RoleChoice[];
  confirmation_copy: string;
  stale_recovery_copy: string;
}}

export interface MembershipDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  summary_cards: MembershipSummaryCard[];
  sections: MembershipSection[];
  directory: UserDirectoryEntry[];
  filters: MembershipDirectoryFilters;
  allowed_scope_options: ReactAdminScopeOption[];
  invite_form: InvitationFormMetadata;
  role_grant_form: RoleGrantFormMetadata;
  invitations: InvitationSummary[];
  role_grants: RoleGrantSummary[];
  status_actions: MembershipStatusSummary[];
  access_history: AccessHistoryRecord[];
  audit_timeline: MembershipAuditRecord[];
  common_states: ReactAdminShellState[];
}}

export interface MembershipAccessHistoryList {{
  scope: ReactAdminScope;
  records: AccessHistoryRecord[];
  partial: boolean;
  safe_summary: string;
}}

export interface MembershipAuditList {{
  scope: ReactAdminScope;
  records: MembershipAuditRecord[];
  unavailable: boolean;
  safe_summary: string;
}}

export interface MembershipMutationResult {{
  status: AdminMutationStatus;
  summary: string;
  toast: ToastHint | null;
  directory_entry: UserDirectoryEntry | null;
  invitation: InvitationSummary | null;
  principal_link: PrincipalLinkSummary | null;
  role_grant: RoleGrantSummary | null;
  membership_status: MembershipStatusSummary | null;
  access_history: AccessHistoryRecord[];
  audit_reference_id: string;
  field_errors: ValidationFieldError[];
  stale_conflict: RevisionConflict | null;
  idempotency_replay: boolean;
  confirmation: ConfirmationRequirement | null;
  next_request_effect: string;
}}

export interface MembershipInvitationSaveRequest {{
  tenant_id: string | null;
  email: string;
  requested_roles: string[];
  idempotency_key: string;
}}

export interface PrincipalLinkRequest {{
  principal_identity_id: string | null;
  display_name: string;
  email: string | null;
  external_subject: string;
  overwrite_confirmed: boolean;
  idempotency_key: string;
}}

export interface RoleGrantSaveRequest {{
  principal_identity_id: string;
  scope_type: MembershipScopeType;
  tenant_id: string | null;
  role_code: string;
  confirmed: boolean;
  idempotency_key: string;
}}

export interface MembershipConfirmationRequest {{
  confirmed: boolean;
  revision: string | null;
  reason: string | null;
  idempotency_key: string;
}}

export interface UsageReactRange {{
  label: string;
  start: string;
  end: string;
}}

export interface UsageReactFilterOption {{
  value: string;
  label: string;
  selected: boolean;
  disabled: boolean;
  disabled_reason: string | null;
}}

export interface UsageReactFilterMetadata {{
  selected_range: UsageReactRange;
  range_options: UsageReactFilterOption[];
  selected_group_by: UsageReactGroupBy;
  group_by_options: UsageReactFilterOption[];
  tenant_options: UsageReactFilterOption[];
  provider_options: UsageReactFilterOption[];
  model_options: UsageReactFilterOption[];
  workflow_options: UsageReactFilterOption[];
  agent_options: UsageReactFilterOption[];
  prompt_options: UsageReactFilterOption[];
  confidence_options: UsageReactFilterOption[];
  availability_options: UsageReactFilterOption[];
  disabled_reasons: Record<string, string>;
}}

export interface UsageReactSummaryCard {{
  card_id: string;
  label: string;
  value: string;
  unit: string;
  status: UsageReactConfidenceStatus;
  tone: UsageReactTone;
  comparison: string | null;
  detail: string;
  audit_reference: string | null;
}}

export interface UsageReactTrendPoint {{
  bucket_start: string;
  bucket_end: string;
  label: string;
  confirmed_tokens: number;
  estimated_tokens: number;
  unavailable_events: number;
  estimated_cost_display: string;
  estimated_cost_micros: number;
  currency: string;
  average_latency_ms: number;
  event_count: number;
  confidence_status: UsageReactConfidenceStatus;
}}

export interface UsageReactRollupRow {{
  row_id: string;
  group_by: UsageReactGroupBy;
  safe_label: string;
  safe_summary: string;
  event_count: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_display: string;
  estimated_cost_micros: number;
  currency: string;
  average_latency_ms: number;
  unavailable_event_count: number;
  confidence_status: UsageReactConfidenceStatus;
  attempt_summary: string | null;
  tool_summary: string | null;
  drilldown_href: string;
}}

export interface UsageReactRollupSection {{
  group_by: UsageReactGroupBy;
  rows: UsageReactRollupRow[];
  limit: number;
  total_rows: number;
}}

export interface UsageReactEventRow {{
  event_id: string;
  recorded_at: string;
  tenant_label: string;
  provider_label: string;
  model_label: string;
  workflow_label: string | null;
  agent_label: string | null;
  prompt_label: string | null;
  graph_node_label: string | null;
  gateway_operation_label: string | null;
  physical_attempt_label: string | null;
  tool_label: string | null;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost_display: string;
  latency_ms: number;
  usage_status: UsageReactConfidenceStatus;
  cost_status: UsageReactConfidenceStatus;
  safe_attribution_summary: string;
  audit_reference: string | null;
  trace_reference: string | null;
}}

export interface UsageReactEventDrilldown {{
  rows: UsageReactEventRow[];
  limit: number;
  total_rows: number;
  truncated: boolean;
}}

export interface UsageReactProblem {{
  reason: UsageReactProblemReason;
  title: string;
  detail: string;
  next_action: string;
  audit_reference: string | null;
}}

export interface UsageReactExportCreateRequest {{
  filters: Record<string, string>;
  requested_group_by: UsageReactGroupBy | null;
  idempotency_key: string | null;
}}

export interface UsageReactExportSummary {{
  usage_export_request_id: string;
  status: UsageReactExportStatus;
  scope_label: string;
  requested_by_label: string;
  filter_snapshot: Record<string, string>;
  row_count: number;
  artifact_reference: string | null;
  artifact_size_label: string | null;
  checksum_prefix: string | null;
  created_at: string;
  completed_at: string | null;
  expires_at: string | null;
  audit_reference: string;
  denial_reason: string | null;
  failure_reason: string | null;
  next_step: string;
}}

export interface UsageReactDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  allowed_scope_options: ReactAdminScopeOption[];
  filters: UsageReactFilterMetadata;
  summary_cards: UsageReactSummaryCard[];
  trend: UsageReactTrendPoint[];
  rollup: UsageReactRollupSection;
  drilldown: UsageReactEventDrilldown;
  exports: UsageReactExportSummary[];
  states: UsageReactProblem[];
  common_states: ReactAdminShellState[];
  updated_at: string;
}}

export interface ChannelAction {{
  action_id: string;
  label: string;
  href: string | null;
  method: ChannelActionMethod;
  enabled: boolean;
  disabled_reason: string | null;
}}

export interface ChannelProblem {{
  reason: string;
  title: string;
  detail: string;
  next_action: string;
  audit_reference: string | null;
}}

export interface ChannelTelegramReadiness {{
  readiness_id: string;
  status: ChannelReadinessStatus;
  channel_label: string;
  tenant_label: string;
  telegram_enabled: boolean;
  webhook_status: WebhookDiagnosticStatus;
  secret_reference_status: ChannelReadinessStatus;
  linked_identity_count: number;
  alias_count: number;
  delivery_health_label: string;
  preference_resolver_label: string;
  audit_reference: string;
  next_step: string;
}}

export interface TelegramTenantConfiguration {{
  tenant_id: string | null;
  tenant_label: string;
  enabled: boolean;
  bot_token_reference_label: string;
  webhook_signing_reference_label: string;
  webhook_url_status: ChannelReadinessStatus;
  revision: string;
  last_validated_at: string | null;
  audit_reference: string;
  actions: ChannelAction[];
}}

export interface TelegramAliasRecord {{
  alias_id: string;
  tenant_label: string;
  alias_text: string;
  target_summary: string;
  protected_readiness: AliasProtectedReadiness;
  status: AliasLifecycleStatus;
  revision: string;
  last_used_at: string | null;
  audit_reference: string;
  actions: ChannelAction[];
}}

export interface LinkTokenResult {{
  link_token_request_id: string;
  token_value: string | null;
  masked_status: string;
  expires_at: string;
  consumed_at: string | null;
  next_step: string;
  audit_reference: string;
  display_mode: "immediate" | "masked";
}}

export interface LinkedTelegramIdentitySummary {{
  identity_id: string;
  principal_label: string;
  telegram_label: string;
  chat_label: string;
  linked_at: string;
  status: LinkedIdentityStatus;
  audit_reference: string;
}}

export interface WebhookDiagnosticSummary {{
  diagnostic_id: string;
  status: WebhookDiagnosticStatus;
  last_checked_at: string;
  safe_update_summary: string;
  receipt_count: number;
  next_step: string;
  audit_reference: string;
}}

export interface DeliveryAttemptSummary {{
  attempt_id: string;
  tenant_label: string;
  alias_label: string;
  status: DeliveryAttemptStatus;
  retry_category: DeliveryRetryCategory;
  bot_api_boundary_status: BotBoundaryStatus;
  run_status_href: string | null;
  safe_error_summary: string;
  attempted_at: string;
  trace_reference: string;
  audit_reference: string;
}}

export interface DeliveryDiagnosticList {{
  attempts: DeliveryAttemptSummary[];
  limit: number;
  total_rows: number;
  webhook_receipts: WebhookDiagnosticSummary[];
}}

export interface RunStatusSummary {{
  run_id: string;
  status: RunStatusCategory;
  workflow_label: string;
  requested_by_label: string;
  started_at: string | null;
  completed_at: string | null;
  next_step: string;
  href: string;
  artifact_references: string[];
  audit_reference: string;
}}

export interface BriefingPreferenceProfile {{
  profile_id: string;
  tenant_label: string;
  principal_label: string;
  timezone: string;
  location_summary: string;
  news_topics_summary: string;
  vip_sender_summary: string;
  workday_hours: string;
  commute_mode: CommuteMode;
  default_account_summary: string;
  output_style: BriefingOutputStyle;
  scheduled_time_summary: string | null;
  revision: string;
  runtime_ready: boolean;
  audit_reference: string;
}}

export interface BriefingPreferenceList {{
  current_user_profile: BriefingPreferenceProfile | null;
  admin_summaries: BriefingPreferenceProfile[];
  import_export_evidence: string[];
}}

export interface BriefingPreferenceMutationResult {{
  status: ChannelMutationStatus;
  profile_summary: string;
  revision: string | null;
  field_errors: Record<string, string>;
  artifact_reference: string | null;
  row_count: number | null;
  audit_reference: string;
  next_step: string;
}}

export interface ChannelMutationResult {{
  status: ChannelMutationStatus;
  summary: string;
  revision: string | null;
  idempotency_key: string | null;
  replayed: boolean;
  field_errors: Record<string, string>;
  audit_reference: string;
  next_step: string;
}}

export interface ChannelTelegramBriefingDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  allowed_scope_options: ReactAdminScopeOption[];
  readiness: ChannelTelegramReadiness[];
  tenant_configs: TelegramTenantConfiguration[];
  aliases: TelegramAliasRecord[];
  link_token_result: LinkTokenResult | null;
  linked_identities: LinkedTelegramIdentitySummary[];
  webhook_diagnostics: WebhookDiagnosticSummary[];
  delivery_attempts: DeliveryAttemptSummary[];
  run_status_links: RunStatusSummary[];
  preference_profiles: BriefingPreferenceList;
  states: ChannelProblem[];
  common_states: ReactAdminShellState[];
  updated_at: string;
}}

export interface TelegramConfigSaveRequest {{
  enabled: boolean;
  bot_token_reference_label: string;
  webhook_signing_reference_label: string;
  revision: string;
  idempotency_key: string | null;
}}

export interface WebhookValidationRequest {{
  tenant_id: string | null;
  revision: string;
  idempotency_key: string | null;
}}

export interface TelegramAliasSaveRequest {{
  alias_id: string | null;
  alias_text: string;
  target_summary: string;
  revision: string | null;
  idempotency_key: string | null;
}}

export interface TelegramAliasActionRequest {{
  revision: string;
  idempotency_key: string | null;
}}

export interface LinkTokenCreateRequest {{
  principal_label: string;
  expires_in_minutes: number;
  idempotency_key: string | null;
}}

export interface BriefingPreferenceSaveRequest {{
  timezone: string;
  location_summary: string;
  news_topics_summary: string;
  vip_sender_summary: string;
  workday_hours: string;
  commute_mode: CommuteMode;
  default_account_summary: string;
  output_style: BriefingOutputStyle;
  scheduled_time_summary: string | null;
  revision: string | null;
  idempotency_key: string | null;
}}

export interface BriefingPreferenceImportRequest {{
  artifact_reference: string;
  field_count: number;
  idempotency_key: string | null;
}}

export interface BriefingPreferenceExportRequest {{
  format: "json" | "csv";
  idempotency_key: string | null;
}}

export interface MigrationHardeningSummary {{
  total_destinations: number;
  react_primary_count: number;
  redirect_count: number;
  retained_fallback_count: number;
  retirement_candidate_count: number;
  blocked_count: number;
  overall_status: MigrationOverallStatus;
  next_step: string;
}}

export interface MigrationRouteEntry {{
  entry_id: string;
  admin_area: string;
  legacy_route: string | null;
  react_route: string | null;
  decision: MigrationRouteDecision;
  scope_requirement: MigrationScopeRequirement;
  auth_modes: string[];
  parity_evidence: string[];
  redirect_preserves: string[];
  fallback_notice: string | null;
  retirement_allowed: boolean;
  rollback_reference: string;
  audit_reference: string;
}}

export interface MigrationRouteGroup {{
  group_id: string;
  label: string;
  spec_refs: string[];
  group_status: MigrationOverallStatus;
  entries: MigrationRouteEntry[];
}}

export interface MigrationRollbackPlan {{
  plan_id: string;
  status: MigrationOverallStatus;
  feature_flag_label: string;
  asset_version_label: string;
  steps: string[];
  verification_steps: string[];
  owner_label: string;
  last_reviewed_at: string;
  audit_reference: string;
}}

export interface MigrationPerformanceMeasurement {{
  measurement_id: string;
  label: string;
  value: number;
  unit: string;
  limit: number;
  status: MigrationEvidenceStatus;
  evidence_reference: string;
}}

export interface MigrationPerformanceBudget {{
  budget_id: string;
  route_bootstrap_ms_limit: number;
  primary_interactive_ms_limit: number;
  compressed_asset_kb_limit: number;
  status: MigrationEvidenceStatus;
  mitigation: string | null;
  measurements: MigrationPerformanceMeasurement[];
}}

export interface MigrationAccessibilityAudit {{
  audit_id: string;
  status: MigrationEvidenceStatus;
  viewport_coverage: string[];
  keyboard_status: MigrationEvidenceStatus;
  focus_status: MigrationEvidenceStatus;
  landmark_status: MigrationEvidenceStatus;
  label_status: MigrationEvidenceStatus;
  contrast_state_status: MigrationEvidenceStatus;
  text_overlap_status: MigrationEvidenceStatus;
  evidence_references: string[];
}}

export interface MigrationSweepSummary {{
  sweep_id: string;
  status: MigrationEvidenceStatus;
  checked_artifacts: number;
  unsafe_match_count: number;
  safe_summary: string;
  evidence_reference: string;
}}

export interface MigrationProblem {{
  reason: string;
  title: string;
  detail: string;
  next_action: string;
  severity: MigrationProblemSeverity;
  audit_reference: string | null;
}}

export interface AdminMigrationHardeningDashboard {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  updated_at: string;
  summary: MigrationHardeningSummary;
  route_groups: MigrationRouteGroup[];
  rollback_plan: MigrationRollbackPlan;
  performance_budget: MigrationPerformanceBudget;
  accessibility_audit: MigrationAccessibilityAudit;
  redaction_sweep: MigrationSweepSummary;
  tenant_isolation_sweep: MigrationSweepSummary;
  states: MigrationProblem[];
}}

export interface WorkbenchExportRequest {{
  scope_type: string;
  range: string;
  include_run_debug: boolean;
}}

export interface SampleRecord {{
  record_id: string;
  name: string;
  status: string;
  owner_scope: string;
  updated_label: string;
  revision: string;
}}

export interface FormFieldDescriptor {{
  field: string;
  label: string;
  input_type: string;
  required: boolean;
  help_text: string | null;
}}

export interface SampleFormDescriptor {{
  fields: FormFieldDescriptor[];
  default_values: Record<string, string | boolean>;
  revision: string;
  idempotency_key: string;
}}

export interface PatternsSampleData {{
  records: SampleRecord[];
  form: SampleFormDescriptor;
  export_snapshot: ExportSnapshot;
  details: EvidenceSummary[];
}}

export interface AdminPageEnvelope {{
  page_id: string;
  title: string;
  description: string;
  scope: ReactAdminScope;
  state: ReactAdminShellState | null;
  data: PatternsSampleData;
  filters: FilterProfile;
  pagination: PaginationState;
  sorting: SortingState;
  actions: AdminAction[];
  evidence: EvidenceSummary[];
  refresh: RefreshHint | null;
}}

export interface SampleActionRequest {{
  sample_name: string;
  revision: string;
  idempotency_key: string;
  confirmed: boolean;
  outcome: string;
}}

export interface ReactAdminFeatureFlags {{
  react_admin_enabled: boolean;
  react_domain_routes: Record<string, boolean>;
  source: string;
}}

export interface ReactAdminVersion {{
  app_name: string;
  app_version: string;
  api_version: string;
  commit_sha: string;
  build_time: string;
}}

export interface ReactAdminAssetManifestSummary {{
  available: boolean;
  base_path: string;
  entrypoints: string[];
  stylesheets: string[];
  version: string | null;
  unavailable_reason: string | null;
}}

export interface ReactAdminActionTokens {{
  csrf_token: string | null;
  issued_at: string | null;
}}

export interface ReactAdminBootstrap {{
  principal: ReactAdminPrincipal;
  active_scope: ReactAdminScope;
  available_scopes: ReactAdminScopeOption[];
  navigation: ReactAdminNavigationGroup[];
  feature_flags: ReactAdminFeatureFlags;
  version: ReactAdminVersion;
  asset_manifest: ReactAdminAssetManifestSummary;
  action_tokens: ReactAdminActionTokens;
  shell: ReactAdminShellChrome;
}}

export interface ReactAdminConfig {{
  mount_path: string;
  asset_base_path: string;
  bootstrap_url: string;
  config_url: string;
  manifest_url: string;
}}

export interface SafeProblem {{
  detail: string;
  reason: string;
  trace_id: string | null;
}}

function isObject(value: unknown): value is Record<string, unknown> {{
  return typeof value === "object" && value !== null && !Array.isArray(value);
}}

function hasString(value: Record<string, unknown>, key: string): boolean {{
  return typeof value[key] === "string";
}}

export function assertReactAdminBootstrap(
  value: unknown,
): ReactAdminBootstrap {{
  if (!isObject(value)) {{
    throw new Error("React admin bootstrap must be an object");
  }}
  const principal = value.principal;
  const activeScope = value.active_scope;
  if (!isObject(principal) || !hasString(principal, "principal_id")) {{
    throw new Error("React admin bootstrap is missing a safe principal");
  }}
  if (!isObject(activeScope) || !hasString(activeScope, "scope_type")) {{
    throw new Error("React admin bootstrap is missing an active scope");
  }}
  if (!Array.isArray(value.navigation)) {{
    throw new Error("React admin bootstrap navigation must be an array");
  }}
  if (!isObject(value.shell) || !Array.isArray(value.shell.breadcrumbs)) {{
    throw new Error("React admin bootstrap is missing shell metadata");
  }}
  return value as unknown as ReactAdminBootstrap;
}}

export function assertReactAdminCommandSearch(
  value: unknown,
): ReactAdminCommandSearch {{
  if (!isObject(value)) {{
    throw new Error("React admin command search must be an object");
  }}
  if (!Array.isArray(value.results)) {{
    throw new Error("React admin command search results must be an array");
  }}
  return value as unknown as ReactAdminCommandSearch;
}}

export function assertAdminPageEnvelope(value: unknown): AdminPageEnvelope {{
  if (!isObject(value)) {{
    throw new Error("Admin page envelope must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Admin page envelope is missing safe page metadata");
  }}
  if (!isObject(value.scope) || !hasString(value.scope, "scope_type")) {{
    throw new Error("Admin page envelope is missing active scope");
  }}
  if (!isObject(value.data) || !Array.isArray(value.data.records)) {{
    throw new Error("Admin page envelope is missing sample records");
  }}
  if (!isObject(value.filters) || !Array.isArray(value.filters.criteria)) {{
    throw new Error("Admin page envelope is missing filter metadata");
  }}
  return value as unknown as AdminPageEnvelope;
}}

export function assertMutationResult(value: unknown): MutationResult {{
  if (!isObject(value)) {{
    throw new Error("Mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Mutation result is missing safe status metadata");
  }}
  return value as unknown as MutationResult;
}}

export function assertExportSnapshot(value: unknown): ExportSnapshot {{
  if (!isObject(value)) {{
    throw new Error("Export snapshot must be an object");
  }}
  if (!hasString(value, "export_id") || !hasString(value, "status")) {{
    throw new Error("Export snapshot is missing safe status metadata");
  }}
  return value as unknown as ExportSnapshot;
}}

export function assertOperationsWorkbenchEnvelope(
  value: unknown,
): OperationsWorkbenchEnvelope {{
  if (!isObject(value)) {{
    throw new Error("Operations workbench envelope must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Operations workbench envelope is missing page metadata");
  }}
  if (!Array.isArray(value.summary_cards) || !Array.isArray(value.health_panels)) {{
    throw new Error("Operations workbench envelope is missing summary panels");
  }}
  if (!isObject(value.exports) || !hasString(value.exports, "export_id")) {{
    throw new Error("Operations workbench envelope is missing export metadata");
  }}
  return value as unknown as OperationsWorkbenchEnvelope;
}}

export function assertRunDebugEnvelope(value: unknown): RunDebugEnvelope {{
  if (!isObject(value)) {{
    throw new Error("Run debug envelope must be an object");
  }}
  if (!hasString(value, "workflow_run_id") || !Array.isArray(value.timeline)) {{
    throw new Error("Run debug envelope is missing timeline metadata");
  }}
  return value as unknown as RunDebugEnvelope;
}}

export function assertWorkbenchExportSnapshot(
  value: unknown,
): WorkbenchExportSnapshot {{
  if (!isObject(value)) {{
    throw new Error("Workbench export snapshot must be an object");
  }}
  if (!hasString(value, "export_id") || !hasString(value, "redaction_summary")) {{
    throw new Error("Workbench export snapshot is missing safe metadata");
  }}
  return value as unknown as WorkbenchExportSnapshot;
}}

export function assertWorkflowBuilderEnvelope(
  value: unknown,
): WorkflowBuilderEnvelope {{
  if (!isObject(value)) {{
    throw new Error("Workflow builder envelope must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Workflow builder envelope is missing page metadata");
  }}
  if (!isObject(value.draft) || !hasString(value.draft, "workflow_draft_id")) {{
    throw new Error("Workflow builder envelope is missing draft metadata");
  }}
  if (!Array.isArray(value.sections) || !isObject(value.reference_catalog)) {{
    throw new Error("Workflow builder envelope is missing guided sections");
  }}
  if (!isObject(value.validation) || !isObject(value.publish_readiness)) {{
    throw new Error("Workflow builder envelope is missing gate metadata");
  }}
  return value as unknown as WorkflowBuilderEnvelope;
}}

export function assertWorkflowReferenceCatalog(
  value: unknown,
): WorkflowReferenceCatalog {{
  if (!isObject(value)) {{
    throw new Error("Workflow reference catalog must be an object");
  }}
  if (!Array.isArray(value.prompt_options) || !Array.isArray(value.skill_options)) {{
    throw new Error("Workflow reference catalog is missing option groups");
  }}
  return value as unknown as WorkflowReferenceCatalog;
}}

export function assertBuilderMutationResult(
  value: unknown,
): BuilderMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Workflow mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Workflow mutation result is missing safe status metadata");
  }}
  return value as unknown as BuilderMutationResult;
}}

export function assertGovernanceDashboard(value: unknown): GovernanceDashboard {{
  if (!isObject(value)) {{
    throw new Error("Governance dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Governance dashboard is missing page metadata");
  }}
  if (!Array.isArray(value.sections) || !Array.isArray(value.providers)) {{
    throw new Error("Governance dashboard is missing setup sections");
  }}
  if (!Array.isArray(value.prompts) || !Array.isArray(value.profiles)) {{
    throw new Error("Governance dashboard is missing prompt/profile summaries");
  }}
  if (!isObject(value.routing_preview) || !Array.isArray(value.policy_history)) {{
    throw new Error("Governance dashboard is missing routing/history evidence");
  }}
  return value as unknown as GovernanceDashboard;
}}

export function assertProviderGovernanceList(
  value: unknown,
): ProviderGovernanceList {{
  if (!isObject(value) || !Array.isArray(value.providers)) {{
    throw new Error("Provider governance list is missing providers");
  }}
  return value as unknown as ProviderGovernanceList;
}}

export function assertPromptGovernanceList(
  value: unknown,
): PromptGovernanceList {{
  if (!isObject(value) || !Array.isArray(value.prompts)) {{
    throw new Error("Prompt governance list is missing prompts");
  }}
  return value as unknown as PromptGovernanceList;
}}

export function assertProfileGovernanceList(
  value: unknown,
): ProfileGovernanceList {{
  if (!isObject(value) || !Array.isArray(value.profiles)) {{
    throw new Error("Profile governance list is missing profiles");
  }}
  return value as unknown as ProfileGovernanceList;
}}

export function assertPolicyHistoryList(value: unknown): PolicyHistoryList {{
  if (!isObject(value) || !Array.isArray(value.history)) {{
    throw new Error("Policy history list is missing records");
  }}
  return value as unknown as PolicyHistoryList;
}}

export function assertGovernanceMutationResult(
  value: unknown,
): GovernanceMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Governance mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Governance mutation result is missing safe metadata");
  }}
  return value as unknown as GovernanceMutationResult;
}}

export function assertSafePromptPreview(value: unknown): SafePromptPreview {{
  if (!isObject(value)) {{
    throw new Error("Safe prompt preview must be an object");
  }}
  if (!hasString(value, "preview_id") || !hasString(value, "safe_output")) {{
    throw new Error("Safe prompt preview is missing safe output");
  }}
  return value as unknown as SafePromptPreview;
}}

export function assertProfileResolutionPreview(
  value: unknown,
): ProfileResolutionPreview {{
  if (!isObject(value)) {{
    throw new Error("Profile resolution preview must be an object");
  }}
  if (!hasString(value, "preview_id") || !hasString(value, "status")) {{
    throw new Error("Profile resolution preview is missing status");
  }}
  return value as unknown as ProfileResolutionPreview;
}}

export function assertSkillLifecycleDashboard(
  value: unknown,
): SkillLifecycleDashboard {{
  if (!isObject(value)) {{
    throw new Error("Skill lifecycle dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Skill lifecycle dashboard is missing page metadata");
  }}
  if (!Array.isArray(value.sections) || !Array.isArray(value.installations)) {{
    throw new Error("Skill lifecycle dashboard is missing lifecycle sections");
  }}
  if (!isObject(value.binding_preview) || !Array.isArray(value.audit_timeline)) {{
    throw new Error("Skill lifecycle dashboard is missing binding or audit evidence");
  }}
  return value as unknown as SkillLifecycleDashboard;
}}

export function assertTenantSkillDiscoveryList(
  value: unknown,
): TenantSkillDiscoveryList {{
  if (!isObject(value) || !isObject(value.discovery)) {{
    throw new Error("Tenant skill discovery is missing discovery data");
  }}
  return value as unknown as TenantSkillDiscoveryList;
}}

export function assertTenantSkillInstallationList(
  value: unknown,
): TenantSkillInstallationList {{
  if (!isObject(value) || !Array.isArray(value.installations)) {{
    throw new Error("Tenant skill installations are missing installation data");
  }}
  return value as unknown as TenantSkillInstallationList;
}}

export function assertSkillExecutionDiagnosticList(
  value: unknown,
): SkillExecutionDiagnosticList {{
  if (!isObject(value) || !Array.isArray(value.diagnostics)) {{
    throw new Error("Skill execution diagnostics are missing diagnostic data");
  }}
  return value as unknown as SkillExecutionDiagnosticList;
}}

export function assertSkillLifecycleAuditList(
  value: unknown,
): SkillLifecycleAuditList {{
  if (!isObject(value) || !Array.isArray(value.audit_timeline)) {{
    throw new Error("Skill lifecycle audit is missing timeline data");
  }}
  return value as unknown as SkillLifecycleAuditList;
}}

export function assertSkillLifecycleMutationResult(
  value: unknown,
): SkillLifecycleMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Skill lifecycle mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Skill lifecycle mutation result is missing safe metadata");
  }}
  return value as unknown as SkillLifecycleMutationResult;
}}

export function assertMembershipDashboard(value: unknown): MembershipDashboard {{
  if (!isObject(value)) {{
    throw new Error("Membership dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Membership dashboard is missing page metadata");
  }}
  if (!Array.isArray(value.sections) || !Array.isArray(value.directory)) {{
    throw new Error("Membership dashboard is missing directory sections");
  }}
  if (!Array.isArray(value.access_history) || !Array.isArray(value.audit_timeline)) {{
    throw new Error("Membership dashboard is missing access evidence");
  }}
  return value as unknown as MembershipDashboard;
}}

export function assertMembershipAccessHistoryList(
  value: unknown,
): MembershipAccessHistoryList {{
  if (!isObject(value) || !Array.isArray(value.records)) {{
    throw new Error("Membership access history is missing records");
  }}
  return value as unknown as MembershipAccessHistoryList;
}}

export function assertMembershipAuditList(value: unknown): MembershipAuditList {{
  if (!isObject(value) || !Array.isArray(value.records)) {{
    throw new Error("Membership audit is missing records");
  }}
  return value as unknown as MembershipAuditList;
}}

export function assertMembershipMutationResult(
  value: unknown,
): MembershipMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Membership mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Membership mutation result is missing safe metadata");
  }}
  return value as unknown as MembershipMutationResult;
}}

export function assertUsageReactDashboard(value: unknown): UsageReactDashboard {{
  if (!isObject(value)) {{
    throw new Error("Usage dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Usage dashboard is missing page metadata");
  }}
  if (!isObject(value.filters) || !Array.isArray(value.summary_cards)) {{
    throw new Error("Usage dashboard is missing filters or cards");
  }}
  if (!Array.isArray(value.trend) || !isObject(value.rollup)) {{
    throw new Error("Usage dashboard is missing trend or rollup data");
  }}
  if (!isObject(value.drilldown) || !Array.isArray(value.exports)) {{
    throw new Error("Usage dashboard is missing drilldown or export data");
  }}
  return value as unknown as UsageReactDashboard;
}}

export function assertUsageReactEventDrilldown(
  value: unknown,
): UsageReactEventDrilldown {{
  if (!isObject(value) || !Array.isArray(value.rows)) {{
    throw new Error("Usage event drilldown is missing rows");
  }}
  return value as unknown as UsageReactEventDrilldown;
}}

export function assertUsageReactExportSummary(
  value: unknown,
): UsageReactExportSummary {{
  if (!isObject(value)) {{
    throw new Error("Usage export summary must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "audit_reference")) {{
    throw new Error("Usage export summary is missing safe status metadata");
  }}
  return value as unknown as UsageReactExportSummary;
}}

export function assertChannelTelegramBriefingDashboard(
  value: unknown,
): ChannelTelegramBriefingDashboard {{
  if (!isObject(value)) {{
    throw new Error("Channel dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Channel dashboard is missing page metadata");
  }}
  if (!Array.isArray(value.readiness) || !Array.isArray(value.tenant_configs)) {{
    throw new Error("Channel dashboard is missing readiness data");
  }}
  if (!Array.isArray(value.aliases) || !Array.isArray(value.delivery_attempts)) {{
    throw new Error("Channel dashboard is missing operational rows");
  }}
  if (!isObject(value.preference_profiles)) {{
    throw new Error("Channel dashboard is missing preference data");
  }}
  return value as unknown as ChannelTelegramBriefingDashboard;
}}

export function assertChannelMutationResult(
  value: unknown,
): ChannelMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Channel mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Channel mutation result is missing safe metadata");
  }}
  return value as unknown as ChannelMutationResult;
}}

export function assertLinkTokenResult(value: unknown): LinkTokenResult {{
  if (!isObject(value)) {{
    throw new Error("Link token result must be an object");
  }}
  if (!hasString(value, "masked_status") || !hasString(value, "audit_reference")) {{
    throw new Error("Link token result is missing safe status metadata");
  }}
  return value as unknown as LinkTokenResult;
}}

export function assertDeliveryDiagnosticList(
  value: unknown,
): DeliveryDiagnosticList {{
  if (!isObject(value) || !Array.isArray(value.attempts)) {{
    throw new Error("Delivery diagnostics are missing attempts");
  }}
  return value as unknown as DeliveryDiagnosticList;
}}

export function assertRunStatusSummary(value: unknown): RunStatusSummary {{
  if (!isObject(value)) {{
    throw new Error("Run status summary must be an object");
  }}
  if (!hasString(value, "run_id") || !hasString(value, "status")) {{
    throw new Error("Run status summary is missing safe metadata");
  }}
  return value as unknown as RunStatusSummary;
}}

export function assertBriefingPreferenceList(
  value: unknown,
): BriefingPreferenceList {{
  if (!isObject(value) || !Array.isArray(value.admin_summaries)) {{
    throw new Error("Briefing preference list is missing summaries");
  }}
  return value as unknown as BriefingPreferenceList;
}}

export function assertBriefingPreferenceMutationResult(
  value: unknown,
): BriefingPreferenceMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Briefing preference mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "profile_summary")) {{
    throw new Error("Briefing preference mutation result is missing safe metadata");
  }}
  return value as unknown as BriefingPreferenceMutationResult;
}}

export function assertAdminMigrationHardeningDashboard(
  value: unknown,
): AdminMigrationHardeningDashboard {{
  if (!isObject(value)) {{
    throw new Error("Migration hardening dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Migration hardening dashboard is missing page metadata");
  }}
  if (!isObject(value.summary) || !Array.isArray(value.route_groups)) {{
    throw new Error("Migration hardening dashboard is missing route evidence");
  }}
  if (!isObject(value.rollback_plan) || !isObject(value.performance_budget)) {{
    throw new Error("Migration hardening dashboard is missing rollback or budget data");
  }}
  if (!isObject(value.accessibility_audit) || !isObject(value.redaction_sweep)) {{
    throw new Error("Migration hardening dashboard is missing audit evidence");
  }}
  return value as unknown as AdminMigrationHardeningDashboard;
}}

export function assertMigrationRouteGroupList(
  value: unknown,
): MigrationRouteGroup[] {{
  if (!Array.isArray(value)) {{
    throw new Error("Migration route groups must be an array");
  }}
  return value as unknown as MigrationRouteGroup[];
}}

export function assertMigrationRollbackPlan(
  value: unknown,
): MigrationRollbackPlan {{
  if (!isObject(value)) {{
    throw new Error("Migration rollback plan must be an object");
  }}
  if (!hasString(value, "plan_id") || !Array.isArray(value.steps)) {{
    throw new Error("Migration rollback plan is missing safe steps");
  }}
  return value as unknown as MigrationRollbackPlan;
}}

export function assertTestBenchDashboard(value: unknown): TestBenchDashboard {{
  if (!isObject(value)) {{
    throw new Error("Test bench dashboard must be an object");
  }}
  if (!hasString(value, "page_id") || !hasString(value, "title")) {{
    throw new Error("Test bench dashboard is missing page metadata");
  }}
  if (!Array.isArray(value.sections) || !Array.isArray(value.suites)) {{
    throw new Error("Test bench dashboard is missing suite sections");
  }}
  if (!Array.isArray(value.recent_runs) || !Array.isArray(value.gate_alerts)) {{
    throw new Error("Test bench dashboard is missing run or gate evidence");
  }}
  return value as unknown as TestBenchDashboard;
}}

export function assertTestSuiteList(value: unknown): TestSuiteList {{
  if (!isObject(value) || !Array.isArray(value.suites)) {{
    throw new Error("Test suite list is missing suites");
  }}
  return value as unknown as TestSuiteList;
}}

export function assertTestSuiteDetail(value: unknown): TestSuiteDetail {{
  if (!isObject(value) || !isObject(value.summary) || !Array.isArray(value.cases)) {{
    throw new Error("Test suite detail is missing safe suite metadata");
  }}
  return value as unknown as TestSuiteDetail;
}}

export function assertTestRunList(value: unknown): TestRunList {{
  if (!isObject(value) || !Array.isArray(value.runs)) {{
    throw new Error("Test run list is missing runs");
  }}
  return value as unknown as TestRunList;
}}

export function assertTestRunDetail(value: unknown): TestRunDetail {{
  if (
    !isObject(value) ||
    !isObject(value.summary) ||
    !Array.isArray(value.trace_steps)
  ) {{
    throw new Error("Test run detail is missing trace evidence");
  }}
  return value as unknown as TestRunDetail;
}}

export function assertPublishGateEvidenceList(
  value: unknown,
): PublishGateEvidenceList {{
  if (!isObject(value) || !Array.isArray(value.gates)) {{
    throw new Error("Publish gate evidence list is missing gates");
  }}
  return value as unknown as PublishGateEvidenceList;
}}

export function assertArtifactReferenceSummary(
  value: unknown,
): ArtifactReferenceSummary {{
  if (!isObject(value) || !hasString(value, "artifact_reference_id")) {{
    throw new Error("Artifact reference is missing safe metadata");
  }}
  return value as unknown as ArtifactReferenceSummary;
}}

export function assertTestBenchAuditList(value: unknown): TestBenchAuditList {{
  if (!isObject(value) || !Array.isArray(value.audit_timeline)) {{
    throw new Error("Test bench audit is missing timeline data");
  }}
  return value as unknown as TestBenchAuditList;
}}

export function assertTestBenchMutationResult(
  value: unknown,
): TestBenchMutationResult {{
  if (!isObject(value)) {{
    throw new Error("Test bench mutation result must be an object");
  }}
  if (!hasString(value, "status") || !hasString(value, "summary")) {{
    throw new Error("Test bench mutation result is missing safe metadata");
  }}
  return value as unknown as TestBenchMutationResult;
}}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate TypeScript contracts for the React admin app."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = render_types()
    output = args.output
    if not output.is_absolute():
        output = REPO_ROOT / output
    if args.check:
        if not output.exists():
            raise SystemExit(f"{output} does not exist")
        existing = output.read_text(encoding="utf-8")
        if existing != rendered:
            raise SystemExit(
                f"{output} is out of date; run this script without --check"
            )
        print(f"{output} is up to date")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
