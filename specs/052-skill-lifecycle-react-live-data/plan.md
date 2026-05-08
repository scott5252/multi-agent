# Implementation Plan: Skill Lifecycle React Live Data

**Branch**: `codex/052-skill-lifecycle-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/052-skill-lifecycle-react-live-data/spec.md`

## Summary

Replace the skill lifecycle React projection helpers that currently return fixed QA032 package, candidate, grant, installation, credential, connector diagnostic, binding eligibility, and audit data with live, authorized projections over existing skill registry, readiness, smoke-test, quarantine, audit, model-skill policy, and SkillExecutionGateway services. Keep the current React route family and generated contracts, but make empty scopes truthful, seeded scopes repository-backed, lifecycle actions durable or explicitly unavailable, local QA diagnostics mocked-safe, and all details redaction-safe.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with React 19 and Vite for the admin UI  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, `SkillRegistryRepository`, skill registry service/readiness/smoke/quarantine/audit helpers, `SkillExecutionGateway`, model-skill configuration policy repositories, React admin shell contracts, generated TypeScript API contracts  
**Storage**: PostgreSQL 16+ through existing skill package, package version, tenant grant, installation, credential readiness, smoke-test, audit, model-skill policy, and diagnostic tables; filesystem/object storage only for artifact references and QA evidence  
**Testing**: Ruff, mypy, pytest/httpx, performance query tests, contract tests, Vitest/Testing Library, generated TypeScript contract checks, Vite build, Spec QA runner, Playwright UI runner, post-UI API/database verification, multi-agent-curl-test  
**Target Platform**: FastAPI-served admin web app with Auth0-shaped backend tests and local-principal browser QA  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Skill lifecycle bootstrap and panel JSON stay bounded by explicit limits, avoid unbounded package/audit/diagnostic scans, and keep empty-state responses cheap in fresh QA databases  
**Constraints**: No raw manifests, credential values, provider authorization headers, raw connector payloads, raw tool payloads, raw test transcripts, private tenant labels, local filesystem paths, stack traces, or unauthorized tenant data in rendered JSON, logs, screenshots, exports, or QA docs; no real connector/provider/credential/outbound calls in local or CI validation unless explicitly approved; production routes cannot return hardcoded QA032 skill lifecycle rows or fake mutation success  
**Scale/Scope**: One bounded skill lifecycle React route family plus backend projection service, route wiring, frontend empty-state handling, generated contracts, scanner inventory updates, QA seed documentation, and validation evidence

## Constitution Check

- **Durable By Default**: PASS. Safe lifecycle mutations must call existing durable skill registry/readiness/diagnostic services or report unavailable/denied/stale states.
- **Immutable State And Memory**: PASS. Package versions, grants, installations, smoke-test evidence, eligibility decisions, and audits are persisted records; no mutable in-memory source of truth.
- **Contract-First Agent Coordination**: PASS. React consumes Pydantic-generated contracts and regenerated TypeScript types with explicit live, empty, denied, unavailable, stale, and blocked states.
- **Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows both exercise authorization and tenant scoping.
- **Operability Is A Product Requirement**: PASS. Skill readiness, smoke tests, diagnostics, eligibility, quarantine, withdrawal, and audit states remain visible through safe operational evidence.
- **Spec-Driven Delivery**: PASS. Specify and clarify are complete; planning outputs define exact files and validation gates before implementation.
- **Test And Documentation Discipline**: PASS. Tasks will include unit, integration, contract, scanner, performance, frontend, QA docs, Playwright, post-UI, and curl validation while preserving the 90 percent coverage gate.
- **Clear Ownership And Small Safe Changes**: PASS. Scope is limited to skill lifecycle route builders, schemas, route wiring, frontend skill panels, generated contracts, scanner mappings, tests, QA docs, and QA seed helpers.
- **Tenant Isolation And Fair Scheduling**: PASS. All projections accept active scope, respect platform versus tenant visibility, and fail closed for cross-tenant package, installation, credential, diagnostic, and audit data.
- **Version-Pinned Execution**: PASS. Binding eligibility and connector diagnostics remain read-only safe evidence about governed skill and policy state; this spec does not alter runtime bundle pinning.
- **Secret Hygiene And Controlled Tool Access**: PASS. Credential references remain labels/fingerprints/readiness only; local QA uses mocked/allowlisted diagnostics.
- **Tiered Storage For Large Payloads**: PASS. Raw manifests, connector payloads, and transcripts are not rendered; artifact references remain metadata-only.
- **Human Approval Is Durable State**: PASS. No approval/resume behavior changes are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/052-skill-lifecycle-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── skill-lifecycle-live-data.openapi.yaml
│   └── skill-lifecycle-live-data-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/skill_lifecycle.py
├── admin/skill_registry/
├── db/repositories/skill_registry.py
├── db/repositories/model_skill_config.py
├── skill_execution/
├── api/routers/admin_react.py
├── api/schemas/admin_skill_lifecycle.py
├── admin/migration_hardening/live_data_inventory.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/skills/
├── test/skillLifecycleTestData.ts
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── integration/skill_registry/
├── performance/skills/test_skill_lifecycle_queries.py
├── unit/admin/test_skill_lifecycle_service.py
├── unit/admin/test_live_data_inventory_scanner.py
└── unit/api/test_admin_skill_lifecycle_schema.py
```

**Structure Decision**: Keep the existing React admin skill route family and frontend component structure from Spec 032. Replace the fixed backend projection implementation in `admin/skill_lifecycle.py` with async live service/repository projection helpers and update route wiring in `admin_react.py` only where dependency injection or async calls are needed.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use existing skill registry repositories and domain services as the source of truth for package, version, grant, installation, readiness, smoke-test, quarantine, and audit records.
- Use SkillExecutionGateway and governed connector diagnostic records as safe diagnostic sources, summarized before React.
- Add explicit provenance and empty-state metadata to skill lifecycle responses so reviewers can tell live data, denied data, unavailable data, and empty data apart.
- Keep local QA smoke tests and connector diagnostics mocked-safe or local allowlisted.
- Prefer one safe durable UI action for Playwright, likely credential readiness save, smoke-test refresh, candidate validation, or tenant installation, then verify persistence through API or database evidence.
- Use scanner assertions to keep fixed QA032 skill lifecycle markers out of production responses while retaining test-only fixtures.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/skill-lifecycle-live-data.openapi.yaml](./contracts/skill-lifecycle-live-data.openapi.yaml)
- [contracts/skill-lifecycle-live-data-ui.md](./contracts/skill-lifecycle-live-data-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts and tests require platform, tenant, denied, empty, and seeded scopes.
- **Authorization**: PASS. Package publication, grants, quarantine, and withdrawal remain platform-controlled; tenant install/readiness actions are scoped.
- **Redaction**: PASS. Manifest summaries, credential references, smoke tests, diagnostics, gateway evidence, and audits render safe summaries only.
- **Durability**: PASS. Mutations persist through existing services or return unavailable/denied/stale states; no browser-only success defaults.
- **Operability**: PASS. Plans require readiness, diagnostics, eligibility, lifecycle state, and audit evidence.
- **Validation**: PASS. The post-spec contract requires QA docs, Spec QA, Playwright, post-UI API/database verification, and curl validation before Spec 053 starts.

## Complexity Tracking

No constitution violations are introduced.
