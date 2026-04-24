# Implementation Plan: Immutable Versioned Memory

**Branch**: `005-immutable-memory` | **Date**: 2026-04-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-immutable-memory/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add an append-only PostgreSQL-backed memory subsystem where every agent memory
write creates a new immutable JSON snapshot version. Memory is scoped by
tenant, workflow lineage, agent, and memory key; a separate head projection
provides fast current-state reads; and runtime writes use optimistic
concurrency checks tied to the expected current version. The design links each
memory version to the pinned execution bundle and workflow run context that
created it, preserves parent-child run lineage for inherited subworkflow writes,
records content-free audit events for writes and reads, and exposes FastAPI
contracts for current-head retrieval, version creation, replay, diffing, and
history inspection.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9,
langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff,
mypy, uv  
**Storage**: PostgreSQL for memory scopes, immutable memory versions, head
projections, read/write audit records, archival markers, links to runtime
execution bundles, workflow runs, run steps, and parent-child lineage; object
storage only for future oversized memory attachments, with PostgreSQL retaining
metadata and hashes  
**Testing**: pytest unit tests for canonical JSON, version lineage,
immutability guards, head projection updates, concurrency failures, diff and
replay behavior, access checks, audit redaction, repository queries, and API
schemas; FastAPI contract tests for memory APIs; PostgreSQL-backed integration
tests for racing initial writes, stale expected-head writes, transaction
rollback, tenant isolation, bundle/run-lineage links, and archival behavior;
coverage enforcement at >=90 percent for relevant memory code  
**Target Platform**: Linux container deployment target for FastAPI API and
background workers; local development on macOS/Linux; PostgreSQL-backed
workflow execution under the existing platform bootstrap model  
**Project Type**: Multi-tenant backend platform with JSON APIs, background
workers, durable workflow runtime services, and operator-facing documentation  
**Performance Goals**: Current-head lookup p95 <100ms for indexed scopes under
normal development-test load; current-head lookup <1 second for SC-003;
authorized memory write p95 <300ms excluding caller authorization latency;
history list p95 <300ms for the latest 100 versions; replay/diff p95 <500ms for
JSON snapshots up to the configured inline size limit  
**Constraints**: Memory versions are never updated in place; non-initial writes
must include the expected current version id; initial writes must assert no
current head exists; memory content is canonical JSON with explicit null and
removal markers; audit records must not store raw memory content; runtime reads
must use the same tenant, pinned run bundle, workflow lineage, and
authorization context as the executing run; PostgreSQL remains the source of
truth and is not used for unbounded blobs; >=90 percent unit-test coverage,
README update, quickstart, testing instructions, and PR review notes are
required  
**Scale/Scope**: Initial scope supports hundreds of active workflow lineages
per tenant, thousands of memory scopes per workflow lineage, low thousands of
versions per hot memory scope, nested parent-child workflow runs at least 5
levels deep, and memory content sized for transactional JSON snapshots with a
future object-storage escape hatch for oversized attachments

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Versions, head changes, runtime links, audit events, and archival markers are persisted transactionally in PostgreSQL before they become authoritative. |
| Immutable State And Memory | PASS | Memory versions are append-only snapshots; existing version content, lineage, creator metadata, timestamps, hashes, and audit metadata are immutable. |
| Contract-First Agent Coordination | PASS | External memory APIs and runtime memory protocol define request/response schemas, expected-head rules, error semantics, and compatibility behavior. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal authorization gates all memory content, diff, replay, audit, and runtime access while preserving deterministic test principals. |
| Operability Is A Product Requirement | PASS | Plan defines audit events, structured logs, metrics, traces, history views, diff/replay diagnostics, archival state, and validation quickstart. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks are traceable to immutable memory requirements and constitution gates. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, focused concurrency and immutability tests, README updates, quickstart validation, testing instructions, and PR notes. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across `memory`, DB models/repositories, API schemas/routers, runtime integration, migration, docs, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | Every scope, version, head, audit event, query, and runtime call is tenant-scoped; cross-tenant ids fail closed and are audited. |
| Version-Pinned Execution | PASS | Runtime memory reads and writes record the pinned `run_bundle_id`, bundle digest, workflow run, run step, and workflow lineage that authorized the operation. |
| Secret Hygiene And Controlled Tool Access | PASS | Memory audit stores hashes and redacted summaries only; raw memory content is returned only through authorized memory/replay/diff paths and is excluded from logs. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores canonical JSON snapshots within configured limits plus hashes and metadata; any future large attachments use object-storage refs anchored in memory metadata. |
| Human Approval Is Durable State | PASS | Memory writes have no separate approval state by spec; if a workflow requires human approval before writing memory, that approval remains in durable runtime approval records before the memory call. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/005-immutable-memory/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── memory.openapi.yaml
│   └── runtime-memory-protocol.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── multi_agent_platform/
    ├── api/
    │   ├── routers/
    │   │   └── memory.py                    # new memory JSON API
    │   └── schemas/
    │       └── memory.py                    # new API schemas
    ├── bootstrap/
    │   └── container.py                     # wire memory services/repository
    ├── db/
    │   ├── models/
    │   │   └── memory.py                    # new memory tables
    │   └── repositories/
    │       └── memory.py                    # transactional DB access
    ├── memory/
    │   ├── __init__.py
    │   ├── canonical.py                     # canonical JSON and hashes
    │   ├── diff.py                          # reviewer diff model
    │   ├── models.py                        # memory domain models
    │   ├── policy.py                        # access/scope validation helpers
    │   ├── replay.py                        # replay/head reconstruction
    │   ├── repository.py                    # service-facing protocol
    │   └── service.py                       # read/write API and runtime facade
    ├── runtime/
    │   └── orchestration/
    │       └── service.py                   # call memory facade at safe nodes
    └── observability/
        ├── logging.py
        ├── metrics.py
        └── tracing.py
