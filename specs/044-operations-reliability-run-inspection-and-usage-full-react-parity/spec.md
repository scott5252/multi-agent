# Feature Specification: Operations, Reliability, Run Inspection, And Usage Full React Parity

**Feature Branch**: `codex/044-operations-reliability-run-inspection-and-usage-full-react-parity`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Operations, Reliability, Run Inspection, and Usage Full React Parity. Specs 029 and 035 added React workspaces, but full Jinja removal requires parity for operations console, reliability index, breakers, dead letters, recovery actions, run search, run detail, timeline, replay, lineage, bundle snapshots, usage dashboard, usage export detail, filters, CSV export metadata, and direct links from incidents and QA docs."

## Clarifications

### Session 2026-05-06

- Q: Which surface owns operations triage after old templates are removed? A: React operations owns the primary triage surface at `/admin/app/operations`; old operations, reliability, run inspection, and usage browser URLs redirect there or to React usage/run detail routes when safe. (autopilot)
- Q: Which reliability actions are available in React? A: React exposes backend-approved retry, breaker, dead-letter, recovery, export, and acknowledgement actions only when the existing policy service marks them safe for the active principal and tenant. (autopilot)
- Q: How should run replay and lineage direct links behave? A: Old admin run replay, lineage, and detail URLs redirect to React operations run-debug panels with run id, tenant scope, filters, and safe breadcrumb intent preserved when authorized; user-facing `/runs` links redirect to React channel run status surfaces where authorized. (autopilot)
- Q: How much timeline data can React fetch? A: Timeline, logs, run events, usage events, and dead-letter lists remain bounded by backend page-size and time-window limits; React cannot request unbounded exports or raw payloads. (autopilot)
- Q: How should usage export detail routes work? A: Usage export pages redirect to React usage export detail routes and expose only safe artifact references, request metadata, filters, checksums, row counts, and audit ids. (autopilot)
- Q: How should operations-auditor and tenant-admin visibility differ? A: Platform operators can see platform-wide operational summaries; tenant admins and auditors see tenant-scoped summaries with unauthorized labels omitted, and denied routes fail closed. (autopilot)
- Q: What should old browser routes do when safe redirect context cannot be proven? A: Return a non-Jinja safe problem or documented retirement response without revealing whether protected operational data exists. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Triage Operations In React (Priority: P1)

Platform operators and authorized tenant administrators can use the React operations workspace to review health, queues, reliability posture, provider/gateway status, channel delivery, run inspection shortcuts, exports, and incident context without opening the old operations console template.

**Why this priority**: The operations console is the central incident triage surface. Jinja removal is safe only when React covers the same summary, drilldown, filter, export, and denial states.

**Independent Test**: Sign in as `platform-admin`, open `/admin/app/operations`, verify operational summary cards, reliability panels, run-debug links, export metadata, and safe actions; then open `/admin/operations` and confirm it redirects to the React route without leaking raw logs or stack traces.

**Acceptance Scenarios**:

1. **Given** an authorized platform operator, **When** they open the React operations workspace, **Then** they see bounded health, queue, reliability, provider, Telegram/channel, usage, audit, and run-debug summaries.
2. **Given** a tenant-scoped operator, **When** they open the same workspace with a tenant id, **Then** the backend scopes all summaries and omits unauthorized platform-only data.
3. **Given** an old operations URL with filters, **When** the user is authorized, **Then** the route redirects to React with safe filters, tenant id, and destination intent preserved.
4. **Given** an unauthorized user, **When** they follow an old operations URL, **Then** the response fails closed without raw logs, stack traces, tenant labels, or incident details.

---

### User Story 2 - Govern Reliability Actions In React (Priority: P1)

Platform operators can inspect reliability policies, queue pressure, circuit breakers, retry schedules, compensation records, dead letters, and safe recovery actions in React while old reliability URLs redirect or return safe non-Jinja problems.

**Why this priority**: Reliability actions can alter durable runtime state. They must stay backend-owned and authorization-checked before removing the old reliability templates.

**Independent Test**: Open React operations reliability panels as `platform-admin`, inspect breaker and dead-letter details, trigger an allowed safe action, verify audit and mutation summaries, and prove old `/admin/reliability/ui...` URLs redirect safely.

**Acceptance Scenarios**:

