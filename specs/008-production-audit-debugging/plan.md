# Implementation Plan: Production Audit And Debugging

**Branch**: `008-production-audit-debugging` | **Date**: 2026-04-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-production-audit-debugging/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a production observability and audit subsystem that turns runtime activity
into operator-visible, tenant-scoped evidence. The feature will capture
structured logs, trace ids, metrics, chronological run timelines, runtime trace
records, PostgreSQL audit tables, parent-child lineage, version-bundle
references, notification delivery state, and secret-access metadata. Admin and
auditor FastAPI endpoints will provide direct run lookup, filtered search,
timeline inspection, replay views, lineage navigation, version-bundle
visualization, and redacted debug-evidence export without requiring database
access. Security and governance audit capture fails closed, while non-security
trace gaps are recorded as explicit unavailable markers.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, existing
local-principal auth mode, Starlette/FastAPI response handling, existing
LangChain 1.2.15 and LangGraph 1.1.9 runtime integration,
langgraph-checkpoint-postgres 3.0.5, existing observability helpers for
structured logging, metrics, and tracing, httpx test clients, pytest,
pytest-asyncio, Ruff, mypy, uv  
**Storage**: PostgreSQL for append-only audit events, run timeline events,
runtime trace records, capture gaps, lineage projections, version-bundle
references, notification delivery projections, secret-access audit metadata,
inspection access audits, export metadata, redaction/classification records,
and replay snapshots; object storage for generated debug-evidence export
payloads with PostgreSQL artifact metadata; existing secret manager stores raw
secret values outside audit records  
**Testing**: pytest unit tests for event builders, redaction/classification,
safe summaries, timeline assembly, query filters, replay view assembly,
lineage/version-bundle projections, metrics/log/trace emission, fail-closed
audit behavior, and Pydantic schemas; FastAPI contract tests for inspection,
search, timeline, replay, lineage, export, and authorization endpoints;
PostgreSQL-backed integration tests for append-only writes, migration
constraints, tenant fail-closed behavior, denied-inspection audits,
notification/secret/runtime trace linkage, and p95 lookup/search targets;
coverage enforcement at >=90 percent for submitted audit capture, inspection,
authorization, redaction, timeline, lineage, export, and observability behavior  
**Target Platform**: Linux container deployment target for FastAPI API and
background workers; local development on macOS/Linux; PostgreSQL-backed
workflow execution under the existing platform bootstrap model  
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
minimal server-rendered admin views, durable workflow runtime services,
PostgreSQL audit storage, and operator-facing documentation  
**Performance Goals**: Direct run lookup p95 <= 2 seconds and filtered
run-debug searches p95 <= 5 seconds in acceptance tests; timeline and replay
assembly use bounded page sizes and indexed tenant/run/time filters; audit
capture adds p95 <= 10 ms in-process builder overhead excluding database
commit time during performance tests; metrics and structured logs emit without
blocking runtime progress after durable audit writes succeed  
**Constraints**: Security and governance audit events must be durably recorded
before protected actions proceed; non-security trace capture failures may not
block execution but must create an unavailable marker linked to the affected
timeline event; audit and trace records are append-only and corrections,
redactions, or supersession are recorded as later linked events; raw secret
values, credential values, unauthorized prompt content, unauthorized memory
content, and large payload bodies never appear in visible timelines, logs,
metrics, traces, exports, or review notes; all inspection, search, export,
lineage, replay, and denied-access audit paths enforce tenant and role
authorization; exported evidence uses existing artifact retention and access
controls  
**Scale/Scope**: Initial scope supports hundreds of active or paused runs per
tenant, thousands of historical run timelines per tenant, low millions of
append-only audit and trace rows over retention windows, timeline pages of up
to 200 events, filtered search pages of up to 100 runs, and debug exports for a
single run plus authorized child lineage at a time

