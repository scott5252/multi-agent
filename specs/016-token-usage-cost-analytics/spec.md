# Feature Specification: Token Usage And Cost Analytics

**Feature Branch**: `codex/016-token-usage-cost-analytics`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Add token usage and cost analytics for model-backed agents and sub-agents. The platform must record normalized usage events for every model invocation routed through ModelGateway, including tenant, initiating principal, workflow run, run step, workflow lineage/version, agent key, sub-agent key when applicable, provider key, model id, prompt version, execution mode, input tokens, output tokens, cached tokens when available, reasoning tokens when available, total tokens, provider billable units, latency, cost estimate, pricing version, and whether values are estimated or confirmed. Platform admins must view all usage; tenant admins must view their tenant; future tenant users may view only their own usage if exposed. Dashboards must support filters, time ranges, rollups, drilldowns, and CSV exports. Raw prompts, completions, secrets, memory content, and unauthorized run content must not be stored in usage records. Require audit records for exports and denied access, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Normalize Every Model Invocation (Priority: P1)

Runtime operators need every ModelGateway invocation to create a tenant-scoped,
content-safe usage event with enough attribution to explain model spend for
workflow runs, run steps, agents, sub-agents, prompt versions, providers, and
models.

**Why this priority**: Without trusted capture, every dashboard and export is
incomplete or misleading. This is the MVP because it creates the authoritative
usage source of truth.

**Independent Test**: Execute a mocked ModelGateway completion for a workflow
run step and verify a usage event is persisted with normalized tokens, latency,
pricing version, cost estimate, attribution fields, and no prompt or completion
content.

**Acceptance Scenarios**:

1. **Given** a tenant-scoped workflow run step invokes a model through
   ModelGateway, **When** the provider returns usage metadata, **Then** the
   platform records a usage event with tenant, principal, run, step, workflow,
   agent, provider, model, prompt, token, latency, pricing, and estimate status
   fields.
2. **Given** a provider omits optional cached, reasoning, or billable-unit
   fields, **When** the invocation completes, **Then** the platform records the
   event with available normalized token values, marks missing provider-derived
   values as estimated or unavailable, and does not fail the model invocation.
3. **Given** a provider response contains raw prompt or completion content in
   adjacent metadata, **When** the event is normalized, **Then** the usage record
   stores only allowed metadata and excludes raw prompts, completions, secrets,
   memory content, and run content.

---

### User Story 2 - Review Tenant-Scoped Usage Dashboards (Priority: P2)

Platform admins and tenant admins need a server-rendered admin dashboard that
shows usage and cost summaries by time range, provider, model, workflow,
agent, sub-agent, prompt version, execution mode, and principal, with drilldown
from rollups to individual safe usage events.

**Why this priority**: Visibility turns captured usage into operational and
financial control, while tenant scoping keeps shared-platform data isolated.

**Independent Test**: Seed usage events for two tenants, sign in as a platform
admin and tenant admin, and verify each role sees only authorized rows,
rollups, filters, and drilldowns.

**Acceptance Scenarios**:

1. **Given** a platform admin opens the usage dashboard, **When** no tenant
   filter is selected, **Then** the dashboard shows all tenants with aggregate
   totals, cost estimates, confirmation status, and filter controls.
2. **Given** a tenant admin opens the usage dashboard, **When** events exist for
   multiple tenants, **Then** only that tenant's usage is visible in summaries,
   event tables, and drilldown links.
3. **Given** a dashboard filter combination is applied, **When** matching usage
   exists, **Then** rollups and event rows use the same filter semantics and
   display clear empty states when no rows match.

---

### User Story 3 - Export Audited CSV Reports (Priority: P3)

Authorized admins need to export filtered usage rows to CSV for finance,
capacity planning, and customer-support workflows, while every export and
denied export attempt is audited without leaking protected content.

**Why this priority**: Finance and compliance workflows need portable reports,
but export access increases data-leakage risk and therefore must be audited.

**Independent Test**: Request a CSV export as a platform admin, a tenant admin,
and an unauthorized principal, then verify filtered CSV contents, export audit
records, and denied-access audit records.

**Acceptance Scenarios**:

1. **Given** a platform admin has applied dashboard filters, **When** they
   request CSV export, **Then** the exported rows match those filters and an
   export audit record captures principal, tenant scope, filters, row count,
   artifact reference, and timestamp.
2. **Given** a tenant admin requests export, **When** the filter attempts to
   include another tenant, **Then** the request is denied, no cross-tenant rows
   are exported, and a denied-access audit record is written.
3. **Given** a generated CSV export is later retrieved, **When** the principal
   is authorized for the export scope, **Then** the file contains only safe
   normalized usage columns and no prompt, completion, secret, memory, or run
   content.

