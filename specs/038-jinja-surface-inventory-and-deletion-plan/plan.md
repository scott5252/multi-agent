# Implementation Plan: Jinja Surface Inventory And Deletion Plan

**Branch**: `codex/038-jinja-surface-inventory-and-deletion-plan` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/038-jinja-surface-inventory-and-deletion-plan/spec.md`

## Summary

Spec 038 creates the deletion-grade ledger for the React UI2 Jinja removal roadmap. The implementation will add a deterministic scanner for templates, Jinja-only static assets, TemplateResponse/Jinja2Templates usage, route metadata, template helper references, and docs/QA direct links; project those findings through backend-owned Pydantic contracts; render a redaction-safe inventory section in the existing `/admin/app/migration` React dashboard; and produce reviewer/QA evidence. This spec is inventory-only: no Jinja templates, fallback routes, app-host templates, or dependencies are deleted.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, Starlette/Jinja2 currently present for legacy surfaces, React 19, Vite, Testing Library, Vitest, pytest, httpx/TestClient  
**Storage**: Repository-generated JSON evidence under `specs/038-jinja-surface-inventory-and-deletion-plan/`; no new PostgreSQL tables  
**Testing**: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, targeted pytest contract/unit/integration tests, frontend `npm test -- --run`, generated TypeScript contract check, Spec 038 QA validation, Playwright validation  
**Target Platform**: FastAPI admin application with React admin UI served by existing backend assets  
**Project Type**: Full-stack web application with backend-owned JSON contracts and React presentation  
**Performance Goals**: Scanner completes against repository fixtures in under 5 seconds in unit tests; migration dashboard bootstrap remains under Spec 037 budget of 500 ms for backend projection in local QA-sized data  
**Constraints**: No real Auth0, Telegram, provider, credential, or connector calls; no deletion of Jinja runtime files; no exposure of local filesystem absolute paths, raw secrets, raw prompts/completions, memory contents, raw run payloads, raw tool payloads, private channel messages, stack traces, full Telegram identifiers, unauthorized tenant labels, or credential values  
**Scale/Scope**: All Jinja templates under `src/multi_agent_platform/web_admin/templates`, legacy assets under `src/multi_agent_platform/web_admin/static`, TemplateResponse and Jinja2Templates references under `src/multi_agent_platform`, docs/QA direct links, and planned removal specs 039 through 047

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I Durable By Default**: PASS. Spec 038 does not change runtime workflow state or side effects; generated evidence is deterministic and can be regenerated.
- **II Immutable State And Memory**: PASS. No mutable runtime memory or workflow state is introduced.
- **III Contract-First Agent Coordination**: PASS. New inventory data is defined through Pydantic schemas and generated TypeScript contracts before React consumption.
- **IV Security With Practical Development Ergonomics**: PASS. Backend tests cover Auth0-shaped principals and local-principal QA exercises browser behavior.
- **V Operability Is A Product Requirement**: PASS. The scanner emits reviewer evidence, blocker reasons, owner categories, planned removal specs, and dashboard summaries.
- **VI Spec-Driven Delivery**: PASS. Specification, clarification, plan, tasks, analysis, implementation, and validation remain sequential.
- **VII Test And Documentation Discipline**: PASS. Tasks include backend/frontend tests, generated contracts, QA docs, Playwright evidence, and user/reviewer guides.
- **VIII Clear Ownership And Small Safe Changes**: PASS. Scope is limited to scanner, contracts, dashboard projection, docs, and tests.
- **IX Tenant Isolation And Fair Scheduling**: PASS. Inventory APIs remain protected and tenant-filtered through existing React admin shell dependencies.
- **X Version-Pinned Execution**: PASS. No workflow execution bundle behavior changes.
- **XI Secret Hygiene And Controlled Tool Access**: PASS. Evidence references are redaction-safe and scanner output uses repo-relative paths only.
- **XII Tiered Storage For Large Payloads**: PASS. No large payload persistence; screenshots/artifacts stay in QA evidence locations.
- **XIII Human Approval Is Durable State**: PASS. Inventory requires explicit reviewer signoff before later deletion specs treat any surface as deletion-approved.

## Project Structure

### Documentation (this feature)

```text
specs/038-jinja-surface-inventory-and-deletion-plan/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── jinja-inventory-react-ui.md
│   └── jinja-inventory.openapi.yaml
├── qa038.md
├── qa038_ui.md
├── qa038_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/migration_hardening/
│   ├── __init__.py
│   ├── jinja_inventory.py
│   └── react_migration_hardening.py
├── api/routers/admin_react.py
└── api/schemas/
    └── admin_migration_hardening_react.py

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/migrationHardening/
│   ├── JinjaInventoryPanel.tsx
│   ├── JinjaInventoryPanel.test.tsx
│   ├── MigrationHardeningPage.tsx
│   └── MigrationSummaryHeader.tsx
├── styles/admin.css
└── test/migrationHardeningTestData.ts

tests/
├── contract/test_admin_migration_jinja_inventory_contract.py
├── integration/api/test_admin_react_migration_inventory_routes.py
├── unit/admin/test_jinja_inventory_scanner.py
└── unit/api/test_admin_migration_hardening_react_schema.py
```

**Structure Decision**: Reuse the Spec 037 migration hardening service and React page so reviewers keep one migration ledger. Add scanner logic under `admin/migration_hardening`, extend the existing `admin_migration_hardening_react` schema, expose inventory through `/admin/app/migration/jinja-inventory.json`, and add a focused React panel in the existing migration workspace.

## Phase 0: Research

Research decisions are captured in [research.md](research.md).

## Phase 1: Design And Contracts

Design artifacts are captured in [data-model.md](data-model.md), [contracts/jinja-inventory.openapi.yaml](contracts/jinja-inventory.openapi.yaml), [contracts/jinja-inventory-react-ui.md](contracts/jinja-inventory-react-ui.md), and [quickstart.md](quickstart.md).

## Post-Design Constitution Check

- **Contract-first** remains satisfied by generated Pydantic and TypeScript contracts.
- **Security and tenant isolation** remain satisfied because the inventory endpoint uses the existing React admin shell auth/scope flow and returns only safe repo-relative evidence references.
- **No deletion behavior** remains explicit in schema, tasks, QA docs, and reviewer notes.
- **Documentation discipline** remains satisfied by required QA docs, user guide, PR notes, generated evidence, and validation manifests.

No constitution violations or justified exceptions are present.

## Complexity Tracking

No constitution violations require complexity exceptions.
