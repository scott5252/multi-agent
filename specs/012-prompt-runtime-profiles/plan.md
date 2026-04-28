# Implementation Plan: Prompt Runtime Profiles V2 Runtime Gateway Completion

**Branch**: `012-prompt-runtime-profiles` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-prompt-runtime-profiles/spec.md`

**Note**: Version 2 is additive to the completed Spec 012 prompt library and
agent runtime profile implementation. The plan preserves prompt authoring,
prompt lifecycle, runtime profile management, browser UI, workflow validation,
model-skill prompt reference integration, tenant grants, immutable versioning,
retirement, docs, and migration behavior except for narrow integration points
needed to route model-backed execution through `ModelGateway`.

## Summary

Close the remaining runtime/provider execution gaps by wiring Spec 011
`ModelGateway` dependencies through the application container and worker
bootstrap, then requiring every model-backed runtime, test bench, and
model-backed validation path to invoke through gateway-managed provider
adapters after Spec 012 prompt/profile pins are resolved. The implementation
adds durable idempotency identities for gateway invocations, provider probes,
and catalog sync; maps normalized provider errors into existing retry and
circuit breaker policy decisions; persists safe gateway attempt evidence; and
adds static plus behavioral guardrails that detect direct provider SDK or HTTP
calls outside allowed adapter modules.

The plan is intentionally narrow: V1 prompt/profile records and browser flows
remain authoritative, and V2 adds runtime invocation context, operation
recovery, observability, and guardrail layers around the existing services.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, existing prompt runtime profiles, existing model_skill_config catalog/resolver, existing Spec 011 ModelGateway/provider adapters, existing reliability retries/breakers, existing audit/redaction helpers, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: PostgreSQL 16+ for existing prompt/profile governance plus additive gateway operation identities, provider probe operation identities, catalog sync operation identities, physical attempt summaries, retry/breaker summaries, prompt/profile/provider provenance links, and safe audit records
**Testing**: pytest, pytest-asyncio, httpx, Alembic migration tests, contract
tests, integration tests for worker/runtime/test bench paths, static guardrail
tests, browser/admin API tests, Ruff, mypy, coverage gate at 90 percent for
submitted code
**Target Platform**: Linux web and worker services using the existing FastAPI
application and async worker process model
**Project Type**: Python web service and durable worker runtime
**Performance Goals**: No unmanaged provider HTTP client per request; gateway
dependencies are container-managed and reused across worker lifetimes. Gateway
attempt recording, retry/breaker decisions, and audit summaries must add
bounded database writes without blocking run queue leasing or worker shutdown.
**Constraints**: Preserve backward-compatible defaults for historical runs and
completed V1 workflows. Fail closed when prompt/profile pins, catalog
visibility, connection health, credential refs, retry/breaker state, or tenant
authorization cannot be verified. Never persist raw prompts, completions,
credentials, provider tokens, API keys, local endpoint secrets, unsafe preview
content, or unauthorized run content in records/logs/audits.
**Scale/Scope**: Applies to all model-backed runtime execution, test bench
execution, model-backed workflow validation, provider probes, catalog sync, and
run provenance review for the existing multi-tenant platform.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. The plan defines one logical operation
  identity per gateway invocation, provider probe, and catalog sync, with
  child physical attempts and recovery states for retries, restarts, duplicate
  suppression, replay, and ambiguous recovery.
- **II. Immutable State And Memory**: PASS. Existing prompt/profile pins remain
  immutable. V2 appends gateway operation and attempt records without rewriting
  historical prompt, profile, run, or gateway records.
- **III. Contract-First Agent Coordination**: PASS. Gateway invocation context,
  worker dependencies, provenance summaries, and guardrails are documented in
  contracts before implementation.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0/local
  principal modes continue through existing authorization checks. Runtime
  profile hints cannot bypass model_skill_config authorization, tenant
  visibility, tool policy, memory policy, or credential checks.
- **V. Operability Is A Product Requirement**: PASS. The plan requires
  metrics, traces, timeline/audit links, retry and breaker summaries, latency,
  usage availability, normalized outcome, and safe provider provenance.
- **VI. Spec-Driven Delivery**: PASS. V2 spec, plan, research, data model,
  contracts, and quickstart are maintained before tasks and implementation.
- **VII. Test And Documentation Discipline**: PASS. Regression tests must prove
  completed V1 workflows still pass, and V2 adds unit, integration, contract,
  migration, guardrail, docs, and coverage evidence.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Work is split across
  container wiring, worker bootstrap, runtime gateway invocation, reliability,
  idempotency, admin probes, guardrails, observability, and docs without a
  broad redesign.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Gateway context carries
  tenant id and uses existing tenant visibility/rate-limit/fairness controls.
  Admin probes are rate-limited by actor and provider connection with tenant
  and global backstops.
- **X. Version-Pinned Execution**: PASS. Gateway calls occur only after
  prompt/profile pins are resolved and before side-effectful runtime work.
  Provenance links selected prompt/profile pins with provider route metadata.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Secret resolution is
  container-managed and adapter-local. Persisted summaries store references and
  safe metadata only; direct provider SDK/HTTP calls outside adapters are
  blocked or detected.
- **XII. Tiered Storage For Large Payloads**: PASS. No new blob storage is
  introduced. Provider payloads are not persisted; only compact metadata and
  safe summaries remain in PostgreSQL.
- **XIII. Human Approval Is Durable State**: PASS. No approval semantics change.
  Gateway hardening preserves existing run wait/resume state and execution
  bundle behavior.

## Project Structure

### Documentation (this feature)

```text
specs/012-prompt-runtime-profiles/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── admin-web-views.md
│   ├── prompt-runtime-profiles.openapi.yaml
│   ├── runtime-gateway-execution.md
│   └── runtime-profile-resolution.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── bootstrap/
│   ├── container.py
│   └── worker.py
├── model_providers/
│   ├── adapters.py
│   ├── catalog_sync.py
│   ├── gateway.py
│   ├── probes.py
│   ├── secrets.py
│   └── service.py
├── runtime/
│   ├── orchestration/
│   ├── queue/
│   ├── versioning.py
│   └── workflow_bundle.py
├── workers/
│   ├── main.py
│   ├── loops.py
│   └── orchestration.py
├── reliability/
│   ├── breakers.py
│   ├── retries.py
│   └── service.py
├── agents/
├── prompts/
├── audit/
├── observability/
└── db/
    ├── models/
    └── repositories/

