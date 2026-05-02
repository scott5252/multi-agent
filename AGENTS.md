# multi-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-04-30

## Active Technologies
- Python 3.12 + FastAPI security dependencies, Auth0 JWT validation, Pydantic
  Settings, SQLAlchemy 2.x, Alembic, PostgreSQL auth metadata, pytest,
  pytest-asyncio, httpx, Ruff, mypy, uv (002-platform-auth-access)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy (003-workflow-studio-registry)
- PostgreSQL for workflow lineages, active drafts, immutable draft revisions, published bundle metadata (003-workflow-studio-registry)
- Python 3.12 + FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (004-durable-orchestration-runtime)
- PostgreSQL for workflow runs, run steps, worker leases, LangGraph checkpoints, handoff envelopes, side-effect intents, approvals, parent-child lineage, audit events, and retention metadata (004-durable-orchestration-runtime)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (005-immutable-memory)
- PostgreSQL for memory scopes, immutable memory versions, head projections, read/write audit records, archival markers, links to runtime execution bundles, workflow runs, run steps, and parent-child lineage (005-immutable-memory)
- Python 3.12 + FastAPI, Starlette `StreamingResponse` for SSE, Pydantic v2,
  SQLAlchemy 2.x, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  httpx, pytest, pytest-asyncio, Ruff, mypy, uv (006-user-interaction-channels)
- PostgreSQL for channel sessions, Telegram identity links, normalized
  requests, idempotency records, notification subscriptions and delivery
  attempts, API callbacks, timeline projections, and interaction audit records
  (006-user-interaction-channels)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x,
  Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
  pytest, pytest-asyncio, httpx, Ruff, mypy, uv (007-model-skill-routing)
- PostgreSQL for model provider catalog entries, versioned model routing,
  prompt references, skill bindings, tool policies, outbound policies,
  secret-reference metadata, credential requirements, active pointers, runtime
  pins, policy decisions, migrations, and configuration audit records
  (007-model-skill-routing)
- Python 3.12 + FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x,
  Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
  LangChain 1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
  pytest, pytest-asyncio, httpx, Ruff, mypy, uv
  (008-production-audit-debugging)
- PostgreSQL for append-only audit events, run timeline events, runtime trace
  records, capture gaps, lineage projections, version-bundle references,
  notification delivery projections, secret-access audit metadata, inspection
  access audits, export metadata, redaction/classification records, and replay
  snapshots (008-production-audit-debugging)
- Python 3.12 + FastAPI, Starlette response handling, Pydantic v2,
  Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
  psycopg 3, Auth0 JWT validation, LangChain 1.2.15, LangGraph 1.1.9,
  langgraph-checkpoint-postgres 3.0.5, prometheus-client, pytest,
  pytest-asyncio, httpx, Ruff, mypy, uv (009-reliability-scale-hardening)
- PostgreSQL for reliability policies, worker leases, queue state, quota
  counters, fairness windows, retry schedules, circuit breaker state,
  compensation requests, dead-letter records, operational snapshots, audit
  events, artifact metadata, and object-storage artifact references
  (009-reliability-scale-hardening)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2,
  SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3,
  Auth0 JWT validation, local-principal test mode, prometheus-client,
  pytest, pytest-asyncio, httpx, Ruff, mypy, uv (010-admin-console-shell)
- PostgreSQL for persisted admin saved filters, plus existing access decision
  and audit records for shell navigation, direct destination access, scope
  selection, and saved-filter restoration (010-admin-console-shell)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2,
  SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, httpx,
  Auth0 JWT validation, existing secret providers, existing
  model_skill_config catalog/resolver, existing audit/debugging capture,
  existing reliability breakers/retries, prometheus-client, pytest,
  pytest-asyncio, Ruff, mypy, uv (011-model-provider-gateway)
