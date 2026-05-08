# Implementation Plan: Live Data Inventory And Mock Guardrails

**Branch**: `codex/048-live-data-inventory-and-mock-guardrails` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/048-live-data-inventory-and-mock-guardrails/spec.md`

## Summary

Build the first live-data cleanup guardrail layer for the React admin UI. The change adds a repository scanner that inventories production React route handlers, backend projection builders, frontend production source, generated contracts, and built assets for prohibited deterministic fixture data. It classifies current findings, exposes reviewer-safe inventory evidence on the migration dashboard, adds CI-suitable guardrail tests, and validates empty and seeded QA route responses. This spec intentionally does not replace the major domain builders; Specs 050 through 057 own those live-data migrations.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async test setup, React 19, Vite, pytest, Playwright, Ruff, mypy, uv  
**Storage**: No database schema change. Scanner inventory is computed from repository files and route responses; QA artifacts are written under `.data/qa048-artifacts`.  
**Testing**: pytest scanner/unit tests, httpx/TestClient integration tests, generated contract check, frontend test/typecheck/build for migration evidence UI, Spec QA runner, Playwright UI runner, post-UI API/database verification, multi-agent curl test  
**Target Platform**: FastAPI web application serving React admin assets and backend-owned JSON contracts  
**Project Type**: Multi-service web platform with backend APIs and React browser UI  
**Performance Goals**: Scanner completes within normal CI bounds on production source and generated assets; route response scans stay bounded to enumerated `/admin/app` JSON endpoints and avoid unbounded database reads  
**Constraints**: No raw secrets, prompts, completions, private channel messages, raw run payloads, raw tool payloads, stack traces, local filesystem paths, full external identifiers, or unauthorized tenant labels in scanner output, route responses, docs, screenshots, or logs  
**Scale/Scope**: Spec 048 owns inventory, classification, guardrails, route response scanning, reviewer evidence, docs, and QA. It does not remove the large deterministic builders for workflows, governance, skills, test bench, memberships, channels, usage, or operations.

## Constitution Check

- **I. Durable By Default**: PASS. No runtime workflow durability changes; QA evidence is filesystem artifact output only.
- **II. Immutable State And Memory**: PASS. No mutable workflow or memory state is introduced.
- **III. Contract-First Agent Coordination**: PASS. React consumes backend-owned Pydantic schemas and generated TypeScript contracts for the new inventory evidence.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright validation are required.
- **V. Operability Is A Product Requirement**: PASS. Scanner summaries and migration dashboard evidence make cleanup status visible to reviewers.
- **VI. Spec-Driven Delivery**: PASS. Spec, clarifications, plan, tasks, analysis, QA docs, and validation evidence are required before completion.
- **VII. Test And Documentation Discipline**: PASS. Scanner, route, frontend, docs, QA, Playwright, and curl validation are required.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is bounded to inventory and guardrails; domain-builder replacement is deferred.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Route response checks exercise platform and tenant principals and must fail closed on cross-tenant access.
- **X. Version-Pinned Execution**: PASS. Runtime version bundles are untouched.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Scanner and schemas must reject unsafe text and avoid live provider, Telegram, connector, or outbound calls.
- **XII. Tiered Storage For Large Payloads**: PASS. Large validation evidence remains artifact-file based; PostgreSQL is not used as a blob store.
- **XIII. Human Approval Is Durable State**: PASS. Approval/resume semantics are out of scope and remain unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/048-live-data-inventory-and-mock-guardrails/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── live-data-inventory-contract.md
│   └── live-data-inventory.openapi.yaml
├── tasks.md
├── qa048.md
├── qa048_ui.md
├── qa048_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── migration_hardening/
│       ├── live_data_inventory.py
│       └── react_migration_hardening.py
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_migration_hardening_react.py
└── web_admin/static/react/

frontend/admin/src/
├── api/
├── components/migrationHardening/
└── test/

tests/
├── contract/test_admin_live_data_inventory_contract.py
├── integration/api/test_admin_live_data_inventory_routes.py
├── unit/admin/test_live_data_inventory_scanner.py
└── unit/admin/test_migration_hardening_service.py
```

**Structure Decision**: Keep the scanner in the migration hardening admin domain because Spec 048 is a migration gate over production React surfaces, not a reusable runtime service. Keep API exposure under existing `/admin/app/migration` routes so reviewers use the established migration dashboard.

## Phase 0 Research

See [research.md](./research.md). Key decisions: use a deterministic filesystem scanner plus explicit route target registry, store no new database state, classify current known findings as mapped legacy findings while failing CI for new unallowlisted production markers, and expose only redaction-safe summaries.

## Phase 1 Design

See [data-model.md](./data-model.md) and [contracts/live-data-inventory-contract.md](./contracts/live-data-inventory-contract.md). The scanner produces Pydantic response models for `LiveDataInventoryDashboard`, `LiveDataInventoryFinding`, `LiveDataAllowlistEntry`, `LiveDataRouteTarget`, and `LiveDataScanSummary`. The endpoint will be served from `/admin/app/migration/live-data-inventory.json`.

## Validation Strategy

- Unit tests cover marker taxonomy, allowlist matching, test-only exclusions, production import guardrails, current roadmap findings, and unsafe text rejection.
- Integration tests cover local-principal and Auth0-shaped access to the inventory route, tenant/cross-tenant behavior, route target coverage against the actual `admin_react.py` JSON route inventory, empty-state route scans, seeded-state route scans, and redaction safety.
- Frontend tests cover the migration evidence panel rendering live-data inventory totals without unsafe markers.
- Generated TypeScript contracts are checked after schema changes.
- Spec QA, Playwright, post-UI API/database verification, and `multi-agent-curl-test` must pass before queue advancement.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