1. **Given** breaker and quota summaries exist, **When** a platform operator views reliability, **Then** React shows bounded breaker, retry, quota, lease, and queue summaries with reasons and remediation.
2. **Given** a dead-letter record is recoverable, **When** the operator invokes a backend-approved action, **Then** the mutation result shows accepted, denied, or queued state with audit reference and no raw payload echo.
3. **Given** an old reliability breaker or dead-letter URL, **When** it can safely map to React, **Then** the redirect preserves active tab, tenant id, filters, and object id.
4. **Given** a tenant admin follows a platform-only reliability action URL, **When** authorization fails, **Then** the system returns a safe denial without revealing platform-only incident details.

---

### User Story 3 - Inspect Runs, Replay, And Lineage In React (Priority: P1)

Operators can search runs, open run details, inspect timelines, replay references, lineage, bundle snapshots, usage, artifacts, and audit evidence through React operations run-debug views.

**Why this priority**: Run inspection surfaces are high-sensitivity because they can include prompts, completions, memory, private messages, tool payloads, and workflow state.

**Independent Test**: Open old `/admin/runs`, `/admin/runs/{run_id}`, replay URLs, and user-facing `/runs` links, verify redirects to React operations or channel run panels, and confirm the React payload contains safe summaries, artifact references, and redacted timeline events only.

**Acceptance Scenarios**:

1. **Given** a run search query, **When** the user opens React operations run inspection, **Then** results are bounded, tenant-scoped, filterable, and linked to authorized run detail panels.
2. **Given** a run detail exists, **When** the user opens it through an admin or user-facing direct link, **Then** React displays status, timeline, lineage, replay references, bundle snapshots, usage, artifact references, approvals, and audit summaries without raw sensitive payloads.
3. **Given** replay or lineage evidence is unavailable, **When** the panel renders, **Then** unavailable state blocks unsafe replay and provides remediation without exposing hidden data.
4. **Given** a cross-tenant run id is requested, **When** authorization cannot be proven, **Then** the response hides whether the run exists.

---

### User Story 4 - Review Usage And Exports In React (Priority: P2)

Platform and tenant users can use React usage analytics to review cost trends, event drilldown, pricing metadata, export requests, export detail, CSV artifact metadata, and old usage direct links without Jinja templates.

**Why this priority**: Usage analytics are already React-backed, but old usage template pages and export detail links must be retired only after React covers export detail, filters, and tenant-specific denial behavior.

**Independent Test**: Open `/admin/app/usage`, create an export, open the export detail in React, verify safe artifact metadata, then open old `/admin/usage` and `/admin/usage/exports/{id}` links and confirm safe redirects.

**Acceptance Scenarios**:

1. **Given** usage events exist, **When** a user opens React usage analytics, **Then** trends, provider/model breakdowns, event drilldown, filters, pricing metadata, and estimates are backend-owned and bounded.
2. **Given** an export is requested, **When** export detail is opened, **Then** React shows status, filters, row count, checksum, artifact reference, audit id, and retention state without raw CSV rows.
3. **Given** an old usage URL includes tenant and filter query parameters, **When** authorization passes, **Then** the route redirects to React with safe filters preserved.
4. **Given** export evidence belongs to another tenant, **When** a user opens the link, **Then** the response fails closed without revealing export existence or artifact metadata.

### Edge Cases

