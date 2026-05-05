# Data Model: React Admin Migration Hardening And Jinja Retirement

## AdminMigrationHardeningDashboard

- `page_id`: stable identifier for the migration dashboard.
- `title`: safe page title.
- `description`: safe operator-facing summary.
- `scope`: current React admin scope.
- `updated_at`: deterministic timestamp in QA.
- `summary`: `MigrationHardeningSummary`.
- `route_groups`: grouped `MigrationRouteGroup` entries.
- `rollback_plan`: `MigrationRollbackPlan`.
- `performance_budget`: `MigrationPerformanceBudget`.
- `accessibility_audit`: `MigrationAccessibilityAudit`.
- `redaction_sweep`: `MigrationSweepSummary`.
- `tenant_isolation_sweep`: `MigrationSweepSummary`.
- `states`: safe migration state and warning cards.

## MigrationHardeningSummary

- `total_destinations`: total primary admin destinations reviewed.
- `react_primary_count`: routes where React is the primary destination.
- `redirect_count`: legacy routes that redirect or alias safely.
- `retained_fallback_count`: legacy routes intentionally retained.
- `retirement_candidate_count`: routes eligible for future retirement.
- `blocked_count`: routes with missing parity or evidence.
- `overall_status`: `ready`, `partial`, `blocked`, or `rollback`.
- `next_step`: safe operator guidance.

## MigrationRouteGroup

- `group_id`: stable group id.
- `label`: domain label, such as Operations or Workflow Builder.
- `spec_refs`: tuple of source specs covered by the group.
- `entries`: bounded route entries.
- `group_status`: aggregate route status.

## MigrationRouteEntry

- `entry_id`: stable route entry id.
- `admin_area`: domain or journey name.
- `legacy_route`: old direct route, when applicable.
- `react_route`: React destination, when available.
- `decision`: `react_primary`, `redirect`, `alias`, `retained_fallback`, `retirement_candidate`, or `blocked`.
- `scope_requirement`: platform, tenant-admin, tenant-user, auditor, or mixed.
- `auth_modes`: validated auth modes.
- `parity_evidence`: tuple of safe evidence references.
- `redirect_preserves`: tuple of preserved route properties, such as tenant id or filters.
- `fallback_notice`: safe message for retained fallback routes.
- `retirement_allowed`: boolean.
- `rollback_reference`: rollback evidence id.
- `audit_reference`: safe audit or trace reference.

## MigrationRollbackPlan

- `plan_id`: stable rollback plan id.
- `status`: ready, partial, or blocked.
- `feature_flag_label`: safe flag label.
- `asset_version_label`: safe asset version label.
- `steps`: ordered safe rollback steps.
- `verification_steps`: ordered checks after rollback.
- `owner_label`: support owner group.
- `last_reviewed_at`: timestamp.
- `audit_reference`: safe evidence reference.

## MigrationPerformanceBudget

- `budget_id`: stable budget id.
- `route_bootstrap_ms_limit`: numeric local QA limit.
- `primary_interactive_ms_limit`: numeric local QA limit.
- `compressed_asset_kb_limit`: numeric local QA limit.
- `measurements`: tuple of `MigrationPerformanceMeasurement`.
- `status`: ready, warning, or blocked.
- `mitigation`: safe note when a budget is exceeded.

## MigrationPerformanceMeasurement

- `measurement_id`: stable evidence id.
- `label`: journey or asset label.
- `value`: numeric measurement.
- `unit`: ms, kb, count, or percent.
- `limit`: numeric limit.
- `status`: pass, warning, or fail.
- `evidence_reference`: safe file or audit reference.

## MigrationAccessibilityAudit

- `audit_id`: stable audit id.
- `status`: pass, warning, or fail.
- `viewport_coverage`: desktop and mobile-sized viewport labels.
- `keyboard_status`: pass, warning, or fail.
- `focus_status`: pass, warning, or fail.
- `landmark_status`: pass, warning, or fail.
- `label_status`: pass, warning, or fail.
- `contrast_state_status`: pass, warning, or fail.
- `text_overlap_status`: pass, warning, or fail.
- `evidence_references`: screenshot and checklist references.

## MigrationSweepSummary

- `sweep_id`: stable sweep id.
- `status`: pass, warning, or fail.
- `checked_artifacts`: count of files or screenshots checked.
- `unsafe_match_count`: count of unsafe matches.
- `safe_summary`: safe summary for reviewers.
- `evidence_reference`: path or audit reference without local private paths.

## MigrationProblem

- `reason`: machine-readable safe reason.
- `title`: safe title.
- `detail`: safe explanation.
- `next_action`: safe remediation.
- `severity`: info, warning, or blocking.
- `audit_reference`: optional safe audit reference.

## Validation Rules

- All rendered strings are passed through the existing safe text patterns plus QA037 unsafe marker checks.
- Route entries are bounded to avoid unbounded matrices in the browser.
- Retirement is allowed only when parity, dual-auth, redaction, tenant-isolation, accessibility, performance, and rollback evidence are present.
- Tenant-admin projections exclude platform-only details except safe route labels needed to explain denied status.
- Tenant-user projections show migration status and user-safe route coverage only.
- No raw secrets, raw prompts, raw completions, raw memory, private messages, raw run payloads, raw tool payloads, full Telegram identifiers, one-time link tokens, stack traces, local filesystem paths, or unauthorized tenant labels can be rendered.
