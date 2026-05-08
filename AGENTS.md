# multi-agent Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-07

## Active Technologies
- Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26` + FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv (codex/048-live-data-inventory-and-mock-guardrails)
- Existing workflow registry, validation, version bundle, sharing, artifact, audit, and test-bench tables in PostgreSQL; no new migration planned unless implementation discovers a missing durable field (codex/048-live-data-inventory-and-mock-guardrails)

- Python 3.12 across the platform.
- TypeScript strict mode and Node.js `>=20.19.0 <26` for the React admin UI
  foundation under `frontend/admin`.
- FastAPI control-plane application with React-served browser UI, static HTML
  compatibility helpers, JSON APIs, channel webhooks, selected streaming/SSE
  responses, and a worker process.
- Pydantic v2 and Pydantic Settings for request/response schemas, domain
  contracts, settings, and validation.
- SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, and psycopg 3 for durable
  tenant-scoped state.
- Auth0 JWT validation for production auth plus explicit local-principal admin
  test mode for deterministic local and CI validation.
- LangChain 1.2.15, LangGraph 1.1.9, and
  langgraph-checkpoint-postgres 3.0.5 for runtime orchestration and durable
  checkpoints.
- Model provider gateway with OpenAI and local OpenAI-compatible adapters,
  provider probes, secret-reference credential resolution, retry/breaker
  behavior, redaction-safe attempt evidence, and usage capture.
- First-party skill execution gateway for governed, read-only connector tools
  with tenant, tool, outbound, credential, and side-effect policy checks.
- prometheus-client, structured logging/tracing, audit/redaction helpers,
  reliability quotas/leases/breakers, and operational dashboards.
- pytest, pytest-asyncio, httpx/TestClient, Playwright QA scripts, Ruff, mypy,
  coverage gates, and uv.
- React 19, React Router, Vite, Vitest, Testing Library, npm, generated
  TypeScript contracts, optional `lucide-react` icons, planned `@xyflow/react`
  graph components, and FastAPI-served built assets for the additive admin
  React migration foundation, shared shell/design system, reusable data/form
  patterns, operations workbench, workflow builder, and governance workspace.
- Object/filesystem storage providers for oversized artifacts, exports,
  validation evidence, fixture payloads, and QA/test-bench outputs.

## Active Domain Areas

- Platform foundation and access control (001-002): tenant/principal metadata,
  role grants, Auth0/local-principal auth, and access decision records.
- Workflow registry, studio, builder, and publish gates (003, 013, 024):
  workflow lineages, active drafts, immutable revisions, published bundles,
  validation results, graph preview, publish gates, sharing grants, and
  repository-backed required test-bench evidence.
- Durable runtime, immutable memory, and graph execution (004, 005, 020):
  workflow runs, run steps, worker leases, checkpoints, handoffs, side-effect
  intents, approvals, timeline events, parent-child lineage, memory scopes,
  immutable memory versions, and parallel sub-agent scheduling.
- User interaction channels and Telegram delivery/configuration (006, 017,
  022): channel sessions, normalized requests, callbacks, notification
  attempts, Telegram tenant config, link-token audit, linked identities,
  command aliases, webhook update receipts, and mocked-safe Bot API delivery.
- Model/skill routing and model provider gateway (007, 011, 012 V2, 021, 025):
  provider catalog entries, versioned model routing, tool/outbound/credential
  policies, prompt/profile/provider provenance, runtime pins, provider
  connections, gateway operations, physical attempts, health snapshots,
  live secret resolution, and skill connector execution summaries.
- Prompt library and runtime profiles (012): prompt lineages, drafts,
  immutable versions, render tests, prompt audit records, agent runtime profile
  versions, tenant grants, bundle pins, and run provenance metadata.
- Audit, debugging, reliability, and operations (008, 009, 019): append-only
  audit events, traces, timeline/search/replay records, redaction and
  classification records, reliability policies, queues, quotas, fairness
  windows, retry schedules, circuit breakers, compensation/dead-letter records,
  operational snapshots, and platform operations console exports.
- Admin console, membership administration, and saved filters (010, 018):
  React admin shell navigation, tenant-scope handling, authorization-aware
  destinations, persisted saved filters, invitations, tenant memberships,
  role-grant refresh, and membership audit records.
- Skill registry lifecycle (014, 014-v2): package manifests, immutable package
  versions, tenant availability and installation state, credential readiness,
  validation evidence, smoke-test evidence, quarantine decisions, upgrade
  lineage, binding eligibility projections, revision tokens, and browser-first
  admin workflows.
- Agent/workflow test bench, usage analytics, and briefing preferences (015,
  016, 023): test suites/cases/assertions/runs/artifacts, publish-gate
  requirements, normalized LLM usage and pricing metadata, export requests,
  briefing preference heads/revisions/imports/exports, and runtime preference
  resolution evidence.

## Project Structure

```text
src/multi_agent_platform/
- admin/                  # Admin domain services: workflow registry, skill registry, memberships, Telegram config, briefing preferences
- api/
  - routers/              # Admin APIs/UI routes, channel webhooks, runtime endpoints, auth, ops
  - schemas/              # Pydantic API schemas
  - ui/                   # Safe admin view helpers and redirect utilities