- Old URLs include unsafe redirect destinations, unknown tabs, unbounded page sizes, invalid UUIDs, stale filters, or unsupported saved-filter state.
- Reliability action requests are repeated, stale, already processed, disabled by policy, cross-tenant, or missing an idempotency key.
- Run timeline, lineage, replay, bundle snapshot, artifact, or usage evidence is unavailable, redaction-blocked, retention-blocked, or audit-unavailable.
- Operations summaries include degraded provider, Telegram, queue, breaker, or worker health and must render safe remediation without stack traces.
- Usage export generation is pending, failed, expired, denied, or redaction-blocked.
- Tenant admins and auditors follow platform-only operations, reliability, or dead-letter links.
- JavaScript fails to load after the Jinja templates are removed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide React coverage for operations console, reliability index, breakers, dead letters, recovery actions, run search, run detail, timeline, replay, lineage, bundle snapshots, usage dashboard, usage events, usage export creation, and usage export detail.
- **FR-002**: System MUST keep backend-owned JSON APIs as the only source of authorization, tenant scoping, operational classification, reliability action eligibility, run redaction, export readiness, and audit status.
- **FR-003**: System MUST preserve old operations, reliability, admin run inspection, user-facing `/runs`, and usage browser URLs through authenticated redirects, non-Jinja safe problems, or documented retirement responses.
- **FR-004**: System MUST preserve tenant id, filters, saved-filter intent, active panel, run id, export id, breaker id, dead-letter id, and safe breadcrumb intent when redirecting old URLs to React.
- **FR-005**: System MUST reject unsafe query parameters, unsafe redirect destinations, unbounded filters, unauthorized object ids, and cross-tenant links without exposing protected data existence.
- **FR-006**: System MUST expose reliability mutations only through backend-approved actions with idempotency, policy decision, audit reference, and redaction-safe mutation results.
- **FR-007**: System MUST render run timeline, replay, lineage, bundle snapshots, usage, approvals, artifacts, and diagnostics as safe summaries or artifact references only.
- **FR-008**: System MUST render usage export detail as metadata and artifact references only, never raw CSV rows or storage paths.
- **FR-009**: System MUST provide loading, empty, denied, degraded, stale, unavailable, redaction unavailable, audit unavailable, export pending, export failed, breaker open, retry scheduled, and safe retirement states.
- **FR-010**: System MUST delete only operations, reliability, run inspection/user-facing runs, and usage Jinja templates or Jinja-only static surfaces proven obsolete by this spec.
- **FR-011**: System MUST retain shared Jinja infrastructure and templates still owned by later specs until Spec 047.
- **FR-012**: System MUST update operations, reliability, run inspection, usage, quickstart, QA, migration ledger, and reviewer documentation to describe React-only browser paths.
- **FR-013**: System MUST prove behavior with Auth0-shaped backend tests, local-principal Playwright, route scanners, import scanners, frontend tests, generated contract checks, performance tests, QA docs, and full Spec QA.
- **FR-014**: System MUST never render, log, export, screenshot, or document raw secrets, credential values, provider authorization headers, raw prompts, raw completions, memory contents, raw run payloads, private channel messages, raw tool payloads, raw transcripts, raw CSV rows, local filesystem paths, object storage paths, stack traces, full Telegram identifiers, link tokens after creation, or unauthorized tenant labels.

### Key Entities *(include if feature involves data)*

- **OperationsReactWorkspace**: React route envelope with active scope, health, reliability, run-debug, usage, export, and audit summaries.
- **ReliabilityActionSummary**: Backend-owned action descriptor with action id, eligibility, required role, side-effect posture, idempotency need, audit label, and remediation.
- **ReliabilityMutationResult**: Safe mutation result with accepted/denied/queued state, retry schedule, affected reference, safe summary, and audit reference.
- **RunInspectionSummary**: Bounded run search row with run id, tenant label, workflow label, status, timestamps, usage, latency, and authorized detail link.
- **RunDebugEnvelope**: Safe run detail payload with timeline, replay references, lineage, bundle snapshot, usage, artifacts, approvals, and redaction evidence.
- **UsageExportDetail**: Export metadata with status, filter snapshot, row count, checksum, artifact reference, retention state, and audit reference.
- **LegacyOperationsRouteRecord**: Route mapping from old operations/reliability/admin-run/user-facing-run/usage browser URLs to React redirects, safe problems, or retirement responses.
- **OperationsAuditRecord**: Safe audit event with actor, tenant scope, action, outcome, target summary, redaction status, and audit reference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Platform operators can complete operations triage, reliability review, run inspection, and usage export review in React without any operations/reliability/run/usage Jinja page.
- **SC-002**: Every old operations, reliability, run inspection, and usage browser route is covered by a redirect, non-Jinja safe problem, or documented retirement test after template deletion.
- **SC-003**: Reliability actions show backend-approved mutation results and audit references, and denied actions reveal no protected incident details.
- **SC-004**: Run detail, timeline, replay, lineage, and artifact panels expose only safe summaries and governed references.
- **SC-005**: Usage export detail exposes only metadata, filters, row counts, checksums, artifact references, and audit ids.
- **SC-006**: Cross-tenant and unauthorized direct links fail closed without revealing run, export, incident, breaker, dead-letter, or tenant-private labels.
- **SC-007**: QA docs, generated contracts, backend tests, frontend tests, route/import scanners, performance tests, Spec QA, and Playwright validation all pass before Spec 045 begins.

## Assumptions

- Specs 029 and 035 provide the baseline React operations and usage workspaces.
- Existing operations, reliability, run inspection, usage, audit, and redaction services remain the source of truth.
- Old browser URLs should redirect to `/admin/app/operations`, `/admin/app/channels/runs/{run_id}`, or `/admin/app/usage` child routes when safe context can be preserved.
- Local and CI validation use deterministic fixtures and do not require real provider, Telegram, credential, connector, model, or external tool calls.
- This spec deletes only the templates for operations, reliability, runs, and usage; shared admin shell and other remaining Jinja surfaces stay in place for later specs.
