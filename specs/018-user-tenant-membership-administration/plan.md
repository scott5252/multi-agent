# Implementation Plan: User And Tenant Membership Administration

**Branch**: `codex/018-user-tenant-membership-administration` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/018-user-tenant-membership-administration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add governed user and tenant membership administration for platform admins and
authorized tenant admins. The implementation introduces a focused
`admin.memberships` domain package, additive PostgreSQL tables for invitations,
tenant memberships, and membership audit records, repository/service layers,
Pydantic schemas, a FastAPI admin router at `/admin/memberships`, a
server-rendered admin shell page, navigation and policy entries, local-principal
grant refresh behavior, tests, QA documents, README updates, and Playwright
evidence.

The feature reuses existing principal identity, role grant, access decision,
Auth0, local-principal, tenant, and admin shell primitives. It never accepts or
stores passwords, and all rendered user/email/subject data is masked or
summarized for screenshots and audit evidence.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing access-control repository, audit/access decision helpers,
prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: Reuse existing `principal_identities`, `role_grants`, and
`access_decision_records`; add `user_invitations`, `tenant_memberships`, and
`membership_audit_records`.  
**Testing**: pytest unit tests for redaction, schemas, service, repository, and
auth next-request behavior; httpx/TestClient integration tests for API and
server-rendered UI authorization, tenant isolation, invitation idempotency, role
guardrails, status transitions, audit records, navigation, and docs; Playwright
validation through the configured QA runner.  
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, local-principal test login, PostgreSQL, and worker process.  
**Project Type**: Multi-tenant Python web service with JSON admin APIs,
server-rendered admin UI, Auth0-backed production auth, and deterministic local
admin test mode.  
**Performance Goals**: Membership page p95 <= 300 ms for 250 principals and
1,000 grants in a tenant; invitation replay p95 <= 150 ms; access history panel
p95 <= 250 ms for 100 recent access decisions.  
**Constraints**: Cross-tenant access fails closed; tenant admins mutate only
their tenant. Production authentication remains Auth0-backed. No password
storage or password handling is introduced. Emails and Auth0 subjects are safe
summaries in UI, API summaries, and audit records. Role grants take effect on
the next protected request.  
**Scale/Scope**: One vertical feature slice: domain models/service, additive
database models and migration, repository, schemas, API/UI router,
server-rendered template, navigation and policy entries, local-principal role
refresh, tests, QA artifacts, PR notes, testing instructions, and README
updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Invitations, memberships, role grants, principal status, access decisions, and audit records persist before admin actions complete. |
| Immutable State And Memory | PASS | Audit records are append-only; role grants retain revoked state instead of disappearing. |
| Contract-First Agent Coordination | PASS | API schemas, UI contract, data model, and role eligibility rules are documented before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0 remains production auth; local-principal mode remains explicit and exercises persisted grants. |
| Operability Is A Product Requirement | PASS | Access history, membership audit events, denials, and trace ids are visible in safe summaries. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation remain traceable. |
| Test And Documentation Discipline | PASS | Test-first tasks cover security, tenant isolation, role changes, UI, docs, and coverage >= 90 percent. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `admin.memberships`, `api`, `db`, auth policy, admin shell, migration, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant id is explicit on invitations, memberships, tenant grants, access history filters, and audit records. |
| Version-Pinned Execution | PASS | No workflow execution bundle changes are introduced. |
| Secret Hygiene And Controlled Tool Access | PASS | No secrets or passwords are stored; Auth0 subjects and emails are masked in safe surfaces. |
| Tiered Storage For Large Payloads | PASS | No large payload storage is introduced. |
| Human Approval Is Durable State | PASS | No approval/resume semantics are introduced; admin changes are persisted and audited as durable decisions. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/018-user-tenant-membership-administration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── memberships.openapi.yaml
│   └── admin-memberships-ui.md
├── tasks.md
├── qa018.md
├── qa018_ui.md
├── qa018_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── memberships/
│       ├── __init__.py
│       ├── models.py
│       ├── redaction.py
│       └── service.py
├── api/
│   ├── routers/
│   │   └── admin_memberships.py
│   ├── schemas/
│   │   └── memberships.py
│   └── ui/
│       └── memberships.py
├── auth/
│   ├── local_principals.py
│   ├── policy.py
│   └── service.py
├── db/
│   ├── models/
│   │   └── user_management.py
│   └── repositories/
│       └── memberships.py
└── web_admin/
    └── templates/
        └── memberships/
            └── index.html

alembic/
└── versions/
    └── 0018_user_tenant_membership_administration.py
```

**Structure Decision**: Add a focused `admin.memberships` domain package and
keep API, UI, repository, and template adapters thin. Reuse existing principal,
role-grant, tenant, access-decision, admin shell, Auth0, and local-principal
infrastructure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves invitation idempotency, safe email display, Auth0 subject
linking, tenant-role guardrails, principal suspension, next-request grant
refresh, access history, and audit boundaries. See [research.md](./research.md).

Key decisions:

- Keep `principal_identities` and `role_grants` as the authoritative identity
  and role tables.
- Add dedicated invitation, membership, and membership audit tables to avoid
  overloading role grants with invitation lifecycle state.
- Normalize emails for idempotency but render masked email text and hashes in
  summaries.
- Merge persisted active role grants and principal status into Auth0 and
  local-principal contexts on each protected request.
- Enforce tenant-admin role eligibility in the membership service and route
  policies, not in templates alone.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines invitations, memberships, audit
  records, principal identity usage, role grant usage, state transitions, and
  tenant boundaries.
- [contracts/memberships.openapi.yaml](./contracts/memberships.openapi.yaml)
  defines the JSON admin API for listing, invites, identities, memberships,
  role grants, suspension, and history.
- [contracts/admin-memberships-ui.md](./contracts/admin-memberships-ui.md)
  defines the server-rendered page, forms, redaction, and authorization states.
- [quickstart.md](./quickstart.md) gives local setup and QA validation flows.

## API And UI Surface

- API routes live under `/admin/memberships/api`.
- UI route lives under `/admin/memberships`.
- All routes require an authenticated platform admin or tenant admin with the
  membership administration permissions.
- Platform admins may view platform scope or select a tenant. Tenant admins are
  forced to their own tenant scope.
- Navigation adds "Membership Administration" with tenant scope preservation.
- The validation plan uses `/admin/memberships` for browser screenshots.

## Migration Strategy

- Add only new membership administration tables and indexes.
- Reuse existing access-control enum values and role-grant lifecycle.
- Add tenant, principal, status, idempotency, and revision indexes for list and
  replay behavior.
- Migration downgrade drops only the new feature tables.

## Observability And Audit

- Membership audit records are created for invitation creation/replay, Auth0
  subject linking, membership creation/update/removal, role grant creation and
  revocation, suspension/reactivation, and denied service-level actions.
- Access history reads existing access decision records and returns safe
  summaries with trace ids and reason codes.
- Metrics can be layered on the service counters later; tests focus on durable
  audit evidence and access-decision behavior.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with Membership Administration,
  `/admin/memberships`, QA018 validation, and quality commands.
- Add feature PR notes and testing instructions under
  `specs/018-user-tenant-membership-administration/`.
- Generate QA docs and non-developer manual QA guide before final validation.
