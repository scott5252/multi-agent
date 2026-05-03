# Feature Specification: Operations Console Logs And Performance

**Feature Branch**: `codex/019-operations-console-logs-performance`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Add an operations console for platform administrators. Platform admins must be able to view system health, dependency readiness, worker capacity, queue pressure, database pool pressure, object-storage status, model-provider health, Telegram/channel status, reliability breaker state, retry/dead-letter state, request latency, run lifecycle throughput, model latency, token throughput, error rate, and redacted structured logs. The console must support filtering logs and operational events by trace id, tenant id, run id, component, severity, status, dependency, and time range. It must link from operational records to run inspection, reliability controls, provider connection tests, and usage dashboards when authorized. It must provide redacted export artifacts and audit every export or denied access. Tenant admins may receive limited tenant-scoped operational views only if explicitly included; platform logs are platform-admin or auditor only. Require safe redaction, retention awareness, performance tests, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## Clarifications

- Q: Should tenant admins receive limited operations-console views in this first release? -> A: No; v1 is limited to platform administrators and auditors with explicit operations permissions. Tenant-admin access fails closed and is audited through existing access-decision records. (autopilot)
- Q: What is the authoritative source for redacted structured logs? -> A: Use persisted safe audit/debugging timeline, trace, gateway, usage, reliability, and channel metadata already stored by the platform; do not read raw application log files or render raw payload fields. (autopilot)
- Q: How should operations log exports be persisted and audited? -> A: Store redacted CSV exports through the existing object/filesystem artifact provider and record export or denial metadata through existing inspection-access audit records; no new persistence table is required for v1. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Platform Health And Capacity (Priority: P1)

Platform operators need one server-rendered operations console that shows whether
the platform is live, ready, dependency-complete, and within capacity limits.

**Why this priority**: Operators need a first-stop view before drilling into
logs, providers, reliability controls, or run inspection.

**Independent Test**: Sign in as `platform-admin`, open `/admin/operations`,
and verify health, dependencies, worker/queue capacity, database pool pressure,
object-storage status, request latency, error rate, and navigation links render.

**Acceptance Scenarios**:

1. **Given** health checks are available, **When** a platform admin opens the
   console, **Then** the page shows live/readiness status and dependency rows.
2. **Given** a capacity snapshot exists, **When** the page renders, **Then**
   worker capacity, queue pressure, DB pool pressure, artifact pressure, retry,
   dead-letter, and breaker state appear with safe summaries.
3. **Given** no capacity snapshot exists, **When** the page renders, **Then**
   the console shows a safe empty state rather than failing.

---

### User Story 2 - Inspect Dependency And Throughput Panels (Priority: P2)

Operators need model-provider health, Telegram/channel readiness, usage/token
throughput, model latency, run lifecycle throughput, and reliability status in
one place with links to dedicated admin surfaces.

**Why this priority**: Platform incidents often cross provider, channel,
runtime, usage, and reliability boundaries.

**Independent Test**: Seed provider, usage, timeline, gateway, Telegram, and
capacity records, then verify `/admin/operations` summarizes them and links to
model providers, Telegram configuration, reliability controls, run inspection,
and usage analytics.

**Acceptance Scenarios**:

1. **Given** model provider connections exist, **When** the operations console
   renders, **Then** provider health counts and model-latency summaries are
   visible with a link to provider tests.
2. **Given** Telegram references are configured safely, **When** the console
   renders, **Then** channel readiness shows safe reference labels only.
3. **Given** usage events exist, **When** the console renders, **Then** token
   throughput and usage event counts reflect the bounded time range.

---

### User Story 3 - Filter Redacted Operational Logs (Priority: P3)

Operators and auditors need to filter redacted operational events by trace id,
tenant id, run id, component, severity, status, dependency, and time range.

**Why this priority**: Filtering turns broad operations visibility into a
focused incident investigation tool.

**Independent Test**: Seed multi-tenant audit timeline and gateway records,
apply each filter through API and UI query parameters, and verify only matching
redacted log rows appear.

**Acceptance Scenarios**:

1. **Given** events exist for multiple traces, **When** a trace id filter is
   applied, **Then** only rows for that trace are returned.
2. **Given** events contain safe details only, **When** logs render or export,
   **Then** raw prompts, model responses, credentials, secrets, and payloads do
   not appear.
3. **Given** a bounded time range is supplied, **When** logs are queried, **Then**
   the query remains bounded and returns results inside that range only.

---

### User Story 4 - Export Redacted Evidence (Priority: P4)

Platform admins and auditors need redacted CSV exports for incident review, and
every export or denied attempt must be auditable.

**Why this priority**: Incident evidence must be portable without weakening
tenant isolation or redaction guarantees.

**Independent Test**: Request a filtered export as a platform admin, auditor,
and tenant admin with operations permissions, then verify artifact metadata,
redacted CSV content, and allowed/denied audit records.

**Acceptance Scenarios**:

1. **Given** a platform admin requests a filtered export, **When** the export
   completes, **Then** an artifact URI, checksum, row count, and audit event are
   returned.
2. **Given** an auditor requests the same export, **When** the export completes,
   **Then** the same redaction rules apply and the action is audited.
