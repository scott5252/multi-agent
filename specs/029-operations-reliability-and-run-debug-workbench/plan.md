# Implementation Plan: Operations, Reliability, And Run Debug Workbench

**Branch**: `codex/029-operations-reliability-and-run-debug-workbench` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/029-operations-reliability-and-run-debug-workbench/spec.md`

## Summary

Add a React operations, reliability, and run debug workbench under the existing
React admin shell. The workbench reuses existing operations, audit debugging,
runtime graph, reliability, model provider, Telegram/channel, skill execution,
usage, storage, and redaction services to produce backend-owned JSON contracts
for platform triage, tenant-limited status, run debug timelines, reliability
recovery, redacted logs, safe cross-links, and export snapshots.

The implementation remains additive. Existing Jinja pages for operations,
reliability, run inspection, provider governance, Telegram, skill diagnostics,
usage, and audit/debugging stay available as fallbacks until Spec 037 proves
retirement criteria.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with React 19, Vite, and Node.js `>=20.19.0 <26` for the admin frontend.  
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing OperationsConsoleService, audit debugging service/repository, reliability repositories and policies, runtime orchestration repositories, model provider gateway health/attempt records, Telegram/channel delivery services, skill execution diagnostics, usage service, object/filesystem storage providers, generated React admin contracts, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv.  
**Storage**: No new tables for v1. Reuse existing health, reliability, audit timeline/trace, gateway attempt, usage, provider, channel delivery, runtime run/step/checkpoint/lineage, skill execution, and artifact metadata sources. Workbench exports use configured artifact storage and existing audit/export evidence patterns.  
**Testing**: Unit tests for workbench schemas, redaction, aggregation, likely-cause summaries, and frontend components; contract tests for OpenAPI and generated TypeScript drift; integration tests for Auth0-shaped and local-principal route behavior, platform/auditor access, tenant-limited access, denied/cross-tenant behavior, run debug, export snapshots, and safe problem details; performance tests for bounded log/timeline aggregation; Vitest component tests; Playwright browser validation for local-principal platform view, tenant view, denied view, run debug, and export flow; QA docs validation and full coverage gate.  
**Target Platform**: Existing FastAPI control-plane application, background worker process, PostgreSQL, local macOS/Linux development, and Linux container deployment.  
**Project Type**: Multi-tenant web service with backend-owned JSON contracts and a React admin frontend served by FastAPI.  
**Performance Goals**: Workbench summary p95 <= 700 ms with deterministic QA fixtures; log table p95 <= 300 ms for a last-60-minutes window over 10,000 redacted operational events; run debug timeline p95 <= 500 ms for 100 timeline/step records; export request response <= 1s excluding storage backend latency; frontend first useful render <= 2s in local Playwright validation.  
**Constraints**: All protected routes fail closed if auth, tenant scope, or audit-safe access cannot be proven. Tenant admins see only explicitly authorized tenant-scoped data. Platform-wide data is platform-admin/auditor only. No real provider, Telegram, credential, or external tool calls in QA. React does not duplicate business rules. Raw prompts, completions, memory contents, private channel messages, provider authorization headers, raw provider responses, raw Telegram updates, raw tool payloads, credential values, stack traces, local filesystem paths, and unauthorized tenant labels never reach React.  
**Scale/Scope**: One React domain migration slice: workbench schemas, aggregation service, protected React routes, generated TypeScript contracts, React page/components, tests, performance coverage, docs, QA artifacts, and validation manifest. No Jinja retirement and no schema migration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Workbench reads durable health, reliability, run, gateway, delivery, audit, and artifact evidence; exports return durable artifact references and audit metadata. |
| Immutable State And Memory | PASS | The feature reads immutable or append-only operational evidence and does not mutate workflow definitions, memory contents, or run payloads. |
| Contract-First Agent Coordination | PASS | Backend-owned workbench contracts, run debug contracts, action contracts, and export snapshots are planned before implementation. |
| Security With Practical Development Ergonomics | PASS | Production Auth0 and local-principal test paths both exercise authorization, tenant scope, and denial behavior. |
| Operability Is A Product Requirement | PASS | The feature is an operator-facing diagnostic surface with health, reliability, graph, gateway, channel, tool, usage, and log evidence. |
| Spec-Driven Delivery | PASS | Specify, clarify, plan, research, data model, contracts, quickstart, tasks, implementation, QA docs, and validation remain traceable. |
| Test And Documentation Discipline | PASS | Plan includes backend, frontend, contract, performance, Playwright, QA docs, README, quickstart, and coverage gates. |
| Clear Ownership And Small Safe Changes | PASS | Changes are scoped to workbench schemas/service/routes, React workbench components, generated types, tests, docs, and validation. |
| Tenant Isolation And Fair Scheduling | PASS | Scope is explicit in every route and contract; tenant admins cannot see platform-only queues, providers, dependencies, or cross-tenant run evidence. |
| Version-Pinned Execution | PASS | The workbench displays pinned run/bundle evidence where available and does not change execution bundle semantics. |
| Secret Hygiene And Controlled Tool Access | PASS | The feature summarizes connector/tool/provider diagnostics without resolving or rendering secret values or raw tool/provider payloads. |
| Tiered Storage For Large Payloads | PASS | Export artifacts use configured object/filesystem storage; PostgreSQL stores metadata and references only. |
| Human Approval Is Durable State | PASS | Replay/remediation actions use confirmation metadata and existing durable approval/reliability records where state could change. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/029-operations-reliability-and-run-debug-workbench/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── operations-workbench.openapi.yaml
│   └── operations-workbench-ui.md
├── tasks.md
├── qa029.md
├── qa029_ui.md
├── qa029_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── operations/
│   └── workbench.py
├── api/
│   ├── routers/
│   │   └── admin_react.py
│   └── schemas/
│       └── admin_workbench.py
└── web_admin/
    └── static/
        └── react/

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/
│   └── workbench/
│       ├── WorkbenchPage.tsx
│       ├── WorkbenchSummaryGrid.tsx
│       ├── WorkbenchTimeline.tsx
│       ├── WorkbenchReliabilityPanel.tsx
│       └── WorkbenchExportPanel.tsx
├── styles/
│   └── admin.css
└── test/
    └── workbenchTestData.ts

tests/
├── contract/
│   └── test_admin_react_contract.py
├── integration/
│   └── test_admin_react_routes.py
├── performance/
│   └── operations/
│       └── test_workbench_queries.py
├── unit/
│   ├── api/
│   │   └── test_admin_workbench_schema.py
│   └── operations/
│       └── test_workbench_service.py
└── docs/
    └── test_react_workbench_docs.py
```

