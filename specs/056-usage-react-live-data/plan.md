# Implementation Plan: Usage React Live Data

**Branch**: `codex/056-usage-react-live-data` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/056-usage-react-live-data/spec.md`

## Summary

Replace deterministic React usage analytics payloads with live, authorized
projections over persisted usage events, pricing versions, usage rollups,
export requests, reconciliation evidence, and safe attribution metadata. The
usage workspace must render true empty states, live totals/trends/drilldowns,
confidence-aware cost displays, and a durable browser-driven export action
verified through qa056 backend/database evidence.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript strict mode with React 19 and Node.js `>=20.19.0 <26` for `frontend/admin`.  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, PostgreSQL, existing `UsageRepository`, `UsageAnalyticsService`, storage provider abstractions, React Router, Vite, Vitest, Testing Library, generated TypeScript contracts.  
**Storage**: PostgreSQL is the source of truth for `llm_usage_events`, pricing versions, optional rollups, usage export requests, reconciliation records, runtime/provider/skill attribution references, audit evidence, and artifact metadata; filesystem/object storage holds export payload bytes behind persisted metadata.  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, repository/integration tests, performance tests for bounded date windows, Ruff, mypy, Vitest, TypeScript typecheck, Vite build, QA document validation, Spec QA, Playwright, post-UI verifier, multi-agent curl test.  
**Target Platform**: FastAPI web service serving React admin assets and backend-owned JSON contracts.  
**Project Type**: Full-stack web application in the existing monorepo.  
**Performance Goals**: Usage dashboard and drilldown queries must apply tenant, date, provider/model/status, grouping, and limit filters before rendering; default range is last 30 days and drilldowns remain capped.  
**Constraints**: No raw prompts, completions, memory content, run payloads, tool payloads, secrets, credential values, authorization headers, local filesystem paths, stack traces, or unauthorized tenant labels in API/UI/docs/artifacts; no real provider or external storage calls in local QA beyond configured local storage.  
**Scale/Scope**: Spec 056 owns `admin/usage` React projection and route surfaces plus directly related schema, frontend, QA, scanner, repository/service, and validation artifacts.

## Constitution Check

*GATE: Passed before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Export creation persists `usage_export_requests` and artifact metadata before the UI reports durable evidence.
- Immutable State And Memory: PASS. Usage events, pricing versions, reconciliation records, export requests, and audit references remain persisted append-only/versioned records.
- Contract-First Agent Coordination: PASS. React consumes Pydantic-owned contracts and generated TypeScript types.
- Security With Practical Development Ergonomics: PASS. Auth0-shaped backend tests and local-principal Playwright validation both exercise authorization and tenant scoping.
- Operability Is A Product Requirement: PASS. Confidence states, rollups, export status, audit references, and source metadata explain data provenance.
- Spec-Driven Delivery: PASS. Specification, clarification, plan, research, model, contracts, tasks, analysis, implementation, and validation are required.
- Test And Documentation Discipline: PASS. QA docs, automated tests, Spec QA, Playwright, post-UI verifier, and curl regression are required.
- Clear Ownership And Small Safe Changes: PASS. Scope is bounded to usage React live-data surfaces and supporting repository/service helpers.
- Tenant Isolation And Fair Scheduling: PASS. Usage access scope and filters fail closed for cross-tenant requests and bounded queries prevent unbounded scans.
- Version-Pinned Execution: PASS. Runtime/workflow/prompt/profile references are rendered as safe persisted identifiers/labels only; this spec does not alter execution bundles.
- Secret Hygiene And Controlled Tool Access: PASS. Usage payloads and exports must redact secrets, credentials, raw prompts, raw completions, memory, and tool payloads.
- Tiered Storage For Large Payloads: PASS. Export bytes stay in storage; PostgreSQL stores request, row count, checksum, size, URI/reference, and audit metadata.
- Human Approval Is Durable State: PASS. No approval semantics are introduced; denied/unavailable export outcomes are persisted or returned safely.

## Project Structure

### Documentation (this feature)

```text
specs/056-usage-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── usage-react-live-data.openapi.yaml
│   └── usage-react-live-data-ui.md
├── qa056.md
├── qa056_ui.md
├── qa056_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/usage/react_usage.py
├── api/routers/admin_react.py
├── api/schemas/admin_usage_react.py
├── db/models/usage.py
├── db/repositories/usage.py
├── usage/
├── storage/
└── web_admin/static/react/

frontend/admin/src/
├── api/generated/reactAdminApi.ts
├── components/usage/
├── test/
└── routes.tsx

scripts/qa/
├── seed_usage_qa056.py
└── verify_usage_qa056.py

tests/
├── fixtures/
├── integration/
├── performance/
└── unit/
```

**Structure Decision**: Use the existing FastAPI admin route, backend usage
projection, usage repository/service, generated contract, React component, and
pytest/Vitest layout. No new package or application boundary is needed.

## Complexity Tracking

No constitution violations require justification.

## Phase 0: Research

Research decisions are captured in [research.md](research.md). The key outcome
is to make `UsageAnalyticsService` and `UsageRepository` the source of truth for
React projections, with narrowly scoped repository helpers for export history or
source metadata when existing public service methods do not yet expose them.

## Phase 1: Design And Contracts

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/usage-react-live-data.openapi.yaml](contracts/usage-react-live-data.openapi.yaml)
- [contracts/usage-react-live-data-ui.md](contracts/usage-react-live-data-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

*GATE: Passed after Phase 1 design.*

Design stays within existing usage services, generated contracts, tenant-scoped
access checks, redaction helpers, bounded queries, local QA seeding, persisted
export requests, storage-backed artifact references, and mandatory validation
before queue advancement.
