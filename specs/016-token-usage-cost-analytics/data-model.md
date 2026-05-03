# Data Model: Token Usage And Cost Analytics

## LlmUsageEvent

Authoritative normalized record for one ModelGateway invocation.

**Fields**:

- `llm_usage_event_id` UUID primary key.
- `tenant_id` UUID, required for production runtime usage.
- `principal_id` string nullable for system-initiated usage.
- `workflow_run_id`, `workflow_run_step_id`, `workflow_lineage_id`,
  `workflow_version_id` UUID nullable attribution.
- `agent_key` string nullable.
- `sub_agent_key` string nullable.
- `provider_key` string required.
- `provider_connection_id` UUID nullable.
- `model_id` string required.
- `prompt_version_id` UUID nullable.
- `agent_profile_version_id` UUID nullable.
- `execution_mode` string required, such as `production`, `test`,
  `validation`, `probe`, or `admin`.
- `operation_identity` string nullable.
- `idempotency_key` string nullable.
- `trace_id` string nullable.
- `input_tokens`, `output_tokens`, `cached_tokens`, `reasoning_tokens`,
  `total_tokens`, `provider_billable_units` integer nullable.
- `input_status`, `output_status`, `cached_status`, `reasoning_status`,
  `total_status`, `billable_status`, `cost_status` enum values:
  `confirmed`, `estimated`, `unavailable`, `not_applicable`.
- `latency_ms` integer.
- `currency` string.
- `estimated_cost_micros` integer nullable.
- `pricing_version_id` UUID nullable.
- `usage_status` enum `estimated`, `confirmed`, `partial`, `unavailable`,
  `malformed`.
- `source_gateway_attempt_id` UUID nullable.
- `safe_attribution` JSON object containing only safe identifiers and compact
  non-content metadata.
- `recorded_at`, `created_at`, `updated_at` timestamps.

**Validation rules**:

- Token and billable-unit values must be non-negative when present.
- `tenant_id`, `provider_key`, `model_id`, `execution_mode`, `latency_ms`, and
  `usage_status` are required.
- Raw prompt, completion, secret, memory, provider credential, and run content
  fields are not allowed in `safe_attribution`.
- Idempotency uses `(tenant_id, idempotency_key, provider_key, model_id)` when
  an idempotency key is present.

## LlmPricingVersion

Immutable provider/model pricing metadata used to estimate costs.

**Fields**:

- `llm_pricing_version_id` UUID primary key.
- `provider_key`, `model_id`, `currency`.
- `input_token_micros`, `output_token_micros`, `cached_token_micros`,
  `reasoning_token_micros` integer nullable prices per token.
- `billable_unit_micros` integer nullable.
- `calculation_method` string.
- `effective_from`, `effective_to` timestamps.
- `source_note` safe string.
- `created_by_principal_id`, `created_at`.

**Validation rules**:

- Prices must be non-negative when present.
- Effective ranges for the same provider/model/currency must not overlap.
- Existing versions used by usage events are never mutated.

## LlmUsageRollup

Future materialized aggregate row for a time bucket and dimension set.

**Fields**:

- `llm_usage_rollup_id` UUID primary key.
- `tenant_id`, `bucket_start`, `bucket_end`, `bucket_granularity`.
- Optional dimension fields for provider, model, workflow, agent, sub-agent,
  prompt version, execution mode, and principal.
- Aggregated token, billable-unit, cost, event-count, estimated-count, and
  confirmed-count values.
- `computed_at` timestamp.

**Validation rules**:

- Bucket end must be after bucket start.
- Rollup rows are derived from event rows and never store raw content.

## UsageExportRequest

Audited CSV export request and artifact metadata.

**Fields**:

- `usage_export_request_id` UUID primary key.
- `tenant_id` UUID nullable for platform-scope exports.
- `requested_by_principal_id` string.
- `scope_type` enum `platform` or `tenant`.
- `filters` JSON safe filter snapshot.
- `status` enum `pending`, `completed`, `failed`, `denied`.
- `row_count` integer.
- `artifact_uri`, `artifact_sha256`, `artifact_size_bytes` nullable.
- `denial_reason`, `failure_reason` safe strings nullable.
- `created_at`, `completed_at`, `expires_at`.

**Validation rules**:

- Tenant-scope exports must include `tenant_id`.
- Denied exports must not have artifact metadata.
- Filters must be safe identifiers and scalar values only.

## UsageReconciliationRecord

Audit link for late confirmed usage updates.

**Fields**:

- `usage_reconciliation_record_id` UUID primary key.
- `llm_usage_event_id` UUID.
- `source` string.
- `previous_values` JSON safe numeric/status snapshot.
- `confirmed_values` JSON safe numeric/status snapshot.
- `reconciled_by_principal_id` string nullable for automated updates.
- `created_at`.

**Validation rules**:

- Only numeric usage, status, pricing, and safe attribution values can appear.
- Reconciliation cannot introduce raw content fields.

## Tenant Boundaries

- Platform admins can query all tenants when using platform scope.
- Tenant admins can query only their own tenant.
- Future tenant users can query only their own `principal_id`.
- Every repository method accepts an explicit access scope and applies tenant
  filters before returning rows or export metadata.