---

### User Story 4 - Reconcile Pricing And Late Usage (Priority: P4)

Operators need usage records to distinguish estimated and confirmed values and
to reconcile late provider usage or pricing updates without losing immutable
history or breaking already exported reports.

**Why this priority**: Provider usage metadata may be incomplete at request
time. Reconciliation improves accuracy after the core capture and dashboard
paths are reliable.

**Independent Test**: Create an estimated usage event, apply a later confirmed
usage update for the same idempotency key, and verify the confirmed event,
rollup totals, pricing version reference, and audit trail reflect the update.

**Acceptance Scenarios**:

1. **Given** an initial event has estimated token or cost values, **When** a
   confirmed provider usage payload arrives for the same invocation, **Then**
   the platform records a reconciled usage event state and preserves the audit
   trail linking the estimate to the confirmed values.
2. **Given** a pricing version is superseded, **When** historical events are
   viewed, **Then** each event still references the pricing version used for
   its original estimate and rollups remain explainable.

### Edge Cases

- Provider returns no usage payload at all.
- Provider returns input and output tokens but omits total tokens.
- Provider returns total tokens that differs from input plus output plus cached
  and reasoning details.
- Provider reports cached tokens that should reduce provider billable units.
- ModelGateway call fails before provider response.
- ModelGateway call succeeds but usage persistence fails.
- The same provider operation is retried with the same idempotency key.
- Late reconciliation payload arrives after dashboard rollups or CSV exports.
- Pricing metadata is missing for a provider or model.
- A tenant admin attempts to filter or export a different tenant's usage.
- A future tenant user role attempts to access another user's usage.
- A usage event references a deleted or retired prompt version, provider
  model, workflow version, or agent profile.
- Time range filters cross daylight-saving boundaries.
- CSV export would exceed inline response limits and must use object storage.
- Usage events contain provider metadata fields that look like secrets or raw
  content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create one normalized usage event for every completed
  model invocation routed through ModelGateway.
- **FR-002**: System MUST associate each usage event with tenant id,
  initiating principal id when known, workflow run id when known, run step id
  when known, workflow lineage id when known, workflow version id when known,
  agent key when known, sub-agent key when applicable, provider key, model id,
  prompt version id when known, and execution mode.
- **FR-003**: System MUST store input tokens, output tokens, cached tokens when
  available, reasoning tokens when available, total tokens, provider billable
  units when available, latency milliseconds, cost estimate, pricing version,
  and usage value status.
- **FR-004**: System MUST mark each token, billable unit, and cost value as
  confirmed, estimated, unavailable, or not applicable.
- **FR-005**: System MUST normalize provider-specific usage payloads through a
  provider-agnostic usage service before persistence.
- **FR-006**: System MUST calculate total tokens when safely derivable and MUST
  preserve provider total tokens when the provider reports a conflicting value.
- **FR-007**: System MUST use versioned pricing metadata for cost estimates.
- **FR-008**: System MUST support pricing metadata by provider key, model id,
  effective time range, token category, currency, and calculation method.
- **FR-009**: System MUST distinguish production usage events from test or QA
  usage events.
- **FR-010**: System MUST support idempotent usage event persistence for
  provider retries and repeated ModelGateway result handling.
- **FR-011**: System MUST support late reconciliation from estimated to
  confirmed usage without deleting the original audit trail.
- **FR-012**: System MUST not store raw prompts, completions, secrets, memory
  content, provider credentials, or unauthorized workflow run content in usage
  records, rollups, exports, or audit payloads.
- **FR-013**: System MUST fail closed for unauthorized usage dashboard,
  drilldown, and export access.
- **FR-014**: Platform admins MUST be able to view and export usage across all
  tenants.
- **FR-015**: Tenant admins MUST be able to view and export only usage scoped
  to their tenant.
- **FR-016**: Future tenant user usage views, if exposed, MUST show only the
  initiating principal's own usage.
- **FR-017**: System MUST write audit records for successful CSV exports,
  failed CSV exports, and denied usage access attempts.
- **FR-018**: The dashboard MUST support filters for tenant, principal,
  workflow lineage, workflow version, run id, run step id, agent key,
  sub-agent key, provider key, model id, prompt version, execution mode,
  usage status, and time range.
- **FR-019**: The dashboard MUST support rollups by hour, day, tenant,
  provider, model, workflow, agent, sub-agent, prompt version, execution mode,
  and principal.
- **FR-020**: The dashboard MUST support drilldown from a rollup row to safe
  usage event rows using the same authorization and filter semantics.
- **FR-021**: CSV exports MUST contain only safe normalized usage columns and
  MUST include the filters applied to produce the export.
