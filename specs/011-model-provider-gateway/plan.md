# Implementation Plan: Model Provider Gateway

**Branch**: `011-model-provider-gateway` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-model-provider-gateway/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add platform-admin-managed model provider connections and a shared runtime
`ModelGateway` for all model calls. The design reuses the existing FastAPI,
Auth0/local-principal authorization, SQLAlchemy async PostgreSQL storage,
secret-provider abstraction, model provider catalog from
`model_skill_config`, production audit/debugging traces, and reliability
breaker/retry primitives. OpenAI and local OpenAI-compatible providers are
implemented through adapter interfaces over `httpx`; local endpoints must pass
the administrator-managed allowlist before tests or runtime calls. Safe probes,
health snapshots, catalog synchronization, runtime invocation metadata, admin
web views under the shared shell, API contracts, tests, docs, PR notes, and
reviewer QA are in scope.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, httpx, Auth0 JWT validation plus deterministic
local-principal mode, existing secret providers, existing model_skill_config
catalog/resolver, existing audit/debugging capture, existing reliability
breakers/retries, LangChain 1.2.15, LangGraph 1.1.9,
langgraph-checkpoint-postgres 3.0.5, prometheus-client, pytest,
pytest-asyncio, Ruff, mypy, uv
**Storage**: PostgreSQL for provider connections, connection model
definitions, tenant visibility allowlists, connection test result history,
latest health snapshots, catalog synchronization records, gateway invocation
attempt metadata, safe audit summaries, and migration state. Raw provider
secrets remain in existing secret providers; large payload storage is not
introduced.
**Testing**: pytest unit tests for Pydantic validation, endpoint allowlist
checks, secret-reference resolution, adapter request/response mapping, safe
probe construction, health derivation, catalog collision checks, gateway error
normalization, retry/breaker inputs, usage metadata extraction, and safe
redaction; FastAPI contract tests for admin JSON APIs and shared-shell web
views; PostgreSQL-backed integration tests for migrations, tenant visibility,
catalog synchronization, mocked OpenAI/local providers, runtime worker and
test bench gateway use, audit/debug trace emission, and fail-closed paths;
contract tests for the gateway invocation protocol and OpenAI-compatible local
provider contract; performance tests proving gateway overhead stays within
target; docs tests for README, quickstart, PR notes, and reviewer QA. Coverage
is enforced at >=90 percent for submitted provider connection and gateway code.
**Target Platform**: Linux container deployment for the existing FastAPI API
and background workers; local macOS/Linux development; PostgreSQL-backed
workflow execution under the existing platform bootstrap model.
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
server-rendered admin web views, durable workflow runtime workers, PostgreSQL
persistence, and operator-facing documentation.
**Performance Goals**: Gateway wrapper overhead p95 <= 25 ms excluding
provider network time in local performance tests; connection listing and
shared-shell admin pages p95 <= 200 ms with indexed tenant/status filters;
catalog synchronization for 100 configured models p95 <= 1 second in
integration tests; safe probes honor configured timeout and return recorded
results for 100 percent of attempts.
**Constraints**: Platform-admin-only mutation and testing by default; tenant
read visibility only through platform defaults or explicit tenant allowlists;
local provider URLs must match the administrator-managed allowlist of schemes,
hosts, ports, and CIDRs; local providers must expose OpenAI-compatible chat
completions; raw API keys, provider tokens, prompts, completions, local
endpoint secrets, and secret-bearing provider errors are never persisted or
logged; routing selects only active, tenant-visible, healthy catalog entries;
timeout policy governs tests and runtime unless a stricter runtime policy
applies; provider failures are normalized; retries and breakers use safe scope
keys and metadata; implementation must update the admin web UI.
**Scale/Scope**: Initial scope supports OpenAI and local OpenAI-compatible
providers, low hundreds of provider connections, up to 100 configured models
per connection, platform-default plus explicit tenant allowlist visibility,
latest health snapshots with retained test history, and gateway calls from
runtime workers and test bench paths. Automatic provider benchmarking,
multi-provider fallback orchestration, streaming responses, and full secret
manager administration are out of scope unless represented through safe
connection metadata and existing routing.

