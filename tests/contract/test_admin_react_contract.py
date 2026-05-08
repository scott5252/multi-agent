from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from multi_agent_platform.api.main import create_app
from multi_agent_platform.auth.policy import SURFACE_POLICIES


def test_openapi_contains_react_admin_contracts() -> None:
    schema = TestClient(create_app()).get("/openapi.json").json()

    assert "/admin/app" in schema["paths"]
    assert "/admin/app/bootstrap.json" in schema["paths"]
    assert "/admin/app/home.json" in schema["paths"]
    assert "/admin/app/config.json" in schema["paths"]
    assert "/admin/app/manifest.json" in schema["paths"]
    assert "/admin/app/search.json" in schema["paths"]
    assert "/auth/local-login.json" in schema["paths"]
    assert "/admin/app/patterns" not in schema["paths"]
    assert "/admin/app/patterns.json" not in schema["paths"]
    assert "/admin/app/patterns/actions/sample" not in schema["paths"]
    assert "/admin/app/patterns/export" not in schema["paths"]
    assert "/admin/app/workflows" in schema["paths"]
    assert "/admin/app/workflows/new" in schema["paths"]
    assert "/admin/app/workflows/registry.json" in schema["paths"]
    assert "/admin/app/workflows/create.json" in schema["paths"]
    assert "/admin/app/workflows/legacy-routes.json" in schema["paths"]
    assert "/admin/app/workflows/builder.json" in schema["paths"]
    assert "/admin/app/workflows/lookups.json" in schema["paths"]
    assert (
        "/admin/app/workflows/drafts/{workflow_draft_id}/detail.json" in schema["paths"]
    )
    assert (
        "/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate.json"
        in schema["paths"]
    )
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/save" in schema["paths"]
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/validate" in schema["paths"]
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/publish" in schema["paths"]
    assert (
        "/admin/app/workflows/versions/{workflow_version_bundle_id}/detail.json"
        in schema["paths"]
    )
    assert "/admin/app/governance" in schema["paths"]
    assert "/admin/app/governance/bootstrap.json" in schema["paths"]
    assert "/admin/app/governance/providers.json" in schema["paths"]
    assert "/admin/app/governance/providers/{provider_id}/probe" in schema["paths"]
    assert (
        "/admin/app/governance/providers/{provider_id}/credential-reference"
        in schema["paths"]
    )
    assert "/admin/app/governance/prompts.json" in schema["paths"]
    assert "/admin/app/governance/prompts/{prompt_lineage_id}/save" in schema["paths"]
    assert (
        "/admin/app/governance/prompts/{prompt_lineage_id}/preview" in schema["paths"]
    )
    assert "/admin/app/governance/profiles.json" in schema["paths"]
    assert "/admin/app/governance/profiles/{profile_id}/save" in schema["paths"]
    assert "/admin/app/governance/profiles/{profile_id}/resolve" in schema["paths"]
    assert "/admin/app/governance/routing/preview" in schema["paths"]
    assert "/admin/app/governance/history.json" in schema["paths"]
    assert "/admin/app/governance/provenance/{run_id}.json" in schema["paths"]
    assert "/admin/app/skills" in schema["paths"]
    assert "/admin/app/skills/bootstrap.json" in schema["paths"]
    assert "/admin/app/skills/legacy-routes.json" in schema["paths"]
    assert "/admin/app/skills/packages/candidates" in schema["paths"]
    assert (
        "/admin/app/skills/packages/candidates/{candidate_id}/validate"
        in schema["paths"]
    )
    assert (
        "/admin/app/skills/packages/candidates/{candidate_id}/publish"
        in schema["paths"]
    )
    assert "/admin/app/skills/packages/{package_id}/grants" in schema["paths"]
    assert "/admin/app/skills/packages/{package_id}/quarantine" in schema["paths"]
    assert "/admin/app/skills/packages/{package_id}/withdraw" in schema["paths"]
    assert "/admin/app/skills/discovery.json" in schema["paths"]
    assert "/admin/app/skills/installations.json" in schema["paths"]
    assert (
        "/admin/app/skills/installations/{installation_id}/credentials"
        in schema["paths"]
    )
    assert (
        "/admin/app/skills/installations/{installation_id}/smoke-tests"
        in schema["paths"]
    )
    assert "/admin/app/skills/diagnostics.json" in schema["paths"]
    assert "/admin/app/skills/diagnostics/run" in schema["paths"]
    assert "/admin/app/skills/eligibility/preview" in schema["paths"]
    assert "/admin/app/skills/audit.json" in schema["paths"]
    assert "/admin/app/test-bench" in schema["paths"]
    assert "/admin/app/test-bench/bootstrap.json" in schema["paths"]
    assert "/admin/app/test-bench/suites" in schema["paths"]
    assert "/admin/app/test-bench/suites/{suite_id}" in schema["paths"]
    assert "/admin/app/test-bench/suites/{suite_id}/cases" in schema["paths"]
    assert "/admin/app/test-bench/suites/{suite_id}/runs" in schema["paths"]
    assert "/admin/app/test-bench/runs.json" in schema["paths"]
    assert "/admin/app/test-bench/runs/{run_id}.json" in schema["paths"]
    assert "/admin/app/test-bench/gates.json" in schema["paths"]
    assert "/admin/app/test-bench/gates/{gate_id}/refresh" in schema["paths"]
    assert (
        "/admin/app/test-bench/artifacts/{artifact_reference_id}.json"
        in schema["paths"]
    )
    assert "/admin/app/test-bench/audit.json" in schema["paths"]
    assert "/admin/agent-tests/ui" in schema["paths"]
    assert "/admin/agent-tests/ui/suites/new" in schema["paths"]
    assert "/admin/agent-tests/ui/suites/{suite_id}" in schema["paths"]
    assert "/admin/agent-tests/ui/runs/{run_id}" in schema["paths"]
    assert "/admin/app/memberships" in schema["paths"]
    assert "/admin/app/memberships/bootstrap.json" in schema["paths"]
    assert "/admin/app/memberships/invitations" in schema["paths"]
    assert "/admin/app/memberships/principals/link" in schema["paths"]
    assert "/admin/app/memberships/role-grants" in schema["paths"]
    assert (
        "/admin/app/memberships/role-grants/{role_grant_id}/revoke" in schema["paths"]
    )
    assert (
        "/admin/app/memberships/principals/{principal_identity_id}/{status_action}"
        in schema["paths"]
    )
    assert (
        "/admin/app/memberships/memberships/{tenant_membership_id}/"
        "{membership_status}" in schema["paths"]
    )
    assert "/admin/app/memberships/access-history.json" in schema["paths"]
    assert "/admin/app/memberships/audit.json" in schema["paths"]
    assert "/admin/app/usage" in schema["paths"]
    assert "/admin/app/usage/bootstrap.json" in schema["paths"]
    assert "/admin/app/usage/events.json" in schema["paths"]
    assert "/admin/app/usage/exports" in schema["paths"]
    assert "/admin/app/usage/exports/{usage_export_request_id}.json" in schema["paths"]
    assert "/admin/app/channels" in schema["paths"]
    assert "/admin/app/channels/shell.json" in schema["paths"]
    assert "/admin/app/channels/bootstrap.json" in schema["paths"]
    assert "/admin/app/channels/telegram/config" in schema["paths"]
    assert "/admin/app/channels/telegram/webhook/validate" in schema["paths"]
    assert "/admin/app/channels/telegram/aliases" in schema["paths"]
    assert "/admin/app/channels/telegram/aliases/{alias_id}/{action}" in schema["paths"]
    assert "/admin/app/channels/telegram/link-tokens" in schema["paths"]
    assert "/admin/app/channels/telegram/deliveries.json" in schema["paths"]
    assert "/admin/app/channels/runs" in schema["paths"]
    assert "/admin/app/channels/runs/{workflow_run_id}" in schema["paths"]
    assert "/admin/app/channels/runs/{workflow_run_id}/status.json" in schema["paths"]
    assert "/admin/app/channels/briefing/preferences.json" in schema["paths"]
    assert "/admin/app/channels/briefing/preferences" in schema["paths"]
    assert "/admin/app/channels/briefing/preferences/import" in schema["paths"]
    assert "/admin/app/channels/briefing/preferences/export" in schema["paths"]
    assert "/admin/app/migration" in schema["paths"]
    assert "/admin/app/migration/shell.json" in schema["paths"]
    assert "/admin/app/migration/bootstrap.json" in schema["paths"]
    assert "/admin/app/migration/routes.json" in schema["paths"]
    assert "/admin/app/migration/decommission-inventory.json" in schema["paths"]
    assert "/admin/app/migration/rollback.json" in schema["paths"]
    assert "/admin/app/operations" in schema["paths"]
    assert "/admin/app/operations.json" in schema["paths"]
    assert "/admin/app/operations/runs/{workflow_run_id}.json" in schema["paths"]
    assert "/admin/app/operations/export" in schema["paths"]
    assert "ReactAdminBootstrap" in schema["components"]["schemas"]
    assert "ConsoleHomeEnvelope" in schema["components"]["schemas"]
    assert "LocalLoginEnvelope" in schema["components"]["schemas"]
    assert "ReactAdminPrincipal" in schema["components"]["schemas"]
    assert "ReactAdminShellChrome" in schema["components"]["schemas"]
    assert "ReactAdminCommandSearch" in schema["components"]["schemas"]
    assert "AdminPageEnvelope" not in schema["components"]["schemas"]
    assert "ReactAdminPageProvenance" in schema["components"]["schemas"]
    assert "ReactAdminEmptyStateMetadata" in schema["components"]["schemas"]
    assert "ReactAdminActionMetadata" in schema["components"]["schemas"]
    assert "SafeProblemDetail" in schema["components"]["schemas"]
    assert "OperationsWorkbenchEnvelope" in schema["components"]["schemas"]
    assert "RunDebugEnvelope" in schema["components"]["schemas"]
    assert "WorkbenchExportSnapshot" in schema["components"]["schemas"]
    assert "WorkflowBuilderEnvelope" in schema["components"]["schemas"]
    assert "WorkflowReferenceCatalog" in schema["components"]["schemas"]
    assert "WorkflowRegistryEnvelope" in schema["components"]["schemas"]
    assert "WorkflowCreateEnvelope" in schema["components"]["schemas"]
    assert "WorkflowLegacyRouteMapping" in schema["components"]["schemas"]
    assert "WorkflowVersionDetail" in schema["components"]["schemas"]
    assert "BuilderMutationResult" in schema["components"]["schemas"]
    assert "GovernanceDashboard" in schema["components"]["schemas"]
    assert "ProviderGovernanceList" in schema["components"]["schemas"]
    assert "PromptGovernanceList" in schema["components"]["schemas"]
    assert "ProfileGovernanceList" in schema["components"]["schemas"]
    assert "GovernanceMutationResult" in schema["components"]["schemas"]
    assert "SafePromptPreview" in schema["components"]["schemas"]
    assert "ProfileResolutionPreview" in schema["components"]["schemas"]
    assert "SkillLifecycleDashboard" in schema["components"]["schemas"]
    assert "SkillLegacyRouteMapping" in schema["components"]["schemas"]
    assert "SkillLifecycleMutationResult" in schema["components"]["schemas"]
    assert "TenantSkillDiscoveryList" in schema["components"]["schemas"]
    assert "TenantSkillInstallationList" in schema["components"]["schemas"]
    assert "SkillExecutionDiagnosticList" in schema["components"]["schemas"]
    assert "SkillLifecycleAuditList" in schema["components"]["schemas"]
    assert "TestBenchDashboard" in schema["components"]["schemas"]
    assert "TestBenchMutationResult" in schema["components"]["schemas"]
    assert "TestSuiteList" in schema["components"]["schemas"]
    assert "TestSuiteDetail" in schema["components"]["schemas"]
    assert "TestRunList" in schema["components"]["schemas"]
    assert "TestRunDetail" in schema["components"]["schemas"]
    assert "PublishGateEvidenceList" in schema["components"]["schemas"]
    assert "ArtifactReferenceSummary" in schema["components"]["schemas"]
    assert "TestBenchAuditList" in schema["components"]["schemas"]
    assert "MembershipDashboard" in schema["components"]["schemas"]
    assert "MembershipMutationResult" in schema["components"]["schemas"]
    assert "MembershipAccessHistoryList" in schema["components"]["schemas"]
    assert "MembershipAuditList" in schema["components"]["schemas"]
    assert "UsageReactDashboard" in schema["components"]["schemas"]
    assert "UsageReactEventDrilldown" in schema["components"]["schemas"]
    assert "UsageReactExportSummary" in schema["components"]["schemas"]
    assert "ChannelTelegramBriefingDashboard" in schema["components"]["schemas"]
    assert "ChannelMutationResult" in schema["components"]["schemas"]
    assert "LinkTokenResult" in schema["components"]["schemas"]
    assert "DeliveryDiagnosticList" in schema["components"]["schemas"]
    assert "RunStatusSummary" in schema["components"]["schemas"]
    assert "RunInvocationResponse" in schema["components"]["schemas"]
    assert any(
        key.endswith("RunStatusResponse") for key in schema["components"]["schemas"]
    )
    assert "TimelineResponse" in schema["components"]["schemas"]
    assert "RunResultResponse" in schema["components"]["schemas"]
    assert "PromptDecisionRequest" in schema["components"]["schemas"]
    assert "PromptDecisionResponse" in schema["components"]["schemas"]
    assert "ArtifactListResponse" in schema["components"]["schemas"]
    assert "ArtifactDownloadUrlResponse" in schema["components"]["schemas"]
    assert "NotificationSubscriptionRequest" in schema["components"]["schemas"]
    assert "NotificationSubscriptionResponse" in schema["components"]["schemas"]
    assert "CallbackRegistrationRequest" in schema["components"]["schemas"]
    assert "CallbackRegistrationResponse" in schema["components"]["schemas"]
    assert "BriefingPreferenceList" in schema["components"]["schemas"]
    assert "BriefingPreferenceMutationResult" in schema["components"]["schemas"]
    assert "AdminMigrationHardeningDashboard" in schema["components"]["schemas"]
    assert "JinjaInventoryDashboard" in schema["components"]["schemas"]
    assert "MigrationRouteGroup" in schema["components"]["schemas"]
    assert "MigrationRollbackPlan" in schema["components"]["schemas"]


