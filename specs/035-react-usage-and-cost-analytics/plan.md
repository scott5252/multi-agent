# Implementation Plan: React Usage And Cost Analytics

**Branch**: `codex/035-react-usage-and-cost-analytics` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/035-react-usage-and-cost-analytics/spec.md`

## Summary

Build an additive React usage analytics workspace for platform and tenant
administrators. Spec 016 usage capture, pricing metadata, safe CSV exports,
audit records, existing usage repositories, Auth0/local-principal
authorization, and tenant scoping remain authoritative. The React route will
consume backend-owned JSON contracts and generated TypeScript types for
summary metric cards, daily trends, safe rollups, bounded event drilldowns,
filter metadata, export creation/detail, confidence states, denied states, and
empty/partial/unavailable guidance.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing `usage` service/repository/export helpers, Auth0/local-principal auth, audit helpers, React admin shell, generated TypeScript contracts, lucide-react  
**Storage**: PostgreSQL 16+ usage, pricing, reconciliation, export-request, tenant, audit, workflow/run, provider, and skill-execution records; object/filesystem storage for CSV export artifacts  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and deterministic local-principal validation  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Default dashboard response uses the last 7 days, returns no more than 25 rollup rows per grouping and no more than 100 drilldown rows, and keeps deterministic fixture queries under 300ms p95 in performance tests  
**Constraints**: Fail closed for auth, tenant scope, unsupported grouping, invalid date range, cross-tenant export, unavailable audit/export storage, unsafe attribution, stale pricing, and malformed usage; preserve all Spec 016 grouping dimensions while adding graph/gateway/tool attribution; never render or export raw prompts, completions, secrets, memory content, provider credentials, credential reference internals, raw tool payloads, local filesystem paths, or unauthorized run content  
**Scale/Scope**: One additive React domain route plus backend contracts/adapters, generated TypeScript, focused deterministic fixtures, docs, and validation evidence

## Constitution Check

- **Durable by default**: PASS. Export requests are persisted through existing usage export records before artifact details are returned.
- **Immutable state and memory**: PASS. The workspace reads usage events, pricing versions, reconciliation records, and audit evidence without changing runtime state except append-like export metadata.
- **Contract-first coordination**: PASS. React consumes explicit contracts for dashboard bootstrap, event drilldown, export creation/detail, filter metadata, confidence states, and denied states.
- **Security ergonomics**: PASS. Production Auth0 and deterministic local-principal modes are both required in tests and validation.
- **Operability**: PASS. Cards, trends, rollups, drilldowns, export status, audit references, latency, unavailable usage, and confidence states expose safe operating evidence.
- **Spec-driven delivery**: PASS. Specify, clarify, plan, tasks, analyze, implementation, docs, and validation are required before advancing.
- **Test and documentation discipline**: PASS. Plan requires focused backend/frontend tests, full validation, QA docs, Playwright, quickstart, README, and PR notes.
- **Small safe changes**: PASS. Backend adapter, generated contract types, React components, route wiring, and tests are scoped to usage analytics.
- **Tenant isolation and fair scheduling**: PASS. Active scope, allowed tenant choices, filters, events, rollups, exports, and denied states are scope-aware and fail closed.
- **Version-pinned execution**: PASS. No workflow execution bundle behavior changes are introduced; workflow/prompt/profile/version references are rendered as safe labels only.
- **Secret hygiene and controlled tool access**: PASS. Local/CI execution uses deterministic fixtures and no live providers, credentials, connectors, Telegram, Auth0 provisioning, or external tool calls.
- **Tiered storage**: PASS. CSV artifact payloads remain in object/filesystem storage with PostgreSQL export metadata.
- **Human approval durable state**: PASS. No new approval/resume workflow is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/035-react-usage-and-cost-analytics/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── usage-react.openapi.yaml
│   └── usage-react-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/usage/
│   └── react_usage.py
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_usage_react.py
├── auth/policy.py
├── usage/
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/usage/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/usage/test_react_usage_queries.py
├── unit/admin/usage/test_react_usage_service.py
└── unit/api/test_admin_usage_react_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from
Specs 026-034. Backend schemas/adapters live under `api/schemas` and
`admin.usage`; FastAPI wiring remains in `api/routers/admin_react.py`; React
components live in `frontend/admin/src/components/usage`; tests extend the
existing React admin contract/integration suite with focused schema, service,
and performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main
decisions:

- Reuse Spec 016 usage services, repositories, pricing, and export helpers as
  the source of truth.
- Build an additive React projection layer for safe labels, formatted values,
  confidence badges, and bounded result sets.
- Extend grouping support through backend-owned React dimensions while keeping
  all existing Spec 016 grouping dimensions and usage filters authoritative.
- Use lightweight SVG/CSS trend rendering in React to avoid adding a charting
  dependency for the bounded dashboard view.
- Validate both Auth0-shaped and local-principal authorization paths.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/usage-react.openapi.yaml](./contracts/usage-react.openapi.yaml)
- [contracts/usage-react-ui.md](./contracts/usage-react-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Durability**: PASS. Export creation persists a request record and returns
  status/audit evidence; dashboard reads are side-effect free.
- **Tenant isolation**: PASS. Data model and contracts include active scope,
  allowed tenant choices, scope-aware filters, tenant-limited drilldowns and
  exports, and cross-tenant denial tests.
- **Authorization**: PASS. Bootstrap, events, export creation, and export detail
  routes are protected and dual-auth tested.
- **Audit safety**: PASS. Export and denied-action summaries include safe audit
  references; raw audit payloads are not rendered.
- **Redaction**: PASS. Contracts restrict rendered content to safe labels,
  aggregate metrics, artifact references, status summaries, and authorized
  filter snapshots.
- **Tool/secret safety**: PASS. Local/CI execution uses deterministic fixtures
  and no live provider, connector, Telegram, credential, or Auth0 calls.
- **Browser-first QA**: PASS. Quickstart and tasks require Playwright workflows
  for platform dashboard, tenant dashboard, grouping changes, drilldowns,
  export creation/detail, empty/partial/denied states, and redaction scans.
- **Operability**: PASS. Plan covers latency, confidence, unavailable usage,
  export state, pricing freshness, gateway/attempt attribution, and safe
  recovery guidance.

## Complexity Tracking

No constitution violations are introduced.
