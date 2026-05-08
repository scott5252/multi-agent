# Implementation Plan: Test Bench React Live Data

**Branch**: `codex/053-test-bench-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/053-test-bench-react-live-data/spec.md`

## Summary

Replace the test bench React projection helpers that currently return fixed QA033/QA043 suite, case, run, artifact, publish-gate, redirect, and audit evidence with live, authorized projections over existing `AgentTestRepository`, `AgentTestBenchService`, safe artifact metadata, workflow publish-gate evidence, and audit records. Keep the current React route family and generated contracts, but make empty scopes truthful, seeded scopes repository-backed, suite/case/run/gate actions durable or explicitly unavailable, local QA execution mocked-safe, and all details redaction-safe.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with React 19 and Vite for the admin UI  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, `AgentTestRepository`, `AgentTestBenchService`, test bench sandbox/redaction helpers, artifact metadata/storage abstractions, workflow publish-gate evidence services, React admin shell contracts, generated TypeScript API contracts  
**Storage**: PostgreSQL 16+ through existing agent test suite, case, assertion, run, run step, artifact, publication requirement, workflow, and audit tables; filesystem/object storage only for artifact metadata and QA evidence references  
**Testing**: Ruff, mypy, pytest/httpx, repository and performance query tests, contract tests, Vitest/Testing Library, generated TypeScript contract checks, Vite build, Spec QA runner, Playwright UI runner, post-UI API/database verification, multi-agent-curl-test  
**Target Platform**: FastAPI-served admin web app with Auth0-shaped backend tests and local-principal browser QA  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Test bench bootstrap and panel JSON stay bounded by explicit limits, avoid unbounded suite/run/audit/artifact scans, and keep empty-state responses cheap in fresh QA databases  
**Constraints**: No raw prompts, completions, memory contents, raw run payloads, private channel messages, raw test transcripts, raw tool payloads, local filesystem paths, stack traces, unsafe artifact contents, or unauthorized tenant data in rendered JSON, logs, screenshots, exports, or QA docs; no real provider/connector/credential/outbound calls in local or CI validation unless explicitly approved; production routes cannot return hardcoded QA033/QA043 test bench rows or fake mutation success  
**Scale/Scope**: One bounded test bench React route family plus backend projection service, route wiring, frontend empty-state handling, generated contracts, scanner inventory updates, QA seed documentation, and validation evidence

## Constitution Check

- **Durable By Default**: PASS. Safe suite/case/run/gate mutations must call existing durable test bench services or report unavailable/denied/stale states.
- **Immutable State And Memory**: PASS. Suites, cases, assertions, runs, run steps, artifact metadata, publish requirements, and audits are persisted records; no mutable in-memory source of truth.
- **Contract-First Agent Coordination**: PASS. React consumes Pydantic-generated contracts and regenerated TypeScript types with explicit live, empty, denied, unavailable, stale, queued, running, passed, failed, and blocked states.
- **Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows both exercise authorization and tenant scoping.
- **Operability Is A Product Requirement**: PASS. Progress, diagnostics, artifacts, publish-gate evidence, and audit states remain visible through safe operational evidence.
- **Spec-Driven Delivery**: PASS. Specify and clarify are complete; planning outputs define exact files and validation gates before implementation.
- **Test And Documentation Discipline**: PASS. Tasks will include unit, repository, integration, contract, scanner, performance, frontend, QA docs, Playwright, post-UI, and curl validation while preserving the 90 percent coverage gate.
- **Clear Ownership And Small Safe Changes**: PASS. Scope is limited to test bench route builders, schemas, route wiring, frontend test bench panels, generated contracts, scanner mappings, tests, QA docs, and QA seed helpers.
- **Tenant Isolation And Fair Scheduling**: PASS. All projections accept active scope, respect tenant visibility, and fail closed for cross-tenant suite, case, run, artifact, workflow, gate, and audit data.
- **Version-Pinned Execution**: PASS. Run launcher and publish-gate projections reflect persisted target revisions and safe mode policy; this spec does not alter runtime bundle pinning.
- **Secret Hygiene And Controlled Tool Access**: PASS. Local QA execution uses mocked-safe or deterministic local modes; real provider, connector, credential, and outbound probes remain denied without explicit approved references.
- **Tiered Storage For Large Payloads**: PASS. Raw transcripts and artifact contents are not rendered; artifact references remain metadata-only.
- **Human Approval Is Durable State**: PASS. Approved real probes remain unavailable without durable approval references; no approval/resume behavior changes are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/053-test-bench-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── test-bench-live-data.openapi.yaml
│   └── test-bench-live-data-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── testing/agent_bench/react_test_bench.py
├── testing/agent_bench/service.py
├── testing/agent_bench/redaction.py
├── db/repositories/agent_tests.py
├── db/models/agent_tests.py
├── api/routers/admin_react.py
├── api/schemas/admin_test_bench.py
├── admin/migration_hardening/live_data_inventory.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/testBench/
├── test/testBenchTestData.ts
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── contract/test_agent_test_bench_contract.py
├── integration/test_admin_react_routes.py
├── integration/api/test_admin_agent_tests_api.py
├── performance/test_bench/test_react_test_bench_queries.py
├── unit/admin/test_test_bench_react_service.py
├── unit/admin/test_live_data_inventory_scanner.py
├── unit/api/test_admin_test_bench_schema.py
├── unit/db/test_agent_tests_repository.py
└── unit/testing/agent_bench/
```

**Structure Decision**: Keep the existing React admin test bench route family and frontend component structure from Spec 033/043. Replace the fixed backend projection implementation in `testing/agent_bench/react_test_bench.py` with async live service/repository projection helpers and update route wiring in `admin_react.py` where repository/service dependency injection or async calls are needed.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use existing agent test repositories and services as the source of truth for suites, cases, assertions, runs, run steps, publication requirements, idempotent launches, and evidence summaries.
- Use safe artifact metadata and artifact references only; do not expose storage paths or artifact contents.
- Add explicit provenance and empty-state metadata to test bench responses so reviewers can tell live data, denied data, unavailable data, and empty data apart.
- Keep local QA run launch mocked-safe or deterministic local-only.
- Prefer one safe durable UI action for Playwright, likely launching a seeded suite or saving a suite/case, then verify persistence through API or database evidence.
- Use scanner assertions to keep fixed QA033/QA043 test bench markers out of production responses while retaining test-only fixtures and historical specs.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/test-bench-live-data.openapi.yaml](./contracts/test-bench-live-data.openapi.yaml)
- [contracts/test-bench-live-data-ui.md](./contracts/test-bench-live-data-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts and tests require tenant, platform shell, denied, empty, and seeded scopes.
- **Authorization**: PASS. Suite authoring, case authoring, run launch, artifact access, gate refresh, and audit read remain permission-controlled.
- **Redaction**: PASS. Fixture summaries, assertion summaries, run diagnostics, trace excerpts, artifact metadata, and audits render safe summaries only.
- **Durability**: PASS. Mutations persist through existing services or return unavailable/denied/stale states; no browser-only success defaults.
- **Operability**: PASS. Plans require progress, diagnostics, artifacts, gate freshness, and audit evidence.
- **Validation**: PASS. The post-spec contract requires QA docs, Spec QA, Playwright, post-UI API/database verification, and curl validation before Spec 054 starts.

## Complexity Tracking

No constitution violations are introduced.
