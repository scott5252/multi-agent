# Implementation Plan: Jinja Infrastructure Decommission

**Branch**: `codex/047-jinja-infrastructure-decommission` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/047-jinja-infrastructure-decommission/spec.md`

## Summary

Remove the final server-side template infrastructure now that Specs 039 through 046 have retired every bounded Jinja-rendered surface. The implementation deletes template provider wiring from the container, removes the server template directory and legacy static assets, updates local login to self-contained non-Jinja HTML, removes the direct `jinja2` dependency, replaces migration dashboard copy with final React-only decommission evidence, adds scanner and route tests, updates docs and QA artifacts, and validates with full backend, frontend, Spec QA, and Playwright gates.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async patterns, React 19, Vite, pytest, Playwright, Ruff, mypy, uv  
**Storage**: No schema or durable state changes; existing PostgreSQL QA setup is used only for validation  
**Testing**: pytest/httpx/TestClient, import/file scanners, docs tests, generated contract checks, Vitest/Testing Library, frontend typecheck/build, Spec QA runner, Playwright UI runner  
**Target Platform**: FastAPI web application serving React static assets and non-Jinja compatibility HTML/redirects  
**Project Type**: Multi-service web platform with backend APIs and React browser UI  
**Performance Goals**: React host keeps bounded bootstrap behavior; decommission scans are test-time and service-time summaries only  
**Constraints**: No runtime Jinja imports, template provider, TemplateResponse, server-side templates, or legacy static files; no raw secrets, prompts, payloads, private messages, local paths, stack traces, or unauthorized tenant labels  
**Scale/Scope**: Presentation infrastructure only; no database migration and no domain behavior move into React

## Constitution Check

- **I. Durable By Default**: PASS. Durable domain state and APIs remain unchanged.
- **II. Immutable State And Memory**: PASS. No memory or runtime checkpoint mutation is introduced.
- **III. Contract-First Agent Coordination**: PASS. React continues to consume backend-owned generated contracts.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped route tests and local-principal browser validation remain required.
- **V. Operability Is A Product Requirement**: PASS. The migration dashboard becomes final decommission evidence with rollback notes.
- **VI. Spec-Driven Delivery**: PASS. Spec, plan, tasks, QA docs, and validation evidence are required.
- **VII. Test And Documentation Discipline**: PASS. Full quality gates, scanner tests, docs updates, and Playwright are mandatory.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is limited to Jinja infrastructure, compatibility routes, docs, and evidence.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Existing backend authorization and tenant checks remain authoritative.
- **X. Version-Pinned Execution**: PASS. Runtime version pinning and workflow bundles are untouched.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Decommission evidence is safe summaries only.
- **XII. Tiered Storage For Large Payloads**: PASS. Storage behavior is unaffected.
- **XIII. Human Approval Is Durable State**: PASS. Approval and run flows remain on retained backend APIs.

## Project Structure

### Documentation (this feature)

```text
specs/047-jinja-infrastructure-decommission/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── jinja-decommission-contract.md
│   └── jinja-decommission.openapi.yaml
├── tasks.md
├── qa047.md
├── qa047_ui.md
├── qa047_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── bootstrap/container.py
├── config/settings.py
├── admin/migration_hardening/
├── api/routers/
│   ├── admin_react.py
│   └── auth.py
├── api/schemas/admin_migration_hardening_react.py
└── web_admin/static/react/

frontend/admin/src/
├── api/
├── components/migrationHardening/
├── components/shell/
└── test/

tests/
├── unit/admin/
├── unit/bootstrap/
├── unit/config/
├── integration/api/
└── integration/test_admin_react_routes.py
```

**Structure Decision**: Keep the existing React app host and migration dashboard route. Remove only server-side template infrastructure and legacy Jinja-only static files. Retain non-Jinja redirect handlers and React static asset serving.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