- PostgreSQL for provider connections, model definitions, tenant visibility,
  connection test results, health snapshots, catalog synchronization records,
  gateway invocation metadata, safe audit summaries, and migration state
  (011-model-provider-gateway)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2,
  Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
  psycopg 3, Auth0 JWT validation, existing workflow registry,
  model_skill_config prompt references, memory policy, audit/redaction helpers,
  prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
  (012-prompt-runtime-profiles)
- PostgreSQL for prompt lineages, prompt drafts, immutable prompt versions,
  render tests, prompt audit records, agent runtime profiles, immutable profile
  versions, tenant grants, workflow validation references, bundle pins, and run
  provenance metadata (012-prompt-runtime-profiles)
- PostgreSQL for additive gateway operation identities, provider probe and
  catalog sync recovery records, physical attempt summaries, retry/breaker
  summaries, prompt/profile/provider provenance links, and safe audit records
  (012-prompt-runtime-profiles V2)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing workflow registry services/schemas/web_admin templates/static workflow_studio assets, prompt library services, agent runtime profile services, model_skill_config resolver and preview APIs, ModelGateway/provider catalog readiness, existing skill binding policy models, audit/redaction helpers, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (013-admin-workflow-builder)
- PostgreSQL for existing workflow lineages, active drafts, immutable draft revisions, validation results, published bundle metadata, sharing grants, audit records, prompt/profile references, provider catalog metadata, skill policy metadata, and future test bench result summaries; object/artifact storage for compiled workflow bundles and oversized validation reports (013-admin-workflow-builder)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2,
  Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
  psycopg 3, Auth0 JWT validation, local-principal admin test mode,
  existing secret providers, existing delegated credential metadata,
  existing model_skill_config skill bindings, allowed tool policies,
  outbound domain policies, credential requirement policies, existing workflow
  registry publish validation hooks, existing object storage providers,
  existing audit and redaction helpers, existing reliability quotas/retries/
  breakers, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
  (014-skill-registry-lifecycle)
- PostgreSQL for skill packages, immutable package versions, tenant
  availability grants, tenant installations, smoke-test evidence, credential
  readiness, quarantine decisions, upgrade lineage, binding eligibility
  projections, and skill audit records; object/artifact storage for immutable
  package artifacts, safe docs, fixtures, pinned manifests, validation
  evidence, and oversized smoke-test reports (014-skill-registry-lifecycle)
- Python 3.12 + FastAPI, Starlette/Jinja2 template responses, Pydantic v2,
  Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
  psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing
  skill registry services/schemas/templates, admin shell navigation,
  audit/redaction helpers, model_skill_config policy preview APIs,
  prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
  (014-skill-registry-lifecycle-v2)
- Reuse existing Spec 014 PostgreSQL tables for skill packages, manifest
  candidates/validation evidence if already present, immutable package
  versions, tenant availability grants, tenant installations, credential
  readiness, smoke-test evidence, binding eligibility projections, revision
  tokens, and audit records; object/artifact storage only for existing package
  artifacts, safe docs, fixtures, pinned manifests, validation evidence, and
  oversized smoke-test reports (014-skill-registry-lifecycle-v2)

- Python 3.12 + FastAPI, Pydantic Settings, LangChain, LangGraph, SQLAlchemy 2.x, Alembic, psycopg 3, pytest, pytest-asyncio, httpx, Ruff, mypy, uv (001-platform-foundation)

## Project Structure

```text
src/multi_agent_platform/
tests/
alembic/
```

## Commands

