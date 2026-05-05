# Implementation Plan: React User And Tenant Membership Administration

**Branch**: `codex/034-react-user-and-tenant-membership-administration` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/034-react-user-and-tenant-membership-administration/spec.md`

## Summary

Build an additive React membership administration workspace for platform and
tenant administrators. Existing Spec 018 membership services, repositories,
schemas, redaction helpers, Auth0/local-principal behavior, access-decision
audit, and server-rendered pages remain authoritative. The new React route
will consume backend-owned JSON contracts and generated TypeScript types for a
safe user directory, invitation flow, principal linking/provisioning, role
grant wizard, grant revocation, principal status changes, tenant membership
status changes, access history, audit timeline, and safe denied states.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing `admin.memberships` services/repositories/redaction helpers, Auth0/local-principal auth, access decision repository, React admin shell, generated TypeScript contracts, audit helpers  
**Storage**: PostgreSQL 16+ through existing principal identity, role grant, user invitation, tenant membership, membership audit, and access decision records  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and local-principal validation  
**Project Type**: Full-stack web application inside existing monorepo  
**Performance Goals**: Keep directory, filters, role choices, access history, and audit timeline bounded; render first dashboard response without unbounded user, grant, or history lists; keep search/filter payloads small enough for repeat admin workflows  
**Constraints**: Fail closed for auth, tenant scope, role eligibility, stale revision, malformed invite, duplicate external subject, unavailable audit, unavailable directory, unsafe email/subject display, and unauthorized raw identifier access; no passwords, raw authorization headers, credential values, private messages, local paths, or unauthorized tenant labels in React contracts or QA artifacts  
**Scale/Scope**: One additive React domain route plus backend contracts/adapters, generated TypeScript, focused deterministic fixtures, docs, and validation evidence

## Constitution Check

- **Durable by default**: PASS. Invitations, memberships, grants, principal status, access decisions, and audit records are persisted before mutation results return.
- **Immutable state and memory**: PASS. Audit records and access decisions are append-only; grants and memberships preserve lifecycle state rather than disappearing from history.
- **Contract-first coordination**: PASS. React consumes explicit contracts for dashboard, directory, invitations, principal links, role grants, status changes, access history, audit timeline, and safe problem states.
- **Security ergonomics**: PASS. Production Auth0 and deterministic local-principal modes are both required in tests and validation.
- **Operability**: PASS. Directory results include safe status, audit references, access history, denied summaries, role-source evidence, and next-request effect copy.
- **Spec-driven delivery**: PASS. Specify, clarify, plan, tasks, analyze, implementation, docs, and validation are required before advancing.
- **Test and documentation discipline**: PASS. Plan requires focused backend/frontend tests, full coverage, QA docs, Playwright, quickstart, README, and PR notes.
- **Small safe changes**: PASS. Backend adapters, generated contracts, React components, and tests are scoped to the membership React route.
- **Tenant isolation and fair scheduling**: PASS. Active scope, allowed tenants, user directory filters, role grants, invitations, memberships, and history are tenant-scoped and fail closed.
- **Version-pinned execution**: PASS. No workflow execution bundle behavior changes are introduced.
- **Secret hygiene and controlled tool access**: PASS. No real Auth0 provisioning, email delivery, provider calls, credential resolution, or external tools are required for local QA.
- **Tiered storage**: PASS. No large payload storage is introduced; QA screenshots remain file evidence.
- **Human approval durable state**: PASS. Confirmation requirements are explicit action state, and mutations are persisted/audited.

## Project Structure

### Documentation (this feature)

```text
specs/034-react-user-and-tenant-membership-administration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── memberships-react.openapi.yaml
│   └── memberships-react-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_membership_react.py
├── admin/memberships/
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/memberships/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/memberships/test_react_membership_queries.py
├── unit/admin/memberships/test_react_membership_service.py
└── unit/api/test_admin_membership_react_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from
Specs 026-033. Backend schema/adapters live under `api/schemas` and
`admin.memberships`; FastAPI wiring remains in `api/routers/admin_react.py`;
React components live in `frontend/admin/src/components/memberships`; tests
extend the existing React admin contract/integration suite with focused schema,
service, and performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main
decisions:

- Reuse Spec 018 membership services and repositories as the source of truth.
- Build additive React contracts that project safe directory, invitation,
  role, status, history, and audit summaries.
- Keep raw identifiers out of the primary view and expose copyable detail only
  when backend-authorized.
- Use backend-owned role eligibility, confirmation requirements, idempotency,
  stale conflicts, and next-request effect summaries.
- Validate both Auth0-shaped and local-principal authorization paths.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/memberships-react.openapi.yaml](./contracts/memberships-react.openapi.yaml)
- [contracts/memberships-react-ui.md](./contracts/memberships-react-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Durability**: PASS. Mutations are idempotent, persisted, and audit-backed.
- **Tenant isolation**: PASS. Data model and contracts include active scope,
  allowed tenant choices, tenant-scoped directory filters, and cross-tenant
  denial tests.
- **Authorization**: PASS. Directory, invite, principal link, role grant,
  revocation, status, and history routes are action-scoped and dual-auth
  tested.
- **Audit safety**: PASS. Mutations, denials, idempotent replays, status
  changes, grants, revocations, and detail access include safe audit references.
- **Redaction**: PASS. Data model restricts rendered content to masked emails,
  safe subject suffixes, labels, summaries, statuses, and authorized links.
- **Tool/secret safety**: PASS. Local/CI execution uses deterministic fixtures
  and no live Auth0, email, provider, connector, Telegram, or credential calls.
- **Browser-first QA**: PASS. Quickstart and tasks require Playwright workflows
  for platform, tenant, invite, role, revoke, status, access-history, and
  cross-tenant denial flows.
- **Operability**: PASS. Plan covers access history, audit timeline, denied
  evidence, next-request effect, and recovery guidance.

## Complexity Tracking

No constitution violations are introduced.
