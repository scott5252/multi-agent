# Data Model: React Agent And Workflow Test Bench

## TestBenchDashboard

- `page_id`, `title`, `description`, and active `scope`.
- `sections` for suites, cases, runs, diagnostics, artifacts, publish gates, and audit.
- `summary_cards` for suite count, running runs, failed runs, stale gates, and passing evidence.
- `gate_alerts` tied to authorized workflow targets.
- `authorized_actions` for suite creation, run launch, gate review, refresh, and export.

## TestSuiteSummary

- `suite_id`, `suite_slug`, `suite_name`.
- `tenant_id`, `tenant_label`.
- `target_type`, `target_label`, `target_revision`, `target_status`.
- `default_safe_mode`, `pass_threshold`, `required_for_publish`.
- `case_count`, `latest_run_status`, `latest_run_id`.
- `publish_gate_status`: missing, stale, running, failing, passing, unavailable.
- `suite_revision`, `archive_status`, `audit_reference_id`.
- `authorized_actions`: edit, add case, launch run, archive, restore, review gate.

## TestSuiteDetail

- Includes `TestSuiteSummary`.
- `cases`: ordered `TestCaseSummary` list.
- `target_binding`: `TargetRevisionBinding`.
- `run_launcher`: safe mode choices, idempotency metadata, and run reason choices.
- `recent_runs`: bounded `TestRunSummary` list.
- `publish_gate`: `PublishGateEvidence`.
- `audit_reference_id`.

## TestCaseSummary

- `case_id`, `case_name`, `case_status`, `case_revision`.
- `fixture_summary`: safe summary, never raw fixture JSON.
- `expected_contract_summary`: safe shape summary.
- `assertions`: ordered `AssertionDefinition` list.
- `evaluator_summary`: evaluator reference and threshold summary, never raw evaluator prompt.
- `threshold_contribution`, `order`, `audit_reference_id`.
- `authorized_actions`: edit, duplicate, archive, restore.

## AssertionDefinition

- `assertion_id`, `label`, `kind`.
- `path_summary`, `comparator`, `expected_summary`.
- `severity`, `threshold_weight`.
- `validation_status`, `field_errors`.
- Raw expected values are summarized before rendering.

## TargetRevisionBinding

- `target_type`, `target_id`, `target_label`.
- `current_revision`, `selected_revision`, `revision_status`.
- `source_links`: authorized workflow builder, governance, prompt/profile, or published workflow links.
- `stale_reason`, `remediation`.

## SafeExecutionModeOption

- `mode_id`, `label`, `side_effect_posture`.
- `model_behavior`, `tool_behavior`, `credential_behavior`.
- `allowed_status`, `policy_reason`.
- `requires_approval`, `approval_reference_id`, `audit_reference_id`.

## TestRunSummary

- `run_id`, `suite_id`, `target_revision`.
- `safe_mode`, `status`, `pass_rate`, `failure_category`.
- `started_label`, `finished_label`, `actor_label`.
- `case_total`, `case_passed`, `case_failed`.
- `usage_summary`, `latency_summary`, `audit_reference_id`.
- `authorized_actions`: open detail, cancel, rerun, view artifacts.

## TestRunDetail

- Includes `TestRunSummary`.
- `progress`: queued/running/completed status snapshot and optional refresh/SSE metadata.
- `case_results`: case-level status and diagnostics.
- `trace_steps`: bounded `TraceStepSummary` list.
- `assertion_diagnostics`: failed assertion and contract diagnostics.
- `artifacts`: `ArtifactReferenceSummary` list.
- `publish_gate`: current evidence for target revision.
- `redaction_summary`, `blocked_side_effects`, `audit_reference_id`.

## TraceStepSummary

- `step_id`, `case_id`, `step_label`, `runtime_role`.
- `status`, `latency_ms`, `token_usage`.
- `model_label`, `provider_label`, `prompt_version_label`, `profile_version_label`, `skill_version_labels`.
- `safe_transcript_excerpt`.
- `blocked_side_effects`, `gateway_decision`, `redaction_class`.
- `artifact_reference_ids`.

## ArtifactReferenceSummary

- `artifact_reference_id`, `label`.
- `content_class`, `checksum`, `size_label`.
- `retention_state`, `redaction_class`, `access_status`.
- `safe_summary`, `authorized_href`, `audit_reference_id`.
- Storage paths and raw payloads are never rendered.

## PublishGateEvidence

- `gate_id`, `target_type`, `target_label`, `target_revision`.
- `required_suite_id`, `required_suite_label`.
- `evidence_status`: missing, stale, running, failing, passing, unavailable.
- `latest_run_id`, `latest_run_revision`, `latest_run_status`.
- `reason`, `remediation`, `audit_reference_id`.
- `authorized_actions`: run suite, open run, open workflow publish flow.

## TestBenchMutationResult

- `status`: accepted, validation_error, stale_conflict, confirmation_required, queued, denied, unavailable.
- `summary`, `revision`, `toast`.
- Optional `suite`, `case`, `run`, `gate`, `artifact`, `audit_reference_id`.
- `field_errors`, `stale_conflict`, `confirmation`, `idempotency`.
- Diagnostics are safe summaries only.

## TestBenchAuditRecord

- `record_id`, `domain`, `tenant_scope_label`, `actor_label`.
- `target_label`, `timestamp_label`, `action`, `outcome`.
- `safe_diff_summary`, `redaction_class`, `audit_reference_id`.
- Authorized links only.

## State Transitions

- Suite: draft -> active -> archived -> restored.
- Case: draft -> active -> archived -> restored.
- Run: queued -> running -> passed | failed | canceled | timed_out | error.
- Gate evidence: missing -> running -> passing | failing | stale | unavailable.
- Artifact: pending -> ready -> expired | unavailable | denied.

## Validation Rules

- Tenant scope must match active principal unless platform-level access is authorized.
- Target revision must be current or explicitly marked stale.
- Run launch requires active suite, active cases, authorized target, safe mode, idempotency key, and audit readiness.
- Real dependency probe mode requires approval reference and cannot be used in local or CI QA.
- Raw prompts, completions, transcripts, fixtures, connector payloads, secrets, storage paths, stack traces, local paths, and unauthorized tenant labels are rejected by safe text validators.
