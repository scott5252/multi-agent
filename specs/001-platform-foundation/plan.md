# Implementation Plan: Platform Foundation

**Branch**: `001-platform-foundation` | **Date**: 2026-04-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-platform-foundation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Establish the production-grade Python foundation for the Multi-Agent AI
Platform as a single deployable codebase with thin API and worker entrypoints,
shared platform modules, async PostgreSQL persistence, operational placeholder
HTTP contracts, tenant/secret/artifact/queue abstractions, and quality gates
that make later workflow, auth, memory, admin, and audit specs additive rather
than restructuring.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic Settings, LangChain, LangGraph,
SQLAlchemy 2.x, Alembic, psycopg 3, pytest, pytest-asyncio, httpx, Ruff, mypy,
uv  
**Storage**: PostgreSQL 16+ for transactional state and metadata; filesystem
artifact provider in local/test; optional MinIO for local S3-compatible
integration; S3-compatible object storage in production  
**Testing**: pytest, pytest-asyncio, httpx, FastAPI dependency overrides,
OpenAPI contract validation, pytest-cov  
**Target Platform**: Linux container deployment target; local development on
macOS/Linux using Docker Compose-backed infrastructure  
**Project Type**: Multi-tenant backend platform foundation with API and worker
entrypoints  
**Performance Goals**: Operational endpoints p95 <100ms when healthy; readiness
evaluation <1s after dependency checks complete; API/worker cold start <60s
after dependencies are healthy. CI duration is monitored for regressions but is
not a release gate for this feature  
**Constraints**: No user-facing channels beyond operational endpoints;
fail-closed tenant scoping; rollback validated in local/test only; identical
secret abstraction in every environment; 90 percent unit-test minimum for
relevant code; operational endpoints only  
**Scale/Scope**: One API and one worker entrypoint in scope now, designed for
later horizontal worker scaling, multi-tenant isolation, and future Web UI,
Telegram, and public API feature layers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Foundation persists migration, queue, lease, artifact, and audit state in PostgreSQL and reserves runtime checkpointer/outbox boundaries for later workflow durability. |
| Immutable State And Memory | PASS | Queue events, audit events, and artifact metadata are planned as append-oriented records; no shared mutable in-memory coordination is used as the source of truth. |
| Contract-First Agent Coordination | PASS | Operational placeholder endpoints are versioned through an OpenAPI contract, and internal runtime/queue schemas are explicitly modeled for later execution work. |
| Security With Practical Development Ergonomics | PASS | Auth is abstracted behind shared dependencies, dev/test stand-ins remain explicit, and secret handling stays behind the same provider boundary in every environment. |
| Operability Is A Product Requirement | PASS | Strict readiness, liveness, dependency status, structured logging, correlation IDs, and audit/event hooks are first-class requirements. |
| Spec-Driven Delivery | PASS | Spec, clarification log, research, data model, contract, quickstart, and plan are all generated before tasks or implementation. |
| Test And Documentation Discipline | PASS | pytest, contract tests, coverage enforcement, README updates, quickstart updates, and PR evidence requirements are part of the plan. |
| Clear Ownership And Small Safe Changes | PASS | Thin entrypoints and explicit module boundaries keep future tasks file-specific and reduce later cross-cutting refactors. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant context fails closed, system scope is explicit, `tenant_id` is mandatory on tenant-scoped tables, and queue abstractions preserve later fairness controls. |
| Version-Pinned Execution | PASS | No workflow execution is implemented yet, but the runtime package reserves explicit execution-bundle interfaces and correlation fields so later pinning is additive. |
| Secret Hygiene And Controlled Tool Access | PASS | Secret material is never stored in app data, providers resolve by reference, and tool-policy hooks are reserved even though live tool execution is out of scope. |
| Tiered Storage For Large Payloads | PASS | Artifact metadata remains in PostgreSQL while blob contents move to filesystem/S3-compatible providers behind a shared abstraction. |
| Human Approval Is Durable State | PASS | Approval flows are not in this feature’s runtime scope, but the runtime and audit boundaries remain compatible with future persisted wait-state support. |

## Project Structure

### Documentation (this feature)

```text
specs/001-platform-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ops-api.openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── multi_agent_platform/
    ├── api/
    │   ├── main.py
    │   ├── lifespan.py
    │   ├── deps.py
    │   ├── routers/
    │   │   └── ops.py
    │   └── schemas/
    │       └── ops.py
    ├── admin/
    ├── audit/
    ├── auth/
    ├── bootstrap/
    │   ├── container.py
    │   └── worker.py
    ├── config/
    │   └── settings.py
    ├── db/
    │   ├── base.py
    │   ├── session.py
    │   ├── models/
    │   └── repositories/
    ├── memory/
    ├── observability/
    ├── runtime/
    │   ├── health/
    │   ├── queue/
    │   └── versioning.py
    ├── secrets/
    ├── storage/
    ├── tenancy/
    └── workers/
        ├── main.py
        └── loops.py
alembic/
tests/
├── unit/
├── integration/
├── contract/
└── fixtures/
.github/workflows/ci.yml
compose.yaml
pyproject.toml
uv.lock
README.md
docs/quickstart.md
```

