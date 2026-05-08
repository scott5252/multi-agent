# Data Model: Usage React Live Data

## Existing Persistent Entities

### LlmUsageEvent

- Durable normalized usage record for model or governed tool activity.
- Key fields: tenant, principal, provider, model, workflow/run/step, prompt,
  profile, agent/sub-agent, operation, trace, token counts, billable units,
  latency, usage status, cost status, pricing version, estimated cost, and safe
  attribution.
- React usage surfaces read this entity through `UsageRepository` and
  `UsageAnalyticsService`.

### LlmPricingVersion

- Versioned pricing metadata used for cost estimation.
- React displays confidence based on pricing/cost status and must not fabricate
  missing costs.

### UsageRollup

- Aggregated usage by bucket or grouping.
- For Spec 056, live event computation is the correctness path. Persisted
  rollups are optional acceleration and must not be required for truthful
  totals.

### UsageExportRequest

- Durable export request row with scope, requester, filters, status, row count,
  artifact URI, checksum, size, denial/failure reason, and timestamps.
- React export results and export detail routes must mirror persisted state.

### UsageReconciliationRecord

- Evidence that a usage event was adjusted, confirmed, or reconciled.
- React may surface safe reconciliation status/counts but must never expose raw
  payloads.

### Attribution Reference

- Safe reference values for tenant, provider, model, workflow lineage/version,
  workflow run/step, prompt version, runtime profile, agent, sub-agent, gateway
  attempt, governed tool, audit, and trace context.
- Resolution order: safe usage event fields, sanitized safe attribution, then
  authorized bounded metadata lookup if needed.

## React Projection Entities

### UsageReactDashboard

- Scope and allowed scope options.
- Filter metadata for range, group by, tenant, provider, model, and confidence.
- Summary cards for tokens, cost, event count, latency, unavailable usage, and
  confidence coverage.
- Trend points for the selected range, including zero-activity buckets.
- Rollup rows for the selected group.
- Initial drilldown rows capped to the contract limit.
- Recent persisted export summaries.
- Common empty/partial/denied/unavailable states.

### UsageReactEventDrilldown

- Bounded rows of redaction-safe usage events.
- Each row includes safe labels, token counts, latency, cost display,
  confidence states, audit/trace references, and safe attribution summary.

### UsageReactExportSummary

- Persisted export request id and status.
- Scope label and requester label.
- Filter snapshot.
- Row count and safe artifact metadata only when persisted.
- Audit reference plus denial or failure reason when applicable.

## State Transitions

### Dashboard Load

1. Resolve active React scope and principal.
2. Convert query params into `UsageFilters` with default last-30-days range.
3. Build `UsageAccessScope` from principal roles and active tenant.
4. Query live usage events through `UsageAnalyticsService`.
5. Compute totals, trends, rollups, drilldowns, and states.
6. List recent export requests for the same authorized scope.

### Export Creation

1. Validate request filters and requested group.
2. Convert React scope/query into `UsageAccessScope` and `UsageFilters`.
3. Persist a pending export request.
4. Write CSV through configured storage.
5. Mark the request completed with row count, URI, checksum, and size; or mark
   denied/failed/unavailable without fake artifact references.
6. Return a `UsageReactExportSummary` backed by the persisted row.

## Validation Rules

- Tenant-scope principals cannot request another tenant's events or exports.
- Platform scope requires platform admin authorization.
- Date ranges must have `end > start`; default range is last 30 days.
- Group-by values outside the usage service contract are rejected or mapped to a
  supported safe grouping.
- Artifact references require persisted export metadata.
- Safe usage text validation blocks raw prompts, completions, credentials,
  authorization headers, memory, raw tool payloads, local paths, stack traces,
  and unauthorized tenant labels.
