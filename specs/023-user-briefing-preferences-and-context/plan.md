# Implementation Plan: User Briefing Preferences And Context

**Branch**: `codex/023-user-briefing-preferences-and-context` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/023-user-briefing-preferences-and-context/spec.md`

## Summary

Add a tenant-scoped Daily Intelligence Briefing preference subsystem with
dedicated PostgreSQL head/revision/audit tables, Pydantic validation, a
server-rendered admin/user console, safe admin summaries, JSON import/export,
and a runtime resolver that can attach a pinned preference revision to Telegram
or future scheduled briefing workflow inputs.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing admin shell, existing channel runtime contracts, audit/redaction helpers, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: PostgreSQL for briefing preference heads, immutable revisions, safe audit events, import/export metadata, and runtime resolution evidence.  
**Testing**: Unit tests for validation/redaction/service behavior; repository tests for immutable revisions and tenant filters; integration tests for API/UI save, admin summary, import/export, runtime resolver, Telegram alias context injection, and cross-tenant denial.  
**Target Platform**: Linux service containers plus local macOS/Linux development, served through the existing FastAPI control-plane app and worker process.  
**Project Type**: Multi-tenant Python web service with server-rendered admin shell and channel runtime.  
**Performance Goals**: Runtime resolver lookup under 50 ms excluding database connection time for one `(tenant_id, principal_id)` head; browser save/reload under 2 minutes during local QA.  
**Constraints**: No raw OAuth tokens, API keys, passwords, or private provider credential values in profile fields, rendered admin summaries, diagnostics, or logs. Cross-tenant access fails closed. Scheduled dispatch execution is not implemented in this slice.  
**Scale/Scope**: One briefing preference profile per tenant/principal, bounded lists for topics and VIP senders, JSON import/export, admin summaries, runtime resolver, docs, QA artifacts, and validation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Profile heads, immutable revisions, and resolver audit records persist in PostgreSQL. |
| Immutable State And Memory | PASS | Updates append revisions and move a head projection; run inputs carry revision provenance. |
| Contract-First Agent Coordination | PASS | API, import/export, admin UI, and runtime resolver contracts are documented. |
| Security With Practical Development Ergonomics | PASS | Local principals exercise permissions, tenant scoping, and redaction. |
| Operability Is A Product Requirement | PASS | Safe audit events cover save, denial, summary inspection, import/export, and runtime resolution. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation are traceable. |
| Test And Documentation Discipline | PASS | Tasks include tests, docs, manual QA guide, Playwright, and quality gates. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to briefing preference admin/API/runtime files plus one additive migration. |
| Tenant Isolation And Fair Scheduling | PASS | Every query uses tenant and principal scope; cross-tenant calls return denied/missing without raw data. |
| Version-Pinned Execution | PASS | Runtime resolver returns `revision_id` and `content_digest` for run input pinning. |
| Secret Hygiene And Controlled Tool Access | PASS | Calendar/email fields accept safe references only and reject credential-looking values. |
| Tiered Storage For Large Payloads | PASS | Preference payloads are bounded JSON; large briefing artifacts remain outside this feature. |
| Human Approval Is Durable State | PASS | No approval state changes; future setup prompts remain compatible with existing durable approval flows. |

Post-Phase-1 re-check: dedicated tables, contracts, and quickstart preserve all `PASS` statuses. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/023-user-briefing-preferences-and-context/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── briefing-preferences.md
├── tasks.md
├── qa023.md
├── qa023_ui.md
├── qa023_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
alembic/versions/
└── 0020_briefing_preferences.py

src/multi_agent_platform/
├── admin/briefing_preferences/
│   ├── models.py
│   ├── redaction.py
│   └── service.py
├── api/
│   ├── routers/admin_briefing_preferences.py
│   ├── schemas/briefing_preferences.py
│   └── ui/briefing_preferences.py
├── db/
│   ├── models/briefing_preferences.py
│   └── repositories/briefing_preferences.py
├── runtime/briefing_preferences.py
└── web_admin/templates/briefing_preferences/index.html

tests/
├── contract/test_briefing_preferences_contract.py
├── integration/api/test_admin_briefing_preferences_api.py
├── integration/api/test_admin_briefing_preferences_ui.py
├── integration/runtime/test_briefing_preference_resolution.py
├── unit/admin/briefing_preferences/
│   ├── test_redaction.py
│   └── test_briefing_preference_service.py
└── unit/db/test_briefing_preferences_repository.py
```

**Structure Decision**: Keep user/admin preference lifecycle in
`admin.briefing_preferences` because the first UI is an admin-shell screen used
by tenant users and admins. Keep the runtime-facing dataclass wrapper in
`runtime` so channel handlers and future schedulers can resolve context without
importing router code.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

See [research.md](./research.md). Key decisions:

- Store preference profiles in dedicated tables with immutable revisions and a head projection.
- Treat calendar/email selections as references only; reject credential-looking values.
- Use IANA timezone validation from Python `zoneinfo`.
- Make admin summaries safe by showing counts, masked values, fingerprints, readiness, revision, and timestamps.
- Attach runtime context only to new run inputs, never mutate active runs.

## Phase 1 Design And Contracts

Design artifacts:

- [data-model.md](./data-model.md) defines profile heads, revisions, audit events, and resolver context.
- [contracts/briefing-preferences.md](./contracts/briefing-preferences.md) defines UI/API/runtime/import-export contracts.
- [quickstart.md](./quickstart.md) defines local QA setup, browser flow, API checks, runtime resolver validation, and redaction evidence.

## API And UI Surface

- Add `/admin/briefing-preferences` browser page.
- Add `/admin/briefing-preferences/api/profile`, `/admin/briefing-preferences/api/summaries`, `/admin/briefing-preferences/api/export`, `/admin/briefing-preferences/api/import`, and `/admin/briefing-preferences/api/resolve`.
- Add admin navigation entry labeled `Briefing Preferences`.
- Extend Telegram natural-language alias handling to include briefing preference context for Daily Intelligence Briefing aliases when available.

## Migration Strategy

- Add `briefing_preference_profiles` for current heads.
- Add `briefing_preference_revisions` for immutable profile versions.
- Add `briefing_preference_audit_events` for safe operational evidence.
- Migration is additive and does not rewrite or delete existing data.

## Observability And Audit

- Audit events store tenant id, principal id, actor principal id, action, decision, safe summary, content digest, revision id, trace id, and redacted metadata.
- Runtime resolver records `runtime_resolved`, `runtime_missing`, or `runtime_denied` without raw profile content.
- Admin views render safe summaries only and never raw VIP sender values or raw account references.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with QA023 entry points.
- Add QA023 guide, QA023 UI walkthrough, non-developer QA user guide, PR review notes, and testing instructions.
