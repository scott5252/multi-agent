# Implementation Plan: No-Jinja React Host, Auth, Shell Utilities, And Local Login

**Branch**: `codex/039-no-jinja-react-host-auth-shell-utilities-and-local-login` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/spec.md`

## Summary

Spec 039 removes server-side Jinja rendering from the admin entry path and local-login path. The implementation will replace `admin_react/app.html` with a non-Jinja React host renderer, convert `/auth/local-login` to React plus backend-owned JSON/action contracts, redirect old `/admin` and shell utility URLs to React or non-Jinja problem responses, port saved-filter management and shell states into React, delete only the proven obsolete shell/auth templates and Jinja-only asset, and record retirement evidence in the migration dashboard and QA artifacts.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async, existing Auth0/local-principal auth dependencies, React 19, Vite, Testing Library, Vitest, pytest, httpx/TestClient  
**Storage**: Existing PostgreSQL admin saved-filter tables and audit records; repository QA artifacts under `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/`; no new durable tables expected  
**Testing**: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, targeted backend contract/unit/integration tests, frontend Vitest/Testing Library tests, `npm run build`, QA docs validation, Spec 039 QA runner, Playwright local-principal validation  
**Target Platform**: FastAPI admin application serving React admin assets with deterministic local QA and Auth0-shaped backend tests  
**Project Type**: Full-stack web application with backend-owned JSON contracts and React presentation  
**Performance Goals**: React host response remains lightweight and cache-safe; bootstrap and saved-filter responses stay within existing Spec 037 local QA budgets; browser refresh on deep React routes loads without additional server-rendering work  
**Constraints**: No real Auth0, Telegram, provider, credential, connector, or external tool calls; no browser-owned auth/tenant/redaction decisions; no raw secrets/private payloads/local filesystem paths/stack traces/unauthorized tenant labels in UI, redirects, docs, screenshots, logs, or artifacts; no global `jinja2` dependency removal until Spec 047  
**Scale/Scope**: Spec 039 owns `/admin`, `/admin/app`, `/admin/app/*` host fallback behavior, `/auth/local-login`, `/auth/local-logout`, shell utility redirects, saved-filter management, unavailable/denied shell states, `admin_react/app.html`, `auth/local_login.html`, `admin_shell/*.html`, and `web_admin/static/admin_shell.js`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I Durable By Default**: PASS. Auth/session behavior keeps server-owned redirects and audit records; no workflow runtime state is changed.
- **II Immutable State And Memory**: PASS. Existing saved-filter and audit persistence is reused; no mutable runtime memory is introduced.
- **III Contract-First Agent Coordination**: PASS. Local-login, shell redirect, saved-filter, and host metadata are defined through Pydantic contracts and generated TypeScript types before React consumption.
- **IV Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal browser flows both remain required; local mode stays explicitly configured and fail-closed outside local/CI.
- **V Operability Is A Product Requirement**: PASS. Retirement evidence, redirect decisions, audit failure handling, unavailable states, and rollback notes are part of the plan.
- **VI Spec-Driven Delivery**: PASS. Specify, clarify, plan, tasks, analysis, implementation, and validation remain sequential.
- **VII Test And Documentation Discipline**: PASS. Plan requires backend/frontend tests, generated contracts, QA docs, Playwright evidence, and reviewer notes.
- **VIII Clear Ownership And Small Safe Changes**: PASS. Deletion scope is limited to shell/auth templates and the shell-only static asset proven obsolete by this spec.
- **IX Tenant Isolation And Fair Scheduling**: PASS. Tenant scope remains explicit in contracts, redirects, saved filters, and tests.
- **X Version-Pinned Execution**: PASS. No workflow execution bundle behavior changes.
- **XI Secret Hygiene And Controlled Tool Access**: PASS. No real credential or connector calls; all surfaced evidence uses redaction-safe summaries.
- **XII Tiered Storage For Large Payloads**: PASS. No new blob persistence; screenshots and QA artifacts remain file/object references.
- **XIII Human Approval Is Durable State**: PASS. Deletion evidence requires reviewer-facing records before later specs rely on retired surfaces.

## Project Structure

### Documentation (this feature)

```text
specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── no-jinja-host-auth-react-ui.md
│   └── no-jinja-host-auth.openapi.yaml
├── qa039.md
├── qa039_ui.md
├── qa039_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/routers/
│   ├── admin_console.py
│   ├── admin_react.py
│   └── auth.py
├── api/schemas/
│   ├── admin_react.py
│   └── auth.py
├── api/ui/admin_console.py
└── web_admin/
    ├── static/
    └── templates/

frontend/admin/src/
├── App.tsx
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/
│   ├── auth/
│   ├── savedFilters/
│   ├── shell/
│   └── states/
├── routes.tsx
└── styles/admin.css

tests/
├── contract/
├── integration/api/
└── unit/
```

**Structure Decision**: Reuse `admin_react.py` as the React host/API router, `auth.py` for local-principal auth endpoints, `admin_console.py` for legacy shell redirects and saved-filter route conversion, `admin_react.py` schemas for shell/bootstrap extensions, and existing React shell/saved-filter components for UI parity. Delete only `admin_react/app.html`, `auth/local_login.html`, `admin_shell/*.html`, and `web_admin/static/admin_shell.js` after tests prove all old browser routes are non-Jinja.

## Phase 0: Research

Research decisions are captured in [research.md](research.md).

## Phase 1: Design And Contracts

Design artifacts are captured in [data-model.md](data-model.md), [contracts/no-jinja-host-auth.openapi.yaml](contracts/no-jinja-host-auth.openapi.yaml), [contracts/no-jinja-host-auth-react-ui.md](contracts/no-jinja-host-auth-react-ui.md), and [quickstart.md](quickstart.md).

## Post-Design Constitution Check

- **Contract-first** remains satisfied by Pydantic/OpenAPI/TypeScript contracts for local-login, shell redirects, host metadata, saved filters, and safe problem responses.
- **Security and tenant isolation** remain satisfied because server-owned auth dependencies validate all host/auth/shell routes and React receives only authorized bootstrap data.
- **Deletion safety** remains satisfied because template deletion is bounded to Spec 039 inventory items and requires route tests proving no TemplateResponse path remains.
- **Documentation discipline** remains satisfied by required QA docs, user guide, PR notes, Playwright evidence, and validation manifests.

No constitution violations or justified exceptions are present.

## Complexity Tracking

No constitution violations require complexity exceptions.