3. **Given** a tenant admin attempts export, **When** the service evaluates the
   request, **Then** export is denied and an audit-safe denial record is stored.

### Edge Cases

- Health checks are degraded or unavailable.
- `alembic_version` is missing during local setup.
- No capacity snapshot has been recorded yet.
- Queue depths exceed configured limits.
- Database pool wait p95 crosses the configured threshold.
- Object storage is configured but contains no artifacts.
- Provider connections are disabled, untested, degraded, or unavailable.
- Telegram is missing token or webhook references.
- Logs contain sensitive-looking keys such as prompt, response, token, secret,
  credential, payload, message, traceback, or memory.
- A trace id exists in gateway attempts but not timeline events.
- A run id exists in timeline events but not gateway attempts.
- Time filters are inverted.
- A platform admin filters by tenant id.
- A tenant admin attempts to view platform logs.
- An auditor lacks export permission.
- Export storage fails after an audit event is started.
- Log query is requested without a bounded time range and must apply a safe
  default limit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a server-rendered Operations Console at
  `/admin/operations` under the existing admin shell.
- **FR-002**: System MUST expose JSON admin APIs under
  `/admin/operations/api` for dashboard summary, log filtering, and redacted
  log export.
- **FR-003**: Platform admins and auditors with explicit operations permissions
  MUST be able to view platform operations data.
- **FR-004**: Tenant admins MUST NOT view platform operations logs in v1 unless
  a future spec explicitly adds tenant-scoped operations views.
- **FR-005**: System MUST fail closed for unauthorized operations access and
  export attempts.
- **FR-006**: Dashboard summary MUST include system health, dependency
  readiness, worker capacity, queue pressure, DB pool pressure, object-storage
  status, model-provider health, Telegram/channel status, reliability breaker
  state, retry/dead-letter state, request latency, run lifecycle throughput,
  model latency, token throughput, and error rate.
- **FR-007**: Operational log filtering MUST support trace id, tenant id, run
  id, component, severity, status, dependency, start time, end time, and limit.
- **FR-008**: Operational log queries MUST use bounded limits and index-backed
  filters where persisted records provide them.
- **FR-009**: Log rows MUST link to authorized run inspection, reliability
  controls, provider connection tests, Telegram configuration, and usage
  dashboards when relevant.
- **FR-010**: System MUST never render or export raw prompts, model responses,
  memory content, secrets, credential values, raw provider payloads, raw channel
  messages, authorization headers, stack traces, or unauthorized tenant data.
- **FR-011**: Redacted exports MUST be stored through existing artifact storage
  and include artifact URI, checksum, size, row count, filters, requester, and
  trace id.
- **FR-012**: Every export and denied export attempt MUST record audit-safe
  inspection-access metadata.
- **FR-013**: UI templates MUST include retention and redaction notices that
  are safe for screenshots.
- **FR-014**: Admin navigation MUST include "Operations Console" and preserve
  platform or tenant scope safely.
- **FR-015**: Tests MUST cover authorization, auditor read-only access,
  tenant-admin denial, health aggregation, dependency mapping, capacity display,
  provider status, Telegram status, reliability links, usage throughput, log
  filtering, redaction, exports, UI rendering, query performance, docs, and
  at least 90 percent coverage.
- **FR-016**: Documentation MUST include README updates, quickstart validation,
  QA guide, UI walkthrough, PR review notes, testing instructions, and a
  non-developer QA user guide.

### Key Entities *(include if feature involves data)*

- **Operations Dashboard Snapshot**: Safe aggregated view of health,
  dependencies, capacity, provider, channel, reliability, usage, latency, and
  error summaries.
- **Operational Log Filter**: Bounded filter set for trace, tenant, run,
  component, severity, status, dependency, time range, and limit.
- **Operational Log Event**: Redacted event row derived from safe persisted
  audit, gateway, runtime, reliability, usage, or channel metadata.
- **Operations Export Artifact**: CSV artifact plus checksum, size, row count,
  filters, requester, trace id, and safe audit metadata.
- **Operations Access Scope**: Platform or auditor scope used to fail closed
  for unauthorized principals.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Platform-admin browser validation reaches `/admin/operations` and
  captures screenshots showing dashboard cards and redacted logs.
- **SC-002**: API tests prove platform admin and auditor can read operations
  data while tenant admin access is denied.
- **SC-003**: Log filtering tests prove trace, tenant, run, component,
  severity, status, dependency, and time-range filters return only matching
  redacted rows.
- **SC-004**: Export tests prove artifact metadata is returned, audit records
  are written, and CSV content contains no protected raw fields.
- **SC-005**: Performance tests over at least 10,000 operational events keep a
  bounded time-range query within the documented budget.
- **SC-006**: Relevant automated coverage remains at or above 90 percent.
- **SC-007**: Non-developer QA guide and Playwright screenshots demonstrate
  login and `/admin/operations` target flows.

## Assumptions

- Existing health, reliability, model-provider, Telegram, usage, and
  audit-debugging records are the source of truth for v1.
- No new database table is required for v1; exports reuse artifact storage and
  existing inspection-access audit records.
- Raw application log files are not read because they may contain process-local
  or deployment-specific content outside persisted redaction controls.
- The first release is platform-operator focused. Tenant-scoped operations
  views require a future explicit spec.
