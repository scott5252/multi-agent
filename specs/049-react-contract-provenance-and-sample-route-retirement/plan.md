# Implementation Plan: React Contract Provenance And Sample Route Retirement

**Branch**: `codex/049-react-contract-provenance-and-sample-route-retirement` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/049-react-contract-provenance-and-sample-route-retirement/spec.md`

## Summary

Establish reusable backend-owned provenance and truthful empty-state metadata for React admin contracts, retire the production sample patterns route, and remove hardcoded QA revision/idempotency defaults from production React components. The implementation updates shared Pydantic schemas and generated TypeScript contracts, removes `/admin/app/patterns` from production navigation and the React router, keeps pattern fixtures in test-only paths, adds route and scanner tests, creates QA049 docs, and validates empty/seeded behavior through Spec QA, Playwright, post-UI API/database evidence, and curl regression.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async session dependencies, React 19, Vite, Vitest, Testing Library, pytest, Playwright, Ruff, mypy, uv  
**Storage**: No schema migration. Empty/seeded evidence uses the dedicated `multi_agent_platform_qa049` database plus existing QA seed flows.  
**Testing**: pytest/httpx/TestClient route and contract tests, scanner tests from Spec 048, generated TypeScript contract check, Vitest/Testing Library, frontend typecheck/build, Spec QA, Playwright UI validation, post-UI API/database verification, multi-agent curl regression  
**Target Platform**: FastAPI admin React JSON APIs and React admin browser UI served by built Vite assets  
**Project Type**: Multi-service web platform with backend-owned contracts and React presentation  
**Performance Goals**: Shared provenance metadata adds no route database round trips; sample route retirement reduces production bundle and route surface  
**Constraints**: No production sample data route, no production component hardcoded `qa0xx` revision/idempotency defaults, no frontend authorization or tenant-scoping decisions, no raw secrets or unsafe evidence in contracts or screenshots  
**Scale/Scope**: Shared contract convention plus sample route retirement only; domain live-data replacements stay in Specs 050 through 057

## Constitution Check

- **I. Durable By Default**: PASS. This spec changes presentation metadata and route availability only; no durable workflow state is altered.
- **II. Immutable State And Memory**: PASS. No memory or checkpoint mutation is introduced.
- **III. Contract-First Agent Coordination**: PASS. Pydantic schemas remain authoritative and generated TypeScript contracts are regenerated and checked.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped route tests and local-principal browser QA remain required; any dev-only route gate is explicit and off in production-like validation.
- **V. Operability Is A Product Requirement**: PASS. Provenance, empty states, route retirement, scanner evidence, and QA docs give operators reviewable proof.
- **VI. Spec-Driven Delivery**: PASS. Spec, clarifications, plan, tasks, implementation, QA docs, and validation are required before queue advancement.
- **VII. Test And Documentation Discipline**: PASS. Focused backend/frontend tests, generated contract checks, QA docs, Playwright, and curl regression are mandatory.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is limited to shared React admin schemas, sample route surfaces, action-default helpers, scanner/contract tests, docs, and validation.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Existing backend shell authorization remains authoritative and route tests cover tenant denial.
- **X. Version-Pinned Execution**: PASS. Runtime bundle pinning is unaffected.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Provenance and empty-state text use existing safe text validators and scanner redaction rules.
- **XII. Tiered Storage For Large Payloads**: PASS. No large payload storage behavior changes.
- **XIII. Human Approval Is Durable State**: PASS. Approval flows are not changed.

## Project Structure

### Documentation (this feature)

```text
specs/049-react-contract-provenance-and-sample-route-retirement/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── react-contract-provenance-contract.md
│   └── react-contract-provenance.openapi.yaml
├── tasks.md
├── qa049.md
├── qa049_ui.md
├── qa049_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/routers/admin_react.py
├── api/schemas/admin_react.py
├── api/schemas/admin_patterns.py
├── admin/migration_hardening/live_data_inventory.py
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── App.tsx
├── routes.tsx
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/StatePanel.tsx
├── components/states/CommonState.tsx
├── hooks/useAdminMutation.ts
└── test/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep shared admin contract primitives in `admin_react.py` and `admin_patterns.py`, remove production sample-pattern routing from `admin_react.py`/`App.tsx`/`routes.tsx`, retain test-only pattern fixtures under `frontend/admin/src/test`, and update Spec 048 scanner expectations for the retired sample surface.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
