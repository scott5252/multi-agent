# Implementation Plan: Durable Orchestration Runtime

**Branch**: `004-durable-orchestration-runtime` | **Date**: 2026-04-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-durable-orchestration-runtime/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a durable LangGraph orchestration runtime that starts only published
workflow bundles, clones each bundle into a pinned per-run execution record,
executes workflow graphs through background workers, persists graph checkpoints
and platform run metadata in PostgreSQL, validates explicit handoff envelopes,
captures side-effect intents before external actions, and resumes interrupted
runs after worker or node failure. The design uses the current LangChain and
LangGraph Python line, `AsyncPostgresSaver` for graph checkpoints, SQLAlchemy
runtime tables for leases, lineage, approvals, handoffs, audit, and side-effect
intent tracking, plus FastAPI contracts for starting, inspecting, approving,
and cancelling runs.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9,
langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff,
mypy, uv  
**Storage**: PostgreSQL for workflow runs, run steps, worker leases, LangGraph
checkpoints, handoff envelopes, side-effect intents, approval gates,
parent-child lineage, audit events, and retention policy metadata; existing
artifact/object storage providers for oversized payload bodies and generated
run artifacts referenced from PostgreSQL  
**Testing**: pytest unit tests for state machines, repositories, contract
validation, worker leasing, checkpoint policy, side-effect intent handling,
approval behavior, and lineage; FastAPI contract tests for runtime APIs;
PostgreSQL-backed integration tests for LangGraph checkpointer setup, crash and
resume, lease expiry, and idempotent side-effect replay; coverage enforcement at
>=90 percent for relevant runtime code  
**Target Platform**: Linux container deployment target for FastAPI API and
background workers; local development on macOS/Linux; PostgreSQL-backed worker
and runtime execution under the existing platform bootstrap model  
**Project Type**: Multi-tenant backend platform with JSON APIs, background
workers, durable workflow runtime services, and operator-facing documentation  
**Performance Goals**: 99 percent of accepted run-start requests persist a
durable initial state within 2 seconds; worker claim p95 <200ms under expected
development-test load; run inspection p95 <300ms for runs with <=500 steps;
handoff validation p95 <100ms for normal payloads; abandoned claims become
eligible exactly after configured expiry with 2-minute default  
**Constraints**: Execute only published workflow bundles; pin the execution
bundle before any agent work; use PostgreSQL as transactional source of truth;
use object storage for large payloads; default child cancellation policy is
cascade-cancel; default approval timeout is no automatic timeout; default worker
claim expiry is 2 minutes; default checkpoint and run payload reference
retention is 90 days while audit and lineage are retained indefinitely; all
runtime actions must preserve tenant, authorization, quota, delegated
credential, and audit context; >=90 percent unit-test coverage and README
update required  
**Scale/Scope**: Initial scope supports hundreds of active or paused workflow
runs per tenant, thousands of historical runs platform-wide, nested
subworkflow trees at least 5 levels deep, low dozens of concurrent workers,
and payload bodies large enough to require object-storage references rather
than PostgreSQL blob storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | LangGraph checkpoints, platform run state, worker leases, side-effect intents, approval waits, retry state, and lineage are persisted before they become authoritative. |
| Immutable State And Memory | PASS | Runtime state changes are represented as versioned records and append-only audit/timeline events; mutable in-memory worker state is never the source of truth. |
| Contract-First Agent Coordination | PASS | Agent handoffs use versioned envelopes, pinned contract digests, strict validation, explicit failure routes, and contract tests before receiver consumption. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal flows and authorization checks gate APIs, workers, approvals, delegated credentials, and tenant scope without adding production bypasses. |
| Operability Is A Product Requirement | PASS | Plan defines structured logs, metrics, traces, run timeline, lineage traversal, replay-ready checkpoints, failure diagnostics, and runbook/README updates. |
| Spec-Driven Delivery | PASS | Clarified spec, plan, research, data model, contracts, quickstart, and future tasks remain traceable to the durable runtime requirements. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent unit coverage, crash/resume tests, contract tests, README updates, quickstart validation, and PR evidence. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across runtime orchestration services, DB models/repositories, API schemas/routers, workers, migrations, and targeted tests. |
| Tenant Isolation And Fair Scheduling | PASS | Every runtime record carries tenant context; worker claiming is tenant-aware and quota-aware; cross-tenant access fails closed and is audited. |
| Version-Pinned Execution | PASS | Each run clones an immutable execution bundle containing workflow, subworkflow, contract, prompt, model, and tool-policy versions before any graph node executes. |
| Secret Hygiene And Controlled Tool Access | PASS | Side-effect intents store only secret references and delegated credential metadata; runtime tool access uses allowlists, egress policy, and audit events. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores metadata, checkpoints, envelopes, refs, and audit records; large payload bodies and artifacts use object storage anchored by PostgreSQL metadata. |
| Human Approval Is Durable State | PASS | Approval gates enter persisted wait state, use LangGraph interrupts and approval records, and resume only through auditable decisions with the same pinned bundle. |

