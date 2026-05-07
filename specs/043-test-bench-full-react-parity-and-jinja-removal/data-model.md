# Data Model: Test Bench Full React Parity And Jinja Removal

## TestBenchReactWorkspace

- `active_scope`: backend-selected tenant/platform scope.
- `sections`: suite, authoring, runs, diagnostics, artifacts, gates, and audit sections with readiness status.
- `legacy_route_mappings`: safe old-route mappings visible to reviewers and tests.
- `migration_summary`: React-only status, deleted template count, retained API count, and rollback note.

## TestSuiteSummary

- `suite_id`, `suite_slug`, `suite_name`: safe identifiers and label.
- `target_type`, `target_label`, `target_revision`: authorized target summary.
- `default_safe_mode`, `pass_threshold`, `required_for_publish`.
- `latest_run_status`, `publish_gate_status`, `archive_status`, `suite_revision`.
- `legacy_href`: old direct link used only in tests/reviewer evidence.

## TestSuiteDetail

- `summary`: suite-level safe summary.
- `cases`: structured case summaries and assertion descriptors.
- `run_launcher`: backend-owned safe-mode, idempotency, and target metadata.
- `target_binding`: selected target plus current/stale revision state.
- `recent_runs`, `artifacts`, `gate_evidence`, `audit_timeline`.
- `legacy_redirects`: old suite, create, edit, case, and launch URLs mapped to React.

## TestCaseEditorState

- `case_id`, `case_name`, `case_revision`.
- `fixture_summary`, `expected_contract_summary`.
- `assertions`: structured descriptors only; no raw fixture or transcript body.
- `evaluator_reference_id`, `pass_threshold`, `validation_errors`.
- `safe_return_path`: React route after successful save.

## AssertionDescriptor

- `assertion_id`, `assertion_kind`, `path_summary`.
- `comparator`, `expected_value_summary`, `severity`, `threshold_impact`.
- `validation_status`, `redaction_class`, `remediation`.

## TargetRevisionBinding

- `target_type`, `target_id`, `target_label`, `selected_revision`.
- `current_revision`, `revision_status`, `stale_reason`.
- `authorized_links`: workflow/prompt/profile destinations allowed for the current principal.

## SafeExecutionMode

- `mode_id`, `label`, `allowed_status`.
- `model_behavior`, `tool_behavior`, `side_effect_posture`.
- `requires_approval`, `policy_reason`, `approved_probe_summary`.
- `local_ci_status`: mocked, denied, or approved fixture path.

## TestRunSummary

- `run_id`, `suite_id`, `target_revision`, `safe_mode`.
- `status`, `failure_category`, `pass_rate`, `started_at_label`, `finished_at_label`.
- `actor_summary`, `audit_reference_id`, `legacy_href`.

## TestRunDetail

- `summary`: run list metadata plus terminal/progress status.
- `case_results`: pass/fail/blocked summaries.
- `trace_steps`: redacted step summaries.
- `diagnostics`: assertion, contract, evaluator, runtime, timeout, and safe-mode findings.
- `usage`, `latency`, `artifact_references`, `blocked_side_effects`.
- `redaction_status`, `audit_status`, `publish_gate_linkage`.

## TraceStepSummary

- `step_id`, `case_id`, `step_label`, `runtime_role`.
- `status`, `latency_label`, `usage_summary`.
- `model_reference`, `provider_reference`, `profile_reference`, `prompt_reference`, `skill_reference`.
- `blocked_side_effects`, `safe_excerpt_summary`, `redaction_class`.

## ArtifactReferenceSummary

- `artifact_reference_id`, `label`, `checksum`, `size_label`.
- `content_class`, `retention_state`, `access_status`, `redaction_class`.
- `authorized_href`: React metadata endpoint only.
- `audit_reference_id`.

## PublishGateEvidence

- `gate_id`, `required_suite_id`, `required_suite_label`.
- `target_type`, `target_id`, `target_revision`.
- `evidence_status`: missing, stale, running, failing, passing, audit_unavailable, redaction_unavailable.
- `latest_run_id`, `latest_run_status`, `artifact_references`.
- `workflow_links`, `remediation`, `safe_reasons`.

## LegacyRouteCompatibilityRecord

- `legacy_method`, `legacy_path`, `react_path`.
- `preserved_query_keys`: tenant id, ids, filters, saved-filter intent, breadcrumbs, conflict state.
- `compatibility_behavior`: redirect, safe_problem, or retired.
- `authorization_required`: always true for protected test bench routes.
- `deletion_evidence`: route tests, scanner test, Playwright screenshot, and QA doc references.

## State Rules

- A legacy route can redirect only after tenant scope and route ids are authorized or safely opaque.
- Unsafe destinations, cross-tenant ids, and unknown object state return safe problems without object-existence disclosure.
- Stale, copied, unauthorized, running, failing, missing, audit-unavailable, or redaction-unavailable evidence cannot satisfy publish gates.
- Artifact and trace records never contain raw prompts, completions, transcripts, connector payloads, local paths, storage paths, or stack traces.
- Template deletion is allowed only when every route that previously rendered that template has redirect or safe-problem coverage.
