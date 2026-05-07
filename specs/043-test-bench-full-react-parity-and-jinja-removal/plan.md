# Implementation Plan: Test Bench Full React Parity And Jinja Removal

**Branch**: `codex/043-test-bench-full-react-parity-and-jinja-removal` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/043-test-bench-full-react-parity-and-jinja-removal/spec.md`

## Summary

Complete the React test bench migration by closing deletion-grade parity gaps for suite and case authoring, run launch and progress, result diagnostics, artifact metadata, publish-gate evidence, audit timeline, safe execution modes, stale evidence handling, and all old `/admin/agent-tests/ui...` direct links. Keep the JSON APIs used by React, convert test-bench browser-rendering Jinja handlers into authenticated redirects or safe non-Jinja compatibility responses, delete only test-bench-owned templates/static surfaces, and prove the result with dual-auth backend tests, focused React tests, route/import scanners, QA docs, Spec QA, and Playwright evidence.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing `testing.agent_bench` services/repositories, `api/schemas/admin_test_bench.py`, `api/schemas/agent_tests.py`, `api/routers/admin_agent_tests.py`, `api/routers/admin_react.py`, React 19, Vite, Testing Library, Vitest, generated TypeScript contracts, audit/redaction helpers  
**Storage**: Existing PostgreSQL-backed agent test suites, cases, assertions, runs, run steps, publication requirements, artifact metadata, audit references, plus object/filesystem artifact references; no new tables planned  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, generated contract drift check, Vitest, Testing Library, Vite build, Spec QA runner, Playwright QA runner  
**Target Platform**: FastAPI admin app with production Auth0 and local-principal validation, served React admin UI, and deterministic local QA database `multi_agent_platform_qa043`  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Keep suite lists, run lists, artifact lookups, gate evidence, and audit lists bounded; maintain existing performance test coverage for React test-bench builders; avoid unbounded client polling or rendering raw trace/artifact payloads  
**Constraints**: No real Auth0, Telegram, provider, credential, connector, or external tool calls in local/CI; no raw secrets, credential values, provider headers, raw prompts/completions, memory contents, raw run payloads, private messages, connector/tool payloads, raw test transcripts, local paths, storage paths, stack traces, full Telegram identifiers, link tokens after creation, or unauthorized tenant labels in UI, redirects, exports, screenshots, QA artifacts, logs, or docs; keep global Jinja infrastructure until Spec 047  
**Scale/Scope**: One bounded admin domain: `/admin/app/test-bench` React child routes, `/admin/agent-tests` JSON APIs retained, `/admin/agent-tests/ui...` browser routes converted, `agent_tests` templates removed, docs/tests/validation refreshed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I Durable By Default**: PASS. Run launch remains idempotent, backend-owned, and resume-safe; browser redirects do not become state authority.
- **II Immutable State And Memory**: PASS. Suites, cases, runs, run steps, artifact references, and gate evidence keep existing revision/audit semantics.
- **III Contract-First Agent Coordination**: PASS. React consumes generated Pydantic/TypeScript contracts; legacy redirect metadata is documented and tested.
- **IV Security With Practical Development Ergonomics**: PASS. Plan requires Auth0-shaped backend tests and local-principal Playwright validation.
- **V Operability Is A Product Requirement**: PASS. Result diagnostics, progress snapshots, trace summaries, artifacts, audit timeline, and gate evidence remain visible.
- **VI Spec-Driven Delivery**: PASS. Work continues through specify, clarify, plan, tasks, analysis, implementation, docs, and validation.
- **VII Test And Documentation Discipline**: PASS. Focused backend/frontend tests, QA docs, generated assets, and full Spec QA are required.
- **VIII Clear Ownership And Small Safe Changes**: PASS. Deletion scope is limited to test-bench-owned Jinja browser surfaces.
- **IX Tenant Isolation And Fair Scheduling**: PASS. Active tenant scope and cross-tenant denials remain backend-owned and route-tested.
- **X Version-Pinned Execution**: PASS. Target revision binding and stale evidence rejection are first-class acceptance criteria.
- **XI Secret Hygiene And Controlled Tool Access**: PASS. Default local/CI execution stays mocked; approved real probes are summarized only when policy permits.
- **XII Tiered Storage For Large Payloads**: PASS. Artifacts render as metadata references, not inline payloads or DB blobs.
- **XIII Human Approval Is Durable State**: PASS. Probe approval and publish readiness remain persisted policy/gate evidence rather than browser state.

## Project Structure

### Documentation (this feature)

```text
specs/043-test-bench-full-react-parity-and-jinja-removal/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── test-bench-react-parity-ui.md
│   └── test-bench-react-parity.openapi.yaml
├── checklists/
│   └── requirements.md
├── qa043.md
├── qa043_ui.md
├── qa043_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/
│   │   ├── admin_agent_tests.py
│   │   └── admin_react.py
│   └── schemas/
│       ├── admin_test_bench.py
│       └── agent_tests.py
├── testing/agent_bench/
│   ├── react_test_bench.py
│   └── service.py
└── web_admin/templates/agent_tests/       # deleted after redirect parity lands

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/testBench/
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/api/test_admin_agent_tests_api.py
├── integration/api/test_admin_agent_tests_legacy_redirects.py
├── integration/test_admin_react_routes.py
├── performance/test_bench/test_react_test_bench_queries.py
├── unit/admin/test_test_bench_jinja_retirement.py
├── unit/admin/test_test_bench_react_service.py
└── unit/api/test_admin_test_bench_schema.py
```

**Structure Decision**: Reuse the existing Spec 033 React test bench schemas, services, routes, components, and tests. Extend only where deletion-grade parity requires route metadata, React child route handling, redirect targets, stale evidence labels, or safe direct-link states. Keep `/admin/agent-tests` JSON APIs available for existing API clients while retiring `/admin/agent-tests/ui...` template rendering.

## Phase 0: Research

Research decisions are recorded in [research.md](research.md). Main decisions:

- Convert `/admin/agent-tests/ui...` GET routes to authenticated redirects into `/admin/app/test-bench` child routes and keep unsafe requests as safe non-Jinja problems.
- Keep `/admin/agent-tests` JSON API routes because they are not browser-rendering Jinja surfaces and are still part of the platform contract.
- Retain backend-owned bounded polling/status snapshots for run progress; do not introduce a new SSE channel in this removal spec.
- Render artifacts as metadata references only, and map old artifact-style links to React metadata panels where authorized.
- Bind gate evidence to the current target revision and require explicit stale/current evidence states in React.

## Phase 1: Design And Contracts

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/test-bench-react-parity.openapi.yaml](contracts/test-bench-react-parity.openapi.yaml)
- [contracts/test-bench-react-parity-ui.md](contracts/test-bench-react-parity-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- **Durability and versioning** remain satisfied because redirects do not create authority and run/gate state remains persisted, idempotent, and target-revision-bound.
- **Tenant isolation and security** remain satisfied because redirect handlers use existing principal and tenant checks, unsafe destinations are rejected, and cross-tenant ids return safe denials.
- **Contract-first delivery** remains satisfied by extending Pydantic/OpenAPI contracts and generated TypeScript types before React consumption.
- **Secret and artifact hygiene** remain satisfied because artifacts and traces are metadata-only and all docs/screenshots are redaction-safe.
- **Documentation/test discipline** remains satisfied by QA docs, focused tests, route/import scanners, Spec QA, and Playwright before queue advancement.

No constitution violations or justified exceptions are present.

## Complexity Tracking

No constitution violations require complexity exceptions.
