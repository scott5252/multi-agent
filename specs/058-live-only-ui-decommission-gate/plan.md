# Implementation Plan: Live-Only UI Decommission Gate

**Branch**: `codex/058-live-only-ui-decommission-gate` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/058-live-only-ui-decommission-gate/spec.md`

## Summary

Turn the live-data inventory introduced in Spec 048 into a final decommission
gate for production admin UI routes. The implementation will harden scanner
policy, scan production-built assets, probe route responses in empty and seeded
QA states, classify each route as live data, computed metadata, empty, denied,
unavailable, or redirect-only, delete or disconnect obsolete deterministic
projection surfaces, and document seed requirements plus rollback guidance.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript strict mode with React 19 frontend  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL, existing migration hardening/live-data inventory schemas, existing admin React route contracts, Vite build assets, Playwright  
**Storage**: PostgreSQL for route-probe and seeded live evidence; filesystem/build output for production asset scans; QA artifact directory for scanner reports  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, coverage gate, generated TypeScript contract check, Vitest where UI copy changes, Playwright, Spec QA, multi-agent curl runner  
**Target Platform**: Local/CI FastAPI admin platform with React admin UI, local-principal QA, Auth0-shaped route tests, and PostgreSQL 16+  
**Project Type**: Web service plus React admin application  
**Performance Goals**: Source and built-asset scans stay bounded to declared production roots; route response probes run once per declared target/principal/state; scanner unit and integration tests complete within normal admin test budgets.  
**Constraints**: No raw secrets, credentials, provider authorization headers, prompts, completions, memory contents, raw run payloads, private messages, raw tool payloads, local filesystem paths, stack traces, unauthorized tenant labels, or full Telegram identifiers in reports, screenshots, docs, logs, or generated artifacts. No intermediate commits are required during autopilot.  
**Scale/Scope**: Migration hardening live-data inventory service/schema, admin migration dashboard route, QA058 seed and verifier scripts, route response scan tests, built asset scan checks, docs, validation manifest, and any obsolete production imports/modules discovered by the gate.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. The gate records deterministic scan evidence and uses persisted QA seed data for live route proof.
- Immutable State And Memory: PASS. The feature reads source/build artifacts and persisted database records; it does not introduce mutable runtime state.
- Contract-First Agent Coordination: PASS. React continues to consume backend-owned Pydantic contracts and generated TypeScript contracts.
- Security With Practical Development Ergonomics: PASS. Route probes cover Auth0-shaped and local-principal behavior without external Auth0 calls.
- Operability Is A Product Requirement: PASS. The feature strengthens the migration dashboard and reviewer evidence for live-only behavior.
- Spec-Driven Delivery: PASS. Specify, clarify, plan, tasks, analyze, implement, and validation are tracked in queue/status.
- Test And Documentation Discipline: PASS. The plan includes scanner tests, route tests, QA docs, Playwright, post-UI verification, curl regression, reviewer notes, and rollback notes.
- Clear Ownership And Small Safe Changes: PASS. Work is bounded to migration-hardening scanner/gate behavior, QA helpers, tests, docs, and obsolete deterministic surface cleanup.
- Tenant Isolation And Fair Scheduling: PASS. Route probes use explicit platform/tenant principals and fail closed for unauthorized scopes.
- Version-Pinned Execution: PASS. No workflow execution changes are introduced; seeded route evidence references persisted versions where route domains require them.
- Secret Hygiene And Controlled Tool Access: PASS. Gate reports use safe excerpts and forbid raw secret/tool/prompt payloads.
- Tiered Storage For Large Payloads: PASS. Large QA artifacts remain filesystem/object-storage style evidence, referenced safely from PostgreSQL-backed or artifact-root metadata.
- Human Approval Is Durable State: PASS. No new approval flow is introduced; rollback guidance is reviewer documentation rather than transient state.

## Project Structure

### Documentation (this feature)

```text
specs/058-live-only-ui-decommission-gate/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── live-only-ui-gate.openapi.yaml
│   └── live-only-ui-gate-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/migration_hardening/
│   ├── live_data_inventory.py
│   └── react_migration_hardening.py
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_migration_hardening_react.py
└── web_admin/static/react/

frontend/admin/src/
├── api/generated/reactAdminApi.ts
└── components/migration/

scripts/qa/
├── seed_live_only_gate_qa058.py
└── verify_live_only_gate_qa058.py

tests/
├── integration/api/test_admin_live_data_inventory_routes.py
├── integration/test_admin_react_routes.py
├── unit/admin/test_live_data_inventory_scanner.py
└── docs/
```

**Structure Decision**: Keep the existing `admin.migration_hardening`
boundary and extend the live-data inventory instead of creating a parallel
scanner subsystem. Add QA058 seed/verifier scripts only where route-response
validation needs persisted representative data.

## Complexity Tracking

No constitution violations are expected.

## Phase 0: Research

Research covers final scanner scope, QA marker policy, built asset scanning,
route response authentication, seeded and empty QA strategy, obsolete module
decommissioning, CI validation shape, and rollback documentation. Findings are
recorded in [research.md](research.md).

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](data-model.md)
- [contracts/live-only-ui-gate.openapi.yaml](contracts/live-only-ui-gate.openapi.yaml)
- [contracts/live-only-ui-gate-ui.md](contracts/live-only-ui-gate-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- Durable scan evidence, fail-closed route probes, tenant isolation, generated
  contracts, redaction, QA docs, rollback guidance, and no-intermediate-commit
  queue/status tracking remain covered by the design artifacts.
- No new constitution violation was introduced by Phase 1 design.
