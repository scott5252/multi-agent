# Implementation Plan: React Admin Migration Hardening And Jinja Retirement

**Branch**: `codex/037-react-admin-migration-hardening-and-jinja-retirement` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/037-react-admin-migration-hardening-and-jinja-retirement/spec.md`

## Summary

Deliver a cautious final React admin migration hardening layer: backend-owned route parity inventory, React migration dashboard, route decision evidence, direct-link and rollback guidance, accessibility/performance/redaction evidence, and validation for major admin journeys from Specs 026 through 036. The implementation will not delete legacy templates by default; it will classify and document routes, redirect primary navigation where already proven, and retain old direct routes as safe fallbacks unless the retirement criteria are met.

## Technical Context

**Language/Version**: Python 3.12; TypeScript/React/Vite admin frontend from Specs 026-036  
**Primary Dependencies**: FastAPI, Pydantic v2, existing React admin router and shell contracts, generated TypeScript API contract generator, React, Vitest, Playwright, Ruff, mypy  
**Storage**: No new durable tables required for QA037; deterministic parity evidence is projected from route inventory, existing protected surfaces, static migration decisions, and validation artifacts. Filesystem/object storage remains the evidence location for screenshots and QA artifacts.  
**Testing**: pytest contract/integration/unit/performance tests, Vitest, TypeScript check, Vite build, Spec QA runner, Playwright UI runner, QA docs validator, redaction scans  
**Target Platform**: FastAPI admin control plane and React admin SPA served from `/admin/app`  
**Project Type**: Web admin application with backend-owned JSON contracts and React rendering  
**Performance Goals**: React admin home and migration dashboard bootstrap under 500 ms in deterministic QA; primary admin journey screens interactive within 2 seconds; compressed React assets remain within documented QA037 budget or include mitigation notes  
**Constraints**: No real Auth0, Telegram, provider, credential, or connector calls in local QA; no backend domain behavior rewrites; no legacy UI deletion unless retirement evidence is explicit; all protected paths fail closed on auth, tenant, audit, or redaction uncertainty  
**Scale/Scope**: Covers migrated React admin surfaces from Specs 026-036 plus legacy route decisions for domains from Specs 003, 006-025 that supplied admin UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. The feature changes admin route ownership and evidence presentation, not runtime side effects; rollback is documented through feature flags and asset versions.
- **II. Immutable State And Memory**: PASS. Migration decisions are static evidence records and QA artifacts; no mutable workflow or memory source of truth is introduced.
- **III. Contract-First Agent Coordination**: PASS. React consumes explicit Pydantic-backed migration hardening contracts and generated TypeScript types.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped integration tests and local-principal Playwright flows remain mandatory.
- **V. Operability Is A Product Requirement**: PASS. Route parity, rollback, direct-link behavior, performance, accessibility, and redaction evidence are operator-facing.
- **VI. Spec-Driven Delivery**: PASS. Specification, clarification, plan, tasks, analysis, implementation, QA docs, and validation are required before completion.
- **VII. Test And Documentation Discipline**: PASS. Focused tests, full QA, Playwright, README, quickstart, QA docs, user guide, and PR notes are required.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Changes are additive and limited to migration schemas, projection service, React dashboard, route wiring, docs, and tests.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Parity evidence explicitly records platform, tenant-admin, and tenant-user route behavior, including denied routes.
- **X. Version-Pinned Execution**: PASS. Safe run/status links remain read-only; no runtime execution bundle behavior changes.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Migration evidence rejects unsafe secret, prompt, channel, run, tool, and local path markers.
- **XII. Tiered Storage For Large Payloads**: PASS. Screenshots and QA artifacts remain filesystem/object-storage evidence, not PostgreSQL blobs.
- **XIII. Human Approval Is Durable State**: PASS. No approval/resume behavior changes are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/037-react-admin-migration-hardening-and-jinja-retirement/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── migration-hardening-react.openapi.yaml
│   └── migration-hardening-react-ui.md
├── qa037.md
├── qa037_ui.md
├── qa037_user_guide.md
├── .env.qa037
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/migration_hardening/                 # React-safe parity and rollback projections
├── api/schemas/admin_migration_hardening_react.py
├── api/routers/admin_react.py                 # React home/migration routes and JSON endpoints
├── auth/policy.py                             # Protected migration route surfaces
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── App.tsx
├── routes.tsx
├── components/migrationHardening/
├── styles/admin.css
└── test/migrationHardeningTestData.ts

tests/
├── unit/api/test_admin_migration_hardening_react_schema.py
├── unit/admin/test_migration_hardening_service.py
├── performance/migration_hardening/test_react_migration_hardening_queries.py
├── contract/test_admin_react_contract.py
└── integration/test_admin_react_routes.py
```

**Structure Decision**: Reuse the established additive React admin migration pattern: safe backend schema module, deterministic admin projection service, protected routes in the existing React admin router, generated frontend contracts, page-specific components, focused tests, QA docs, and validation manifest. Legacy templates are not removed unless the parity matrix marks them eligible.

## Phase 0 Research

Research output is recorded in [research.md](research.md). All planning unknowns are resolved by the Spec 037 clarifications and Specs 026-036 implementation patterns.

## Phase 1 Design

Design outputs:

- [data-model.md](data-model.md)
- [contracts/migration-hardening-react.openapi.yaml](contracts/migration-hardening-react.openapi.yaml)
- [contracts/migration-hardening-react-ui.md](contracts/migration-hardening-react-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

PASS. The design remains additive, auditable, reversible, tenant-scoped, redaction-first, contract-first, and mock-safe for local validation. No constitution waivers are required.

## Complexity Tracking

No constitution violations require justification.
