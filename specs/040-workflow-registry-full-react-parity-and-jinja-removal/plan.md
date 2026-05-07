# Implementation Plan: Workflow Registry Full React Parity And Jinja Removal

**Branch**: `codex/040-workflow-registry-full-react-parity-and-jinja-removal` | **Date**: 2026-05-06 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/040-workflow-registry-full-react-parity-and-jinja-removal/spec.md`

## Summary

Replace the remaining workflow registry Jinja browser surface with React-backed workflow list, create, draft, validation, publish-gate, revision, published-version, sharing, field-help, reference-picker, graph, direct-link, denied, and unavailable journeys. Existing workflow registry services, publish gates, tenant authorization, audit, redaction, and test-bench evidence stay authoritative. Legacy workflow browser URLs become authenticated redirects to `/admin/app/workflows` routes or non-Jinja compatibility/problem responses, and only workflow-owned templates/static assets proven obsolete by tests are deleted.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode; React 19; Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, PostgreSQL, existing workflow registry/admin services, React admin shell, generated TypeScript contracts, Vite, Testing Library, Playwright QA runner  
**Storage**: PostgreSQL 16+ through existing workflow draft/revision/publish/test evidence models; filesystem/object storage references for safe artifacts and QA screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Spec QA runner, Playwright UI runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0-shaped backend validation and local-principal browser QA  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Keep deterministic workflow registry, draft, graph, validation, and publish-gate contract responses bounded for local QA fixtures; avoid unbounded graph/render loops for 100-node workflow fixtures  
**Constraints**: Fail closed on auth, tenant, redaction, audit, publish, or stale revision uncertainty; no real Auth0, provider, Telegram, credential, connector, or external tool calls in validation; no raw protected payloads in UI, responses, docs, screenshots, exports, or logs  
**Scale/Scope**: One workflow admin domain migration slice: workflow browser routes, React contracts/components, redirect/compatibility handlers, focused tests, scanner evidence, QA docs, and workflow-owned template/static deletion

## Constitution Check

- **Durable by default**: PASS. Workflow publish and draft mutation decisions remain in existing services with persisted revisions, gate state, audit references, and idempotent/stale conflict behavior.
- **Immutable state and memory**: PASS. Published bundles and revision history remain immutable; React surfaces render summaries and request backend mutations rather than mutating runtime state in-browser.
- **Contract-first coordination**: PASS. Browser behavior uses Pydantic-owned API contracts and generated TypeScript types for workflow envelopes, redirects, mutation results, and compatibility states.
- **Security with practical ergonomics**: PASS. Auth0-shaped route tests and local-principal Playwright flows are required; local auth cannot bypass backend authorization or tenant checks.
- **Operability**: PASS. Reviewer notes, migration ledger evidence, route tests, scanner output, QA docs, and screenshots document deleted/retained workflow surfaces and recovery paths.
- **Spec-driven delivery**: PASS. Spec, plan, tasks, analysis, implementation, docs, and validation remain traceable through Spec 040.
- **Test and documentation discipline**: PASS. Tasks include focused backend/frontend tests, Spec QA, Playwright, QA guides, user guide, and reviewer notes with coverage preservation.
- **Small safe changes**: PASS. Scope is bounded to workflow browser routes and workflow-owned assets; shared shell/global Jinja infrastructure is explicitly deferred.
- **Tenant isolation and fair scheduling**: PASS. Tenant scope remains explicit in routes/contracts and cross-tenant access fails closed before contract rendering.
- **Version-pinned execution**: PASS. Workflow published version and draft revision views surface pinned bundle/revision metadata without changing runtime execution pinning.
- **Secret hygiene and controlled tool access**: PASS. No live provider/tool calls are introduced and all displayed evidence uses safe summaries or artifact references.
- **Tiered storage**: PASS. Large evidence remains referenced through artifact metadata; no blob payloads are added to PostgreSQL.
- **Human approval as durable state**: PASS. Publish confirmation and gate state remain persisted service decisions, not browser-only approval state.

## Project Structure

### Documentation (this feature)

```text
specs/040-workflow-registry-full-react-parity-and-jinja-removal/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-react-parity.openapi.yaml
│   └── workflow-react-parity-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/workflow_builder.py
├── api/
│   ├── routers/admin_react.py
│   ├── routers/admin_workflow_ui.py
│   └── schemas/admin_workflow_builder.py
└── web_admin/
    ├── templates/workflows/
    └── static/workflow_studio.*

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/workflows/
├── App.tsx
└── routes.tsx

tests/
├── contract/
├── integration/api/
├── integration/
├── unit/admin/
├── unit/api/
└── performance/workflows/
```

**Structure Decision**: Extend the existing Spec 030 React workflow builder pattern rather than introducing a second workflow UI stack. Backend route compatibility stays in `admin_workflow_ui.py`; React JSON/API contracts stay in `admin_react.py` and `admin_workflow_builder.py`; workflow React components stay under `frontend/admin/src/components/workflows`; deleted assets are limited to `web_admin/templates/workflows/*` and workflow-only static files after tests prove no remaining references.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use `/admin/app/workflows` as the canonical workflow browser surface and preserve old `/admin/workflows*` links with authenticated redirects or non-Jinja compatibility responses.
- Extend the existing workflow builder envelope instead of creating a new persistence model.
- Keep legacy workflow JSON API routes used by React and tests; retire only browser-rendering Jinja handlers.
- Validate visual graph parity with keyboard/list alternatives.
- Delete `workflow_studio.js` and `workflow_studio.css` only after scanner and tests prove no remaining references.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/workflow-react-parity.openapi.yaml](./contracts/workflow-react-parity.openapi.yaml)
- [contracts/workflow-react-parity-ui.md](./contracts/workflow-react-parity-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Durability and immutable publish state**: PASS. Draft save, stale conflict, validation, publish, revision, and published version flows remain backend-owned.
- **Contract-first React migration**: PASS. Required UI states and legacy route mappings are represented by backend contracts and generated TypeScript.
- **Security, tenant isolation, and redaction**: PASS. Dual-auth tests, local-principal browser QA, denied states, and redaction sweeps are required before template deletion.
- **Bounded deletion**: PASS. Only workflow-owned templates/static assets may be deleted in Spec 040; shared shell/global Jinja infrastructure stays for later specs.
- **Docs and validation**: PASS. QA docs, reviewer notes, Spec QA, and Playwright evidence are planned before queue advancement.

## Complexity Tracking

No constitution violations are introduced.
