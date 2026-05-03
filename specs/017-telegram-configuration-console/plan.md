# Implementation Plan: Telegram Configuration Console

**Branch**: `codex/017-telegram-configuration-console` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/017-telegram-configuration-console/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a server-rendered Telegram Configuration Console for platform admins and
authorized tenant admins. The implementation introduces a focused
`admin.telegram_config` domain package, additive PostgreSQL tables for
tenant enablement, safe token audit, linked identity summaries, and diagnostics,
Pydantic schemas, a FastAPI admin router at `/admin/telegram`, Jinja2 templates
under the existing admin shell, navigation and policy entries, local fake-secret
readiness, webhook validation without external side effects, tests, QA docs,
README updates, and Playwright evidence.

The feature reuses existing Spec 006 Telegram link-token and webhook services
for command behavior. The console stores and renders only safe references,
fingerprints, masked Telegram ids, trace ids, categories, and status metadata.
It never stores or displays real bot tokens, webhook secrets, private messages,
raw prompts, run results, or unauthorized tenant data.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing channel/Telegram services, existing secret providers,
audit/redaction helpers, reliability retry/breaker metadata,
prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: New additive PostgreSQL tables for `telegram_tenant_configs`,
`telegram_link_token_audits`, `telegram_linked_identity_summaries`, and
`telegram_diagnostic_events`; existing Spec 006 channel tables remain the
runtime channel source.  
**Testing**: pytest unit tests for schemas, readiness, redaction, service
commands, repository behavior, and UI view models; httpx/TestClient integration
tests for API and server-rendered UI authorization, tenant isolation, forms,
link-token issue/revoke, diagnostics, production guardrails, stale revisions,
and navigation; docs tests for README, QA guide, testing instructions, and PR
notes; Playwright validation through the configured QA runner.  
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, local-principal test login, PostgreSQL, and worker process.  
**Project Type**: Multi-tenant Python web service with JSON admin APIs,
server-rendered admin UI, channel runtime support, and background workers.  
**Performance Goals**: Console page p95 <= 300 ms for a tenant with 100 linked
identities and 200 diagnostics; readiness check p95 <= 100 ms because it is
local-only; link-token issue p95 <= 150 ms excluding database commit.  
**Constraints**: Cross-tenant access fails closed; tenant admins see and mutate
only their tenant. Production readiness requires secret references. Local QA
does not call Telegram or production hosts. Diagnostics are redaction-safe.
PostgreSQL stores metadata only, never message bodies or secrets.  
**Scale/Scope**: One vertical feature slice: domain models/service, database
models and migration, repository, schemas, API/UI router, server-rendered
templates, navigation and policy entries, settings validation tests, docs, QA
artifacts, manual QA user guide, and validation commands.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Tenant config, token audit, identity summaries, diagnostics, and stale revision decisions persist safely. |
| Immutable State And Memory | PASS | Diagnostics and token audits are append-mostly; tenant config uses revision tokens rather than hidden overwrites. |
| Contract-First Agent Coordination | PASS | API schemas, UI contract, data model, diagnostics categories, and redaction rules are documented before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal paths reuse admin authorization while local QA uses explicit fake references. |
| Operability Is A Product Requirement | PASS | Readiness, webhook validation, delivery diagnostics, token actions, revocations, and denied access have safe traceable records. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation remain traceable. |
| Test And Documentation Discipline | PASS | Test-first tasks cover security, tenant isolation, redaction, UI, docs, and coverage >= 90 percent. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `admin.telegram_config`, `api`, `db`, `web_admin`, migration, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant id is explicit on config, identity, token audit, diagnostics, and access scopes. |
| Version-Pinned Execution | PASS | No workflow execution bundle changes; protected command readiness references existing channel command contracts. |
| Secret Hygiene And Controlled Tool Access | PASS | Only safe secret references and fingerprints are persisted or rendered; external calls are blocked by default. |
| Tiered Storage For Large Payloads | PASS | No large payload storage is introduced; private messages and run results are excluded. |
| Human Approval Is Durable State | PASS | No new approval/resume semantics are introduced; admin actions are persisted/audited as configuration decisions. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/017-telegram-configuration-console/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── admin-telegram-ui.md
│   └── telegram-configuration.openapi.yaml
├── tasks.md
├── qa017.md
├── qa017_ui.md
├── qa017_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── telegram_config/
│       ├── __init__.py
│       ├── models.py
│       ├── redaction.py
│       └── service.py
├── api/
│   ├── routers/
│   │   └── admin_telegram.py
│   ├── schemas/
│   │   └── telegram_config.py
│   └── ui/
│       └── telegram_config.py
├── db/
│   ├── models/
│   │   └── telegram_config.py
│   └── repositories/
│       └── telegram_config.py
└── web_admin/
    └── templates/
        └── telegram/
            └── index.html