- audit/                  # Audit capture, inspection, classification, exports
- auth/                   # Auth0/local-principal auth, policies, dependencies
- bootstrap/              # API/worker container wiring
- channels/               # Web/REST/Telegram channels, notifications, delivery
- config/                 # Model/skill config catalog, policies, resolver
- db/                     # Async session, models, repositories
- memory/                 # Immutable memory service and repository
- model_providers/        # Provider catalog, probes, gateway, adapters, secret resolution
- observability/          # Logging, metrics, tracing
- operations/             # Platform operations console aggregation and exports
- prompts/                # Prompt library, previews, workflow hooks
- reliability/            # Admission, leases, quotas, retries, breakers, dead letters
- runtime/                # Orchestration, graph execution, skill tools, runtime resolvers
- secrets/                # Secret provider abstractions
- skill_execution/        # Governed first-party tool connector gateway
- storage/                # Object/filesystem storage abstractions
- tenancy/                # Tenant context and guards
- testing/                # Agent/workflow test bench helpers
- usage/                  # Token usage and cost analytics
- web_admin/              # React static assets and non-Jinja browser support
- workers/                # Worker loop entrypoints

alembic/versions/           # Migrations 0001 through 0020 as of 2026-05-04
tests/
- contract/
- docs/
- fixtures/
- integration/
- performance/
- unit/

specs/                      # Spec Kit feature artifacts 001 through 033
docs/
scripts/
```

## Commands

- `uv sync`
- `uv run alembic upgrade head`
- `uv run uvicorn multi_agent_platform.api.main:app --reload`
- `uv run python -m multi_agent_platform.workers.main`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest`
- `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- `uv run python scripts/qa/run_spec_qa.py <validation.yml>`
- `uv run python scripts/qa/run_playwright_ui.py <validation.yml> --start-processes`

## Code Style

Python 3.12: follow standard conventions with explicit type annotations on
public boundaries. Keep FastAPI routers thin and wire services through
dependencies/container helpers. Put business behavior in domain services and
repository modules that follow existing SQLAlchemy 2.x async patterns.

Use Pydantic v2 models for contracts and validation. Keep all tenant,
principal, workflow version, profile version, prompt version, provider, skill,
and revision identifiers explicit at boundaries. Cross-tenant checks fail
closed.

Never persist, render, log, export, or include in QA artifacts raw secrets,
credential values, provider authorization headers, private channel messages,
raw prompts/completions, memory contents, unauthorized run payloads, or raw
external tool payloads. Use existing redaction, fingerprinting, safe-summary,
artifact-reference, and audit helpers.

Local and CI validation should avoid real provider, Telegram, credential, and
external tool calls unless a spec explicitly marks an approved live probe path.
Prefer deterministic mocks/fakes that still exercise authorization, tenancy,
secret-reference, policy, idempotency, and persistence behavior.

Tests should scale with the changed surface: unit coverage for domain logic,
repository tests for persistence and tenant filters, httpx/TestClient
integration coverage for API/UI flows, performance tests for bounded queries,
docs/QA tests for generated guides, and Playwright validation for browser-first
admin workflows.

## Recent Changes
- codex/048-live-data-inventory-and-mock-guardrails: Added Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26` + FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv

