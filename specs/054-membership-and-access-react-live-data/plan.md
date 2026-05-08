# Implementation Plan: Membership And Access React Live Data

**Branch**: `codex/054-membership-and-access-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/054-membership-and-access-react-live-data/spec.md`

## Summary

Replace the membership React projection helpers that currently return fixed QA034 users, invitations, role grants, status actions, access history, raw identifier summaries, and audit evidence with live, authorized projections over `MembershipRepository`, `MembershipAdministrationService`, access-control decisions, membership audit records, safe redaction helpers, and existing React shell scope resolution. Keep the current React route family and generated contracts, but make empty scopes truthful, seeded scopes repository-backed, safe actions durable, local-principal QA mocked-safe, and all identity/audit details redaction-safe.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with React 19 and Vite for the admin UI  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, `MembershipRepository`, `MembershipAdministrationService`, membership redaction helpers, access-control policy records, audit repository/service helpers, React admin shell contracts, generated TypeScript API contracts  
**Storage**: PostgreSQL 16+ through existing principal identity, tenant membership, user invitation, role grant, access decision, membership audit, tenant, and role tables; QA evidence files only for validation artifacts  
**Testing**: Ruff, mypy, pytest/httpx, repository and performance query tests, contract tests, Vitest/Testing Library, generated TypeScript contract checks, Vite build, Spec QA runner, Playwright UI runner, post-UI API/database verification, multi-agent-curl-test  
**Target Platform**: FastAPI-served admin web app with Auth0-shaped backend tests and local-principal browser QA  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Membership bootstrap and history/audit JSON stay bounded by explicit repository limits, avoid unbounded identity/grant/audit scans, and keep empty-state responses cheap in fresh QA databases  
**Constraints**: No raw identity provider claims, full emails, full external subjects, full Telegram identifiers, tokens, secrets, credential values, raw audit payloads, unauthorized tenant labels, local filesystem paths, stack traces, private channel data, or fake QA034 rows in rendered JSON, logs, screenshots, exports, or QA docs; production routes cannot return hardcoded membership entities or fake mutation success  
**Scale/Scope**: One bounded membership React route family plus backend projection service, route wiring, frontend empty-state handling, generated contracts, scanner mappings, tests, QA docs, QA seed helpers, and validation evidence

## Constitution Check

- **Durable By Default**: PASS. Safe invitation, principal link/status, role grant/revoke, and membership status mutations must call existing durable services or report unavailable/denied/stale states.
- **Immutable State And Memory**: PASS. Principal identities, invitations, memberships, grants, access decisions, support override evidence, and audit events are persisted records; no mutable in-memory source of truth.
- **Contract-First Agent Coordination**: PASS. React consumes Pydantic-generated contracts and regenerated TypeScript types with explicit live, empty, denied, unavailable, stale, accepted, replayed, revoked, suspended, and removed states.
- **Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows both exercise authorization, tenant scoping, and audit-safe behavior.
- **Operability Is A Product Requirement**: PASS. Projections expose safe provenance, next-request effects, access history, audit references, and mutation evidence without raw payloads.
- **Spec-Driven Delivery**: PASS. Specify and clarify are complete; planning outputs define exact files and validation gates before implementation.
- **Test And Documentation Discipline**: PASS. Tasks will include unit, repository, integration, contract, scanner, performance, frontend, QA docs, Playwright, post-UI, and curl validation while preserving the 90 percent coverage gate.
- **Clear Ownership And Small Safe Changes**: PASS. Scope is limited to membership route builders, schemas, route wiring, frontend membership panels, generated contracts, scanner mappings, tests, QA docs, and QA seed helpers.
- **Tenant Isolation And Fair Scheduling**: PASS. All projections accept active scope, respect platform versus tenant authority, and fail closed for cross-tenant identity, invitation, membership, grant, access, support override, and audit data.
- **Version-Pinned Execution**: PASS. This spec does not alter runtime execution bundle pinning.
- **Secret Hygiene And Controlled Tool Access**: PASS. Local QA uses local principals only; no real IdP, provider, credential, connector, or outbound calls are introduced.
- **Tiered Storage For Large Payloads**: PASS. Raw audit payloads and external identity claims are not rendered; only safe summaries and references are exposed.
- **Human Approval Is Durable State**: PASS. Support override evidence remains persisted and audited; no approval/resume semantics are changed.

## Project Structure

### Documentation (this feature)

```text
specs/054-membership-and-access-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── membership-live-data.openapi.yaml
│   └── membership-live-data-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/memberships/
│   ├── react_memberships.py
│   ├── service.py
│   ├── models.py
│   └── redaction.py
├── db/repositories/memberships.py
├── db/models/access_control.py
├── db/models/user_management.py
├── api/routers/admin_react.py
├── api/schemas/admin_membership_react.py
├── admin/migration_hardening/live_data_inventory.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/memberships/
├── test/membershipTestData.ts
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── contract/test_membership_administration_contract.py
├── integration/test_admin_react_routes.py
├── integration/api/test_admin_memberships_api.py
├── integration/api/test_admin_memberships_ui.py
├── performance/memberships/test_react_membership_queries.py
├── unit/admin/memberships/test_react_membership_service.py
├── unit/admin/memberships/test_membership_service.py
├── unit/admin/test_live_data_inventory_scanner.py
├── unit/api/test_admin_membership_react_schema.py
├── unit/api/test_admin_memberships_router_edges.py
└── unit/db/test_membership_repository.py
```

**Structure Decision**: Keep the existing React admin membership route family and frontend component structure from Specs 034 and 045. Replace the fixed backend projection implementation in `admin/memberships/react_memberships.py` with async live service/repository projection helpers and update route wiring in `admin_react.py` where repository/service dependency injection or async calls are needed.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use existing membership repositories and services as the source of truth for principal identities, invitations, memberships, grants, status changes, and audit writes.
- Use access-control and audit records for history panels, bounded by explicit limits and filtered by active platform or tenant scope.
- Add explicit provenance and empty-state metadata to membership responses so reviewers can distinguish live data, empty data, denied data, and unavailable data.
- Keep identity and audit redaction in backend schemas and projection helpers, not in browser-only logic.
- Prefer one safe durable UI action for Playwright, likely creating/replaying a tenant invitation, then verify persistence through the membership bootstrap/API and a redaction-safe QA database check.
- Use scanner assertions to keep fixed QA034 membership markers out of production responses while retaining test-only fixtures and historical specs.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/membership-live-data.openapi.yaml](./contracts/membership-live-data.openapi.yaml)
- [contracts/membership-live-data-ui.md](./contracts/membership-live-data-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts and tests require platform, tenant, denied, cross-tenant, empty, and seeded scopes.
- **Authorization**: PASS. Invitation, principal link/status, role grant/revoke, membership status, history, and audit surfaces remain permission-controlled.
- **Redaction**: PASS. Full email addresses, raw subjects, raw claims, raw audit payloads, tenant labels outside scope, paths, stack traces, tokens, and secrets are rejected by backend-safe schemas/tests.
- **Durability**: PASS. Mutations persist through existing services or return unavailable/denied/stale states; no browser-only success defaults.
- **Operability**: PASS. Plans require access history, audit evidence, next-request effects, replay state, conflict state, and safe provenance.
- **Validation**: PASS. The post-spec contract requires QA docs, Spec QA, Playwright, post-UI API/database verification, and curl validation before Spec 055 starts.

## Complexity Tracking

No constitution violations are introduced.
