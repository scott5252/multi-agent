# Implementation Plan: Token Usage And Cost Analytics

**Branch**: `codex/016-token-usage-cost-analytics` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/016-token-usage-cost-analytics/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add normalized token usage and estimated-cost analytics for every
ModelGateway-backed model invocation. The implementation introduces a focused
`usage` domain package, additive PostgreSQL tables, versioned pricing metadata,
idempotent capture from `ModelGateway`, tenant-scoped dashboard APIs,
server-rendered admin views under `/admin/usage`, safe CSV export metadata,
audit-safe access logging, tests, QA docs, README updates, and Playwright
evidence.

The first implementation uses query-time rollups backed by indexed
`llm_usage_events` rows and a lightweight `llm_usage_rollups` table reserved for
future materialization. Usage capture stores safe identifiers, counts, status
flags, pricing version references, latency, and attribution metadata only. Raw
prompts, completions, secrets, memory content, provider credentials, and
unauthorized run content are never stored.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing `ModelGateway`, existing model provider catalog/attempt records,
existing admin shell, audit/redaction helpers, filesystem/object storage,
prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: New additive PostgreSQL tables for `llm_usage_events`,
`llm_usage_rollups`, `llm_pricing_versions`, `usage_export_requests`, and
`usage_reconciliation_records`. CSV payloads use object/filesystem storage
metadata rather than database blobs.  
**Testing**: pytest unit tests for usage normalization, pricing, models,
repository filters, service capture, redaction, UI view models, and export
authorization; pytest-asyncio/httpx integration tests for dashboard APIs,
server-rendered UI, tenant isolation, ModelGateway capture, CSV export audit,
late reconciliation, and query performance; docs tests for README, QA guide,
testing instructions, and PR notes; Playwright validation through the configured
QA runner.  
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, local-principal test login, PostgreSQL, and worker process.  
**Project Type**: Multi-tenant Python web service with JSON admin APIs,
server-rendered admin UI, durable runtime support, and background workers.  
**Performance Goals**: Dashboard summary p95 <= 300 ms for 10,000 usage events
inside a tenant-scoped 30-day window; event drilldown p95 <= 350 ms for 200
rows; CSV export metadata creation p95 <= 500 ms excluding artifact write;
ModelGateway capture adds <= 10 ms overhead in mocked unit tests.  
**Constraints**: Cross-tenant usage access fails closed; tenant admins see only
their tenant; future tenant users are constrained to their own principal if
exposed. No raw prompts, completions, secrets, memory content, provider
credentials, or unauthorized run content are stored, exported, or audited.
Production validation must not call real providers or production hosts.
PostgreSQL stores metadata and normalized numeric values only for CSV exports.  
**Scale/Scope**: One vertical feature slice: domain models and pricing,
database models and migration, repository, service, ModelGateway integration,
schemas, admin API router, server-rendered UI pages, auth policy entries, tests,
QA docs, manual QA user guide, PR notes, testing instructions, and README
updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Usage capture persists idempotent events and reconciliation records; CSV exports persist request state and artifact metadata. |
| Immutable State And Memory | PASS | Usage events are append-mostly, reconciliation links preserve original estimates, and pricing versions are immutable once used. |
| Contract-First Agent Coordination | PASS | Gateway capture payloads, API schemas, UI filters, CSV columns, and export audit metadata are documented before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal routes reuse admin authorization and deterministic QA principals. |
| Operability Is A Product Requirement | PASS | Capture, normalization failures, reconciliation, exports, denied access, and query summaries are logged and auditable. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation remain traceable. |
| Test And Documentation Discipline | PASS | Test-first tasks cover capture, filters, rollups, export, redaction, reconciliation, docs, Playwright, and coverage >= 90 percent. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `usage`, `model_providers`, `api`, `db`, `web_admin`, migration, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant scope is explicit in events, queries, exports, indexes, and access decisions; platform scope is role-gated. |
| Version-Pinned Execution | PASS | Usage events store workflow, prompt, profile, model routing, provider/model, pricing version, and operation identifiers when available. |
| Secret Hygiene And Controlled Tool Access | PASS | Capture uses safe metadata only and redaction tests guard storage, export, and audit paths. |
| Tiered Storage For Large Payloads | PASS | CSV export content uses storage provider artifacts with PostgreSQL metadata and retention state. |
| Human Approval Is Durable State | PASS | No new approval/resume path is introduced; denied/export access decisions are persisted as audit-safe events. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/016-token-usage-cost-analytics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── admin-usage-ui.md
│   └── usage-analytics.openapi.yaml
├── tasks.md
├── qa016.md
├── qa016_ui.md
├── qa016_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── usage/
│   ├── __init__.py
│   ├── export.py
│   ├── models.py
│   ├── pricing.py
│   └── service.py
├── model_providers/
│   ├── gateway.py
│   ├── models.py
│   └── usage.py
├── api/
│   ├── routers/
│   │   └── admin_usage.py
│   ├── schemas/
│   │   └── usage.py
│   └── ui/
│       └── usage.py
├── db/
│   ├── models/
│   │   └── usage.py
│   └── repositories/
│       └── usage.py
└── web_admin/
    └── templates/
        └── usage/
            ├── index.html
            └── export_detail.html

