import {
  assertAdminPageEnvelope,
  assertBuilderMutationResult,
  assertGovernanceDashboard,
  assertGovernanceMutationResult,
  assertMembershipAccessHistoryList,
  assertMembershipAuditList,
  assertMembershipDashboard,
  assertMembershipMutationResult,
  assertAdminMigrationHardeningDashboard,
  assertBriefingPreferenceList,
  assertBriefingPreferenceMutationResult,
  assertChannelMutationResult,
  assertChannelTelegramBriefingDashboard,
  assertDeliveryDiagnosticList,
  assertLinkTokenResult,
  assertMigrationRollbackPlan,
  assertMigrationRouteGroupList,
  assertUsageReactDashboard,
  assertUsageReactEventDrilldown,
  assertUsageReactExportSummary,
  assertPolicyHistoryList,
  assertProfileGovernanceList,
  assertProfileResolutionPreview,
  assertPromptGovernanceList,
  assertProviderGovernanceList,
  assertSafePromptPreview,
  assertExportSnapshot,
  assertMutationResult,
  assertOperationsWorkbenchEnvelope,
  assertReactAdminBootstrap,
  assertReactAdminCommandSearch,
  assertRunStatusSummary,
  assertRunDebugEnvelope,
  assertSkillExecutionDiagnosticList,
  assertSkillLifecycleAuditList,
  assertSkillLifecycleDashboard,
  assertSkillLifecycleMutationResult,
  assertTenantSkillDiscoveryList,
  assertTenantSkillInstallationList,
  assertArtifactReferenceSummary,
  assertPublishGateEvidenceList,
  assertTestBenchAuditList,
  assertTestBenchDashboard,
  assertTestBenchMutationResult,
  assertTestRunDetail,
  assertTestRunList,
  assertTestSuiteDetail,
  assertTestSuiteList,
  assertWorkbenchExportSnapshot,
  assertWorkflowBuilderEnvelope,
  assertWorkflowReferenceCatalog,
  type AdminPageEnvelope,
  type BuilderMutationResult,
  type ExportSnapshot,
  type GovernanceDashboard,
  type GovernanceMutationResult,
  type MembershipAccessHistoryList,
  type MembershipAuditList,
  type MembershipConfirmationRequest,
  type MembershipDashboard,
  type MembershipInvitationSaveRequest,
  type MembershipMutationResult,
  type AdminMigrationHardeningDashboard,
  type BriefingPreferenceExportRequest,
  type BriefingPreferenceImportRequest,
  type BriefingPreferenceList,
  type BriefingPreferenceMutationResult,
  type BriefingPreferenceSaveRequest,
  type ChannelMutationResult,
  type ChannelTelegramBriefingDashboard,
  type DeliveryDiagnosticList,
  type LinkTokenCreateRequest,
  type LinkTokenResult,
  type MigrationRollbackPlan,
  type MigrationRouteGroup,
  type UsageReactDashboard,
  type UsageReactEventDrilldown,
  type UsageReactExportCreateRequest,
  type UsageReactExportSummary,
  type MutationResult,
  type OperationsWorkbenchEnvelope,
  type PolicyHistoryList,
  type ProfileGovernanceList,
  type ProfileResolutionPreview,
  type ProfileSaveRequest,
  type PromptGovernanceList,
  type PromptPreviewRequest,
  type PromptSaveRequest,
  type ProviderCredentialReferenceRequest,
  type ProviderGovernanceList,
  type PrincipalLinkRequest,
  type ReactAdminBootstrap,
  type ReactAdminCommandSearch,
  type RunStatusSummary,
  type TelegramAliasActionRequest,
  type TelegramAliasSaveRequest,
  type TelegramConfigSaveRequest,
  type WebhookValidationRequest,
  type BindingEligibilityPreviewRequest,
  type CredentialConfigurationRequest,
  type ReadinessRefreshRequest,
  type RoutingPreviewRequest,
  type RoleGrantSaveRequest,
  type SafePromptPreview,
  type RunDebugEnvelope,
  type SampleActionRequest,
  type SkillExecutionDiagnosticList,
  type SkillLifecycleAuditList,
  type SkillLifecycleDashboard,
  type SkillLifecycleMutationResult,
  type SkillPackageCandidateRequest,
  type SkillPackagePublishRequest,
  type TenantGrantMutationRequest,
  type TenantSkillDiscoveryList,
  type TenantSkillInstallRequest,
  type TenantSkillInstallationList,
  type ArtifactReferenceSummary,
  type GateEvidenceRefreshRequest,
  type PublishGateEvidenceList,
  type TestBenchAuditList,
  type TestBenchDashboard,
  type TestBenchMutationResult,
  type TestCaseSaveRequest,
  type TestRunDetail,
  type TestRunLaunchRequest,
  type TestRunList,
  type TestSuiteDetail,
  type TestSuiteList,
  type TestSuiteSaveRequest,
  type WorkflowBuilderEnvelope,
  type WorkflowDraftSaveRequest,
  type WorkflowPublishRequest,
  type WorkflowReferenceCatalog,
  type WorkbenchExportRequest,
  type WorkbenchExportSnapshot,
} from "./generated/reactAdminApi";

