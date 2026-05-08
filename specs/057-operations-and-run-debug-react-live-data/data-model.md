# Data Model: Operations And Run Debug React Live Data

## Operations Evidence Snapshot

Represents the workbench page projection for a principal, scope, and bounded
time range.

**Fields**

- `scope_type`: platform or tenant.
- `tenant_id`: present for tenant scopes.
- `range_start`, `range_end`: bounded query window.
- `summary_cards`: live health, pressure, provider, usage, delivery, and
  reliability cards.
- `health_panels`: dependency, capacity, worker, storage, and tenant activity
  panels.
- `likely_causes`: deterministic safe cause summaries derived from live
  symptoms.
- `logs`: bounded safe operational log summaries.
- `reliability`: retry, breaker, compensation, dead-letter, and confirmation
  summaries.
- `exports`: recent persisted workbench export summaries.
- `states`: empty, partial, denied, unavailable, and validation states.

**Validation rules**

- Tenant scopes cannot include platform-only database, worker, provider fleet,
  storage pressure, or other-tenant labels.
- Lists must be bounded by contract-defined limits.
- Empty evidence must render empty states, not synthetic rows.

## Run Debug Projection

Represents a direct run-debug view for one requested workflow run.

**Fields**

- `workflow_run_id`
- `tenant_scope`
- `run_status`
- `safe_title`
- `timeline`
- `branches`
- `gateway_attempts`
- `tool_calls`
- `deliveries`
- `lineage`
- `replay_links`
- `bundle_summary`
- `states`

**Validation rules**

- The requested run ID must resolve from authorized runtime/audit-debug records.
- Missing runs return not found or unavailable state.
- Unauthorized runs fail closed.
- Timeline, gateway, tool, delivery, and bundle details must be safe summaries.

## Workbench Log Summary

Represents a single safe operational log or audit-debug event.

**Fields**

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

**Validation rules**

- `safe_details` cannot include raw payloads, stack traces, prompts,
  completions, secrets, credentials, private messages, or local paths.
- Tenant users see only logs authorized for their tenant.

## Likely Cause

Represents deterministic triage guidance from live symptoms.

**Fields**

- `cause_id`
- `severity`
- `affected_subsystem`
- `symptom`
- `likely_cause_category`
- `recommended_next_step`
- `href`
- `evidence_reference_id`

**Validation rules**

- Must be derived from live safe evidence categories.
- Must not call a live model during rendering.
- Must not expose raw payload content.

## Reliability Recovery Item

Represents a retry, breaker, queue, compensation, dead-letter, or confirmation
item surfaced in the workbench.

**Fields**

- `item_id`
- `label`
- `status`
- `severity`
- `summary`
- `href`
- `confirmation`

**Validation rules**

- Empty reliability tables render empty states.
- Tenant scopes omit platform-only remediation links.

## Workbench Export

Represents a persisted workbench export request and safe artifact metadata.

**Fields**

- `export_id`
- `status`
- `summary`
- `artifact_reference_id`
- `progress_label`
- `audit_reference_id`
- `scope_label`
- `redaction_summary`
- `row_count`
- `filters`
- `included_sections`
- `created_at`
- `completed_at`

**Validation rules**

- Artifact references appear only when backed by persisted storage metadata.
- Browser/API output cannot expose `file:` URIs, storage URLs, or local paths.
- Tenant exports cannot include other-tenant or platform-only evidence.

## Scope And Filter Context

Represents the authorized query context.

**Fields**

- `principal_id`
- `scope_type`
- `tenant_id`
- `range_preset`
- `severity`
- `subsystem`
- `workflow_run_id`
- `include_run_debug`
- `include_reliability`
- `include_logs`
- `include_exports`

**Validation rules**

- Unsupported range, severity, subsystem, or section selections return
  validation errors.
- Cross-tenant filters fail closed.
- Default range is last 60 minutes.
