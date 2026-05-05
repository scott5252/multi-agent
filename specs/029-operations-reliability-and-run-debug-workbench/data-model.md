# Data Model: Operations, Reliability, And Run Debug Workbench

## OperationsWorkbenchEnvelope

Backend-owned page envelope for `/admin/app/operations.json`.

Fields:

- `page_id`: stable identifier, `react-operations-workbench`.
- `scope`: active platform or tenant scope.
- `generated_at`: safe generation timestamp.
- `time_range`: selected safe time window.
- `summary_cards`: ordered `WorkbenchSummaryCard` collection.
- `likely_causes`: ordered `LikelyCauseSummary` collection.
- `health_panels`: ordered `HealthPressurePanel` collection.
- `run_debug`: optional `RunDebugSummary`.
- `reliability`: `ReliabilityRecoverySummary`.
- `logs`: bounded `WorkbenchLogSummary` collection.
- `filters`: backend-owned filter profile.
- `actions`: backend-owned action metadata.
- `exports`: current `WorkbenchExportSnapshot`.
- `fallback_links`: authorized cross-links to existing admin routes.
- `state`: optional common state for empty, partial, denied, or unavailable data.
- `refresh`: manual plus optional short polling hint for health panels.

Validation:

- Scope is resolved before the envelope is built.
- Tenant views cannot include platform-only summary cards.
- Every string is safe text.
- No raw payload, local path, or secret-like value is allowed.

## WorkbenchSummaryCard

Compact status card for a health, capacity, reliability, provider, channel,
tool, gateway, usage, or run signal.

Fields:

- `card_id`
- `label`
- `value`
- `status`: ready, degraded, unavailable, warning, critical.
- `severity`
- `summary`
- `freshness_label`
- `trend`
- `href`
- `evidence_reference_id`

Validation:

- `href` must point to an authorized internal route.
- `summary` must be a safe cause-oriented sentence.

## LikelyCauseSummary

Plain-language guidance from symptom to likely cause.

Fields:

- `cause_id`
- `severity`
- `affected_subsystem`
- `symptom`
- `likely_cause_category`
- `recommended_next_step`
- `href`
- `confidence_label`
- `evidence_reference_id`

Validation:

- Categories are controlled by backend enums.
- No raw logs or provider details appear in guidance.

## HealthPressurePanel

Safe aggregate panel for health, dependency, queue, database, provider,
channel, connector, and usage pressure.

Fields:

- `panel_id`
- `title`
- `status`
- `metrics`
- `dependencies`
- `freshness`
- `polling_allowed`
- `partial_reason`
- `links`

Validation:

- Only aggregate metrics are exposed to tenant scopes.
- `polling_allowed` is true only for redacted aggregate panels.

## RunDebugEnvelope

Backend-owned run-centric envelope for
`/admin/app/operations/runs/{workflow_run_id}.json`.

Fields:

- `workflow_run_id`
- `tenant_scope`
- `run_status`
- `safe_title`
- `timeline`
- `branches`
- `joins`
- `gateway_attempts`
- `tool_calls`
- `deliveries`
- `lineage`
- `replay_links`
- `bundle_summary`
- `fallback_links`
- `state`

Validation:

- The requesting principal must be authorized for the run tenant.
- Cross-tenant denials must not include run title or tenant label.
- Raw prompts, completions, memory, provider payloads, and tool payloads are forbidden.

## TimelineEventSummary

Safe run or operations timeline item.

Fields:

- `event_id`
- `occurred_at`
- `sequence`
- `category`
- `severity`
- `status`
- `summary`
- `details`
- `trace_id`
- `audit_reference_id`
- `links`

Validation:

- `details` contains safe key-value summaries only.
- Stack traces and raw exception text are forbidden.

## GraphBranchSummary

Summary of a graph branch or join state.

Fields:

- `branch_id`
- `label`
- `status`
- `node_count`
- `completed_count`
- `failed_count`
- `waiting_count`
- `join_policy`
- `join_decision`
- `manual_resolution_required`
- `summary`

Validation:

- Join decisions use controlled categories.
- Manual resolution links require authorization.

## GatewayAttemptSummary

Safe model gateway attempt metadata.

Fields:

- `attempt_id`
- `provider_label`
- `model_label`
- `status`
- `latency_ms`
- `retry_category`
- `breaker_category`
- `credential_diagnostic_category`
- `usage_reference_id`
- `safe_summary`
- `evidence_reference_id`

Validation:

- Provider authorization headers and raw provider responses are forbidden.
- Credential values never appear.

## ToolCallSummary

Safe governed skill execution metadata.

Fields:

- `tool_call_id`
- `tool_label`
- `connector_label`
- `readiness_status`
- `policy_outcome`
- `side_effect_classification`
- `result_category`
- `safe_summary`
- `evidence_reference_id`

Validation:

- Raw external tool payloads are forbidden.
- Policy denials use safe categories.

## ChannelDeliverySummary

Safe Telegram or channel delivery metadata.

Fields:

- `delivery_id`
- `channel`
- `alias_label`
- `identity_status`
- `receipt_status`
- `notification_status`
- `delivery_status`
- `failure_category`
- `safe_summary`
- `evidence_reference_id`

Validation:

- Private messages, raw Telegram updates, link tokens, and full external IDs are forbidden.

## ReliabilityRecoverySummary

Safe reliability and recovery state.

Fields:

- `breakers`
- `retries`
- `dead_letters`
- `compensations`
- `quotas`
- `leases`
- `replay_actions`
- `confirmation_requirements`
- `partial_reason`

Validation:

- State-affecting actions include backend-owned confirmation metadata.
- Tenant scopes see only authorized tenant data.

## WorkbenchLogSummary

Bounded redacted log or evidence row.

Fields:

- `log_id`
- `occurred_at`
- `source`
- `severity`
- `status`
- `subsystem`
- `tenant_scope`
- `run_reference`
- `correlation_reference`
- `summary`
- `safe_details`
- `links`

Validation:

- Rows are bounded by time range and limit.
- Raw log lines and stack traces are forbidden.

## WorkbenchExportSnapshot

Safe export status and artifact reference.

Fields:

- `export_id`
- `status`
- `summary`
- `scope`
- `artifact_reference_id`
- `redaction_summary`
- `expires_at`
- `row_count`
- `audit_reference_id`

Validation:

- No local filesystem path is exposed.
- Raw exported content is not embedded in the React response.

## State Transitions

Workbench export:

1. Requested.
2. Accepted or denied.
3. Generating.
4. Complete with artifact reference.
5. Failed with safe reason category.
6. Expired.

Replay/remediation action:

1. Previewed.
2. Confirmation required.
3. Confirmed.
4. Accepted, denied, replayed, or dependency unavailable.
5. Audit reference returned.