- 033-react-agent-and-workflow-test-bench: Planned additive React test bench
  workspace for guided suite and case authoring, safe execution-mode selection,
  deterministic run launch, backend-owned run progress, pass/fail diagnostics,
  redacted traces, artifact references, current-revision publish-gate evidence,
  and browser-first QA over existing Spec 015/020/024/025 services.
- 032-react-skill-registry-and-tool-execution-lifecycle: Completed additive
  React skill lifecycle workspace for platform package publication, manifest
  validation, tenant grants, tenant discovery and installation, credential
  reference configuration, smoke-test/readiness evidence, first-party connector
  diagnostics, SkillExecutionGateway evidence, binding eligibility previews,
  quarantine/withdrawal states, stale conflict recovery, audit timeline, and
  browser-first redaction-safe QA over existing Specs 014/014-v2/021 services.
  governance workspace for provider setup/health, credential-reference
  diagnostics, platform-admin-only probes and credential-reference actions,
  prompt versions and safe previews, runtime profiles, read-only routing
  previews, policy history, direct-call guardrail evidence, and run provenance
  over existing provider/prompt/profile/routing/gateway services with QA docs
  and Playwright evidence.
  backend-owned draft/reference/graph/validation/publish contracts, guided
  semantic saves, stale-revision recovery, React Flow graph preview with
  accessible lists, required evidence, publish confirmation, revision history,
  read-only JSON inspection, QA docs, and Playwright evidence.
  operations workbench over existing operations, reliability, run inspection,
  graph runtime, provider gateway, Telegram/channel delivery, skill execution,
  usage, audit, redaction, export, and fallback route services with QA docs and
  Playwright evidence.
  backend-owned React admin page envelopes, safe problem details, form and
  mutation result contracts, filter/pagination/sorting metadata, export
  snapshots, evidence summaries, reusable React table/form/mutation helpers,
  harmless `/admin/app/patterns` sample page, QA docs, and Playwright evidence.
  shell and design system with backend-authorized navigation, persistent
  scope awareness, breadcrumbs, saved-filter chips, command/search over safe
  destinations, responsive shell layouts, WCAG-oriented primitives, QA docs,
  and Playwright evidence.
  with `/admin/app`, backend-owned bootstrap/navigation contracts,
  generated TypeScript types, Vite/npm tooling, FastAPI-served built assets,
  dual Auth0/local-principal validation, QA docs, and Playwright evidence.
  credential resolution for provider probes and ModelGateway calls using
  `ProviderSecretResolver`, safe secret reference selection, fail-closed OpenAI
  behavior, local allowlisted no-auth behavior, redaction-safe diagnostics, and
  focused provider/gateway tests.
  Completed repository-backed required test-bench evidence for workflow
  validation, publish gate responses, published bundle summaries, and admin UI
  evidence rendering.
  Intelligence Briefing preferences with immutable revisions, admin/user UI,
  JSON import/export, safe admin summaries, runtime resolver, and Telegram alias
  context injection.
  tenant-scoped Telegram command aliases, persistent identity/link-token
  consumption, update receipts, readiness checks, mockable Bot API delivery,
  and durable delivery attempts.
  `SkillExecutionGateway` support for first-party read-only Daily Briefing
  connector tools with policy enforcement, redaction, normalized outputs, and
  admin diagnostics.
  graph execution for published workflow bundles, deterministic role execution
  for QA, parallel branch scheduling, join policies, step/timeline evidence,
  manual resolution pauses, and worker integration.
  Operations Console aggregation over existing health, reliability, provider,
  Telegram, usage, gateway, and audit/debugging records with redacted CSV
  exports.
  administration with invitations, tenant memberships, role guardrails,
  next-request grant refresh, admin UI/API flows, and safe audit records.
  with tenant enablement, safe token audit, linked identity summaries,
  diagnostics, local fake-secret readiness, and redaction-safe admin UI.
  estimated-cost analytics with usage/pricing tables, ModelGateway capture,
  tenant dashboards, safe CSV export metadata, and audit-safe access logging.
  tenant-scoped suites, cases, assertions, durable runs, artifacts, mocked-safe
  execution, and workflow publication gate evidence.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the latest plan:
`specs/059-admin-ui-transitional-react-label-removal/plan.md`
<!-- SPECKIT END -->