- `uv sync`
- `uv run alembic upgrade head`
- `uv run uvicorn multi_agent_platform.api.main:app --reload`
- `uv run python -m multi_agent_platform.workers.main`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`

## Code Style

Python 3.12: Follow standard conventions with type annotations on public
boundaries, FastAPI dependency injection for service wiring, and SQLAlchemy 2.x
async patterns for PostgreSQL access.

## Recent Changes
- 014-skill-registry-lifecycle-v2: Planned browser-first skill registry
  lifecycle workflows to replace primary QA curl/API helper steps with
  server-rendered admin UI forms for package creation, manifest paste/upload,
  candidate validation, immutable publication, tenant grants, tenant
  discovery, tenant installation, credential reference configuration,
  smoke-test/readiness evidence, binding eligibility preview, stale conflict
  recovery, tenant isolation, and redaction-safe screenshot evidence.
- 014-skill-registry-lifecycle: Planned governed skill registry and tenant
  installation lifecycle with immutable package artifacts, manifest schema,
  validation, credential readiness, smoke tests, quarantine, upgrade/rollback
  semantics, Spec 007 skill-binding eligibility, workflow publish validation,
  admin views, APIs, audit, reliability controls, docs, and tests.
- 013-admin-workflow-builder: Planned guided admin workflow builder UX on top
  of existing workflow registry services, workflow schemas, admin templates,
  workflow_studio assets, prompt library, agent profiles, model routing
  previews, provider catalog readiness, skill policies, reusable subworkflows,
  field-level validation, graph preview, publish gate, draft revisions,
  optimistic concurrency, audit events, docs, and reviewer QA tests.
- 012-prompt-runtime-profiles V2: Planned additive runtime gateway completion
  with container-managed ModelGateway wiring, gateway-ready worker bootstrap,
  profile-governed model execution, test bench parity, durable provider
  operation idempotency, retry and circuit breaker summaries, admin probe
  limits, direct provider call guardrails, and safe combined prompt/profile plus
  provider provenance.
- 012-prompt-runtime-profiles: Planned prompt library and agent runtime profile
  management with prompt lineages, draft revisions, template variable
  validation, safe fixture previews, immutable prompt publication, retirement,
  tenant grants, profile versioning, workflow validation hooks, Spec 007 prompt
  reference integration, run acceptance and dynamic first-use pinning, safe
  audit records, browser admin views for non-developers, API contracts, docs,
  and tests.
- 011-model-provider-gateway: Planned model provider connection management
  and shared ModelGateway with OpenAI/local OpenAI-compatible adapters, safe
  probes, health snapshots, catalog synchronization, secret-reference
  resolution, gateway runtime contracts, timeout/retry/breaker behavior,
  usage metadata extraction, tenant visibility, admin web views, tests, docs,
  PR notes, and reviewer QA.
- 010-admin-console-shell: Implemented shared server-rendered admin console
  shell with FastAPI/Jinja2 templates, Auth0/local-principal authorization,
  validated tenant-scope query handling, authorization-aware navigation,
  item-level navigation audit evidence, fail-closed audit persistence behavior,
  common empty/error/flash states, breadcrumbs, saved filters, accessibility,
  docs, and tests while preserving existing admin routes.
- 009-reliability-scale-hardening: Planned reliability and scale hardening with
  tenant-aware admission and backpressure, worker autoscaling signals, lease
  tuning, DB pooling, partitioning, retry budgets, circuit breakers,
  compensation orchestration, dead-letter handling, operational dashboards,
  tenant fairness controls, artifact-throughput limits, failure-mode research,
  and resume-after-failure validation under load.
- 008-production-audit-debugging: Planned production observability and audit
  debugging with structured logs, trace IDs, metrics, append-only audit tables,
  admin timeline/search/replay APIs, lineage and version-bundle views,
  redaction/classification, exports, and completeness testing.
- 007-model-skill-routing: Planned versioned model routing and skill/tool
  configuration, deterministic precedence resolution, run and first-use
  pinning, rollback, outbound and credential policy enforcement, audit
  provenance, and admin preview/history views.
- 006-user-interaction-channels: Planned FastAPI channel adapters for Web UI,
  Telegram webhooks, and REST APIs with normalized requests, shared run status,
  SSE/polling, callbacks, approval/resume flows, notifications, and artifact
  access.
- 005-immutable-memory: Planned append-only PostgreSQL-backed memory scopes,
  immutable version lineage, head projections, runtime-safe reads/writes,
  retrieval APIs, audit redaction, archival markers, and concurrency tests.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/015-agent-workflow-test-bench/plan.md`
<!-- SPECKIT END -->