alembic/
└── versions/
    └── 0017_telegram_configuration_console.py

tests/
├── contract/
│   └── test_telegram_configuration_contract.py
├── integration/
│   ├── api/
│   │   ├── test_admin_telegram_api.py
│   │   └── test_admin_telegram_ui.py
│   └── db/
│       └── test_telegram_config_migration.py
├── unit/
│   ├── admin/
│   │   └── telegram_config/
│   │       ├── test_redaction.py
│   │       └── test_service.py
│   ├── api/
│   │   ├── test_telegram_config_schemas.py
│   │   └── test_telegram_config_ui_models.py
│   ├── auth/
│   │   └── test_telegram_config_policy.py
│   └── db/
│       └── test_telegram_config_repository.py
└── docs/
    └── test_telegram_configuration_docs.py
```

**Structure Decision**: Add a focused `admin.telegram_config` domain package
and keep router, repository, schema, and template adapters thin. Reuse the
existing admin shell, local-principal login, settings validation, secret
reference conventions, and Spec 006 channel service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves secret-reference readiness, local webhook validation,
tenant-scoped enablement, link-token auditing, redacted identity summaries,
diagnostics, stale revisions, and audit boundaries. See [research.md](./research.md).

Key decisions:

- Treat Settings `telegram_provider_token_ref` and `telegram_webhook_secret` as
  read-only global inputs and render only readiness state plus masked reference
  labels.
- Store tenant enablement separately from global provider readiness.
- Use existing `ChannelService.create_telegram_link_token` for one-time token
  creation and persist safe token fingerprints in a console audit table.
- Mirror linked identities into safe summary rows for admin inspection and
  revocation; never persist message bodies or raw webhook payloads.
- Record local webhook validation as a diagnostic event with no network call.
- Use monotonically changing revision tokens to detect stale tenant form writes.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines tenant config, token audit, identity
  summaries, diagnostics, states, validation rules, and tenant boundaries.
- [contracts/telegram-configuration.openapi.yaml](./contracts/telegram-configuration.openapi.yaml)
  defines the JSON admin API for readiness, tenant config, link tokens,
  identities, and diagnostics.
- [contracts/admin-telegram-ui.md](./contracts/admin-telegram-ui.md) defines
  the server-rendered console, forms, stale conflict state, and redaction.
- [quickstart.md](./quickstart.md) gives local setup and QA validation flows.

## API And UI Surface

- API routes live under `/admin/telegram/api`.
- UI route lives under `/admin/telegram`.
- All routes require an authenticated platform admin or tenant admin.
- Platform admins may view platform readiness and select tenant scope. Tenant
  admins are forced to their own tenant scope.
- Navigation adds "Telegram Configuration" with tenant scope preservation.
- The validation plan uses `/admin/telegram` for browser screenshots.

## Migration Strategy

- Add only new Telegram console tables and indexes; do not rewrite existing
  Spec 006 channel tables.
- Use JSON for safe diagnostics and command lists only.
- Add tenant/status/revision indexes for tenant config, token audit, identity
  summaries, and diagnostics.
- Migration downgrade drops only the new feature tables.

## Observability And Audit

- Diagnostics are persisted for readiness checks, webhook validation, link-token
  issue/revoke, identity revocation, denied access, and stale conflicts.
- Metrics are represented by service counters where existing metrics are
  enabled; tests focus on safe diagnostic records and status categories.
- Logs and diagnostics include tenant id, principal id, trace id, action,
  status, and category without secrets, messages, prompts, or run results.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with Telegram Configuration,
  `/admin/telegram`, QA017 validation, and quality commands.
- Add feature PR notes and testing instructions under
  `specs/017-telegram-configuration-console/`.
- Generate QA docs and non-developer manual QA guide before final validation.