Post-Phase-1 re-check: design artifacts below keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/004-durable-orchestration-runtime/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── runtime-orchestration.openapi.yaml
│   └── worker-runtime-protocol.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── multi_agent_platform/
    ├── api/
    │   ├── routers/
    │   │   └── runtime_runs.py              # new runtime JSON API
    │   └── schemas/
    │       └── runtime_runs.py              # new API schemas
    ├── bootstrap/
    │   ├── container.py                     # wire runtime services
    │   └── worker.py                        # wire orchestration worker
    ├── db/
    │   ├── models/
    │   │   └── runtime_orchestration.py     # new runtime tables
    │   └── repositories/
    │       └── runtime_orchestration.py     # new DB access
    ├── runtime/
    │   ├── orchestration/
    │   │   ├── __init__.py                  # new package
    │   │   ├── approvals.py                 # approval wait/resume rules
    │   │   ├── checkpointing.py             # LangGraph checkpointer adapter
    │   │   ├── compiler.py                  # bundle-to-graph assembly
    │   │   ├── contracts.py                 # contract validation
    │   │   ├── events.py                    # timeline/audit event models
    │   │   ├── handoffs.py                  # handoff envelope service
    │   │   ├── leasing.py                   # worker claim policy
    │   │   ├── lineage.py                   # parent-child run service
    │   │   ├── models.py                    # runtime domain models
    │   │   ├── repository.py                # service-facing repository
    │   │   ├── service.py                   # run start/inspect/cancel/resume
    │   │   ├── side_effects.py              # intent capture and compensation
    │   │   └── state.py                     # graph state schema
    │   ├── versioning.py
    │   └── workflow_bundle.py               # extend run bundle blueprint
    ├── workers/
    │   ├── loops.py                         # route orchestration work
    │   └── orchestration.py                 # new worker loop/handler
    └── observability/
        ├── logging.py
        ├── metrics.py
        └── tracing.py