**Tenant Limits And Fairness**: Connection and catalog reads are tenant-scoped
and bounded by indexed filters. Runtime gateway calls inherit orchestration
tenant context, existing admission/fairness controls, and retry budgets.
Breaker and metrics labels include tenant scope but avoid high-cardinality
secret or prompt data. Admin test probes are rate-limited through existing
operational controls and audit every denied or throttled attempt.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Provider connections, test results, health snapshots, catalog synchronization, invocation attempts, retry/breaker decisions, and safe audit summaries are persisted before they become authoritative for routing or review. |
| Immutable State And Memory | PASS | Test result history, gateway attempt records, audit events, and catalog sync records are append-only; mutable connection and catalog heads are derived projections with timestamps and actor evidence. |
| Contract-First Agent Coordination | PASS | Admin APIs, admin web view contracts, provider adapter interfaces, local OpenAI-compatible contract, and runtime gateway invocation protocol are defined before implementation. |
| Security With Practical Development Ergonomics | PASS | Existing Auth0/local-principal dependencies gate mutation, testing, tenant reads, and runtime use while preserving deterministic local principals for tests. |
| Operability Is A Product Requirement | PASS | Design includes health states, last-test evidence, normalized errors, metrics, traces, admin shell views, run/debug links, PR notes, testing instructions, and reviewer QA. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks trace to provider configuration, gateway invocation, web UI, tests, docs, and review evidence. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, unit/integration/contract/performance tests, README/docs updates, quickstart validation, testing instructions, PR notes, and reviewer QA. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across provider domain services, DB models/repositories, adapters, gateway runtime integration, admin APIs/web views, observability, migrations, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant visibility is explicit, catalog collisions are checked per tenant scope plus model id, runtime selection fails closed, and gateway calls reuse existing tenant fairness and retry controls. |
| Version-Pinned Execution | PASS | Gateway invocations use the resolved catalog entry and pinned runtime configuration already captured by model_skill_config; invocation evidence records the selected catalog and connection versions. |
| Secret Hygiene And Controlled Tool Access | PASS | Connection records persist secret references only; resolution uses existing secret providers and emits safe secret-access audit metadata without raw values. Local endpoint allowlists govern outbound access. |
| Tiered Storage For Large Payloads | PASS | No new blob storage is introduced; PostgreSQL stores compact metadata and audit evidence only, never prompts, completions, or raw provider responses. |
| Human Approval Is Durable State | PASS | No new approval/resume workflow is introduced; admin activation, deactivation, testing, and catalog publication are explicit authorized actions with durable audit evidence. |

