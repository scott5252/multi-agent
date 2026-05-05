# Data Model: React Usage And Cost Analytics

## UsageReactDashboard

Represents the complete backend-owned bootstrap payload for the React usage
workspace.

**Fields**

- `scope`: active platform or tenant scope, selected tenant label, and allowed
  scope choices.
- `filters`: `UsageReactFilterMetadata` with defaults and selectable options.
- `summary_cards`: ordered `UsageReactSummaryCard` list.
- `trend`: ordered `UsageReactTrendPoint` list for the selected range.
- `rollup`: `UsageReactRollupSection` for the active grouping dimension.
- `drilldown`: `UsageReactEventDrilldown` preview for the active filters or
  selected rollup row.
- `exports`: recent `UsageReactExportSummary` entries and export action
  metadata.
- `states`: safe empty, partial, denied, stale-pricing, export-unavailable, and
  audit-unavailable state summaries.
- `updated_at`: backend timestamp used for freshness copy.

**Validation Rules**

- Tenant scope requires an active tenant id and may not include other-tenant
  labels.
- Platform scope is available only to platform administrators.
- All labels must pass unsafe-marker validation.
- Result sizes are bounded to the limits documented in `quickstart.md`.

## UsageReactFilterMetadata

Backend-owned filters and selected values.

**Fields**

- `selected_range`: start/end ISO timestamps plus display label.
- `range_options`: safe range presets, including default last 7 days.
- `selected_group_by`: active grouping dimension, including all Spec 016
  grouping values plus React graph/gateway/tool attribution dimensions.
- `group_by_options`: backend-authorized grouping choices.
- `tenant_options`: platform-only tenant choices or the active tenant choice.
- `provider_options`, `model_options`, `workflow_options`, `agent_options`,
  `prompt_options`, `confidence_options`, `availability_options`.
- `disabled_reasons`: optional field-keyed safe reasons.

**Validation Rules**

- End must be after start.
- Unsupported grouping values fail closed.
- Tenant administrators receive only their active tenant option.
- Option labels are safe display strings, not raw prompts, completions, tool
  payloads, credential internals, or unauthorized run content.

## UsageReactSummaryCard

Readable metric card for non-technical administrators.

**Fields**

- `card_id`, `label`, `value`, `unit`, `status`, `tone`.
- `comparison`: safe range or prior-period summary.
- `detail`: short backend-owned explanation.
- `audit_reference`: optional safe reference when the value is derived from an
  audited export or denial.

**Validation Rules**

- Costs use backend-owned currency formatting.
- Confidence status is one of confirmed, estimated, partial, or unavailable.
- No card contains raw ids as the primary display label.

## UsageReactTrendPoint

Daily bucket used by the trend chart and accessible fallback table.

**Fields**

- `bucket_start`, `bucket_end`, `label`.
- `confirmed_tokens`, `estimated_tokens`, `unavailable_events`.
- `estimated_cost_display`, `estimated_cost_micros`, `currency`.
- `average_latency_ms`, `event_count`, `confidence_status`.

**Validation Rules**

- Buckets are ordered ascending and bounded to the selected range.
- Missing pricing or usage values are represented as partial/unavailable
  rather than inferred in the browser.

## UsageReactRollupRow

Grouped usage summary by a backend-owned dimension.

**Fields**

- `row_id`, `group_by`, `safe_label`, `safe_summary`.
- `event_count`, `total_tokens`, `input_tokens`, `output_tokens`,
  `estimated_cost_display`, `estimated_cost_micros`, `currency`.
- `average_latency_ms`, `unavailable_event_count`, `confidence_status`.
- `attempt_summary`: safe gateway/physical-attempt retry summary when
  applicable.
- `tool_summary`: safe governed tool/connector summary when applicable.
- `drilldown_href`: route/query target for bounded event details.

**Validation Rules**

- Spec 016 dimensions such as sub-agent, execution mode, principal, and tenant
  use existing normalized usage fields.
- Graph, gateway, physical-attempt, and governed-tool rows must come from safe
  attribution fields.
- Row labels never expose raw prompt text, completion text, memory content,
  tool payloads, provider credentials, or credential reference internals.
- Response returns at most 25 rows.

## UsageReactEventRow

Bounded event-level summary for reviewer investigation.

**Fields**

- `event_id`, `recorded_at`, `tenant_label`, `provider_label`, `model_label`.
- `workflow_label`, `agent_label`, `prompt_label`, `graph_node_label`.
- `gateway_operation_label`, `physical_attempt_label`, `tool_label`.
- `total_tokens`, `input_tokens`, `output_tokens`, `estimated_cost_display`,
  `latency_ms`, `usage_status`, `cost_status`.
- `safe_attribution_summary`, `audit_reference`, `trace_reference`.

**Validation Rules**

- Event rows are capped at 100 rows.
- Tenant admins see only active-tenant rows.
- Unsafe attribution keys are redacted before rendering.
- Unauthorized run content is never dereferenced from event rows.

## UsageReactExportRequest

Request body for creating a CSV export from the active safe filters.

**Fields**

- `filters`: safe dashboard filter snapshot.
- `requested_group_by`: optional grouping context for reviewer evidence.
- `idempotency_key`: optional client-generated key for replay-safe UX.

**Validation Rules**

- Filters are validated by the backend and converted to `UsageFilters`.
- Cross-tenant exports by tenant administrators create a denied result and do
  not expose unauthorized rows.

## UsageReactExportSummary

Safe export status and artifact metadata.

**Fields**

- `usage_export_request_id`, `status`, `scope_label`, `requested_by_label`.
- `filter_snapshot`, `row_count`, `artifact_reference`, `artifact_size_label`.
- `checksum_prefix`, `created_at`, `completed_at`, `expires_at`.
- `audit_reference`, `denial_reason`, `failure_reason`, `next_step`.

**Validation Rules**

- Artifact references are logical references, not local paths.
- Denied and failed exports include safe reasons only.
- Export detail respects the same platform/tenant access scope as creation.

## UsageReactProblem

Safe problem or dependency state rendered in the workspace.

**Fields**

- `reason`: denied, empty, partial, unavailable, stale_pricing,
  export_pending, audit_unavailable, unsupported_filter, invalid_range.
- `title`, `detail`, `next_action`, `audit_reference`.

**Validation Rules**

- Problems disclose no unauthorized tenant labels or raw system internals.
- Security and tenant-scope problems use generic safe denial copy.

## State Transitions

```text
dashboard_loaded -> filters_changed -> dashboard_loaded
dashboard_loaded -> drilldown_requested -> drilldown_loaded
dashboard_loaded -> export_requested -> export_pending
export_pending -> export_completed
export_pending -> export_failed
export_requested -> export_denied
any_loaded_state -> dependency_unavailable
any_loaded_state -> authorization_denied
```

## Redaction Rules

All React usage schemas reject or redact the following markers before they can
appear in JSON evidence or UI text: raw prompt, raw completion, memory content,
private message, provider token, credential value, authorization header,
credential reference secret internals, raw tool payload, local filesystem path,
and unauthorized tenant label.
