# Research: Operations, Reliability, And Run Debug Workbench

## Source-Of-Truth Strategy

Decision: Reuse existing services and repositories as authoritative sources
for health, operations logs, reliability state, runtime runs, gateway attempts,
provider health, channel/Telegram delivery, skill diagnostics, usage, audit,
and exports.

Rationale: Specs 019 through 025 already created safe operational summaries,
redaction helpers, durable graph execution evidence, tool execution summaries,
delivery persistence, and gateway credential diagnostics. A React workbench
should adapt those summaries into page envelopes instead of creating new
storage or duplicating domain calculations.

Alternatives considered: Build new operational snapshot tables for the React
workbench. Rejected for v1 because it adds storage and reconciliation risk
without improving the user-visible triage flow.

## Access And Scope

Decision: Platform administrators and auditors may see platform-wide
workbench summaries. Tenant administrators may see only explicitly authorized
tenant-scoped summaries and run evidence.

Rationale: This follows the Spec 029 clarification defaults and the existing
operations console policy. Platform-only infrastructure data such as queue
pressure, provider health, and shared dependencies can reveal cross-tenant
state, so tenant views must be deliberately scoped.

Alternatives considered: Allow tenant admins to see global degraded cards with
labels hidden. Rejected because partial platform summaries can still leak
shared infrastructure pressure and provider status.

## Time Range And Refresh

Decision: Default to the last 60 minutes, manual full-page refresh, and safe
short polling only for health/pressure panels with aggregate redacted data.

Rationale: The default is recent enough for incident triage, bounded enough for
performance, and consistent with the roadmap clarification. Short polling is
limited to already-safe aggregate panels so raw logs and timelines remain
explicitly fetched.

Alternatives considered: Real-time streaming for all panels. Rejected for this
spec because SSE is unnecessary for the first React workbench and expands
failure modes.

## Query Bounds And Performance

Decision: Bound log and timeline queries by time range, tenant/scope, run
reference, and limit; reuse pagination/sorting patterns from Spec 028.

Rationale: Operations and audit tables can grow quickly. The workbench should
prefer top-level summaries and bounded drilldowns, not unbounded log searches.

Alternatives considered: Load all recent records client-side and filter in
React. Rejected because React must not own filtering rules and the payload
would be too large and risky.

## Redaction Model

Decision: Redact before React using existing operations redaction, audit safe
summary, model provider redaction, skill execution redaction, and channel-safe
summary helpers. React receives only safe text, categories, IDs, timestamps,
and artifact references.

Rationale: The workbench crosses high-risk domains. Browser redaction would be
too late and would duplicate backend policy.

Alternatives considered: Send raw details and hide them in collapsed sections.
Rejected because hidden browser data is still exposed.

## Run Debug Composition

Decision: Compose run debug envelopes from existing audit debugging timeline,
runtime orchestration step/lineage evidence, graph execution summaries,
gateway attempts, tool execution summaries, and channel delivery summaries.

Rationale: Operators need one run-centric story, but each underlying domain
already owns its safe evidence. The workbench should normalize presentation
and cross-links while preserving backend ownership.

Alternatives considered: Create a new run debug projection table. Rejected for
v1; deterministic aggregation over existing records is sufficient.

## Reliability Recovery

Decision: Show breaker, retry, dead-letter, compensation, quota, lease, and
replay/remediation summaries with backend-provided confirmation requirements.
Any state-affecting action remains backend-authoritative and audit-aware.

Rationale: Recovery controls can affect platform behavior. React should render
safe action metadata and confirmation prompts from contracts.

Alternatives considered: Implement replay/remediation decisions in React.
Rejected because policy, audit, and idempotency must stay server-side.

## Export Workflow

Decision: Return safe export snapshots with artifact reference ID, scope,
expiry, redaction summary, row/count metadata, and audit reference.

Rationale: This matches Spec 028 export patterns and existing operations/audit
export behavior while avoiding local filesystem paths and raw payload display.

Alternatives considered: Render export contents in the browser. Rejected
because exported evidence may be large and must be controlled by artifact
storage.

## Frontend UX

Decision: Build a dense operations workbench using summary cards, compact
trend indicators, table/filter controls, a run timeline panel, reliability
recovery panel, export panel, partial-data states, and cross-links to existing
authorized pages.

Rationale: Operations users need scan density and fast drilldown, not a
marketing-style dashboard. The UI should guide from symptom to likely cause
while preserving the shared shell and Spec 028 data/form patterns.

Alternatives considered: A large hero dashboard. Rejected because operational
triage needs compact, repeated-use information.
