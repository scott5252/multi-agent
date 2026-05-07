# Implementation Plan: User-Facing Run UI React Port And Jinja Removal

**Branch**: `codex/046-user-facing-run-ui-react-port-and-jinja-removal` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/046-user-facing-run-ui-react-port-and-jinja-removal/spec.md`

## Summary

Replace the remaining user-facing `/runs` browser experience with React-only direct links while retaining the established channel run JSON APIs for lifecycle behavior. The implementation extends generated frontend contracts for the channel run schemas, adds a focused React run workspace at `/admin/app/channels/runs` and `/admin/app/channels/runs/{run_id}` for start/status/timeline/actions/result/artifact/subscription/callback flows, keeps `/runs` browser routes as authenticated redirects to React, and proves deleted Jinja run templates remain unused through route, scanner, backend, frontend, QA, and Playwright evidence.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async patterns where durable state is used, React 19, Vite, generated TypeScript contracts, pytest, Playwright  
**Storage**: Existing PostgreSQL-backed runtime/channel state plus filesystem/object storage metadata for artifacts; no schema migration expected  
**Testing**: pytest/httpx/TestClient, Ruff, mypy, Vitest/Testing Library, generated contract checks, QA docs validator, Spec QA runner, Playwright UI runner  
**Target Platform**: FastAPI web application with React browser client served by existing static host  
**Project Type**: Multi-service web platform with backend APIs and frontend admin/channel React app  
**Performance Goals**: React run pages load bounded safe summaries from retained APIs; timeline polling remains bounded by API limits and avoids unbounded event streams in browser QA  
**Constraints**: No Jinja rendering for `/runs`; no raw prompts, run payloads, private messages, callback secrets, full external identifiers, stack traces, local paths, or unauthorized tenant labels; retain JSON APIs used by web, Telegram, and API channels  
**Scale/Scope**: User-facing run browser route family plus retained run lifecycle APIs; admin run inspection remains owned by Spec 044

## Constitution Check

- **I. Durable By Default**: PASS. Run lifecycle behavior stays in retained service/API paths with existing idempotency and persisted state; React is a view/action client.
- **II. Immutable State And Memory**: PASS. The feature does not mutate memory models or runtime snapshots outside retained service methods.
- **III. Contract-First Agent Coordination**: PASS. React uses generated TypeScript contracts from Pydantic channel run schemas plus documented API contract artifacts.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend route tests and local-principal Playwright flows remain mandatory.
- **V. Operability Is A Product Requirement**: PASS. The UI surfaces trace/audit references and preserves status/timeline/action evidence.
- **VI. Spec-Driven Delivery**: PASS. Spec, plan, tasks, QA docs, and validation artifacts are in scope before completion.
- **VII. Test And Documentation Discipline**: PASS. Focused backend/frontend tests, scanner tests, docs validation, full Spec QA, and Playwright are required.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is bounded to user-facing `/runs` compatibility, channel run contracts, and React run workspace components.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Existing scope dependencies and actor mapping remain backend-owned; tests prove cross-tenant denial.
- **X. Version-Pinned Execution**: PASS. The feature does not alter runtime bundle pinning; run execution APIs remain authoritative.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Artifact/callback handling shows only safe metadata and never secrets or storage paths.
- **XII. Tiered Storage For Large Payloads**: PASS. Artifact downloads remain short-lived grants from retained metadata APIs.
- **XIII. Human Approval Is Durable State**: PASS. Prompt decisions continue through retained persisted approval APIs with version checks.

## Project Structure

### Documentation (this feature)

```text
specs/046-user-facing-run-ui-react-port-and-jinja-removal/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── user-facing-run-react-ui.md
│   └── user-facing-run-react.openapi.yaml
├── tasks.md
├── qa046.md
├── qa046_ui.md
├── qa046_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/routers/
│   ├── channel_runs.py
│   └── web_run_ui.py
├── api/schemas/channel_runs.py
└── web_admin/
    ├── static/react/
    └── templates/

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/userRuns/
│   ├── UserRunPage.tsx
│   └── UserRunPage.test.tsx
└── App.tsx

tests/
├── contract/test_admin_react_contract.py
├── integration/api/test_channel_run_api.py
├── integration/api/test_web_run_ui.py
├── integration/channels/test_cross_channel_recovery.py
└── unit/admin/test_user_runs_jinja_retirement.py
```

**Structure Decision**: Extend the existing React admin/channel app host rather than adding a second frontend bundle. Existing `/runs` and `/runs/new` browser routes stay FastAPI-authenticated and redirect to `/admin/app/channels/runs`; `/runs/{run_id}` redirects to `/admin/app/channels/runs/{run_id}` after a safe access check; retained `/runs` JSON APIs remain the lifecycle contract.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