export async function fetchBootstrap(
  bootstrapUrl: string,
): Promise<ReactAdminBootstrap> {
  const response = await fetch(bootstrapUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertReactAdminBootstrap(await response.json());
}

export async function fetchCommandSearch(
  searchUrl: string,
  query: string,
): Promise<ReactAdminCommandSearch> {
  const url = new URL(searchUrl, window.location.origin);
  if (query.trim()) {
    url.searchParams.set("q", query.trim());
  }
  const response = await fetch(url.toString(), {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertReactAdminCommandSearch(await response.json());
}

export async function fetchPatternsEnvelope(
  patternsUrl: string,
): Promise<AdminPageEnvelope> {
  const response = await fetch(patternsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertAdminPageEnvelope(await response.json());
}

export async function submitSampleAction(
  actionUrl: string,
  payload: SampleActionRequest,
): Promise<MutationResult> {
  const response = await fetch(actionUrl, {
    body: JSON.stringify(payload),
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMutationResult(await response.json());
}

export async function requestSampleExport(
  exportUrl: string,
): Promise<ExportSnapshot> {
  const response = await fetch(exportUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertExportSnapshot(await response.json());
}

export async function fetchOperationsWorkbench(
  workbenchUrl: string,
): Promise<OperationsWorkbenchEnvelope> {
  const response = await fetch(workbenchUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertOperationsWorkbenchEnvelope(await response.json());
}

export async function fetchRunDebugEnvelope(
  runDebugUrl: string,
): Promise<RunDebugEnvelope> {
  const response = await fetch(runDebugUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertRunDebugEnvelope(await response.json());
}

export async function requestWorkbenchExport(
  exportUrl: string,
  payload: WorkbenchExportRequest = {
    include_run_debug: true,
    range: "60m",
    scope_type: "active",
  },
): Promise<WorkbenchExportSnapshot> {
  const response = await fetch(exportUrl, {
    body: JSON.stringify(payload),
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertWorkbenchExportSnapshot(await response.json());
}

export async function fetchWorkflowBuilder(
  builderUrl: string,
): Promise<WorkflowBuilderEnvelope> {
  const response = await fetch(builderUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertWorkflowBuilderEnvelope(await response.json());
}

export async function fetchWorkflowLookups(
  lookupsUrl: string,
): Promise<WorkflowReferenceCatalog> {
  const response = await fetch(lookupsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertWorkflowReferenceCatalog(await response.json());
}

export async function saveWorkflowDraft(
  saveUrl: string,
  payload: WorkflowDraftSaveRequest,
): Promise<BuilderMutationResult> {
  const response = await fetch(saveUrl, {
    body: JSON.stringify(payload),
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertBuilderMutationResult(await response.json());
}

export async function validateWorkflowDraft(
  validateUrl: string,
  ready = false,
): Promise<BuilderMutationResult> {
  const url = new URL(validateUrl, window.location.origin);
  if (ready) {
    url.searchParams.set("ready", "true");
  }
  const response = await fetch(url.toString(), {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertBuilderMutationResult(await response.json());
}

export async function publishWorkflowDraft(
  publishUrl: string,
  payload: WorkflowPublishRequest,
): Promise<BuilderMutationResult> {
  const response = await fetch(publishUrl, {
    body: JSON.stringify(payload),
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertBuilderMutationResult(await response.json());
}

export async function fetchGovernanceDashboard(
  governanceUrl: string,
): Promise<GovernanceDashboard> {
  const response = await fetch(governanceUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertGovernanceDashboard(await response.json());
}

export async function fetchProviderGovernance(
  providersUrl: string,
): Promise<ProviderGovernanceList> {
  const response = await fetch(providersUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertProviderGovernanceList(await response.json());
}

export async function fetchPromptGovernance(
  promptsUrl: string,
): Promise<PromptGovernanceList> {
  const response = await fetch(promptsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertPromptGovernanceList(await response.json());
}

export async function fetchProfileGovernance(
  profilesUrl: string,
): Promise<ProfileGovernanceList> {
  const response = await fetch(profilesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertProfileGovernanceList(await response.json());
}

export async function fetchPolicyHistory(
  historyUrl: string,
): Promise<PolicyHistoryList> {
  const response = await fetch(historyUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertPolicyHistoryList(await response.json());
}

export async function runProviderProbe(
  probeUrl: string,
): Promise<GovernanceMutationResult> {
  return postGovernanceMutation(probeUrl);
}

export async function saveProviderCredentialReference(
  saveUrl: string,
  payload: ProviderCredentialReferenceRequest,
): Promise<GovernanceMutationResult> {
  return postGovernanceMutation(saveUrl, payload);
}

export async function savePromptSummary(
  saveUrl: string,
  payload: PromptSaveRequest,
): Promise<GovernanceMutationResult> {
  return postGovernanceMutation(saveUrl, payload);
}

export async function previewPrompt(
  previewUrl: string,
  payload: PromptPreviewRequest,
): Promise<SafePromptPreview> {
  const response = await postJson(previewUrl, payload);
  return assertSafePromptPreview(await response.json());
}

export async function saveRuntimeProfile(
  saveUrl: string,
  payload: ProfileSaveRequest,
): Promise<GovernanceMutationResult> {
  return postGovernanceMutation(saveUrl, payload);
}

export async function resolveRuntimeProfile(
  resolveUrl: string,
): Promise<ProfileResolutionPreview> {
  const response = await postJson(resolveUrl);
  return assertProfileResolutionPreview(await response.json());
}

export async function previewRouting(
  previewUrl: string,
  payload: RoutingPreviewRequest,
): Promise<GovernanceMutationResult> {
  return postGovernanceMutation(previewUrl, payload);
}

export async function fetchSkillLifecycleDashboard(
  skillsUrl: string,
): Promise<SkillLifecycleDashboard> {
  const response = await fetch(skillsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertSkillLifecycleDashboard(await response.json());
}

export async function fetchTenantSkillDiscovery(
  discoveryUrl: string,
): Promise<TenantSkillDiscoveryList> {
  const response = await fetch(discoveryUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTenantSkillDiscoveryList(await response.json());
}

export async function fetchTenantSkillInstallations(
  installationsUrl: string,
): Promise<TenantSkillInstallationList> {
  const response = await fetch(installationsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTenantSkillInstallationList(await response.json());
}

export async function fetchSkillExecutionDiagnostics(
  diagnosticsUrl: string,
): Promise<SkillExecutionDiagnosticList> {
  const response = await fetch(diagnosticsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertSkillExecutionDiagnosticList(await response.json());
}

export async function fetchSkillLifecycleAudit(
  auditUrl: string,
): Promise<SkillLifecycleAuditList> {
  const response = await fetch(auditUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertSkillLifecycleAuditList(await response.json());
}

export async function saveSkillCandidate(
  candidateUrl: string,
  payload: SkillPackageCandidateRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(candidateUrl, payload);
}

export async function validateSkillCandidate(
  validateUrl: string,
  ready = true,
): Promise<SkillLifecycleMutationResult> {
  const url = new URL(validateUrl, window.location.origin);
  if (!ready) {
    url.searchParams.set("ready", "false");
  }
  return postSkillLifecycleMutation(url.toString());
}

export async function publishSkillCandidate(
  publishUrl: string,
  payload: SkillPackagePublishRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(publishUrl, payload);
}

export async function updateSkillTenantGrant(
  grantUrl: string,
  payload: TenantGrantMutationRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(grantUrl, payload);
}

export async function updateSkillPackageLifecycle(
  lifecycleUrl: string,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(lifecycleUrl);
}

export async function installTenantSkill(
  installUrl: string,
  payload: TenantSkillInstallRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(installUrl, payload);
}

export async function configureSkillCredential(
  credentialUrl: string,
  payload: CredentialConfigurationRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(credentialUrl, payload);
}

export async function refreshSkillReadiness(
  refreshUrl: string,
  payload: ReadinessRefreshRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(refreshUrl, payload);
}

export async function runSkillDiagnostic(
  diagnosticUrl: string,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(diagnosticUrl);
}

export async function previewSkillBinding(
  previewUrl: string,
  payload: BindingEligibilityPreviewRequest,
): Promise<SkillLifecycleMutationResult> {
  return postSkillLifecycleMutation(previewUrl, payload);
}

export async function fetchMembershipDashboard(
  membershipsUrl: string,
): Promise<MembershipDashboard> {
  const response = await fetch(membershipsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMembershipDashboard(await response.json());
}

export async function saveMembershipInvitation(
  invitationUrl: string,
  payload: MembershipInvitationSaveRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(invitationUrl, payload);
}

export async function linkMembershipPrincipal(
  linkUrl: string,
  payload: PrincipalLinkRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(linkUrl, payload);
}

export async function saveMembershipRoleGrant(
  roleGrantUrl: string,
  payload: RoleGrantSaveRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(roleGrantUrl, payload);
}

export async function revokeMembershipRoleGrant(
  revokeUrl: string,
  payload: MembershipConfirmationRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(revokeUrl, payload);
}

export async function updateMembershipPrincipalStatus(
  statusUrl: string,
  payload: MembershipConfirmationRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(statusUrl, payload);
}

export async function updateTenantMembershipStatus(
  statusUrl: string,
  payload: MembershipConfirmationRequest,
): Promise<MembershipMutationResult> {
  return postMembershipMutation(statusUrl, payload);
}

export async function fetchMembershipAccessHistory(
  historyUrl: string,
): Promise<MembershipAccessHistoryList> {
  const response = await fetch(historyUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMembershipAccessHistoryList(await response.json());
}

export async function fetchMembershipAudit(
  auditUrl: string,
): Promise<MembershipAuditList> {
  const response = await fetch(auditUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMembershipAuditList(await response.json());
}

export async function fetchUsageDashboard(
  usageUrl: string,
): Promise<UsageReactDashboard> {
  const response = await fetch(usageUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertUsageReactDashboard(await response.json());
}

export async function fetchUsageEvents(
  eventsUrl: string,
): Promise<UsageReactEventDrilldown> {
  const response = await fetch(eventsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertUsageReactEventDrilldown(await response.json());
}

export async function createUsageExport(
  exportUrl: string,
  payload: UsageReactExportCreateRequest,
): Promise<UsageReactExportSummary> {
  const response = await postJson(exportUrl, payload);
  return assertUsageReactExportSummary(await response.json());
}

export async function fetchUsageExportDetail(
  exportUrl: string,
): Promise<UsageReactExportSummary> {
  const response = await fetch(exportUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertUsageReactExportSummary(await response.json());
}

export async function fetchChannelTelegramBriefingDashboard(
  channelsUrl: string,
): Promise<ChannelTelegramBriefingDashboard> {
  const response = await fetch(channelsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertChannelTelegramBriefingDashboard(await response.json());
}

export async function saveTelegramConfig(
  configUrl: string,
  payload: TelegramConfigSaveRequest,
): Promise<ChannelMutationResult> {
  const response = await postJson(configUrl, payload);
  return assertChannelMutationResult(await response.json());
}

export async function validateTelegramWebhook(
  validationUrl: string,
  payload: WebhookValidationRequest,
): Promise<ChannelMutationResult> {
  const response = await postJson(validationUrl, payload);
  return assertChannelMutationResult(await response.json());
}

export async function saveTelegramAlias(
  aliasesUrl: string,
  payload: TelegramAliasSaveRequest,
): Promise<ChannelMutationResult> {
  const response = await postJson(aliasesUrl, payload);
  return assertChannelMutationResult(await response.json());
}

export async function runTelegramAliasAction(
  actionUrl: string,
  payload: TelegramAliasActionRequest,
): Promise<ChannelMutationResult> {
  const response = await postJson(actionUrl, payload);
  return assertChannelMutationResult(await response.json());
}

export async function createTelegramLinkToken(
  tokenUrl: string,
  payload: LinkTokenCreateRequest,
): Promise<LinkTokenResult> {
  const response = await postJson(tokenUrl, payload);
  return assertLinkTokenResult(await response.json());
}

export async function fetchTelegramDeliveries(
  deliveriesUrl: string,
): Promise<DeliveryDiagnosticList> {
  const response = await fetch(deliveriesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertDeliveryDiagnosticList(await response.json());
}

export async function fetchChannelRunStatus(
  runStatusUrl: string,
): Promise<RunStatusSummary> {
  const response = await fetch(runStatusUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertRunStatusSummary(await response.json());
}

export async function fetchBriefingPreferences(
  preferencesUrl: string,
): Promise<BriefingPreferenceList> {
  const response = await fetch(preferencesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertBriefingPreferenceList(await response.json());
}

export async function saveBriefingPreferences(
  preferencesUrl: string,
  payload: BriefingPreferenceSaveRequest,
): Promise<BriefingPreferenceMutationResult> {
  const response = await postJson(preferencesUrl, payload);
  return assertBriefingPreferenceMutationResult(await response.json());
}

export async function importBriefingPreferences(
  importUrl: string,
  payload: BriefingPreferenceImportRequest,
): Promise<BriefingPreferenceMutationResult> {
  const response = await postJson(importUrl, payload);
  return assertBriefingPreferenceMutationResult(await response.json());
}

export async function exportBriefingPreferences(
  exportUrl: string,
  payload: BriefingPreferenceExportRequest,
): Promise<BriefingPreferenceMutationResult> {
  const response = await postJson(exportUrl, payload);
  return assertBriefingPreferenceMutationResult(await response.json());
}

export async function fetchMigrationHardeningDashboard(
  dashboardUrl: string,
): Promise<AdminMigrationHardeningDashboard> {
  const response = await fetch(dashboardUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertAdminMigrationHardeningDashboard(await response.json());
}

export async function fetchMigrationRouteGroups(
  routesUrl: string,
): Promise<MigrationRouteGroup[]> {
  const response = await fetch(routesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMigrationRouteGroupList(await response.json());
}

export async function fetchMigrationRollbackPlan(
  rollbackUrl: string,
): Promise<MigrationRollbackPlan> {
  const response = await fetch(rollbackUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertMigrationRollbackPlan(await response.json());
}

export async function fetchTestBenchDashboard(
  testBenchUrl: string,
): Promise<TestBenchDashboard> {
  const response = await fetch(testBenchUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestBenchDashboard(await response.json());
}

export async function fetchTestSuites(
  suitesUrl: string,
): Promise<TestSuiteList> {
  const response = await fetch(suitesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestSuiteList(await response.json());
}

export async function fetchTestSuiteDetail(
  suiteUrl: string,
): Promise<TestSuiteDetail> {
  const response = await fetch(suiteUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestSuiteDetail(await response.json());
}

export async function saveTestSuite(
  suiteUrl: string,
  payload: TestSuiteSaveRequest,
): Promise<TestBenchMutationResult> {
  return postTestBenchMutation(suiteUrl, payload);
}

export async function saveTestCase(
  caseUrl: string,
  payload: TestCaseSaveRequest,
): Promise<TestBenchMutationResult> {
  return postTestBenchMutation(caseUrl, payload);
}

export async function launchTestRun(
  runUrl: string,
  payload: TestRunLaunchRequest,
): Promise<TestBenchMutationResult> {
  return postTestBenchMutation(runUrl, payload);
}

export async function fetchTestRuns(runsUrl: string): Promise<TestRunList> {
  const response = await fetch(runsUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestRunList(await response.json());
}

export async function fetchTestRunDetail(
  runUrl: string,
): Promise<TestRunDetail> {
  const response = await fetch(runUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestRunDetail(await response.json());
}

export async function fetchPublishGateEvidence(
  gatesUrl: string,
): Promise<PublishGateEvidenceList> {
  const response = await fetch(gatesUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertPublishGateEvidenceList(await response.json());
}

export async function refreshPublishGateEvidence(
  gateUrl: string,
  payload: GateEvidenceRefreshRequest,
): Promise<TestBenchMutationResult> {
  return postTestBenchMutation(gateUrl, payload);
}

export async function fetchArtifactReference(
  artifactUrl: string,
): Promise<ArtifactReferenceSummary> {
  const response = await fetch(artifactUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertArtifactReferenceSummary(await response.json());
}

export async function fetchTestBenchAudit(
  auditUrl: string,
): Promise<TestBenchAuditList> {
  const response = await fetch(auditUrl, {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return assertTestBenchAuditList(await response.json());
}

async function postGovernanceMutation(
  url: string,
  payload?: unknown,
): Promise<GovernanceMutationResult> {
  const response = await postJson(url, payload);
  return assertGovernanceMutationResult(await response.json());
}

async function postSkillLifecycleMutation(
  url: string,
  payload?: unknown,
): Promise<SkillLifecycleMutationResult> {
  const response = await postJson(url, payload);
  return assertSkillLifecycleMutationResult(await response.json());
}

async function postTestBenchMutation(
  url: string,
  payload?: unknown,
): Promise<TestBenchMutationResult> {
  const response = await postJson(url, payload);
  return assertTestBenchMutationResult(await response.json());
}

async function postMembershipMutation(
  url: string,
  payload?: unknown,
): Promise<MembershipMutationResult> {
  const response = await postJson(url, payload);
  return assertMembershipMutationResult(await response.json());
}

async function postJson(url: string, payload?: unknown): Promise<Response> {
  const response = await fetch(url, {
    body: payload === undefined ? undefined : JSON.stringify(payload),
    credentials: "same-origin",
    headers:
      payload === undefined
        ? { Accept: "application/json" }
        : {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
    method: "POST",
  });
  if (!response.ok) {
    const detail = await safeErrorDetail(response);
    throw new Error(detail);
  }
  return response;
}

async function safeErrorDetail(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    if (typeof payload.detail === "string" && payload.detail.length <= 120) {
      return payload.detail;
    }
  } catch {
    return `React admin request failed with ${response.status}`;
  }
  return `React admin request failed with ${response.status}`;
}