**Structure Decision**: Keep the React route surface in `admin_react.py` so
the workbench shares the existing React shell, bootstrap, assets, and policy
entries. Add a focused operations workbench service that adapts existing
operations/reliability/runtime/provider/channel/tool/usage/audit services into
safe React contracts. Keep browser components under a new `workbench` folder
and reuse Spec 028 data/form primitives.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves source-of-truth boundaries, role/scope behavior, aggregation
strategy, performance bounds, redaction, run debug composition, reliability
recovery, exports, refresh behavior, and frontend UX. See [research.md](./research.md).

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines the workbench envelope, health and
  pressure summaries, likely-cause guidance, run debug timeline, graph branch
  summaries, gateway/tool/channel summaries, reliability recovery summaries,
  log summaries, and export snapshots.
- [contracts/operations-workbench.openapi.yaml](./contracts/operations-workbench.openapi.yaml)
  defines the protected React workbench, run debug, export, and safe problem
  endpoints.
- [contracts/operations-workbench-ui.md](./contracts/operations-workbench-ui.md)
  defines the React user journeys, states, filters, timeline drawer, recovery
  panel, and screenshot expectations.
- [quickstart.md](./quickstart.md) gives local QA029 setup, deterministic curl
  checks, frontend checks, full Spec QA, and Playwright validation.

## API And UI Surface

- React page route: `/admin/app/operations`.
- Workbench envelope: `/admin/app/operations.json`.
- Run debug envelope: `/admin/app/operations/runs/{workflow_run_id}.json`.
- Workbench export request: `/admin/app/operations/export`.
- Existing Jinja fallbacks remain `/admin/operations`,
  `/admin/reliability/ui/`, `/admin/runs`, `/admin/model-providers`,
  `/admin/telegram`, `/admin/skill-execution/ui/diagnostics`, and
  `/admin/usage`.
- Browser validation uses local-principal login at
  `/auth/local-login?redirect_to=/admin/app/operations`.

## Migration Strategy

- No database migration is required for v1.
- Existing Jinja routes stay enabled.
- React workbench contracts are additive and can be disabled by removing the
  route/policy entries without affecting existing operations routes.
- Future specs may deepen individual domain pages but should keep these
  workbench contracts as the overview and triage layer.

## Observability And Audit

- Workbench reads use existing access decisions and route-level authorization.
- Export requests must persist safe audit/export metadata and return artifact
  references.
- Denied export or replay-oriented requests must record safe denial categories
  where existing helpers support that evidence.
- Redaction tests cover every unsafe source category listed in the spec.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with React operations workbench
  route, QA029 validation, and fallback behavior.
- Add QA029 API/database guide, UI walkthrough, manual user guide, and
  reviewer notes under the feature directory.
- Update `AGENTS.md` to point the Spec Kit context at this plan.
