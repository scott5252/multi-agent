# Feature Specification: Usage React Live Data

**Feature Branch**: `codex/056-usage-react-live-data`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Usage React Live Data. Replace the in-code React usage fixture events with live data from llm_usage_events, pricing versions, usage rollups, usage export requests, reconciliation records, runtime run/step attribution, provider gateway attempts, skill execution summaries, and workflow/prompt/profile metadata. React must show real totals, trend points, rollups, drilldowns, confidence states, cost estimates, attribution, and export requests. Empty states must be truthful when no usage has been recorded."

## Clarifications

### Session 2026-05-08

- Q: Should usage rollups require persisted rollup rows before the dashboard can show totals? → A: Compute from live usage events on read, using persisted rollups only as optional acceleration when they are present (autopilot).
- Q: How should missing pricing be displayed? → A: Show missing, estimated, or reconciliation-pending confidence states and never fabricate costs (autopilot).
- Q: How should workflow, run, step, prompt, profile, provider, model, and skill attribution be resolved? → A: Use safe attribution stored on usage events first, then authorized live metadata lookups; missing references render unavailable safe labels (autopilot).
- Q: What are the export status semantics? → A: Usage export actions persist export request rows with queued, completed, failed, denied, validation, or unavailable states; artifact references appear only when backed by storage metadata (autopilot).
- Q: What default date range and QA seed behavior should validation use? → A: Default to a last-30-days window; qa056 seeds Acme usage inside that window and leaves Globex empty for isolation checks (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Usage Totals (Priority: P1)

Platform operators and tenant administrators need the usage workspace to show
actual recorded token and cost activity for the scope they are allowed to
inspect, with clear empty states when no usage exists.

**Why this priority**: The existing usage page is misleading if it looks
populated from fixed events. The primary value is making totals, trends,
rollups, and cost estimates reflect durable usage records.

**Independent Test**: Load the usage dashboard for an empty scope and a seeded
scope, then verify that the seeded scope matches persisted usage records while
the empty scope reports no live usage.

**Acceptance Scenarios**:

1. **Given** an authorized platform operator and multiple tenants with recorded
   usage in the default last-30-days window, **When** the operator opens the
   usage workspace, **Then** the dashboard shows aggregate totals, trends,
   rollups, confidence states, and cost estimates derived from live usage
   records only.
2. **Given** a tenant administrator and usage records for their tenant, **When**
   they open the usage workspace for that tenant, **Then** they see only their
   tenant's totals, trends, rollups, drilldowns, and export history.
3. **Given** an authorized tenant with no usage records, **When** the user
   opens the usage workspace, **Then** the page shows a truthful empty state and
   does not invent events, costs, models, workflows, or exports.

---

### User Story 2 - Inspect Redaction-Safe Attribution And Drilldowns (Priority: P2)

Operators and tenant administrators need to understand which providers, models,
workflows, prompt versions, runtime profiles, runs, steps, agents, and skill
activities contributed to usage without exposing raw prompts, completions,
memory content, private payloads, or unauthorized run data.

**Why this priority**: Live totals are not enough for operational review.
Reviewers must be able to explain usage changes and confidence levels safely.

**Independent Test**: Seed usage records with provider, workflow, prompt,
profile, run, step, and skill attribution, then assert JSON responses,
browser text, screenshots, and exports include only safe identifiers, labels,
counts, estimates, and references.

**Acceptance Scenarios**:

1. **Given** usage events linked to runs, steps, providers, models, prompts,
   profiles, workflows, and skill execution summaries, **When** an authorized
   user opens a drilldown, **Then** the details show redaction-safe attribution,
   token counts, latency, pricing confidence, and audit references.
2. **Given** usage records with missing or estimated pricing, **When** the
   dashboard renders rollups and trends, **Then** the confidence state clearly
   distinguishes confirmed, estimated, missing, and reconciliation-pending
   values without inventing cost amounts.
3. **Given** a tenant user tries to inspect another tenant's usage, **When** the
   request is evaluated, **Then** the response denies or omits the forbidden
   rows without rendering unauthorized tenant labels or run details.

---

### User Story 3 - Create Durable Usage Exports (Priority: P3)

Authorized reviewers need to request exports from the usage workspace and see
persisted export request evidence rather than a fake artifact id or browser-only
success message.

**Why this priority**: Exports are a mutation surface and must create durable,
auditable evidence before the spec can be considered live-data complete.

**Independent Test**: Use the browser to request a usage export from a seeded
scope, then verify the export request, safe artifact metadata, filters, row
count, and audit evidence through an API or redaction-safe QA database query.

**Acceptance Scenarios**:

1. **Given** an authorized platform operator viewing usage, **When** they
   request an export, **Then** the system persists an export request with the
   selected filters, safe artifact metadata, row count or queued status, and an
   audit reference.
2. **Given** an authorized tenant administrator viewing tenant usage, **When**
   they request an export, **Then** the export is scoped to their tenant and
   excludes rows from other tenants.
3. **Given** an export cannot be created because the dependency is unavailable,
   **When** the user submits the request, **Then** the UI shows a truthful
   unavailable state with no fake artifact reference.

---

### Edge Cases

- A fresh database has tenants but no usage events, pricing rows, rollups, or
  export requests.
- Usage events exist with no matching pricing version.
- Pricing exists but is estimated or superseded.
- Usage events reference workflow runs or steps that the current principal
  cannot inspect.
- Provider gateway attempt metadata is partial or unavailable.
- Skill execution usage attribution is missing a safe display label.
- Reconciliation records mark totals as adjusted or pending.
- Export creation succeeds but artifact storage has not completed yet.
- Export creation is denied by tenant scope or role.
- Trend buckets span days with zero usage between active days.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The usage workspace MUST derive dashboard totals, token counts,
  cost estimates, trends, rollups, and drilldowns from live usage records and
  related durable usage evidence for the authorized scope.
- **FR-001a**: Usage rollups MUST be computed from live usage events on read
  unless a matching persisted rollup is available as an acceleration path; the
  absence of a persisted rollup row MUST NOT cause fake or missing dashboard
  totals when matching usage events exist.
- **FR-002**: The usage workspace MUST show a truthful empty state when the
  authorized scope has no usage records, pricing data, rollups, or exports.
- **FR-003**: Platform operators MUST be able to review cross-tenant usage only
  when their role allows platform scope.
- **FR-004**: Tenant administrators MUST be able to review usage only for their
  tenant.
- **FR-005**: The system MUST fail closed for cross-tenant, unauthorized, or
  malformed usage filters.
- **FR-006**: Usage rollups MUST support provider, model, workflow, principal,
  agent, execution mode, and day-level grouping when matching live data exists.
- **FR-007**: Trend points MUST represent actual usage buckets and MUST include
  zero-activity buckets only as computed empty intervals, not invented events.
- **FR-008**: Drilldowns MUST include redaction-safe attribution for provider,
  model, workflow, prompt, profile, run, step, agent, sub-agent, skill
  execution, pricing, and audit evidence when those references are available.
- **FR-009**: Drilldowns, dashboard cards, browser text, screenshots, exports,
  and QA artifacts MUST NOT include raw prompts, raw completions, memory
  contents, raw run payloads, raw tool payloads, secrets, credential values,
  provider authorization headers, local filesystem paths, stack traces, or
  unauthorized tenant labels.
- **FR-010**: Cost estimate displays MUST distinguish confirmed pricing,
  estimated pricing, missing pricing, and reconciliation-pending states.
- **FR-010a**: Missing pricing MUST render explicit missing or unavailable
  confidence states and MUST NOT fabricate costs.
- **FR-011**: Usage export requests MUST be persisted with filters, requester,
  scope, row count or queued state, safe artifact metadata, and audit evidence.
- **FR-012**: Export mutation results MUST reflect persisted, denied, conflict,
  validation, queued, completed, or unavailable states; they MUST NOT return
  fake artifact ids.
- **FR-012a**: Export artifact references MUST appear only when backed by
  persisted storage metadata.
- **FR-013**: Existing usage API behavior SHOULD be reused where it already
  provides authorized, redaction-safe live data.
- **FR-014**: The usage workspace MUST expose enough source metadata for QA to
  prove whether data came from live usage records, computed empty state, or
  unavailable dependencies.
- **FR-014a**: The default dashboard window MUST cover the last 30 days unless
  the user selects a different authorized date range.
- **FR-015**: Automated validation MUST exercise empty live data, seeded live
  data, Auth0-shaped principal behavior, local-principal browser behavior, a
  persisted export action, post-UI persistence verification, and curl
  regression.

### Key Entities *(include if feature involves data)*

- **Usage Event**: A normalized usage record for model or tool-related activity,
  including safe scope, attribution, token, latency, pricing, and confidence
  fields.
- **Pricing Version**: Versioned pricing metadata used to calculate or qualify
  usage cost estimates.
- **Usage Rollup**: Aggregated usage values for a time bucket or grouping, with
  confidence and reconciliation metadata; generated from live events on read or
  read from a matching persisted acceleration row.
- **Usage Drilldown**: A scoped list of usage events and safe attribution
  details behind a dashboard card, trend point, or rollup row.
- **Usage Export Request**: A durable request for exportable usage evidence,
  including filters, requester, scope, artifact metadata, row count, status, and
  audit reference.
- **Reconciliation Record**: Evidence that usage totals or costs were adjusted,
  confirmed, estimated, or left pending.
- **Attribution Reference**: Safe labels or identifiers for run, step, workflow,
  provider, model, prompt, profile, agent, sub-agent, and skill execution
  context, resolved from usage event fields first and authorized live metadata
  second.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a seeded QA database, dashboard totals, rollups, trend points,
  drilldown rows, and export history match the persisted usage evidence for the
  authorized scope and default last-30-days window.
- **SC-002**: In an empty QA database, the usage workspace renders no usage
  events, no fake costs, no fake workflows, no fake providers, and no fake
  exports.
- **SC-003**: Cross-tenant usage access attempts are denied or omitted without
  rendering forbidden tenant labels or run details.
- **SC-004**: A browser-driven usage export action creates persisted export and
  audit evidence that can be verified after the UI flow.
- **SC-005**: Redaction checks find zero raw prompts, completions, secrets,
  credential values, raw run payloads, raw tool payloads, local paths, stack
  traces, or unauthorized tenant labels in JSON responses, screenshots, and QA
  artifacts.
- **SC-006**: Required automated validation passes: QA document validation,
  Spec QA, Playwright UI validation, post-UI API or database verification, and
  multi-agent curl regression.

## Assumptions

- Existing usage analytics tables and services from the token usage and cost
  analytics feature are the source of truth for usage events, pricing, rollups,
  reconciliation, and exports.
- Existing authorization rules define platform and tenant usage visibility.
- Missing pricing is displayed as estimated, unavailable, or pending rather
  than blocking the whole dashboard.
- Persisted rollup rows are optional acceleration evidence; usage events remain
  the correctness source when rollups are missing.
- QA056 seeds Acme usage, pricing, attribution, and export rows in the default
  date window and leaves Globex empty unless a test explicitly creates Globex
  usage.
- QA may seed usage and pricing rows in the qa056 database, but production
  routes must only render those rows because they are persisted.
- Test-only fixtures may remain in test directories and frontend test data, but
  production usage routes and projection services cannot import or mirror them.
- Export creation is the required visible persisted browser action for qa056
  unless implementation discovers a safer existing usage mutation.
