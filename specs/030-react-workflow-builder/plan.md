# Implementation Plan: React Workflow Builder

**Branch**: `codex/030-react-workflow-builder` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/030-react-workflow-builder/spec.md`

## Summary

Build an additive React workflow builder at `/admin/app/workflows` that lets non-technical platform and tenant administrators create, edit, validate, review, and publish workflow drafts through guided forms and graph-oriented review. The backend remains authoritative for workflow documents, graph semantics, validation, tenant authorization, stale revisions, required evidence, and publish decisions. React consumes generated TypeScript contracts, presents accessible graph/list views, and keeps the existing Jinja editor as fallback during migration.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing workflow registry/admin services, React admin shell, generated TypeScript contracts, `@xyflow/react` pending implementation research validation  
**Storage**: PostgreSQL 16+ through existing workflow draft/revision/publish/test evidence models; filesystem storage for QA artifacts and screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and local-principal validation  
**Project Type**: Full-stack web application inside existing monorepo  
**Performance Goals**: Render deterministic 100-node workflow fixture without unbounded loops; keep validation/lookup responses bounded and local QA validation under two seconds for deterministic fixtures  
**Constraints**: Fail closed for auth/tenant/audit uncertainty; no live provider, Telegram, credential-store, or connector calls in local QA; no raw protected payloads in contracts, logs, docs, screenshots, or exports  
**Scale/Scope**: One additive React domain route plus backend contracts/services, focused fixtures, docs, and validation evidence

## Constitution Check

- **Tenant isolation**: PASS. All protected routes must resolve active scope through existing admin shell helpers and deny cross-tenant access before contract generation.
- **Authorization**: PASS. Dual-auth-mode tests are mandatory for local-principal and Auth0-shaped principals.
- **Audit safety**: PASS. Save, validation, and publish actions must fail closed when audit persistence cannot be proven.
- **Redaction**: PASS. Schema validators and service builders must sanitize raw prompts, completions, memory, credentials, provider responses, connector outputs, stack traces, local paths, and unauthorized tenant labels.
- **Immutable publishing**: PASS. Published bundles remain immutable; the builder only edits drafts and requests backend publish decisions.
- **Deterministic QA**: PASS. Local QA uses deterministic fixtures and does not call live model, Telegram, credential, or connector providers.
- **Accessibility**: PASS. Graph canvas must have keyboard/list alternatives and Playwright evidence.

## Project Structure

### Documentation (this feature)

```text
specs/030-react-workflow-builder/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-builder.openapi.yaml
│   └── workflow-builder-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_workflow_builder.py
├── admin/
│   └── workflow_builder.py
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/workflows/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/workflows/test_workflow_builder_queries.py
├── unit/admin/test_workflow_builder_service.py
└── unit/api/test_admin_workflow_builder_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from Specs 026-029. Backend schemas and deterministic service builders live under `api/schemas` and `admin`; FastAPI wiring remains in `api/routers/admin_react.py`; React components live in `frontend/admin/src/components/workflows`; tests extend the existing React admin contract/integration suite with focused workflow builder unit and performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use a proven React graph library (`@xyflow/react`) for visual graph editing/review if implementation dependency addition is accepted, because official docs describe keyboard focus and screen-reader support and built-in graph navigation.
- Keep graph layout annotations as client-side visual state only; save payloads submit semantic document changes to backend contracts.
- Expose read-only JSON inspector content from backend as redacted summaries rather than direct database documents.
- Reuse existing workflow registry, validation, publish gate, and required evidence concepts instead of inventing a new workflow persistence model.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/workflow-builder.openapi.yaml](./contracts/workflow-builder.openapi.yaml)
- [contracts/workflow-builder-ui.md](./contracts/workflow-builder-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts include explicit active scope and cross-tenant denial tests.
- **Authorization**: PASS. Contract and integration tasks include local-principal and Auth0-shaped principals.
- **Audit safety**: PASS. Save/validate/publish mutation results include audit references and dependency-unavailable states.
- **Redaction**: PASS. Data model marks all rendered text as safe summaries or artifact/reference IDs.
- **Immutable publishing**: PASS. Publish route returns immutable bundle summary only after backend gate decision.
- **Accessibility**: PASS. UI contract requires graph canvas plus list/table alternatives and keyboard tests.

## Complexity Tracking

No constitution violations are introduced.