alembic/versions/
└── 0004_durable_orchestration_runtime.py    # new migration
tests/
├── contract/
│   └── test_runtime_orchestration_contract.py
├── integration/
│   ├── runtime/
│   │   ├── test_langgraph_checkpoint_resume.py
│   │   ├── test_orchestration_crash_resume.py
│   │   └── test_runtime_api_flows.py
│   └── workers/
│       └── test_orchestration_worker.py
├── unit/
│   ├── api/
│   │   └── test_runtime_run_schemas.py
│   ├── db/
│   │   └── test_runtime_orchestration_models.py
│   └── runtime/
│       └── orchestration/
│           ├── test_approvals.py
│           ├── test_contracts.py
│           ├── test_handoffs.py
│           ├── test_leasing.py
│           ├── test_lineage.py
│           ├── test_service.py
│           └── test_side_effects.py
README.md
docs/quickstart.md
docs/durable-orchestration-runtime.md        # new operator/runbook doc
```

**Structure Decision**: Keep the durable runtime inside the existing Python
package, FastAPI application, SQLAlchemy/Alembic database layer, worker
bootstrap, and observability helpers. Add a focused `runtime/orchestration`
package so graph execution, leases, contracts, handoffs, side effects,
approvals, and lineage can be implemented and tested independently without
rewriting the existing workflow registry or queue foundation.

## Failure Recovery And Durability Decisions

- **Checkpoint Boundaries**: Compile every executable workflow graph with
  `AsyncPostgresSaver` and use `thread_id = workflow_run_id` for the root run
  and `thread_id = child_run_id` for each child run. LangGraph persists graph
  state at super-step boundaries. The platform also writes runtime metadata at
  run creation, worker claim/renewal/release, before and after every handoff,
  before every external side-effect intent, after every side-effect result,
  when entering approval wait state, when resuming from approval, at child-run
  creation/completion, and on terminal state.
- **Retry Strategy**: Default retry policy is 3 attempts with exponential
  backoff and jitter for transient node, model, tool, and storage errors.
  Contract violations, authorization denials, quota denials, incompatible
  checkpoints, and missing pinned bundles do not retry automatically. Retry
  state is persisted per run step and per side-effect intent so resume uses the
  same attempt budget. Worker leases expire by workflow or tenant policy with a
  2-minute default, and expired leases become eligible for another worker.
- **Compensation Strategy**: External side effects require a captured intent
  record before execution. Workflows may declare compensation hooks by bundle
  reference. Compensation hooks run as explicit workflow steps with their own
  intents and audit events; the runtime never invents a compensation for an
  undeclared side effect. If a side effect has no compensation hook, recovery
  relies on idempotent replay and operator diagnostics.
- **Idempotency Strategy**: Every run, step, handoff, child run, approval
  decision, and side-effect intent uses deterministic idempotency keys derived
  from tenant id, run id, step id, bundle digest, attempt number, and operation
  kind. Resume first checks existing completed intents and handoff envelopes;
  completed externally visible actions return their recorded result instead of
  being repeated.

## Tenant Isolation And Fair Use Decisions

- **Tenant Context Propagation**: `tenant_id`, `scope_type`, initiating
  principal, delegated credential metadata, and trace id flow from run-start
  request into the pinned bundle, LangGraph config, worker lease, checkpoint
  metadata, handoff envelope, side-effect intent, approval gate, child run, and
  audit event.
- **Isolation Controls**: Runtime repositories require tenant-scoped predicates
  for reads and writes. Workers claim only work visible to their platform role
  and preserve the run tenant on every mutation. Cross-tenant run ids,
  approval ids, handoff ids, child-run ids, and artifact refs fail closed.
- **Quota And Fairness Controls**: Worker claiming orders runnable work by
  tenant concurrency budget, priority, and age. Tenant limits cover active
  runs, active child runs, worker leases, pending approval count, side-effect
  retry budget, and checkpoint/payload storage retention. Metrics expose
  denied starts, throttled claims, active leases, and per-tenant queue depth.

## Subworkflow And Parent-Child Lineage Decisions

- **Subworkflow Boundaries**: A published subworkflow executes as a separate
  workflow run with its own LangGraph thread and pinned child execution bundle.
  Parent graph nodes create and await child runs through the orchestration
  service instead of embedding child state as opaque in-memory calls.
- **Parent-Child Run Model**: Child runs store `parent_run_id`,
  `parent_step_id`, `relationship_reason`, inherited tenant context, child
  bundle digest, join policy, cancellation policy, and status propagation
  rules. The default child cancellation policy is cascade-cancel unless the
  parent workflow declares another policy.
- **Replay And Debug Visibility**: Operators can traverse lineage from parent
  to children and child to parent, inspect child checkpoint ids, view join
  outcomes, and compare child output envelopes against the parent step
  contract.

## Version Bundle And Contract Decisions

- **Pinned Bundle Contents**: A per-run bundle record copies the published
  workflow version id, workflow digest, subworkflow version ids, handoff
  contract versions and digests, prompt versions, model configuration versions,
  tool-policy versions, approval timeout behavior, child cancellation policy,
  retry policy, checkpoint policy, and compiler/runtime version metadata.
- **Resume Policy**: Resume always uses the per-run pinned bundle. Published
  workflow changes affect only future runs. In-flight migration is out of
  scope unless a later spec adds an explicit audited migration command.
- **Contract Compatibility Plan**: Runtime validates handoff payloads against
  the exact pinned contract digest. Invalid payloads are stored as rejected
  handoff envelopes and follow the workflow's declared failure route, defaulting
  to failure of the affected run path. Contract evolution is handled at publish
  time by the registry; runtime never swaps contract versions mid-run.

## Secret Management And Tool Policy Decisions

- **Secret Manager Integration**: Runtime records store secret references and
  delegated credential references only. Workers resolve secrets just-in-time
  through the existing secret manager adapter and redact values from logs,
  checkpoints, handoff envelopes, and audit records.
- **Delegated Credential Handling**: Run start captures delegated credential
  linkage and validity metadata. Resume revalidates credential availability
  before executing a side-effect intent; expired or revoked credentials move
  the affected step to recoverable failure or approval-required state according
  to workflow policy.
- **Tool Access Policy**: Tool execution checks the pinned bundle allowlist,
  outbound egress policy, tenant quota, delegated credential scope, and
  side-effect intent state before execution. Denied tool use is audited and is
  not retried automatically.

## Artifact Storage Decisions

- **Transactional Metadata**: PostgreSQL stores run metadata, step state,
  worker leases, checkpoint references, handoff envelope metadata, small
  payload summaries, side-effect intent state, approval decisions, lineage,
  retention settings, and audit events.
- **Blob Storage**: Large handoff payload bodies, run artifacts, transcripts,
  model/tool raw outputs, and exports use the existing object storage provider
  with PostgreSQL artifact metadata and content hashes.
- **Retention And Access**: Tenant-configurable retention applies to
  checkpoints and run payload references with a 90-day default. Audit events
  and run lineage are retained indefinitely by default. Access checks use the
  run tenant and artifact metadata before any payload ref is resolved.

## Approval And Resume Decisions

- **Approval Triggers**: Approval gates come from the pinned execution bundle
  and may be triggered by graph nodes, contract failure routes, delegated
  credential gaps, or explicit human-review nodes.
- **Persisted Wait State**: Approval nodes use LangGraph `interrupt()` with a
  JSON-serializable payload and persist a platform `ApprovalGate` record. The
  run remains paused until an authorized approval, rejection, cancellation, or
  workflow-declared timeout behavior occurs. The default timeout behavior is no
  automatic timeout.
- **Audit Trail**: Approval requested, viewed, approved, rejected, duplicated,
  denied, cancelled, timed out, and resumed events are captured with principal,
  tenant, run id, gate id, decision payload hash, and trace id. Resume invokes
  LangGraph with `Command(resume=...)` and the same `thread_id`.

## Observability Requirements

- **Logs**: Structured logs for run start, bundle pin, worker claim/renewal,
  checkpoint reference, handoff validation, side-effect intent transitions,
  approval wait/resume, child-run transitions, retries, compensation, terminal
  state, and retention cleanup. Logs include tenant id, run id, step id, lease
  id, child run id, bundle digest, trace id, and redaction flags.
- **Metrics**: Counters and histograms for run-start latency, claim latency,
  active leases, expired leases, checkpoint writes, resume attempts, retry
  attempts, contract violations, approval wait age, child-run counts,
  side-effect intent statuses, terminal outcomes, per-tenant throttling, and
  storage-retention cleanup.
- **Traces**: Distributed traces propagate through API request, run creation,
  worker claim, graph node execution, handoff validation, side-effect execution,
  approval pause/resume, and child-run orchestration. External tool spans carry
  intent id and redacted credential reference.
- **Timeline And Replay**: Authorized users can inspect current state, state
  history, run timeline, checkpoint ids, lineage tree, handoff envelope status,
  retry history, side-effect intents, approval decisions, and terminal result.
- **Operational Runbooks**: README and feature docs cover starting workers,
  checking checkpoint health, diagnosing expired leases, resuming after crash,
  finding blocked approvals, investigating contract failures, and validating
  retention behavior.

## Test Strategy

- **Unit Tests**: Cover runtime domain models, run state transitions, pinned
  bundle cloning, worker lease expiry and exclusivity, contract validator,
  handoff envelope status, side-effect intent idempotency, compensation hook
  selection, approval gate state, lineage traversal, quota guards, and
  retention policy calculations. Maintain >=90 percent unit coverage for new
  runtime code.
- **Integration And Contract Tests**: Validate OpenAPI request/response shapes,
  FastAPI authorization and tenant scoping, repository persistence, Alembic
  migration, object-storage payload refs, and LangGraph/Postgres checkpointer
  setup against a PostgreSQL test service.
- **Failure And Recovery Tests**: Simulate worker crash after checkpoint, crash
  after side-effect intent creation, crash after side-effect completion before
  ack, expired lease takeover, duplicate worker claim, invalid handoff, paused
  approval across restart, child-run failure propagation, parent cancellation,
  and terminal run with stale queued work.
- **Operational Validation**: Quickstart requires run-start, worker execution,
  forced worker stop, resume from checkpoint, approval pause/resume, contract
  failure, child-run lineage inspection, metrics exposure, and README evidence.

## Documentation Tasks

- **README.md Updates**: Add runtime worker startup, required dependency
  versions, Postgres checkpointer setup, run-start API example, crash/resume
  test command, approval-resume example, and retention defaults.
- **Quickstart Updates**: Add feature quickstart in
  `specs/004-durable-orchestration-runtime/quickstart.md` and link the broader
  operator flow from `docs/quickstart.md` when implementation lands.
- **Feature Docs**: Add `docs/durable-orchestration-runtime.md` with operator
  runbook, failure modes, handoff contract troubleshooting, side-effect intent
  behavior, compensation hook expectations, lineage inspection, and retention.
- **PR Evidence Requirements**: PR description must include coverage summary,
  latest LangChain/LangGraph versions used, migration evidence, crash/resume
  logs, approval pause/resume logs, contract validation evidence, worker lease
  takeover evidence, and README/doc updates.

## Security Review Notes

- **Auth/Authz Impact**: Runtime APIs, approval decisions, cancellation, run
  inspection, and worker actions must reuse existing Auth0/local-principal
  authorization checks and emit audit events.
- **Tenant/Security Boundaries**: Highest risks are cross-tenant run inspection,
  cross-tenant worker claims, payload reference leakage, stale delegated
  credentials on resume, and child-run inheritance of the wrong tenant context.
- **Secret/Tool Risk Review**: Review secret-reference-only persistence,
  redaction in checkpoints/logs, tool allowlist enforcement, outbound egress
  policy, and side-effect intent payload handling before merge.
- **Additional Review Needed**: Security review is required for delegated
  credential resume and persisted side-effect intent metadata. Privacy review
  is required if future payload categories include regulated data beyond the
  existing tenant data model.

## Complexity Tracking

No constitution violations or exceptions are required.