**Structure Decision**: Use a single Python distribution with a `src/`
package for all reusable platform code and thin `api` and `workers` subpackage
entrypoints. This keeps API, runtime, memory, auth, admin, audit, tenancy,
secret, and artifact concerns separated without introducing multi-package build
overhead before the platform actually has multiple independently releasable
services. `compose.yaml`, Alembic, and CI live at the repo root so local
development and pipeline commands stay predictable.

## Failure Recovery And Durability Decisions

- **Checkpoint Boundaries**: The foundation will durably commit migration state,
  queue job transitions, queue leases, artifact metadata, secret references,
  and audit events in PostgreSQL. Any future external side-effect emitter must
  write its outbox intent in the same transaction as the state mutation it
  depends on. Runtime checkpointer and outbox interfaces will live in
  `runtime/` and `audit/` so later LangGraph workflow persistence can reuse the
  same unit-of-work boundary.
- **Retry Strategy**: API and worker bootstrap will use bounded exponential
  backoff for transient dependency failures. Queue leases will use heartbeats
  and expiry-based reclamation. Automatic retries stop at explicit migration
  errors, invalid configuration, or authorization/tenant-scope failures.
- **Compensation Strategy**: No business compensation is implemented in this
  feature. Foundation compensation is limited to releasing leases, abandoning
  incomplete startup resources, and replay-safe outbox behavior. Shared and
  production schema failures are recovered through documented forward-fix or
  operator-controlled restore, not blind rollback automation.
- **Idempotency Strategy**: Queue jobs, future outbox events, and worker
  dispatches carry explicit idempotency keys. Migration commands are serialized
  per environment. Artifact completion verifies checksum and metadata before an
  upload is marked available.

## Tenant Isolation And Fair Use Decisions

- **Tenant Context Propagation**: HTTP middleware and FastAPI dependencies will
  construct a `ScopeContext` carrying `tenant_id`, `scope_type`, `trace_id`,
  and request metadata. Worker envelopes must carry either a tenant context or
  an explicit system context; no implicit default tenant is allowed.
- **Isolation Controls**: Tenant-scoped tables require `tenant_id`. Repository
  methods refuse tenant-scoped access without context. Schema and repository
  boundaries remain ready for PostgreSQL row-level security in later specs, and
  operational endpoints run only under explicit platform scope.
- **Quota And Fairness Controls**: The foundation persists tenant limit policy
  records and queue priority/availability fields. The initial queue abstraction
  will be PostgreSQL-backed and leasing-aware, with scheduling strategy hooks
  so weighted fair queueing or fair round-robin can be added later without
  changing callers.

## Subworkflow And Parent-Child Lineage Decisions

- **Subworkflow Boundaries**: The `runtime/` package owns future orchestration,
  workflow compilation, worker dispatch, and state checkpoint integration. The
  `memory/` package owns immutable memory concerns. API routes and workers call
  into those modules rather than embedding orchestration logic directly.
- **Parent-Child Run Model**: Full workflow execution is not implemented in this
  feature, but queue envelopes, audit events, and future artifact records will
  reserve optional `run_id`, `parent_run_id`, and `trace_id` fields from day
  one so later lineage support does not require a schema reshape.
- **Replay And Debug Visibility**: Every operational request, queue lease, and
  startup check will carry correlation identifiers so future runtime replay and
  operator timelines can join foundation-era audit data with later workflow
  records.

## Version Bundle And Contract Decisions

- **Pinned Bundle Contents**: The foundation introduces a `runtime/versioning`
  boundary that will own future execution-bundle references for workflow,
  contract, prompt, model, and tool-policy versions. No workflow bundles are
  persisted in this feature because no executable workflows are introduced yet.
- **Resume Policy**: Workflow resume is out of scope for this feature, but the
  foundation avoids mutable module-level execution configuration and keeps all
  settings, providers, and future bundle lookups injectable so later resume
  logic can stay pinned to explicit references.
- **Contract Compatibility Plan**: Operational placeholder endpoints are
  versioned via the OpenAPI document in `contracts/ops-api.openapi.yaml`. Schema
  changes must remain additive unless a later spec explicitly introduces a
  breaking contract migration.

## Secret Management And Tool Policy Decisions

- **Secret Manager Integration**: All environments use a shared
  `SecretProvider` interface. Local and test use safe stand-in providers backed
  by environment variables or static test fixtures; production uses a secret
  manager adapter. Application code only receives resolved secret values from
  the provider, never raw environment reads.