Post-Phase-1 re-check: design artifacts keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/011-model-provider-gateway/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- testing-instructions.md
+-- pr-review-notes.md
+-- contracts/
|   +-- model-provider-gateway.openapi.yaml
|   +-- runtime-model-gateway-protocol.md
|   +-- admin-web-views.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- admin_model_providers.py       # JSON APIs and shared-shell web routes
    |   +-- schemas/
    |       +-- model_providers.py             # request/response schemas and errors
    |   +-- ui/
    |       +-- model_providers.py             # web view context builders and safe states
    +-- bootstrap/
    |   +-- container.py                       # wire services, adapters, httpx client
    |   +-- worker.py                          # wire gateway into workers/test bench
    +-- model_providers/
    |   +-- __init__.py
    |   +-- adapters.py                        # provider adapter protocol and registry
    |   +-- allowlist.py                       # local endpoint allowlist validation
    |   +-- catalog_sync.py                    # publish/update model_skill_config entries
    |   +-- gateway.py                         # ModelGateway runtime facade
    |   +-- health.py                          # health derivation and snapshots
    |   +-- models.py                          # domain value objects and enums
    |   +-- probes.py                          # safe probe construction and execution
    |   +-- redaction.py                       # provider-safe diagnostics
    |   +-- service.py                         # admin connection facade
    |   +-- usage.py                           # token usage normalization
    |   +-- validation.py                      # connection and publication validation
    +-- db/
    |   +-- models/
    |   |   +-- model_providers.py             # connections, models, tests, health, attempts
    |   +-- repositories/
    |       +-- model_providers.py             # transactional storage and sync queries
    +-- runtime/
    |   +-- orchestration/
    |       +-- service.py                     # replace direct provider calls with gateway
    |       +-- side_effects.py                # model side-effect metadata and gateway guard
    +-- config/
    |   +-- resolver.py                        # consume healthy gateway-backed catalog entries
    +-- audit/
    |   +-- capture.py                         # gateway/admin safe audit events
    +-- observability/
    |   +-- logging.py                         # provider/gateway safe structured fields
    |   +-- metrics.py                         # probe, health, gateway latency/error metrics
    |   +-- tracing.py                         # provider/gateway spans
    +-- web_admin/
        +-- static/
        |   +-- model_providers.js             # test/probe and catalog UI interactions
        |   +-- workflow_studio.css            # shared admin-shell styling extensions
        +-- templates/
            +-- model_providers/
                +-- index.html
                +-- detail.html
                +-- edit.html
                +-- test_results.html
                +-- catalog.html
alembic/versions/
+-- 0011_model_provider_gateway.py
tests/
+-- contract/
|   +-- test_model_provider_gateway_contract.py
|   +-- test_runtime_model_gateway_protocol.py
|   +-- test_local_openai_compatible_contract.py
+-- integration/
|   +-- api/
|   |   +-- test_admin_model_providers_api.py
|   |   +-- test_admin_model_providers_ui.py
|   |   +-- test_admin_model_provider_tests_and_catalog.py
|   |   +-- test_admin_model_provider_probe_rate_limits.py
|   |   +-- test_admin_model_providers_browser_flows.py
|   +-- db/
|   |   +-- test_model_provider_gateway_migration.py
|   +-- runtime/
|       +-- test_model_gateway_runtime.py
|       +-- test_model_gateway_test_bench.py
|       +-- test_model_gateway_audit_traces.py
|       +-- test_model_provider_side_effect_recovery.py
|       +-- test_model_gateway_secret_hygiene.py
|   +-- workers/
|   |   +-- test_no_direct_provider_calls.py
|   +-- providers/
|       +-- test_mock_model_providers.py
+-- performance/
|   +-- model_providers/
|       +-- test_gateway_latency_overhead.py
|       +-- test_admin_provider_listing_latency.py
|       +-- test_catalog_sync_latency.py
+-- docs/
|   +-- test_model_provider_gateway_docs.py
|   +-- test_readme_model_provider_gateway.py
|   +-- test_model_provider_gateway_review_evidence.py
+-- unit/
    +-- api/
    |   +-- test_model_provider_schemas.py
    +-- auth/
    |   +-- test_model_provider_policy.py
    +-- config/
    |   +-- test_model_provider_settings.py
    +-- db/
    |   +-- test_model_provider_models.py
    |   +-- test_model_provider_connection_repository.py
    +-- model_providers/
        +-- test_adapters.py
        +-- test_allowlist.py
        +-- test_catalog_sync.py
        +-- test_gateway.py
        +-- test_health.py
        +-- test_models.py
        +-- test_probes.py
        +-- test_redaction.py
        +-- test_secret_references.py
        +-- test_usage.py
        +-- test_validation.py