**Tenant Limits And Fairness**: Inspection APIs require tenant scope from the
authorized principal and use bounded pagination. Search filters are indexed by
tenant, run id, workflow id, status, failure category, time range, agent, tool,
model-selection source, notification status, and lineage relationship. Export
requests are rate-limited per tenant and actor through existing admin
authorization and operational controls. Rejected export requests return safe
retry metadata, emit tenant-scoped metrics, and create an inspection/access
audit event without creating export artifacts. Metrics track per-tenant lookup
latency, search latency, denied inspection count, capture failure count, export
rejection count, and export volume.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Security/governance audit records are committed before protected side effects proceed; runtime timeline and replay evidence are durable across worker restarts, retries, cancellations, and retention transitions. |
| Immutable State And Memory | PASS | Timeline, trace, audit, correction, redaction, supersession, memory-write, and secret-access records are append-only; projections are derived from immutable rows. |
| Contract-First Agent Coordination | PASS | Admin inspection APIs, runtime audit capture protocol, replay view contract, and event schemas define boundaries before implementation. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal authorization gates every inspection, export, lineage, and denied-access audit path while preserving deterministic local test principals. |
| Operability Is A Product Requirement | PASS | Plan defines structured logs, trace ids, metrics, workflow timelines, lineage, replay views, failure-debugging APIs, capture-gap markers, and operator documentation. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks trace directly to production audit/debugging outcomes. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, contract/integration/performance tests, README update, testing instructions, and PR review notes. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across audit/observability services, DB models/repositories, runtime capture hooks, admin APIs/views, export handling, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | All records carry tenant scope; cross-tenant run ids fail closed; search/export use bounded pages, indexed filters, and per-tenant metrics. |
| Version-Pinned Execution | PASS | Run inspection exposes pinned execution/version bundle references, first-use runtime decisions, and any audited migration records without mutating historical evidence. |
| Secret Hygiene And Controlled Tool Access | PASS | Secret access records store requester, reference metadata, policy outcome, and reason only; raw secret and credential values are rejected by classification/redaction gates. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores transactional audit/export metadata; generated debug evidence payloads use object storage through existing artifact metadata. |
| Human Approval Is Durable State | PASS | Waiting, approval, resume, retry, cancellation, and timeout transitions are first-class timeline events linked to durable approval/resume records. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/008-production-audit-debugging/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- production-audit-debugging.openapi.yaml
|   +-- runtime-audit-capture-protocol.md
|   +-- admin-replay-views.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- admin_run_inspection.py       # timeline, search, replay, lineage, export APIs
    |   +-- schemas/
    |       +-- audit_debugging.py            # inspection and export request/response schemas
    +-- audit/
    |   +-- classification.py                 # sensitivity labels and redaction decisions
    |   +-- capture.py                        # runtime audit capture facade
    |   +-- export.py                         # redacted debug-evidence exports
    |   +-- inspection.py                     # timeline/replay/search assemblers
    |   +-- models.py                         # domain value objects
    |   +-- service.py                        # append-only write and query facade
    +-- db/
    |   +-- models/
    |   |   +-- audit_debugging.py            # timelines, traces, gaps, exports, projections
    |   +-- repositories/
    |       +-- audit_debugging.py            # transactional storage and indexed queries
    +-- observability/
    |   +-- logging.py                        # trace/run-aware structured logging context
    |   +-- metrics.py                        # capture/query/export metrics
    |   +-- tracing.py                        # trace/span helpers and propagation
    +-- runtime/
    |   +-- orchestration/
    |       +-- service.py                    # emit lifecycle, handoff, validation, tool, model events
    |       +-- events.py                     # map runtime events to audit capture
    |       +-- handoffs.py                   # handoff trace records
    |       +-- side_effects.py               # tool/model/secret policy trace hooks
    +-- web_admin/
        +-- static/
        |   +-- run_inspection.js             # replay/lineage/timeline interactions
        +-- templates/
            +-- runs/
                +-- index.html
                +-- detail.html
                +-- replay.html