def test_generated_types_are_in_sync() -> None:
    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "scripts/frontend/generate_admin_react_types.py",
            "--check",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_contract_document_lists_safe_problem_responses() -> None:
    contract = Path(
        "specs/027-modern-admin-shell-and-design-system/contracts/"
        "react-admin-shell.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "ReactAdminBootstrap" in contract
    assert "ReactAdminShellChrome" in contract
    assert "ReactAdminCommandSearch" in contract
    assert "SafeProblem" in contract
    assert "/admin/app/bootstrap.json" in contract
    assert "/admin/app/search.json" in contract


def test_contract_provenance_document_lists_retired_patterns_and_metadata() -> None:
    contract = Path(
        "specs/049-react-contract-provenance-and-sample-route-retirement/contracts/"
        "react-contract-provenance.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "ReactAdminPageProvenance" in contract
    assert "ReactAdminEmptyStateMetadata" in contract
    assert "ReactAdminActionMetadata" in contract
    assert "Retired production sample route" in contract
    assert "/admin/app/patterns.json" in contract
    assert "/admin/app/patterns/actions/sample" not in contract


def test_operations_workbench_contract_document_lists_debug_and_export() -> None:
    contract = Path(
        "specs/029-operations-reliability-and-run-debug-workbench/contracts/"
        "operations-workbench.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "OperationsWorkbenchEnvelope" in contract
    assert "RunDebugEnvelope" in contract
    assert "WorkbenchExportSnapshot" in contract
    assert "/admin/app/operations.json" in contract
    assert "/admin/app/operations/runs/{workflow_run_id}.json" in contract
    assert "/admin/app/operations/export" in contract


def test_workflow_builder_contract_document_lists_builder_actions() -> None:
    contract = Path(
        "specs/030-react-workflow-builder/contracts/workflow-builder.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "WorkflowBuilderEnvelope" in contract
    assert "WorkflowReferenceCatalog" in contract
    assert "BuilderMutationResult" in contract
    assert "/admin/app/workflows/builder.json" in contract
    assert "/admin/app/workflows/lookups.json" in contract
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/save" in contract
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/validate" in contract
    assert "/admin/app/workflows/drafts/{workflow_draft_id}/publish" in contract


def test_governance_contract_document_lists_safe_actions() -> None:
    contract = Path(
        "specs/031-model-prompt-profile-and-provider-governance/contracts/"
        "governance.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "GovernanceDashboard" in contract
    assert "ProviderGovernanceSummary" in contract
    assert "SafePromptPreview" in contract
    assert "RoutingPreviewResult" in contract
    assert "/admin/app/governance/bootstrap.json" in contract
    assert "/admin/app/governance/providers/{provider_id}/probe" in contract
    assert "/admin/app/governance/prompts/{prompt_lineage_id}/preview" in contract
    assert "/admin/app/governance/routing/preview" in contract
    assert "/admin/app/governance/provenance/{run_id}.json" in contract


def test_skill_lifecycle_contract_document_lists_safe_actions() -> None:
    contract = Path(
        "specs/032-react-skill-registry-and-tool-execution-lifecycle/contracts/"
        "skill-lifecycle.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "SkillLifecycleDashboard" in contract
    assert "SkillPackageCandidate" in contract
    assert "TenantSkillInstallationSummary" in contract
    assert "SkillExecutionDiagnosticSummary" in contract
    assert "/admin/app/skills/bootstrap.json" in contract
    assert "/admin/app/skills/packages/candidates/{candidate_id}/publish" in contract
    assert "/admin/app/skills/installations/{installation_id}/credentials" in contract
    assert "/admin/app/skills/installations/{installation_id}/smoke-tests" in contract
    assert "/admin/app/skills/diagnostics.json" in contract


def test_test_bench_contract_document_lists_safe_actions() -> None:
    contract = Path(
        "specs/043-test-bench-full-react-parity-and-jinja-removal/contracts/"
        "test-bench-react-parity.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "Test Bench React Parity And Legacy Route Compatibility" in contract
    assert "/admin/app/test-bench/bootstrap.json" in contract
    assert "/admin/app/test-bench/suites/{suite_id}/runs" in contract
    assert "/admin/app/test-bench/runs/{run_id}.json" in contract
    assert "/admin/app/test-bench/gates.json" in contract
    assert "/admin/app/test-bench/artifacts/{artifact_reference_id}.json" in contract
    assert "/admin/agent-tests/ui/suites/{suite_id}" in contract
    assert "Legacy browser route redirecting to React" in contract


def test_membership_contract_document_lists_safe_actions() -> None:
    contract = Path(
        "specs/034-react-user-and-tenant-membership-administration/contracts/"
        "memberships-react.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "React Membership Administration Contracts" in contract
    assert "MembershipInvitationSaveRequest" in contract
    assert "PrincipalLinkRequest" in contract
    assert "RoleGrantSaveRequest" in contract
    assert "/admin/app/memberships/bootstrap.json" in contract
    assert "/admin/app/memberships/role-grants/{role_grant_id}/revoke" in contract
    assert "/admin/app/memberships/access-history.json" in contract


def test_usage_contract_document_lists_safe_actions() -> None:
    contract = Path(
        "specs/035-react-usage-and-cost-analytics/contracts/usage-react.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "React Usage And Cost Analytics API" in contract
    assert "UsageReactDashboard" in contract
    assert "UsageReactExportSummary" in contract
    assert "/admin/app/usage/bootstrap.json" in contract
    assert "/admin/app/usage/events.json" in contract
    assert "/admin/app/usage/exports" in contract
    assert "/admin/app/usage/exports/{usage_export_request_id}.json" in contract


def test_migration_hardening_contract_document_lists_safe_routes() -> None:
    contract = Path(
        "specs/037-react-admin-migration-hardening-and-jinja-retirement/contracts/"
        "migration-hardening-react.openapi.yaml"
    ).read_text(encoding="utf-8")

    assert "AdminMigrationHardeningDashboard" in contract
    assert "MigrationRouteGroup" in contract
    assert "MigrationRollbackPlan" in contract
    assert "/admin/app/migration/bootstrap.json" in contract
    assert "/admin/app/migration/routes.json" in contract
    assert "/admin/app/migration/rollback.json" in contract


def test_migration_hardening_surfaces_are_protected() -> None:
    for surface_key in (
        "GET:/admin/app/migration",
        "GET:/admin/app/migration/shell.json",
        "GET:/admin/app/migration/bootstrap.json",
        "GET:/admin/app/migration/routes.json",
        "GET:/admin/app/migration/rollback.json",
    ):
        assert surface_key in SURFACE_POLICIES
        assert SURFACE_POLICIES[surface_key].requested_action.startswith(
            "read_react_admin_migration"
        ) or SURFACE_POLICIES[surface_key].requested_action.startswith(
            "render_react_admin_migration"
        )