README.md
docs/quickstart.md
docs/model-provider-gateway.md
```

**Structure Decision**: Keep provider configuration and gateway execution
inside the existing Python/FastAPI backend. Add a focused
`multi_agent_platform.model_providers` package for adapter, validation, probe,
gateway, usage, and catalog synchronization logic. Persistence stays in
SQLAlchemy models/repositories; routers and shared-shell templates remain thin
over the service layer; runtime orchestration consumes `ModelGateway` rather
than provider SDKs or direct HTTP calls.

## Provider Connection Design

- **Connection record**: `model_provider_connections` stores provider type,
  display name, optional safe base URL, timeout policy, visibility mode,
  active flag, health state, local endpoint allowlist decision hash, credential
  secret reference ids, safe metadata, created/updated actor ids, and
  timestamps. It never stores raw secrets, prompt text, completion text, or raw
  provider responses.
- **Provider model definitions**: `model_provider_connection_models` stores
  configured model ids, display labels, capability metadata, cost metadata,
  default selection flags, and per-model availability. Duplicate model ids
  within one connection are rejected.
- **Tenant visibility**: Platform-default visibility publishes a `NULL`
  tenant catalog entry for platform-visible defaults. Tenant allowlist
  visibility creates one allowlist row per tenant and publishes tenant-scoped
  catalog rows. Reads fail closed when tenant visibility cannot be verified.
- **Local endpoint allowlist**: Add Pydantic settings for permitted schemes,
  hosts, ports, and CIDRs. Validation normalizes URL host/port, blocks userinfo
  and secret-like query params, rejects redirects to disallowed destinations,
  and refuses probes before any network call when the URL does not match.
- **Secret references**: Connections reference existing
  `secret_reference`/secret-provider identifiers. Tests and gateway invocations
  resolve references at use time, emit `secret_access_audit_metadata`, and
  pass only the in-memory secret value into the adapter.

## Adapter And Probe Decisions

- **Adapter interface**: `ModelProviderAdapter` exposes `safe_probe()` and
  `chat_completion()` async methods accepting normalized request objects,
  credentials, timeout policy, and safe trace context; it returns normalized
  response, usage metadata, and safe provider diagnostics.
- **OpenAI adapter**: Use `httpx.AsyncClient` against OpenAI chat completions
  API using the configured secret reference for bearer auth. The adapter maps
  HTTP 401/403, 404/model errors, 408/timeouts, 429, 5xx, malformed JSON, and
  unexpected schema to stable platform categories.
- **Local adapter**: Use the same OpenAI-compatible chat-completions request
  and response shape against the configured base URL. Adapter-specific headers
  may be referenced through secret references, but header values are never
  stored in connection metadata or diagnostics.
- **Safe probe**: The probe sends a deterministic, non-tenant prompt such as a
  short health check with `max_tokens` capped and no customer context. The
  stored result captures outcome, latency, tested model id, normalized reason,
  HTTP status class when safe, provider request id when non-secret, and a
  sanitized summary. It discards prompt and completion content.
- **Health state**: Health is derived from active flag plus the latest relevant
  test: `disabled`, `untested`, `healthy`, `degraded`, `failing`, or
  `unavailable`. Routing may select only `healthy`.

## Catalog Synchronization

- Successful tests for active connections trigger catalog synchronization.
  Sync upserts existing `model_provider_catalog_entries` from
  `model_skill_config`, adding gateway fields in migration `0011`:
  `provider_connection_id`, `health_state`, `availability_status`,
  `visibility_mode`, `tenant_visibility_hash`, and `last_synced_at`.
- Catalog uniqueness is enforced for `(tenant_id, model_id)` and platform
  defaults through partial unique indexes. Collisions block publication with a
  safe actionable error rather than overwriting an entry.
- Deactivation, failed health, removed tenant visibility, or deleted model
  definitions marks governed catalog entries unavailable/unselectable while
  preserving historical rows and runtime evidence.
- Runtime model routing continues to resolve through the existing
  `model_skill_config` resolver, but resolver validation now requires active,
  tenant-visible, healthy, gateway-backed catalog entries.

## Runtime ModelGateway Contract

- **Inputs**: tenant id, run/test-bench context, resolved catalog entry id,
  model id, messages or provider-neutral request payload in memory, timeout
  override if stricter, trace id, idempotency key, and safe caller metadata.
- **Execution**: Gateway verifies tenant visibility, active connection, healthy
  latest test, credential reference status, breaker allowance, timeout policy,
  and retry budget before adapter invocation. It fails closed when any check is
  unavailable.
- **Retries and timeouts**: Use connection timeout policy for connect/read
  timeout and total deadline unless runtime provides a stricter deadline.
  Retry only normalized transient categories: timeout, rate limit, provider
  unavailable, and selected network failures. Authorization, invalid model,
  malformed response, policy/visibility denial, and secret resolution failure
  are not retried.
- **Breaker scope names**: Use
  `model_provider:{tenant_scope}:{provider_type}:{connection_id}:{model_id}`
  for runtime calls and
  `model_provider_probe:{provider_type}:{connection_id}:{model_id}` for admin
  probes. Scope components are stable ids or normalized enums, never URLs,
  secrets, prompts, completions, or user input.
- **Evidence**: Every attempt records latency, normalized outcome, normalized
  error category, retry input, breaker input, selected catalog entry, selected
  connection version, selected model id, usage metadata availability, safe
  provider request id when available, and audit/debug trace ids. Raw messages
  and completions remain in memory only and are not persisted.
- **Usage metadata**: Normalize `prompt_tokens`, `completion_tokens`,
  `total_tokens`, provider model id, cache-read/write tokens when available,
  and `usage_available=false` when absent. Missing usage does not fail a
  successful invocation.

### Side-Effect Durability And Recovery

- **Safe probes** use a persisted probe attempt record before network
  execution. Retries reuse the same probe attempt id and idempotency key;
  duplicate completions update only the derived latest-health snapshot. Failed
  or interrupted probes remain reviewable and never publish catalog entries.
- **Catalog synchronization** runs inside one repository transaction per
  connection/model visibility scope. Publication uses upsert by governing
  connection plus tenant/model uniqueness checks. Interrupted syncs can be
  retried safely because unavailable/selectable state is derived from
  connection health, active state, and visibility.
- **Gateway invocations** persist an invocation attempt before adapter dispatch
  with tenant id, run/test-bench context, catalog entry id, connection version,
  model id, idempotency key, timeout, retry budget, and breaker scope. Retries
  append attempt evidence and never duplicate authoritative workflow side
  effects.
- **Compensation** for deactivation, failed health, removed tenant visibility,
  or catalog collision marks governed catalog entries unavailable/unselectable
  while preserving historical rows and invocation evidence.
- **Lease/checkpoint boundary** for runtime calls is the existing workflow step
  checkpoint: no model-backed step is considered complete until gateway attempt
  evidence and safe audit/debug metadata are persisted.

## Admin Web UI Updates

- Add shared-shell navigation item "Model Providers" under platform
  configuration. Tenant-scoped users with read authority see visible
  connections/catalog entries; mutation and testing controls render only for
  platform administrators.
- Add `/admin/model-providers` list page with provider type, display name,
  active state, health state, last test outcome, model count, tenant visibility
  summary, catalog sync status, and safe filters for type/health/tenant/model.
- Add `/admin/model-providers/new` and
  `/admin/model-providers/{connection_id}/edit` forms for provider type,
  display name, base URL, model definitions, capability/cost metadata, timeout
  policy, tenant visibility, secret references, and active state.
- Add `/admin/model-providers/{connection_id}` detail page with connection
  metadata, latest health snapshot, last test result, catalog entries,
  visibility table, audit/debug links, and safe error summaries.
- Add `/admin/model-providers/{connection_id}/tests` page for retained safe
  test results, normalized failures, latency trend, tested model id, actor, and
  source. The "Run Test" action posts through platform-admin-only route and
  shows a shared-shell flash result.
- Add `/admin/model-providers/catalog` page for tenant-visible catalog entries,
  collision warnings, health/availability state, governing connection, and
  routing selectability. This directly satisfies the requirement to update the
  Web UI for the new feature.

## API And Authorization Decisions

- JSON API routes live under `/admin/model-providers/api/...`; server-rendered
  routes live under `/admin/model-providers...` and use the shared admin shell.
- Platform administrators may create, update, activate, deactivate, test, and
  sync connections. Tenant administrators/readers may list or inspect only
  visible connections and catalog entries, with mutation controls denied and
  audited.
- Direct attempts to mutate or test without platform-admin authority return a
  safe denial, preserve prior state, and create audit/debug evidence.
- All response schemas redact secret references to safe identifiers and never
  include resolved secret values, Authorization headers, endpoint userinfo, raw
  prompts, raw completions, or raw provider errors.

## Migration Strategy

- Add migration `0011_model_provider_gateway.py` after
  `0010_admin_console_shell.py`.
- Create provider connection, model definition, visibility, test result,
  health snapshot, catalog sync, and invocation attempt tables.
- Extend existing `model_provider_catalog_entries` with nullable gateway
  governance fields so existing catalog rows remain readable during migration.
- Backfill existing catalog entries as `legacy_unmanaged` with
  `availability_status='unmanaged'` and `health_state='unavailable'` unless a
  later task maps them to a managed connection. Managed gateway routing selects
  only healthy connection-governed rows.
- Add partial unique indexes for tenant-scoped and platform-default catalog
  uniqueness by model id, plus indexes for tenant visibility, health, active
  state, provider type, and connection id.
- Rollback drops new gateway tables and nullable catalog columns only before
  managed connections are published in production; after publication, rollback
  requires an operator migration plan to preserve audit/history.

## Observability, Audit, And Reliability

- Emit metrics for connection tests, health state transitions, catalog sync
  outcomes, gateway invocation latency, normalized error categories, retry
  attempts, breaker state, usage metadata availability, and denied visibility
  checks.
- Use existing audit/debug capture for admin connection mutations, denied
  mutations, safe probes, catalog publication changes, gateway failures, and
  runtime invocation summaries. Security/governance audit writes fail closed.
- Structured logs and trace spans include tenant id, connection id, catalog
  entry id, provider type, model id, result category, retry count, breaker
  scope, and latency. They exclude base URL userinfo, headers, secrets, prompts,
  completions, and raw provider bodies.
- Reliability integration uses existing retry classifier and circuit breaker
  state machines. Breakers recover through cooldown plus successful configured
  probe evidence before half-open runtime traffic.

## Test Strategy

- Unit tests cover validation, allowlist normalization, adapter interfaces,
  mocked OpenAI/local response mapping, probe safety, health derivation,
  catalog collision detection, secret-reference summaries, redaction, usage
  extraction, timeout/retry decisions, and breaker scope construction.
- Contract tests verify the OpenAPI schema, shared-shell UI contract, runtime
  gateway invocation protocol, and local OpenAI-compatible provider request and
  response expectations.
- Integration tests use mocked `httpx` transports for OpenAI and local
  providers, exercise migrations, provider CRUD, test success/failure,
  tenant visibility, catalog synchronization, runtime worker calls, test bench
  calls, audit/debug traces, and fail-closed secret/visibility/health paths.
- Performance tests measure gateway wrapper latency overhead against a mocked
  provider and assert p95 <= 25 ms excluding provider network delay.
- Docs/reviewer tests confirm README, docs, quickstart, testing instructions,
  PR notes, and reviewer QA mention OpenAI/local setup, Web UI, safe probes,
  catalog visibility, gateway use, usage metadata, retry/breaker behavior, and
  sensitive-data checks.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