alembic/
└── versions/
    └── 0016_token_usage_cost_analytics.py

tests/
├── contract/
│   └── test_usage_analytics_contract.py
├── integration/
│   ├── api/
│   │   ├── test_admin_usage_api.py
│   │   └── test_admin_usage_ui.py
│   ├── db/
│   │   └── test_usage_migration.py
│   └── model_providers/
│       └── test_gateway_usage_capture.py
├── unit/
│   ├── api/
│   │   └── test_usage_ui_models.py
│   ├── db/
│   │   └── test_usage_repository.py
│   └── usage/
│       ├── test_export.py
│       ├── test_pricing.py
│       └── test_usage_service.py
└── docs/
    └── test_usage_analytics_docs.py
```

**Structure Decision**: Add a focused `usage` domain package and keep
ModelGateway capture, database repositories, API schemas, and UI view models
thin. Reuse the existing admin shell and storage provider rather than creating
a separate analytics frontend.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves capture boundary, pricing, missing provider fields, rollups,
exports, tenant isolation, redaction, and reconciliation. See
[research.md](./research.md).

Key decisions:

- Capture usage only at ModelGateway because it is the policy-governed provider
  boundary and already records gateway operation attempts.
- Extend `GatewayUsage` normalization to include cached tokens, reasoning
  tokens, provider billable units, and per-field status flags while keeping
  backward-compatible defaults.
- Use versioned internal pricing metadata and deterministic fallback estimates;
  do not call provider pricing pages during request handling or QA validation.
- Compute dashboard rollups query-time for MVP, with a `llm_usage_rollups`
  table reserved for materialization when query performance requires it.
- Write CSV exports through storage provider artifacts and keep PostgreSQL
  export request metadata for audit and retention.
- Represent late provider usage corrections as reconciliation records that
  update current event values without deleting original safe audit evidence.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines usage events, rollups, pricing
  versions, export requests, reconciliation records, states, validation rules,
  and tenant boundaries.
- [contracts/usage-analytics.openapi.yaml](./contracts/usage-analytics.openapi.yaml)
  defines the JSON admin API for summaries, event drilldown, and CSV exports.
- [contracts/admin-usage-ui.md](./contracts/admin-usage-ui.md) defines the
  server-rendered admin dashboard, filters, export action, and denied states.
- [quickstart.md](./quickstart.md) gives local setup and QA validation flows.

## API And UI Surface

- API routes live under `/admin/usage/api`.
- UI routes live under `/admin/usage`.
- All routes require an authenticated platform admin or tenant admin. Platform
  admins may select platform scope or a tenant scope. Tenant admins are forced
  to their own tenant scope.
- Navigation adds an Admin Console entry for "Usage Analytics" with tenant
  scope preservation.
- The validation plan uses `/admin/usage` for browser screenshots.

## Migration Strategy

- Add only new tables and indexes; do not rewrite existing feature tables.
- Use explicit numeric columns for token, billable-unit, latency, and cost
  values so rollups are index-friendly and simple to audit.
- Use JSON only for safe filter snapshots, safe attribution details, and export
  summaries where shape varies by provider or UI filter.
- Add tenant/time/provider/model/workflow/agent/principal indexes for dashboard
  and export filters.
- Migration downgrade drops only the new usage tables.

## Observability And Audit

- Audit-safe records are emitted for successful exports, failed exports, denied
  dashboard access, denied export access, and late reconciliation.
- Metrics include usage events captured by provider/model/status, capture
  failures, export requests by status, and reconciliation counts.
- Logs include trace id, tenant id, provider key, model id, idempotency key,
  event id, export id, and status without raw request/response content.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with usage analytics,
  `/admin/usage`, QA016 validation, and quality commands.
- Add feature PR notes and testing instructions under
  `specs/016-token-usage-cost-analytics/`.
- Generate QA docs and non-developer manual QA guide before final validation.
