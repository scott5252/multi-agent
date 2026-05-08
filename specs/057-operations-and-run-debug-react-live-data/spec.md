# Feature Specification: Operations And Run Debug React Live Data

**Feature Branch**: `codex/057-operations-and-run-debug-react-live-data`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Operations And Run Debug React Live Data. Replace deterministic operations workbench and run-debug projection data with live evidence from operations logs, audit debugging records, reliability policies/counters/breakers/dead letters, runtime orchestration runs/timeline, provider health/attempts, Telegram/channel delivery records, skill execution diagnostics, usage analytics, worker/queue state, and export metadata. React must show real health, pressure, timeline, likely causes, run debug, export, and remediation data, or honest empty states."

## Clarifications

### Session 2026-05-08

- Q: What is the source of truth for workbench health and pressure? → A: Use live OperationsConsoleService, dependency health, reliability/runtime/provider/channel/skill/usage repositories, and computed system state; persisted snapshots are optional evidence, never fallback fixture rows (autopilot).
- Q: What can tenant administrators see on the operations workbench? → A: Tenant admins see tenant-scoped run, delivery, usage, reliability, export, and safe log evidence only; platform-only database, provider, worker, queue, and storage pressure renders hidden or unavailable (autopilot).
- Q: What time range should qa057 validate? → A: Default to the last 60 minutes, seed qa057 evidence inside that window, and allow only bounded presets backed by bounded queries (autopilot).
- Q: How should direct run-debug links resolve? → A: Resolve requested run IDs from authorized runtime and audit-debug records; missing runs return not found, unauthorized runs fail closed, and no deterministic fallback run is rendered (autopilot).
- Q: How should likely causes and exports be created? → A: Derive likely causes deterministically from live symptoms and persist exports with safe storage metadata; UI artifact references must not expose storage URLs or local paths (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Operational Health (Priority: P1)

Platform operators need the operations workbench to show actual health,
capacity, dependency, reliability, provider, usage, and channel pressure for the
scope they are allowed to inspect, with clear empty or unavailable states when
no live evidence exists.

**Why this priority**: The operations workbench is a triage surface. Fixed
health cards, fake queue depth, fake provider warnings, and fake delivery
pressure can send operators toward the wrong remediation.

**Independent Test**: Load the workbench for an empty QA database and a seeded
QA database, then verify that cards, panels, likely causes, logs, and links
come from persisted live records or computed system state for the authorized
scope.

**Acceptance Scenarios**:

1. **Given** a platform operator and persisted operational evidence across
   health, reliability, runtime, provider, usage, channel, and skill surfaces,
   **When** the operator opens the workbench, **Then** the summary cards,
   pressure panels, likely causes, logs, and fallback links reflect that live
   evidence only.
2. **Given** an authorized tenant administrator and tenant-scoped operational
   evidence, **When** they open the workbench for their tenant, **Then** they
   see tenant-visible run, delivery, usage, reliability, and safe log evidence
   without platform-only database, provider, or queue details.
3. **Given** no matching operational evidence in the selected time range,
   **When** an authorized user opens the workbench, **Then** the page renders
   truthful empty or unavailable states and does not invent incidents, queue
   pressure, gateway attempts, delivery attempts, or exports.

---

### User Story 2 - Inspect Live Run Debug Evidence (Priority: P2)

Operators and tenant administrators need to inspect a run debug view that shows
the actual run timeline, branch state, gateway attempts, tool calls, delivery
attempts, lineage, replay links, and pinned bundle evidence they are authorized
to see.

**Why this priority**: A run-debug page with fake timeline events or fake
gateway attempts is dangerous because it can mask real runtime failure causes
or leak data across tenant boundaries.

**Independent Test**: Seed an authorized run with timeline, graph, gateway,
tool, delivery, and bundle evidence; request its debug projection as platform
and tenant principals; verify rows match live run evidence and cross-tenant
requests fail closed.

**Acceptance Scenarios**:

1. **Given** a persisted workflow run with timeline events, graph branch
   status, provider attempts, skill/tool calls, delivery attempts, lineage, and
   bundle evidence, **When** an authorized user opens the run debug route,
   **Then** the debug response shows those live records with safe summaries and
   bounded links.
2. **Given** a run belongs to another tenant, **When** a tenant administrator
   requests that run debug view, **Then** the request is denied or returns no
   run detail without showing the other tenant label.
3. **Given** a requested run does not exist or is outside retention, **When** an
   authorized user opens the run debug route, **Then** the response shows a
   truthful not-found or unavailable state rather than a fixed run.

---

### User Story 3 - Export Durable Operations Evidence (Priority: P3)

Authorized reviewers need to create and inspect operations workbench exports
that are backed by persisted audit/debug evidence and storage metadata instead
of fake artifact references.

**Why this priority**: Operations exports are reviewer evidence and must be
auditable, scoped, and safe before they can support incident review.

**Independent Test**: Use the browser to request a workbench export from a
seeded operations view, then verify the export request, row count or section
count, safe artifact metadata, filters, scope, and audit reference through an
API or redaction-safe QA database query.

**Acceptance Scenarios**:

1. **Given** an authorized platform operator viewing live workbench evidence,
   **When** they request an export, **Then** the system persists export evidence
   with selected filters, included sections, safe artifact metadata, requester,
   scope, status, and audit reference.
2. **Given** an authorized tenant administrator requesting a tenant-scoped
   export, **When** the export is created, **Then** the export excludes
   platform-only and other-tenant records.
3. **Given** export storage or dependencies are unavailable, **When** the user
   requests an export, **Then** the UI shows a truthful unavailable or queued
   state without returning a fake artifact id.

---

### Edge Cases

- A fresh database has tenants but no runs, audit timeline records, reliability
  records, usage events, delivery attempts, provider attempts, skill
  diagnostics, or exports.
- Platform health checks are available but a downstream dependency cannot be
  queried.
- Runtime run rows exist without timeline events or graph branch evidence.
- Timeline events exist but contain redacted or partial safe details only.
- Gateway attempts exist without credential readiness or usage attribution.
- Delivery attempts exist without private message text.
- Skill execution diagnostics exist without raw tool payloads.
- Reliability queues, retries, breakers, dead letters, and compensation records
  are empty.
- Workbench filters request unsupported time ranges, severities, subsystems, or
  tenant scopes.
- Export creation succeeds but artifact storage completion is delayed.
- Export creation is denied by tenant scope or role.
- A user follows a direct run-debug link after the run becomes unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The operations workbench MUST derive summary cards, health
  panels, pressure metrics, likely causes, logs, reliability recovery items,
  fallback links, and export summaries from live operational evidence or
  computed system state for the authorized scope.
- **FR-001a**: Persisted workbench snapshots MAY be used as evidence when they
  are live records, but the absence of a snapshot MUST NOT cause deterministic
  fixture rows to render.
- **FR-002**: The workbench MUST show truthful empty states when no matching
  live evidence exists and MUST NOT invent runs, provider attempts, delivery
  attempts, queue pressure, dead letters, logs, likely causes, or exports.
- **FR-003**: Platform operators MUST be able to see platform-scope dependency,
  queue, provider, storage, worker, usage, delivery, skill, reliability, and
  audit evidence only when their role allows platform operations access.
- **FR-004**: Tenant administrators MUST see only tenant-authorized run,
  delivery, usage, reliability, export, and safe log evidence.
- **FR-004a**: Tenant administrator views MUST hide or mark unavailable
  platform-only database, provider, worker, queue, and storage pressure details
  unless an existing policy explicitly allows safe tenant visibility.
- **FR-005**: Cross-tenant and unauthorized workbench, run-debug, and export
  requests MUST fail closed without rendering unauthorized tenant labels or
  operational details.
- **FR-006**: Workbench filters MUST support bounded time ranges, severity, and
  subsystem filtering; unsupported filters MUST return validation errors rather
  than falling back to fake rows.
- **FR-006a**: The default time range MUST be the last 60 minutes; QA seed data
  MUST create live operational evidence inside that window.
- **FR-007**: The run debug projection MUST resolve live workflow run status,
  timeline events, branch summaries, gateway attempts, tool calls, delivery
  attempts, lineage, replay links, and bundle evidence when those records
  exist.
- **FR-008**: Missing run debug evidence MUST render truthful not-found,
  unavailable, partial, or empty states rather than deterministic fallback
  events.
- **FR-008a**: Direct run-debug links MUST resolve requested run IDs from
  authorized runtime and audit-debug records; unauthorized runs MUST fail
  closed and missing runs MUST return a truthful not-found response.
- **FR-009**: Likely-cause summaries MUST be derived from live operational
  symptoms such as dependency health, reliability records, runtime failure
  categories, gateway attempt outcomes, delivery failures, usage anomalies, or
  skill diagnostics.
- **FR-009a**: Likely-cause summaries MUST be deterministic safe summaries and
  MUST NOT call a live model or inspect raw payloads during workbench rendering.
- **FR-010**: Reliability recovery panels MUST reflect live queue, retry,
  breaker, compensation, and dead-letter records or explicit empty states.
- **FR-011**: Workbench exports MUST persist requester, scope, filters, included
  sections, row or section counts, status, safe artifact metadata, and audit
  references.
- **FR-011a**: Workbench export UI references MUST be safe artifact references
  derived from persisted storage metadata and MUST NOT expose storage URLs,
  `file:` URIs, or local filesystem paths.
- **FR-012**: Export mutation results MUST reflect persisted, queued, completed,
  failed, denied, validation, conflict, or unavailable states and MUST NOT
  return fake artifact references.
- **FR-013**: Browser text, JSON responses, screenshots, logs, exports, and QA
  artifacts MUST NOT include raw secrets, credential values, provider
  authorization headers, raw prompts, raw completions, raw memory contents, raw
  run payloads, private channel messages, raw tool payloads, raw test
  transcripts, full Telegram identifiers, local filesystem paths, stack traces,
  or unauthorized tenant labels.
- **FR-014**: Auth0-shaped route tests and local-principal Playwright flows MUST
  both prove seeded live behavior, empty behavior, tenant isolation, export
  persistence, and redaction.
- **FR-015**: Required post-spec validation MUST include QA document
  validation, Spec QA, Playwright UI validation, post-UI API or database
  verification, and multi-agent curl regression before the next spec starts.

### Key Entities *(include if feature involves data)*

- **Operations Evidence Snapshot**: A safe projection of health checks,
  dependency status, queue pressure, worker state, usage throughput, provider
  state, channel delivery state, reliability state, and audit logs for a scope
  and time range.
- **Run Debug Projection**: A safe view of workflow run status, timeline,
  branch state, gateway attempts, tool calls, delivery attempts, lineage,
  replay links, and bundle evidence.
- **Likely Cause**: A derived explanation linking live symptoms to a safe
  operational category, recommended next step, and evidence reference.
- **Reliability Recovery Item**: A retry, breaker, compensation, dead-letter,
  queue, or confirmation item that may require operator review.
- **Workbench Log Summary**: A redaction-safe operational log or audit timeline
  entry with bounded details, status, subsystem, tenant scope, trace, and links.
- **Workbench Export**: A persisted export request and artifact metadata record
  for selected operational evidence.
- **Scope And Filter Context**: The authorized platform or tenant scope, time
  range, severity, subsystem, run ID, and export section selection used to
  bound queries and output.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a seeded QA database, workbench summary cards, health panels,
  logs, likely causes, reliability items, run-debug sections, and export
  summaries match persisted live evidence for the authorized scope.
- **SC-002**: In an empty QA database, the workbench and run-debug routes render
  no fake incidents, no fake gateway attempts, no fake deliveries, no fake runs,
  no fake queue depth, and no fake exports.
- **SC-003**: Cross-tenant operations, run-debug, and export attempts are
  denied or omitted without rendering forbidden tenant labels or details.
- **SC-004**: A browser-driven workbench export action creates persisted export
  and audit evidence that can be verified after the UI flow.
- **SC-005**: Redaction checks find zero raw secrets, credential values,
  provider authorization headers, raw prompts, raw completions, memory contents,
  raw run payloads, private messages, raw tool payloads, local paths, stack
  traces, or unauthorized tenant labels in JSON responses, screenshots, and QA
  artifacts.
- **SC-006**: Required automated validation passes: QA document validation, Spec
  QA, Playwright UI validation, post-UI API or database verification, and
  multi-agent curl regression.

## Testing Instructions

- Validate seeded and empty live-data behavior through Auth0-shaped route tests,
  local-principal Playwright, and post-UI API or database verification.
- Verify tenant isolation with Acme seeded data and Globex empty/cross-tenant
  requests for workbench, run-debug, and export routes.
- Run focused backend, frontend, QA document, Spec QA, Playwright, post-UI
  verifier, and multi-agent curl validation before advancing the queue.

## Documentation Impact

- Add Spec 057 QA, UI QA, user guide, and PR reviewer notes.
- Review `README.md` and `docs/quickstart.md` for operations workbench command
  or QA workflow changes, updating them only if this spec changes shared
  project-level guidance.

## PR Review Guidance

- Reviewers should confirm production workbench and run-debug routes no longer
  return deterministic QA029 rows or fake artifact references.
- Reviewers should inspect authorization, tenant-scope filtering, redaction,
  storage artifact metadata, empty-state behavior, and validation evidence.

## Assumptions

- Operations workbench data should use live service/repository projections first
  and return explicit empty or unavailable states when dependencies have no
  data.
- Platform-only dependency, queue, provider, database, and storage pressure may
  be summarized for tenant users only when an existing policy already allows
  safe tenant visibility.
- The default workbench range is the last 60 minutes unless the plan selects a
  bounded set of additional supported ranges.
- QA seed data may create safe operational records directly through services,
  repositories, migrations, or admin APIs, but production builders must not
  import test fixtures.
- Existing operations, audit debugging, reliability, runtime, provider,
  channel, skill execution, usage, and storage services are preferred sources
  of truth when they already expose authorized safe summaries.