alembic/versions/
└── 0005_immutable_memory.py                 # new migration
tests/
├── contract/
│   └── test_memory_contract.py
├── integration/
│   ├── api/
│   │   └── test_memory_api.py
│   ├── db/
│   │   └── test_memory_migration.py
│   └── runtime/
│       └── test_runtime_memory_flows.py
├── unit/
│   ├── api/
│   │   └── test_memory_schemas.py
│   ├── db/
│   │   └── test_memory_models.py
│   └── memory/
│       ├── test_canonical.py
│       ├── test_diff.py
│       ├── test_policy.py
│       ├── test_replay.py
│       ├── test_repository.py
│       └── test_service.py
README.md
docs/quickstart.md
docs/immutable-memory.md                      # new operator/reviewer guide
```

**Structure Decision**: Keep memory as a first-class package under the existing
Python backend, FastAPI application, SQLAlchemy/Alembic database layer, runtime
services, and observability helpers. The memory package owns canonical JSON,
lineage, diff, replay, and write safety rules; runtime orchestration consumes
the memory facade rather than manipulating tables directly.

## Memory Scope And Lineage Decisions

- **Scope Identity**: A memory scope is uniquely identified by
  `(tenant_id, workflow_lineage_id, agent_key, memory_key)`. The workflow
  lineage id comes from the published workflow lineage, not from an individual
  run, so memory is shared across runs of the same workflow lineage.
- **Stable Scope Record**: `memory_scopes` stores one row per scope with a
  generated `memory_scope_id`. The natural key has a unique index, making
  runtime calls idempotently resolve or create the same scope under tenant
  constraints.
- **Version Lineage**: `memory_versions` stores immutable snapshots. The first
  version has `previous_memory_version_id = null` and defines the lineage for
  the scope. Every non-initial version points to the immediately prior current
  head and records `version_sequence = previous.version_sequence + 1`.
- **Current Head Projection**: `memory_heads` stores exactly one current head
  row per scope. It is a projection, not the source of history. It is updated
  only in the same transaction that inserts a new version and audit event.
- **Runtime Source Links**: Every version created during execution stores
  `workflow_run_id`, `run_step_id`, `run_bundle_id`, `bundle_digest`, and
  optional `run_lineage_id`. These fields let reviewers answer which pinned
  runtime bundle and parent-child edge produced a memory state.
- **Parent-Child Runs**: Child runs write to the same workflow-lineage memory
  scope when their pinned bundle declares the same `workflow_lineage_id`.
  `run_lineage_id` records the parent-child edge that introduced the write.
  Cross-tenant parent-child memory access is rejected unless a future spec adds
  explicit delegated cross-tenant memory contracts.

## Runtime Read And Write Safety

- **Safe Read Path**: Runtime nodes request memory through
  `MemoryService.get_current_head_for_runtime(...)` with tenant id,
  workflow lineage id, agent key, memory key, workflow run id, run step id,
  run bundle id, and bundle digest. The service verifies the run and bundle are
  tenant-matched and still pinned, resolves the scope, reads `memory_heads`,
  returns an explicit no-memory result when absent, and records a content-free
  read audit event.
- **Safe Write Path**: Runtime nodes call
  `MemoryService.write_version_for_runtime(...)` after authorization and any
  workflow-level approval or side-effect preconditions. The call requires new
  canonical JSON content plus either `expected_current_version_id` for
  non-initial writes or `assert_no_current_head = true` for initial writes.
- **Pinned Bundle Guard**: Writes verify that the provided `run_bundle_id` and
  `bundle_digest` match the runtime run's immutable execution bundle. Resume
  uses the same pinned bundle and therefore cannot silently reinterpret memory
  writes under a newer workflow definition.
- **Tenant Guard**: All runtime and API queries include tenant predicates on
  scope, version, head, audit, run, bundle, and lineage tables. Missing,
  unauthorized, or cross-tenant ids return the same fail-closed not-found or
  forbidden semantics used by the platform.
- **Audit Guard**: Audit payloads include actor or workflow source, scope,
  version ids, run/bundle ids, action, outcome, hashes, and redacted summary.
  Raw memory JSON is never written to audit, timeline, logs, traces, or metrics.

## Concurrency And Transaction Decisions

- **Optimistic Head Check**: Non-initial writes update the head only when the
  current head equals the supplied `expected_current_version_id`. Stale writes
  return HTTP 409 / domain `MemoryConflict` and include the latest head id when
  the caller is authorized to see it.
- **Initial Race Handling**: Initial writes require `assert_no_current_head`.
  The repository attempts to insert the scope/head under the unique scope/head
  constraints and rejects the loser of a race with HTTP 409 instead of merging
  or overwriting.
- **Transaction Boundary**: Scope resolution, head row lock, version insert,
  head projection update, and audit insert run in one database transaction.
  The service emits domain events only after commit.
- **Locking Strategy**: Existing head rows are selected `FOR UPDATE` before
  non-initial writes. For first writes, the unique `memory_heads.memory_scope_id`
  constraint and unique natural scope key are the arbiter. This keeps the write
  path simple and avoids serializable isolation for all requests.
- **Database Immutability Guard**: Application code never updates
  `memory_versions`. The migration adds a PostgreSQL trigger that raises on
  `UPDATE` or `DELETE` of memory versions, providing a second line of defense
  for migrations, scripts, and future repository mistakes.
- **Idempotency**: Optional caller idempotency keys are unique per
  `(tenant_id, memory_scope_id, idempotency_key)`. Replayed runtime attempts
  with the same key return the already-created version when the content hash
  and expected-head precondition match; conflicting replays return 409.

## Retrieval APIs And Access Patterns

- **Current Head**: Resolve by natural scope or `memory_scope_id`, read
  `memory_heads`, join to `memory_versions`, and return version metadata,
  content hash, version id, sequence, and authorized content. Return
  `has_memory = false` when no head exists.
- **Version History**: List versions by scope ordered by descending
  `version_sequence`, with cursor pagination over `(version_sequence,
  memory_version_id)`. Content is included only when the caller is authorized
  for raw memory access.
- **Version Read**: Fetch a single version by id plus tenant predicate. The
  response includes previous/next lineage metadata when available and never
  mutates head state.
- **Replay**: Because each version is a canonical full snapshot, replay to a
  version returns that version's snapshot after verifying the target belongs to
  the requested scope. Lineage traversal is still available to prove ancestry
  and produce reviewer history.
- **Diff**: Validate both versions are tenant-visible and belong to the same
  memory scope. Produce JSON-pointer based additions, removals, and changes,
  treating explicit removal markers and JSON null as distinct values.
- **Audit Review**: List content-free memory audit entries by scope, version,
  run, bundle, actor, action, outcome, and time range. Audit views include
  hashes and redacted summaries only.

## Indexing Strategy

- `memory_scopes`: unique btree on
  `(tenant_id, workflow_lineage_id, agent_key, memory_key)`; secondary btree on
  `(tenant_id, workflow_lineage_id, agent_key)` for agent memory listings.
- `memory_versions`: primary key on `memory_version_id`; unique btree on
  `(tenant_id, memory_scope_id, version_sequence)`; btree on
  `(tenant_id, memory_scope_id, created_at desc)` for history; btree on
  `(tenant_id, previous_memory_version_id)` for lineage traversal; btree on
  `(tenant_id, workflow_run_id)` and `(tenant_id, run_bundle_id)` for runtime
  traceability; unique partial or full btree on idempotency key where present.
- `memory_heads`: unique btree on `memory_scope_id`; composite btree on
  `(tenant_id, workflow_lineage_id, agent_key, memory_key)` denormalized from
  the scope for single-index current-head lookup when needed.
- `memory_audit_events`: btree on `(tenant_id, created_at desc)`,
  `(tenant_id, memory_scope_id, created_at desc)`, `(tenant_id,
  memory_version_id)`, `(tenant_id, workflow_run_id)`, and `(tenant_id,
  action_type, outcome, created_at desc)`.
- `memory_archive_events`: btree on `(tenant_id, memory_version_id,
  archived_at desc)` and `(tenant_id, archived_at desc)`.
- `JSONB Content`: Do not add a broad GIN index on raw memory content in the
  initial implementation. Querying memory by arbitrary content is out of scope,
  and avoiding content indexes reduces privacy exposure and write overhead.

## Archival And Retention Decisions

- **Default Retention**: Scope, version lineage, head metadata, and audit
  metadata are retained indefinitely by default, matching the spec assumption
  and constitution. A later retention spec may introduce deletion or
  compaction, but it must preserve auditability and lineage semantics.
- **Archival Marker**: Archival state is recorded in append-only
  `memory_archive_events` rows linked to `memory_versions`, rather than by
  updating `memory_versions`. Archived versions remain immutable and replayable
  unless a future governance-approved retention policy redacts content.
- **Head Protection**: Current head versions cannot be marked as archived into
  an unavailable tier. If future cold storage is introduced, the head projection
  must continue to dereference the current version within the current-head
  latency target.
- **Large Payload Escape Hatch**: Initial implementation stores canonical JSON
  snapshots in PostgreSQL up to a configured size limit. If a memory snapshot
  exceeds the limit, the write is rejected until a later object-storage-backed
  memory payload spec defines encryption, retention, hashes, and replay rules.
- **Vacuum And Partition Readiness**: Audit events are candidates for monthly
  partitioning once volume requires it. The initial migration keeps standard
  tables and indexes, with table names and time columns chosen to support
  future partition migration.

## Tenant Fairness And Limit Decisions

- **Per-Tenant Budgets**: Memory write, current-head read, history, replay,
  diff, and audit-list operations are evaluated against tenant-scoped
  concurrency and rate budgets before expensive database or JSON work begins.
- **Noisy-Neighbor Controls**: Hot memory scopes may not monopolize shared
  workers or database sessions; repository and service calls expose
  tenant/action labels so limits can be enforced by middleware or runtime
  policy.
- **Payload Limits**: Canonical JSON snapshots remain bounded by the configured
  inline memory size limit. Oversized snapshots are rejected until an
  object-storage-backed memory payload spec exists.
- **Fairness Telemetry**: Metrics record tenant-scoped limit checks, throttled
  memory operations, conflict rates, and latency by operation type without raw
  memory content.
- **Test Coverage**: Policy, service, and integration tests must cover
  quota-denied writes, quota-denied replay/diff, and unchanged memory state
  after limit rejection.

## Observability And Security Decisions

- **Logs**: Structured logs record memory action, tenant id, scope id, version
  ids, run/bundle ids, conflict outcomes, latency, and trace id. Logs exclude
  raw memory content and redacted summaries can be omitted by configuration.
- **Metrics**: Counters cover writes, conflicts, initial-write races, reads,
  no-memory reads, replay requests, diff requests, authorization denials, audit
  failures, and archive marks. Histograms cover current-head lookup, write
  transaction duration, history list, replay, and diff latency.
- **Traces**: Runtime memory spans attach tenant id, workflow lineage id,
  memory scope id, version id, run id, bundle digest, and action outcome. Raw
  memory content is never attached to spans.
- **Access Checks**: Memory content read, version write, replay, diff, and
  audit review use separate policy checks so audit-only users can inspect
  metadata without receiving raw content.
- **Workflow Timeline Events**: Runtime memory reads, writes, conflicts,
  no-memory reads, replay requests, diff requests, authorization denials, and
  invalid comparisons emit content-free workflow timeline/debug events linked to
  tenant id, workflow run id, run step id, memory scope id, version ids, action,
  outcome, latency, and trace id.
- **Operator Debugging Surface**: Operators can diagnose memory behavior through
  audit records, structured logs, traces, metrics, and workflow timeline events
  without access to raw memory content unless separately authorized through
  memory read/replay/diff paths.
- **Security Review Notes**: Review must confirm tenant predicates are present
  in every repository query, audit contains no raw content, content hashes use
  canonical JSON bytes, runtime writes validate pinned bundle context, and DB
  triggers prevent version mutation.

## Test Strategy

- **Canonical JSON Unit Tests**: Validate deterministic ordering, hash
  stability, explicit nulls, explicit removal markers, rejection of unsupported
  values, and identical hashes for semantically identical snapshots.
- **Data Model Unit Tests**: Validate scope natural-key uniqueness, version
  sequence rules, predecessor requirements, head uniqueness, DB trigger
  immutability, idempotency constraints, append-only archive events, and
  archived-head protections.
- **Service Unit Tests**: Validate initial writes, non-initial writes,
  stale-head rejection, no-memory current-head result, authorized history,
  unauthorized fail-closed behavior, diff categories, replay target checks, and
  audit redaction.
- **Concurrency Integration Tests**: Use PostgreSQL-backed async sessions to
  run racing initial writes and racing non-initial writes; assert only one
  succeeds, no prior version is mutated, and the head points to the accepted
  version.
- **Runtime Integration Tests**: Start a pinned workflow run fixture, perform
  memory reads and writes from root and child runs, verify bundle/run/step and
  `runtime_run_lineage` links, simulate resume with the same idempotency key,
  and confirm stale resumed work cannot advance memory.
- **API Contract Tests**: Validate OpenAPI examples for write, current-head,
  history, replay, diff, and audit paths with success, 403/404, and 409 cases.
- **Coverage Gate**: `uv run pytest --cov=src/multi_agent_platform
  --cov-report=term-missing --cov-fail-under=90` remains the required coverage
  command; PR evidence must include the coverage summary and focused memory
  test output.

## Complexity Tracking

No constitution violations or justified complexity exceptions.
