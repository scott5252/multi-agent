# Implementation Plan: Operations Console Logs And Performance

**Branch**: `codex/019-operations-console-logs-performance` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/019-operations-console-logs-performance/spec.md`

## Summary

Add a platform-operator Operations Console that aggregates existing safe
operational records into a server-rendered dashboard and JSON APIs. The feature
introduces an `operations` domain package, Pydantic schemas, an admin router at
`/admin/operations`, UI view models, an admin shell template, navigation and
authorization entries, redacted CSV exports through existing storage, audit
metadata through existing inspection-access audit records, tests, QA docs, PR
notes, testing instructions, and README/quickstart updates.

The implementation intentionally avoids raw log-file reads and new tables. It
uses existing health checks, reliability capacity snapshots, model provider
records, Telegram settings/diagnostics, usage events, gateway attempts, and
audit-debugging timeline/trace records.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing runtime health service, reliability repositories, model provider
repositories, Telegram config services/settings, usage analytics service,
audit-debugging repository, object/filesystem storage providers,
prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: No new tables. Reuse existing operational source tables and
artifact storage. Export and denial audit metadata uses
`audit_inspection_access_events`.  
**Testing**: pytest unit tests for redaction, service aggregation, schemas, UI
models, policy entries, and export CSV; httpx/TestClient integration tests for
API and UI authorization, filtering, tenant-admin denial, auditor access, export
artifact/audit behavior, and screenshot-safe rendering; performance test for
bounded log queries over 10,000 events; docs tests; Playwright validation
through the configured QA runner.  
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, local-principal test login, PostgreSQL, and worker process.  
**Project Type**: Multi-tenant Python web service with JSON admin APIs,
server-rendered admin UI, durable runtime support, and background workers.  
**Performance Goals**: Dashboard p95 <= 500 ms for 500 recent operational rows;
bounded log query p95 <= 250 ms for a one-hour window over 10,000 timeline
events in local SQLite/PostgreSQL-compatible tests; export of 500 rows under 1s
excluding storage backend latency.  
**Constraints**: Platform logs are platform-admin/auditor only in v1.
Cross-tenant access fails closed. Raw prompts, responses, secrets, credentials,
memory content, channel messages, payloads, stack traces, and authorization
headers are never rendered or exported. Log queries are bounded. PostgreSQL
stores metadata only; CSV payloads use object/filesystem storage.  
**Scale/Scope**: One vertical feature slice: domain models/service/redaction,
schemas, API/UI router, server-rendered template, navigation/policy/local
principal entries, tests, docs, QA artifacts, manual QA user guide, and
validation commands.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Dashboard reads durable health/audit/reliability/provider/usage records; exports persist as artifacts with audit metadata. |
| Immutable State And Memory | PASS | The console reads append-only or immutable operational evidence and does not mutate runtime state. |
| Contract-First Agent Coordination | PASS | API and UI contracts define filter, export, and redaction semantics before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal paths reuse existing authorization; QA uses explicit local principals. |
| Operability Is A Product Requirement | PASS | The feature directly improves health, dependency, capacity, latency, throughput, error, and log visibility. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and code remain traceable. |
| Test And Documentation Discipline | PASS | Test tasks include auth, filtering, redaction, export, performance, docs, QA, and coverage gates. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `operations`, `api`, `auth`, `web_admin`, tests, docs, and feature artifacts. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant-admin platform log access is denied for v1; tenant id filters are explicit for platform/auditor users. |
| Version-Pinned Execution | PASS | No workflow execution bundle changes are introduced. |
| Secret Hygiene And Controlled Tool Access | PASS | Raw logs are not read; sensitive keys are redacted or dropped. |
| Tiered Storage For Large Payloads | PASS | Export CSV payloads use configured artifact storage, not PostgreSQL blobs. |
| Human Approval Is Durable State | PASS | No new approval/resume semantics are introduced. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/019-operations-console-logs-performance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── admin-operations-ui.md
│   └── operations-console.openapi.yaml
├── tasks.md
├── qa019.md
├── qa019_ui.md
├── qa019_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── operations/
│   ├── __init__.py
│   ├── export.py
│   ├── models.py
│   ├── redaction.py
│   └── service.py
├── api/
│   ├── routers/
│   │   └── admin_operations.py
│   ├── schemas/
│   │   └── operations.py
│   └── ui/
│       └── operations.py
└── web_admin/
    └── templates/
        └── operations/
            └── index.html

tests/
├── contract/
│   └── test_operations_console_contract.py
├── integration/
│   └── api/
│       ├── test_admin_operations_api.py
│       └── test_admin_operations_ui.py
├── performance/
│   └── operations/
│       └── test_log_filtering.py
├── unit/
│   ├── api/
│   │   ├── test_operations_schemas.py
│   │   └── test_operations_ui_models.py
│   ├── auth/
│   │   └── test_operations_policy.py
│   └── operations/
│       ├── test_export.py
│       ├── test_redaction.py
│       └── test_service.py
└── docs/
    └── test_operations_console_docs.py
```

**Structure Decision**: Add a focused `operations` domain package and keep
router, schema, UI, and template adapters thin. Reuse existing admin shell,
runtime health, reliability, provider, Telegram, usage, storage, and
audit-debugging services.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves source-of-truth, role boundaries, query strategy, export
storage/audit, and UI approach. See [research.md](./research.md).

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines dashboard, filters, log events,
  export artifacts, access scope, and source records.
- [contracts/operations-console.openapi.yaml](./contracts/operations-console.openapi.yaml)
  defines dashboard, log query, and export APIs.
- [contracts/admin-operations-ui.md](./contracts/admin-operations-ui.md)
  defines the server-rendered console, filters, redaction, export, and
  navigation behavior.
- [quickstart.md](./quickstart.md) gives local setup and QA validation flows.

## API And UI Surface

- API routes live under `/admin/operations/api`.
- UI route lives under `/admin/operations`.
- Browser export wrapper lives at `/admin/operations/logs/export`.
- Routes require an authenticated platform admin or auditor with operations
  permissions.
- Navigation adds "Operations Console" with platform/auditor visibility.
- Validation uses `/admin/operations` for browser screenshots.

## Migration Strategy

- No migration is required for v1.
- If future releases add saved operational snapshots or export lifecycle
  tracking, use additive tables only.

## Observability And Audit

- Export and denied export attempts are written to
  `audit_inspection_access_events`.
- Dashboard reads are covered by existing access-decision audit.
- Redaction helpers are tested against prompts, responses, secrets,
  credentials, raw payloads, memory content, channel messages, authorization
  headers, and stack traces.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with Operations Console,
  `/admin/operations`, QA019 validation, and quality commands.
- Add feature PR notes and testing instructions under
  `specs/019-operations-console-logs-performance/`.
- Generate QA docs and non-developer manual QA guide before final validation.
