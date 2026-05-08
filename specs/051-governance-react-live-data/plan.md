# Implementation Plan: Governance React Live Data

**Branch**: `codex/051-governance-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/051-governance-react-live-data/spec.md`

## Summary

Replace the governance React projection helpers that currently return fixed QA031 providers, prompts, profiles, routing previews, policy history, mutation results, and provenance with live, authorized projections over the existing governance domain repositories. Keep the current React route family and generated contracts, but make empty scopes truthful, seeded scopes repository-backed, provider probe/credential actions platform-admin-only, prompt/profile/routing actions durable or explicitly unavailable, and all rendered details redaction-safe.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with React 19 and Vite for the admin UI  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, `ModelProviderRepository`, `PromptRepository`, `AgentProfileRepository`, `ModelSkillConfigRepository`, provider gateway health/attempt records, `ProviderSecretResolver`, audit/redaction helpers, React admin shell contracts, generated TypeScript API contracts  
**Storage**: PostgreSQL 16+ through existing provider, prompt, profile, model-skill configuration, gateway attempt, usage/provenance, tenant, and audit tables; filesystem/object storage only for QA artifacts and screenshots  
**Testing**: Ruff, mypy, pytest/httpx, performance query tests, contract tests, Vitest/Testing Library, generated TypeScript contract checks, Vite build, Spec QA runner, Playwright UI runner, post-UI API/database verification, multi-agent-curl-test  
**Target Platform**: FastAPI-served admin web app with Auth0-shaped backend tests and local-principal browser QA  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Governance bootstrap and panel JSON stay bounded by explicit limits, avoid unbounded history/provenance scans, and keep empty-state responses cheap in fresh QA databases  
**Constraints**: No raw secrets, credential values, provider authorization headers, raw prompts, raw completions, private run payloads, local filesystem paths, stack traces, or unauthorized tenant labels in rendered JSON, logs, screenshots, exports, or QA docs; no real provider/credential/outbound calls in local or CI validation unless explicitly approved; production routes cannot return hardcoded QA031 domain rows or fake mutation success  
**Scale/Scope**: One bounded governance React route family plus backend projection service, route wiring, frontend empty-state handling, generated contracts, scanner inventory updates, QA seed documentation, and validation evidence

## Constitution Check

- **Durable By Default**: PASS. Safe governance mutations must call the existing durable provider, prompt, profile, routing, or policy services; unavailable actions must report backend-owned unavailable states rather than fake success.
- **Immutable State And Memory**: PASS. Prompt/profile versions, policy history, gateway attempts, and run provenance are read as versioned or append-only records; this spec introduces no mutable in-memory source of truth.
- **Contract-First Agent Coordination**: PASS. React consumes Pydantic-generated contracts and regenerated TypeScript types; nullable and empty states are represented explicitly.
- **Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows both exercise tenant scoping and authorization.
- **Operability Is A Product Requirement**: PASS. Provider health, credential readiness, gateway diagnostics, policy history, and provenance states are shown from live safe evidence.
- **Spec-Driven Delivery**: PASS. Specify and clarify are complete; planning outputs define exact files and validation gates before implementation.
- **Test And Documentation Discipline**: PASS. Tasks will include focused unit, integration, contract, performance, frontend, QA docs, Playwright, post-UI, and curl validation while preserving the 90 percent coverage gate.
- **Clear Ownership And Small Safe Changes**: PASS. Scope is limited to governance route builders, schemas, route wiring, frontend governance panels, generated contracts, scanner mappings, tests, and QA docs.
- **Tenant Isolation And Fair Scheduling**: PASS. All projections accept active scope, respect platform versus tenant visibility, and fail closed for cross-tenant requests.
- **Version-Pinned Execution**: PASS. Run provenance remains read-only safe evidence about pinned runtime configuration; this spec does not alter runtime bundle pinning.
- **Secret Hygiene And Controlled Tool Access**: PASS. Credential references are labels/fingerprints/readiness only; local QA uses mocked/allowlisted diagnostics.
- **Tiered Storage For Large Payloads**: PASS. Large raw attempt payloads, prompt/completion content, and exports are not rendered; artifact references remain metadata-only.
- **Human Approval Is Durable State**: PASS. No approval/resume behavior changes are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/051-governance-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── governance-live-data.openapi.yaml
│   └── governance-live-data-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/governance.py
├── api/routers/admin_react.py
├── api/schemas/admin_governance.py
├── admin/migration_hardening/live_data_inventory.py
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/governance/
├── test/governanceTestData.ts
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/governance/test_governance_queries.py
├── unit/admin/test_governance_service.py
├── unit/admin/test_live_data_inventory_scanner.py
└── unit/api/test_admin_governance_schema.py
```

**Structure Decision**: Keep the existing React admin governance route family and frontend component structure from Spec 031. Replace the fixed backend projection implementation in `admin/governance.py` with live service/repository projection helpers and update route wiring in `admin_react.py` only where dependency injection or async calls are needed.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use existing repositories and domain services as the source of truth for provider, prompt, profile, routing, policy, gateway diagnostic, and provenance records.
- Add explicit provenance and empty-state metadata to governance responses so reviewers can tell live data, denied data, unavailable data, and empty data apart.
- Keep platform-only provider probe and credential-reference actions fail-closed and mocked/local-only in QA.
- Prefer one safe durable UI action for Playwright, likely creating or saving a prompt/profile draft through existing services, then verifying persistence through API or database evidence.
- Use scanner assertions to keep fixed QA031 governance markers out of production responses while retaining test-only fixtures.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/governance-live-data.openapi.yaml](./contracts/governance-live-data.openapi.yaml)
- [contracts/governance-live-data-ui.md](./contracts/governance-live-data-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts and tests require platform, tenant, denied, empty, and seeded scopes.
- **Authorization**: PASS. Provider probe and credential actions remain platform-only; tenant read paths are scoped.
- **Redaction**: PASS. Prompt previews, credential references, provider diagnostics, gateway attempts, and provenance render safe summaries only.
- **Durability**: PASS. Mutations persist through existing services or return unavailable/denied states; no browser-only success defaults.
- **Operability**: PASS. Plans require health, readiness, diagnostic, policy, and provenance evidence.
- **Validation**: PASS. The post-spec contract requires QA docs, Spec QA, Playwright, post-UI API/database verification, and curl validation before Spec 052 starts.

## Complexity Tracking

No constitution violations are introduced.
