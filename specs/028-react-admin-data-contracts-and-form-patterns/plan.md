# Implementation Plan: React Admin Data Contracts And Form Patterns

**Branch**: `codex/028-react-admin-data-contracts-and-form-patterns` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/028-react-admin-data-contracts-and-form-patterns/spec.md`

## Summary

Build reusable backend-owned data contracts and frontend form/table patterns for
future React admin pages. Spec 028 adds typed page envelopes, safe problem
details, mutation result contracts, filters, pagination, sorting, export
snapshots, evidence summaries, and a harmless sample patterns page mounted
inside the Spec 027 React shell. The implementation keeps domain rules,
authorization, tenant scoping, redaction, audit evidence, and export artifact
references in backend services while React renders generated TypeScript
contracts and shared helpers.

## Technical Context

**Language/Version**: Python 3.12; TypeScript 5.8; React 19; Node `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async patterns where needed, Vite, React Testing Library, Vitest, Playwright, lucide-react  
**Storage**: No new durable tables expected; sample contracts use deterministic in-memory data and existing tenant/auth/audit surfaces  
**Testing**: pytest, TestClient/httpx, contract tests, route integration tests, Vitest, Testing Library, Playwright QA scripts, Ruff, mypy  
**Target Platform**: FastAPI-served admin web app with React assets under `/admin/static/react`  
**Project Type**: Web app with Python backend contracts and TypeScript frontend workspace  
**Performance Goals**: Page envelopes remain bounded; sample pagination caps page size; frontend helpers avoid unbounded client-side work  
**Constraints**: Backend owns authorization, scope, allowed filters, mutation acceptance, stale conflict checks, action token semantics, audit references, export references, and redaction  
**Scale/Scope**: Shared contracts and sample page for all future React admin domain specs; no major domain page migration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Tenant isolation remains backend-enforced for every page, action, export, and command.
- Browser code receives generated contracts and does not duplicate domain policy.
- Redaction rules remain fail-closed for problem details, mutation results, evidence, exports, and sample records.
- No production provider, Telegram, credential, Auth0, or external connector calls are required for local QA.
- Existing Jinja routes remain active.
- Tests cover backend contract/routes, frontend helpers/components, dual auth behavior, redaction, stale conflict, idempotency, exports, QA docs, and Playwright evidence.
- The implementation must preserve full-suite coverage above 90 percent.

**Gate Status**: PASS. No constitution violation is required.

## Project Structure

### Documentation (this feature)

```text
specs/028-react-admin-data-contracts-and-form-patterns/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── react-admin-patterns.openapi.yaml
├── tasks.md
├── qa028.md
├── qa028_ui.md
├── qa028_user_guide.md
├── .env.qa028
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/api/
├── routers/admin_react.py
└── schemas/
    ├── admin_react.py
    └── admin_patterns.py

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/
│   ├── data/
│   ├── forms/
│   └── patterns/
├── hooks/
└── App.tsx

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
└── unit/api/test_admin_patterns_schema.py
```

**Structure Decision**: Extend the existing React admin backend router and generated-type workflow while adding a dedicated schema module for reusable data/form contracts. Add frontend helpers under `frontend/admin/src/components/data`, `frontend/admin/src/components/forms`, and `frontend/admin/src/hooks` so future domain pages can consume them without coupling to the sample page.

## Phase 0: Research

Research outputs are captured in [research.md](./research.md).

Key decisions:

- Use a generic `AdminPageEnvelope` and specific sample payloads instead of one envelope per domain.
- Use safe problem details rather than raw HTTP exceptions in browser-facing contracts.
- Use revision and idempotency metadata in contracts while keeping real mutation semantics in backend services.
- Use backend-owned filter profiles, sorting fields, and pagination bounds.
- Use safe export snapshots and artifact references rather than raw export payloads.
- Use a harmless sample page at `/admin/app/patterns` for visual and contract validation.

## Phase 1: Design

Design outputs:

- [data-model.md](./data-model.md)
- [contracts/react-admin-patterns.openapi.yaml](./contracts/react-admin-patterns.openapi.yaml)
- [quickstart.md](./quickstart.md)

Contract additions:

- Admin page envelope.
- Safe problem details.
- Field validation and form descriptor metadata.
- Mutation action/result contracts.
- Stale conflict and idempotency replay metadata.
- Filter profile, filter chips, sorting, and pagination metadata.
- Safe export snapshots and artifact references.
- Evidence, delivery, runtime, and gateway safe summaries.
- Sample page payload and sample action endpoints.

## Phase 1 Constitution Re-check

- Backend remains authoritative for all protected metadata and mutations.
- React routes remain additive and do not retire Jinja routes.
- Contract additions use safe summaries and generated TypeScript validation.
- QA remains deterministic through `.env.qa028`, local-principal login, Auth0-shaped route tests, and sample-only mutation behavior.

**Gate Status**: PASS.

## Complexity Tracking

No constitution violations are introduced.