alembic/versions/
+-- 0008_production_audit_debugging.py
tests/
+-- contract/
|   +-- test_production_audit_debugging_contract.py
+-- integration/
|   +-- api/
|   |   +-- test_admin_run_inspection_api.py
|   |   +-- test_admin_run_inspection_ui.py
|   +-- db/
|   |   +-- test_audit_debugging_migration.py
|   +-- runtime/
|       +-- test_audit_capture_runtime.py
|       +-- test_timeline_completeness.py
+-- performance/
|   +-- audit/
|       +-- test_run_inspection_latency.py
+-- unit/
|   +-- api/
|   |   +-- test_audit_debugging_schemas.py
|   +-- audit/
|   |   +-- test_capture.py
|   |   +-- test_classification.py
|   |   +-- test_export.py
|   |   +-- test_inspection.py
|   |   +-- test_redaction.py
|   |   +-- test_replay.py
|   +-- observability/
|       +-- test_audit_logging.py
|       +-- test_audit_metrics.py
|       +-- test_audit_tracing.py
README.md
docs/quickstart.md
docs/production-audit-debugging.md
```

**Structure Decision**: Keep audit/debugging in the existing Python/FastAPI
backend. Add focused audit capture, classification, inspection, replay, and
export modules under `multi_agent_platform.audit`; keep low-level persistence
in SQLAlchemy models/repositories; expose admin inspection through thin FastAPI
routers and minimal admin templates; extend existing observability helpers
instead of introducing a separate telemetry service.

## Audit Capture And Observability Decisions

- **Trace id propagation**: Every accepted run receives or inherits a
  `trace_id`, `workflow_run_id`, `tenant_id`, `correlation_id`, and optional
  `parent_run_id`. Runtime services pass these identifiers through lifecycle,
  handoff, validation, memory, tool, model, notification, and secret-access
  capture calls.
- **Structured logs**: Runtime and admin inspection logs include safe fields:
  tenant id, run id, trace id, timeline event id, event category, actor type,
  policy outcome, status, duration, and safe error category. Log builders
  reject sensitive payload classes before serialization.
- **Metrics**: Counters and histograms cover audit events recorded, capture
  failures by criticality, unavailable trace markers, denied inspections,
  export requests, direct lookup latency, filtered search latency, timeline
  assembly latency, replay assembly latency, and redaction decisions.
- **PostgreSQL audit tables**: `audit_timeline_events`,
  `audit_runtime_trace_records`, `audit_capture_gaps`,
  `audit_inspection_access_events`, `audit_debug_exports`, and projection
  tables store append-only evidence and query-ready summaries.
- **Capture criticality**: Events are classified as `security_governance`,
  `runtime_required`, or `diagnostic`. Security/governance events fail closed
  if durable write fails. Runtime-required failures block only when the event
  is needed to preserve authoritative state. Diagnostic capture failures create
  an unavailable marker and increment metrics.
- **Idempotency**: Capture requests use `(tenant_id, workflow_run_id,
  event_source, source_event_id, event_kind)` idempotency keys so retries after
  worker crashes return the first persisted evidence row.

## Query, Replay, And Visualization Decisions

- **Direct run lookup**: `GET /admin/runs/{workflow_run_id}/timeline` returns
  run summary, pinned bundle summary, lifecycle timeline, linked trace records,
  capture gaps, lineage summary, notification delivery state, and export links
  visible to the caller.
- **Filtered search**: `GET /admin/runs/debug-search` supports run identity,
  workflow identity, status, failure category, time range, agent, tool, model
  selection source, notification status, and lineage relationship filters with
  cursor pagination and tenant-scoped indexes.
- **Replay views**: Replay APIs assemble an ordered, redacted event stream from
  immutable timeline and trace records. The response includes sequence,
  timestamp, event category, status after event, trace ids, actor, safe detail,
  linked runtime record ids, capture gaps, and replay checkpoints. Replay does
  not re-execute tools, models, notifications, or secret resolution.
- **Lineage visualization**: Parent-child runs, retries, resumptions, and
  delegated executions are exposed as graph JSON with nodes for authorized
  runs and edges labeled by relationship type, source event, status, and time.
  Unauthorized related runs are represented as redacted boundary nodes.
- **Version-bundle visualization**: Timeline and replay responses show the
  pinned execution bundle, workflow version, contract versions, prompt
  references, model configuration versions, tool-policy versions, activation
  state at run acceptance, and audited migration records when present.
- **Exports**: Debug evidence exports package timeline, trace, lineage,
  notification, secret-access, and version-bundle evidence after applying the
  requesting actor's authorization and redaction policy. Export metadata is
  audit logged before the artifact is made available.
- **Export durability and recovery**: Debug evidence export creation is a
  two-phase durable workflow: PostgreSQL export metadata is created first with
  an idempotency key and `pending` status, object-storage upload is retried with
  bounded attempts, and the row transitions to `available`, `failed`, or
  `expired` only through append-only status events. If object storage succeeds
  but metadata finalization fails, reconciliation uses the idempotency key and
  artifact pointer to complete or mark the export failed without exposing a
  partial artifact.

## Classification And Redaction Decisions

- **Sensitivity labels**: Captured fields are classified as `public_metadata`,
  `tenant_internal`, `operator_safe`, `restricted_prompt`,
  `restricted_memory`, `secret_reference`, `credential_secret`, `raw_secret`,
  `external_payload`, or `artifact_pointer`.
- **Default redaction**: Unclassified dynamic payloads default to
  `external_payload` and are summarized rather than stored. Raw secrets,
  credential values, provider tokens, raw prompt bodies, and unauthorized
  memory content are rejected from visible evidence and logs.
- **Safe summaries**: Runtime capture records stable identifiers, lengths,
  digests, schema names, status categories, policy outcomes, duration, and
  bounded error summaries. Large payloads use artifact/object-storage pointers
  only when allowed by existing artifact policy.
- **Append-only redactions**: If a prior record requires correction or
  redaction, the original row remains immutable and a linked
  `redaction_applied`, `correction_applied`, or `superseded` event changes
  query projections for future viewers.
- **Viewer-aware fields**: API serializers apply caller role and tenant scope
  before returning memory metadata, prompt references, tool inputs, model
  traces, notification destinations, secret references, or export links.

## Complexity Tracking

No constitution violations require justification.