- **Delegated Credential Handling**: User-delegated credentials are out of
  scope for this feature. The foundation reserves a separate provider boundary
  so later user-delegated tokens do not share persistence or access patterns
  with platform-managed secrets.
- **Tool Access Policy**: No live tool execution is introduced in this feature.
  The runtime and secrets packages will still reserve policy-model hooks for
  allowed secret references and outbound destinations so later tool execution is
  added without reworking the configuration model.

## Artifact Storage Decisions

- **Transactional Metadata**: PostgreSQL stores artifact ownership, scope,
  retention class, provider, checksum, media type, size, and correlation fields.
- **Blob Storage**: Local and test environments default to a filesystem-backed
  provider behind the shared storage interface. `compose.yaml` includes an
  optional MinIO profile for local S3-compatible validation. Production targets
  an S3-compatible object store.
- **Retention And Access**: Providers return handles or signed-access metadata;
  blobs never live in PostgreSQL. Retention classes drive cleanup behavior, and
  readiness should not fail on optional local storage profiles that are not
  enabled.

## Approval And Resume Decisions

- **Approval Triggers**: None. The platform foundation does not implement human
  approval or supplemental-input flows.
- **Persisted Wait State**: Not implemented in this feature. Runtime status
  models and audit schema must remain extensible enough to add `waiting_for_input`
  later without changing entrypoint boundaries.
- **Audit Trail**: The audit/event model already records action type, actor,
  scope, and correlation IDs so future approval requests and resumes can append
  to the same audit spine.

## Observability Requirements

- **Logs**: Structured JSON logs with `trace_id`, `request_id`, `tenant_id`,
  `scope_type`, `process_role`, and event name. Configuration, migration,
  tenant, and secret failures log only redacted context.
- **Metrics**: Prometheus-compatible counters and gauges for request volume,
  readiness check results, dependency failures, queue depth, active leases,
  worker heartbeat age, and migration drift.
- **Traces**: OpenTelemetry instrumentation for FastAPI and SQLAlchemy with
  W3C trace context propagated from API requests into worker envelopes.
- **Timeline And Replay**: Full workflow timelines are deferred, but foundation
  audit events and queue events must be queryable by trace ID and tenant to
  support later replay tooling.
- **Operational Runbooks**: `README.md`, `docs/quickstart.md`, and a new
  foundation runbook must cover startup, migrations, readiness failures,
  dependency outages, and local storage/secret provider troubleshooting.

## Test Strategy

- **Unit Tests**: Cover settings parsing, dependency/container wiring, readiness
  aggregation, queue lease rules, tenant scope guards, secret-provider
  abstraction behavior, artifact provider behavior, and audit event assembly.
  The target is >=90 percent unit coverage for relevant code.
- **Integration And Contract Tests**: Validate Alembic upgrade/downgrade in
  local/test, FastAPI operational endpoints, worker bootstrap, dependency
  overrides, queue repository behavior against PostgreSQL, and the OpenAPI
  contract for operational endpoints.
- **Failure And Recovery Tests**: Simulate missing configuration, unreachable
  database, stale migration state, lease expiry and reclaim, secret-provider
  failure, and artifact-provider failure. No workflow replay tests are required
  yet because workflow execution is not in scope.
- **Operational Validation**: Run the documented Docker Compose bootstrap,
  readiness/liveness smoke checks, optional MinIO profile smoke checks, lint,
  type checks, and coverage enforcement in CI.

## Documentation Tasks

- **README.md Updates**: Add repository layout, dependency management, local
  bootstrap, migration workflow, operational endpoints, and CI expectations.
- **Quickstart Updates**: Add `uv` setup, `docker compose` infrastructure
  bootstrap, migration commands, API and worker startup commands, validation
  curls, and cleanup steps.
- **Feature Docs**: Add a foundation runbook for readiness failures, migration
  recovery expectations, tenant context rules, secret-provider rules, and
  artifact provider behavior.
- **PR Evidence Requirements**: Coverage summary, lint/type-check output,
  migration smoke-test result, operational endpoint smoke-test output, and any
  contract-test result diffs reviewers should inspect.

## Security Review Notes

- **Auth/Authz Impact**: This feature introduces auth and principal abstraction
  boundaries only. Auth0 integration and external identity validation are
  deferred, but dev/test principal behavior must remain explicit and auditable.
- **Tenant/Security Boundaries**: Tenant-scoped work fails closed without
  explicit tenant context. Operational endpoints run under explicit platform
  scope. No implicit default tenant is allowed.
- **Secret/Tool Risk Review**: Secret resolution always flows through the same
  provider interface in every environment. Raw secret injection into platform
  code is disallowed. Tool execution remains out of scope but future policy
  hooks are reserved.
- **Additional Review Needed**: Perform a lightweight threat-model review for
  operational endpoints, queue lease ownership, and local/test secret stand-ins
  before implementation starts.

## Complexity Tracking

No constitution violations or approved exceptions are required at planning
time.