tests/
├── contract/
├── integration/
├── unit/
└── docs/

alembic/
└── versions/
```

**Structure Decision**: Keep the existing single Python service and worker
layout. V2 adds container factories and narrow runtime/model provider
integration points in existing packages instead of introducing a new gateway
service, runtime subsystem, or front-end architecture.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves the V2 design decisions for container-managed gateway
dependencies, worker lifecycle, runtime invocation ordering, profile-governed
routing context, test bench parity, reliability mapping, idempotency/recovery,
admin probe limits, direct-call guardrails, and safe observability. See
[research.md](./research.md).

Key decisions:

- Build `ModelProviderService`, `ModelGateway`, `ProviderAdapterRegistry`,
  repository factories, secret resolver, metrics/tracing/audit hooks, retry
  decision helpers, and breaker decision helpers from `Container`.
- Expose gateway-ready worker dependencies from `WorkerBootstrap`; adapters own
  any managed provider clients and close them through container or registry
  lifecycle hooks.
- Invoke `ModelGateway` only after run acceptance or first-use prompt/profile
  pins are resolved and before model, tool, memory, approval, or other
  side-effectful runtime work.
- Preserve model_skill_config as the authorization owner; runtime profiles
  contribute hints and provenance but never expand tenant/provider/model access.
- Use one logical operation idempotency identity per gateway invocation,
  provider probe, and catalog sync, with physical attempts recorded beneath it.
- Reuse existing retry and breaker helpers; map provider error categories into
  retry categories and provider-connection/model breaker scopes.
- Add both static usage checks and runtime/integration detection for direct
  provider calls outside `model_providers/*adapter*.py`.

## Phase 1 Design And Contracts

Design artifacts are additive:

- [data-model.md](./data-model.md) keeps V1 prompt/profile entities and adds
  V2 gateway operation identity, physical attempt, probe operation, catalog
  sync operation, runtime invocation context, provenance projection, and
  guardrail evidence entities.
- [contracts/runtime-gateway-execution.md](./contracts/runtime-gateway-execution.md)
  defines container factories, worker dependencies, gateway invocation context,
  retry/breaker mapping, idempotency behavior, safe audit fields, and guardrail
  expectations.
- Existing prompt/profile API and admin web contracts remain in force. V2 adds
  admin probe behavior by reusing Spec 011 provider admin surfaces and existing
  reliability controls rather than changing prompt/profile authoring screens.
- [quickstart.md](./quickstart.md) includes V2 reviewer flows and regression
  checks for completed V1 workflows.

## Implementation Guidance

### Container Wiring

- Add container-managed factories for `ModelProviderRepository`,
  `ModelProviderService`, `ModelGateway`, `ProviderAdapterRegistry`, provider
  secret resolution, metrics/tracing/audit hooks, retry decision helpers, and
  breaker decision helpers.
- Keep factory signatures session-aware where database repositories are needed.
  Avoid global sessions and unmanaged request-time HTTP clients.
- Prefer additive container fields and backward-compatible defaults so existing
  API startup, tests, and workers continue to build.

### Worker Bootstrap

- Extend `WorkerBootstrap` to expose gateway-ready dependencies before workers
  accept model-backed work.
- Adapter registry or container lifecycle owns provider client cleanup. Worker
  loops must not create direct provider HTTP clients per request.
- Startup health should fail closed when gateway dependencies, secret resolver,
  provider repository, retry helper, breaker helper, metrics, tracing, or audit
  hooks are missing.

### Runtime Orchestration

- Runtime execution must resolve run-accepted or dynamic first-use
  prompt/profile pins before constructing gateway context.
- Gateway context must include tenant id, workflow run id, step id where
  available, trace id, selected profile version id, selected prompt version
  ids, model routing provenance, provider selection provenance, idempotency
  identity, and safe policy summaries.
- Persist gateway operation identity before provider activity and before any
  model, tool, memory, approval, handoff, artifact, or other side-effectful
  runtime action.

### Agent Profile Integration

- Active profile versions feed model routing hints, prompt/profile provenance,
  memory policy context, tool policy expectations, and output contract metadata
  into gateway context.
- Model selection still flows through model_skill_config authorization,
  provider catalog visibility, tenant grants, health checks, and credential
  policy. Conflicts fail closed.
- Tenant profile precedence over platform profile fallback is preserved.

### Test Bench And Validation

- Profile test bench and model-backed workflow validation paths must use the
  same gateway invocation metadata and safe audit behavior as production
  runtime calls when they execute model-backed behavior.
- Non-model-backed validation remains unchanged and must not create gateway
  attempts.

### Reliability Integration

- Map normalized provider errors to existing retry failure categories:
  timeouts to timeout, rate limits to rate limited, provider unavailable and
  malformed responses to dependency unavailable, authorization and visibility
  failures to non-retryable authorization/policy denial, inactive catalog and
  invalid model to non-retryable configuration/catalog failure.
- Record retry decision categories: `retryable`, `non-retryable`,
  `exhausted`, `skipped`, and `recovered`.
- Scope circuit breakers by provider connection and model/catalog identity.
  Persist tenant, run, and step context as evidence without making tenant a
  breaker key unless an existing policy explicitly requires it.

### Idempotency And Recovery

- Gateway invocation, provider probe, and catalog sync each use one logical
  operation identity. Retries and restarts reuse it; every physical provider
  attempt is a child record.
- Completed authoritative outcomes are returned on duplicate submit rather
  than launching duplicate provider work.
- Pending or ambiguous outcomes are recovered by consulting persisted state,
  retry/breaker policy, provider-safe request ids when available, and timeout
  windows. Ambiguous recovery must fail closed or retry only when policy allows.

### Admin Probe Controls

- Provider probes must pass existing bounded-operation and rate-limit controls
  before provider activity.
- Rate limits apply by actor and provider connection, with tenant and global
  backstops.
- Denied or throttled probe attempts persist safe audit evidence with actor,
  scope, provider identity, recovery identity, decision category, and safe
  summary.

### Guardrails

- Add static checks that reject direct provider SDK imports or direct provider
  HTTP calls from runtime, worker, test bench, workflow validation, agents, or
  prompt/profile modules unless the usage is in explicit gateway adapter
  modules.
- Add integration detection that exercises representative runtime/test bench
  paths and fails when model-backed calls bypass `ModelGateway`.
- Allowed adapter modules must be named and covered in the guardrail contract.

### Observability And Audit

- Correlate prompt/profile pins, selected provider connection, model id,
  tenant, workflow run, step, trace, idempotency identity, retry decision,
  breaker decision, latency, usage availability, normalized outcome, and safe
  summaries.
- Logs, traces, audits, browser views, and database summaries must exclude raw
  prompts, completions, credentials, provider tokens, API keys, local endpoint
  secrets, unsafe preview content, and unauthorized run content.

## Migration Guidance

- Prefer additive columns, tables, indexes, and constraints. Do not rewrite
  historical run, prompt, profile, or gateway records.
- Add uniqueness only where existing tables cannot express one authoritative
  logical operation identity, for example unique logical operation keys for
  gateway invocation, provider probe, and catalog sync records.
- Existing `gateway_invocation_attempts` may receive additive nullable columns
  for step id, profile version id, prompt version ids, operation identity,
  physical attempt number, retry category, breaker scope, provenance summaries,
  and recovered/duplicate-suppressed outcomes if separate operation tables are
  not introduced.
- Historical rows without V2 fields remain valid and render as
  pre-V2/metadata-unavailable in review surfaces.

## Risk Controls

- Backward-compatible defaults keep existing runs, historical provenance,
  prompt/profile browser flows, workflow validation, and migration tests
  working.
- Runtime and admin provider operations fail closed when any required
  prompt/profile pin, catalog visibility, connection health, credential
  reference, retry/breaker state, bounded-operation authorization, or tenant
  authorization check cannot be verified.
- Persisted evidence stores identifiers, normalized categories, digests, and
  safe summaries only.
- Regression tests must re-run completed Spec 012 prompt authoring, lifecycle,
  profile activation, tenant grants, browser UI, workflow validation,
  model-skill prompt reference integration, migration, docs, and coverage
  workflows.

## Post-Design Constitution Check

- **Durability and recovery**: PASS. Logical operation identities and child
  attempts define retry, restart, duplicate suppression, and ambiguous recovery
  behavior.
- **Immutability and version pinning**: PASS. Prompt/profile pins remain
  immutable and are linked to gateway metadata without rewriting history.
- **Security and tenant isolation**: PASS. Authorization remains with existing
  services; sensitive payloads are excluded from all evidence.
- **Operability**: PASS. Metrics, traces, safe audit, retry/breaker decisions,
  latency, usage availability, and normalized outcomes are required.
- **Small safe changes**: PASS. Integration is additive and scoped to
  container, worker, runtime gateway invocation, provider reliability, guardrail
  tests, docs, and narrow migrations.
