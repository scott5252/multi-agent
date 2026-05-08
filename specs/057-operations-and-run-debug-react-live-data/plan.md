# Implementation Plan: Operations And Run Debug React Live Data

**Branch**: `codex/057-operations-and-run-debug-react-live-data` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/057-operations-and-run-debug-react-live-data/spec.md`

## Summary

Replace deterministic operations workbench and run-debug projections with live
service/repository-backed evidence. The implementation will migrate
`src/multi_agent_platform/operations/workbench.py` and the React operations
routes to read bounded operational evidence from existing operations,
reliability, runtime, provider, channel, skill-execution, usage, audit-debug,
and storage sources, returning truthful empty/denied/unavailable states when no
evidence exists. Workbench exports will persist backend evidence and expose only
safe artifact references.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript strict mode with React 19 frontend  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL, existing operations/reliability/runtime/audit/provider/channel/usage services, React Router, Vite, Testing Library, Playwright  
**Storage**: PostgreSQL for operational evidence and export metadata; filesystem/object storage provider for export artifacts  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, frontend typecheck/build, Playwright, Spec QA, multi-agent curl runner  
**Target Platform**: Local/CI FastAPI admin platform with React admin UI and PostgreSQL 16+  
**Project Type**: Web service plus React admin application  
**Performance Goals**: Workbench and run-debug queries stay bounded to the selected time range and return at most contract-defined list limits; performance tests verify bounded query behavior with seeded data.  
**Constraints**: No raw secrets, credentials, provider authorization headers, prompts, completions, memory contents, raw run payloads, private channel messages, raw tool payloads, local filesystem paths, stack traces, or unauthorized tenant labels in browser/API/docs/artifacts. No intermediate commits are required during autopilot.  
**Scale/Scope**: Operations workbench routes, run-debug route, export route, React workbench components/tests, QA seed/verifier, scanner guardrails, generated contracts, docs, and validation manifest for Spec 057.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Workbench exports persist export metadata and artifact references; live evidence comes from durable services and PostgreSQL-backed records.
- Immutable State And Memory: PASS. The feature reads append-only audit/runtime records and creates export evidence rather than mutating operational state except through explicit export requests.
- Contract-First Agent Coordination: PASS. React consumes backend-owned Pydantic contracts regenerated into TypeScript.
- Security With Practical Development Ergonomics: PASS. Auth0-shaped route tests and local-principal browser QA remain required.
- Operability Is A Product Requirement: PASS. This spec directly improves operational visibility and records QA evidence.
- Spec-Driven Delivery: PASS. Specify, clarify, plan, tasks, analyze, implement, and validation phases are tracked in queue/status.
- Test And Documentation Discipline: PASS. Plan includes focused backend/frontend tests, performance tests, QA docs, Playwright, and curl regression.
- Clear Ownership And Small Safe Changes: PASS. Work is bounded to operations/run-debug workbench surfaces, repositories needed for live reads, QA helpers, tests, and scanner expectations.
- Tenant Isolation And Fair Scheduling: PASS. Tenant views hide platform-only pressure and fail closed for cross-tenant run/debug/export access.
- Version-Pinned Execution: PASS. Run-debug projections use persisted runtime bundle/timeline evidence where available.
- Secret Hygiene And Controlled Tool Access: PASS. Output and artifacts expose safe summaries only.
- Tiered Storage For Large Payloads: PASS. Export artifacts use the configured storage provider with PostgreSQL metadata.
- Human Approval Is Durable State: PASS. No new approval flow is introduced; run-debug/replay links remain evidence links only.

## Project Structure

### Documentation (this feature)

```text
specs/057-operations-and-run-debug-react-live-data/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── operations-run-debug-live-data.openapi.yaml
│   └── operations-run-debug-live-data-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── operations/
│   ├── service.py
│   └── workbench.py
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_workbench.py
├── db/repositories/
│   ├── audit_debugging.py
│   ├── runtime_orchestration.py
│   ├── channels.py
│   ├── usage.py
│   └── skill_registry.py
└── admin/migration_hardening/live_data_inventory.py

frontend/admin/src/
├── components/workbench/
├── api/generated/reactAdminApi.ts
└── test/

tests/
├── fixtures/
├── integration/test_admin_react_routes.py
├── performance/operations/
├── unit/admin/
└── unit/api/

scripts/qa/
├── seed_operations_qa057.py
└── verify_operations_qa057.py
```

**Structure Decision**: Keep the existing backend `operations.workbench`
projection boundary, but convert it to dependency-injected live builders and
repository/service reads. Keep React components in `frontend/admin/src/components/workbench`
and regenerate the existing admin React API contract after schema changes.

## Complexity Tracking

No constitution violations are expected.

## Phase 0: Research

Research covers source-of-truth decisions, tenant/platform visibility, bounded
query behavior, export persistence, likely-cause derivation, and QA seed
strategy. Findings are recorded in [research.md](research.md).

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](data-model.md)
- [contracts/operations-run-debug-live-data.openapi.yaml](contracts/operations-run-debug-live-data.openapi.yaml)
- [contracts/operations-run-debug-live-data-ui.md](contracts/operations-run-debug-live-data-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Durable export evidence, tenant isolation, generated contracts, redaction,
  object-storage boundaries, local/Auth0 validation, and QA docs remain covered
  by the design artifacts.
- No new constitution violation was introduced by Phase 1 design.