- **FR-022**: Large CSV exports MUST be stored in configured object storage
  with PostgreSQL metadata rather than stored as database blobs.
- **FR-023**: Usage query paths MUST be index-backed for tenant, timestamp,
  provider, model, workflow, agent, prompt, and principal filters.
- **FR-024**: Usage rollups MUST be consistent with event-level data for the
  same filter window.
- **FR-025**: System MUST expose API contracts for dashboard summaries, event
  drilldowns, and CSV export requests.
- **FR-026**: Server-rendered admin views MUST be available under the existing
  admin console shell.
- **FR-027**: Usage services MUST emit safe structured logs and metrics for
  event capture, normalization failures, export requests, and reconciliation.
- **FR-028**: Tests MUST cover usage event normalization, provider-specific
  missing fields, estimated and confirmed usage, attribution, tenant isolation,
  dashboard filters, rollups, pricing calculations, CSV authorization,
  redaction, late reconciliation, and time-range query performance.
- **FR-029**: Feature documentation MUST include README updates, quickstart
  validation, testing instructions, PR review notes, and non-developer QA
  guidance.
- **FR-030**: Automated test coverage for relevant code MUST meet or exceed
  the repository's 90 percent coverage threshold.

### Key Entities *(include if feature involves data)*

- **Usage Event**: Immutable normalized record for one ModelGateway invocation,
  including safe attribution, token counts, billable units, latency, cost,
  pricing version, status flags, idempotency key, and environment mode.
- **Usage Rollup**: Queryable aggregate of usage events over a time bucket and
  dimension set, used for dashboard summaries and performance-sensitive
  reports.
- **Pricing Version**: Versioned provider/model pricing metadata with effective
  dates, currency, token category prices, calculation method, and source notes.
- **Usage Export Request**: Audited request for a filtered CSV export,
  including requester, authorized scope, filters, status, artifact metadata,
  row count, and retention metadata.
- **Usage Reconciliation Record**: Link between an original estimated event
  and a later confirmed or corrected provider usage payload.
- **Usage Access Audit**: Safe audit event for allowed exports, failed exports,
  denied access, and administrative usage inspection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 99 percent of successful ModelGateway invocations in
  tests create exactly one idempotent usage event.
- **SC-002**: Dashboard summaries and event drilldowns return tenant-scoped
  results for seeded two-tenant data with zero cross-tenant leakage.
- **SC-003**: CSV export tests prove platform admin, tenant admin, and denied
  principal behavior, including audit records for both export and denial.
- **SC-004**: Rollup totals match event-level totals for seeded hourly and
  daily windows across provider, model, workflow, agent, and principal filters.
- **SC-005**: Redaction tests verify usage storage, exports, and audits contain
  no raw prompt, completion, secret, memory, or unauthorized run content.
- **SC-006**: Time-range query tests over at least 10,000 seeded usage events
  complete within the repository's documented performance budget.
- **SC-007**: Relevant automated coverage remains at or above 90 percent.
- **SC-008**: Non-developer QA guide and Playwright screenshots demonstrate
  the login path and `/admin/usage` dashboard target.

## Assumptions

- ModelGateway is the required capture boundary for model-backed agents and
  sub-agents; direct provider calls remain guarded by existing policy tests.
- Pricing metadata is maintained by platform configuration and is not fetched
  from live provider pricing pages during request handling.
- Usage events may reference nullable workflow, step, prompt, or principal
  fields when an invocation is system-initiated or occurs outside a workflow
  run, but tenant and provider/model attribution are required.
- CSV export artifacts use the existing object storage abstraction when
  available and may use a deterministic local artifact provider in tests.
- Dashboard and export APIs reuse existing admin shell, Auth0/local-principal
  test mode, tenant-scoped authorization, and audit/redaction helpers.
- Rollups may be generated query-time for MVP when indexed event queries meet
  performance requirements; persisted rollups are added when performance tests
  require them.

## Autopilot Clarifications

- Q: What source should pricing estimates use? -> A: Use versioned internal
  pricing metadata managed by the platform, with no live external pricing calls
  during request handling or QA validation. (autopilot)
- Q: How should missing provider usage fields be handled? -> A: Persist the
  event with available fields, compute only safely derivable totals, and mark
  missing token, billable unit, or cost values as estimated, unavailable, or
  not applicable. (autopilot)
- Q: How should late confirmed usage update an estimated event? -> A: Apply an
  idempotent reconciliation record that preserves the original audit trail and
  updates current dashboard totals to the confirmed values. (autopilot)
- Q: Are raw prompts, completions, secrets, or memory snippets allowed in usage
  events for debugging? -> A: No. Store only safe identifiers, counts, statuses,
  latency, pricing, and authorized attribution metadata. (autopilot)
