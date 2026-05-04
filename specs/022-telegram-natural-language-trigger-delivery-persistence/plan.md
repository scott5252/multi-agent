# Implementation Plan: Telegram Natural-Language Trigger Delivery Persistence

**Branch**: `codex/022-telegram-natural-language-trigger-delivery-persistence` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/022-telegram-natural-language-trigger-delivery-persistence/spec.md`

## Summary

Add tenant-scoped Telegram command aliases that route natural-language messages such as `Morning briefing` to published workflow versions, persist link-token and identity state in PostgreSQL, enforce tenant Telegram readiness at webhook runtime, and deliver deterministic final run results through a mocked-safe Telegram Bot API boundary with durable delivery attempts.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing Telegram admin configuration services/schemas/templates, existing channel models and ChannelService contracts, runtime orchestration run facade, secret provider abstractions, audit/redaction helpers, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: PostgreSQL for Telegram command aliases, persistent Telegram identity links, Telegram update receipts, token audit consumption, notification delivery attempts, and diagnostics.  
**Testing**: Unit tests for alias normalization and result formatting; repository tests for alias/update receipt/persistent identity records; integration tests for admin alias API/UI, webhook alias routing, idempotency, Bot API mock delivery, tenant isolation, revoked identities, disabled config, and docs.  
**Target Platform**: Linux service containers plus local macOS/Linux development, served through the existing FastAPI control-plane app and worker process.  
**Project Type**: Multi-tenant Python web service with server-rendered admin shell and Telegram webhook channel.  
**Performance Goals**: Resolve one tenant alias in under 50 ms excluding database connection time; replay duplicate updates from persistence in under 50 ms; persist delivery attempt evidence in the same request transaction for deterministic QA.  
**Constraints**: No real Telegram Bot API calls in local/CI QA. Production code must use safe secret references, never raw token values in records or diagnostics. Cross-tenant alias and identity checks fail closed.  
**Scale/Scope**: One tenant Telegram delivery slice: alias CRUD, runtime routing, persistent link/identity consumption, mocked Bot API boundary, delivery evidence, admin UI updates, docs, QA artifacts, and validation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Alias state, link token consumption, identity links, update receipts, run invocation, and delivery attempts persist. |
| Immutable State And Memory | PASS | Published workflow version IDs are referenced immutably; update receipts and delivery attempts are append-oriented evidence. |
| Contract-First Agent Coordination | PASS | Webhook, admin API, alias router, Bot API client, and delivery attempt contracts are documented. |
| Security With Practical Development Ergonomics | PASS | Local QA uses local principals and a mocked Bot API while preserving tenant authorization and secret-reference checks. |
| Operability Is A Product Requirement | PASS | Runtime denials, duplicate updates, alias routing, and deliveries emit safe diagnostics and persisted attempts. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation are traceable. |
| Test And Documentation Discipline | PASS | Tasks include test-first coverage, docs, QA guides, README/quickstart updates, and quality gates. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to Telegram channel/admin modules, channel persistence, tests, docs, and one additive migration. |
| Tenant Isolation And Fair Scheduling | PASS | Alias lookup and identity validation are tenant-scoped; cross-tenant access fails closed. |
| Version-Pinned Execution | PASS | Alias maps to a published workflow version ID that is handed to existing run creation. |
| Secret Hygiene And Controlled Tool Access | PASS | Bot token usage is by secret reference; diagnostics and attempts store labels/fingerprints only. |
| Tiered Storage For Large Payloads | PASS | Delivery text is bounded and safe; large outputs are summarized or referenced. |
| Human Approval Is Durable State | PASS | Existing prompt approval paths are unchanged and remain durable when runs enter waiting state. |

Post-Phase-1 re-check: data model, contracts, and quickstart preserve all `PASS` statuses. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/022-telegram-natural-language-trigger-delivery-persistence/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── telegram-alias-delivery.md
├── tasks.md
├── qa022.md
├── qa022_ui.md
├── qa022_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
alembic/versions/
└── 0019_telegram_alias_delivery.py

src/multi_agent_platform/
├── admin/telegram_config/
│   ├── models.py
│   └── service.py
├── api/
│   ├── routers/
│   │   ├── admin_telegram.py
│   │   └── telegram_webhook.py
│   ├── schemas/telegram_config.py
│   └── ui/telegram_config.py
├── channels/
│   ├── telegram.py
│   └── telegram_delivery.py
├── db/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── channels.py
│   │   └── telegram_config.py
│   └── repositories/
│       ├── channels.py
│       └── telegram_config.py
└── web_admin/templates/telegram/index.html

tests/
├── contract/test_telegram_alias_delivery_contract.py
├── integration/api/
│   ├── test_admin_telegram_api.py
│   ├── test_admin_telegram_ui.py
│   └── test_telegram_webhook.py
├── unit/channels/
│   └── test_telegram_delivery.py
└── unit/db/
    ├── test_channel_models.py
    └── test_telegram_config_repository.py
```

**Structure Decision**: Keep alias management in `admin.telegram_config` because it extends the existing Telegram configuration console. Keep Bot API delivery in `channels` because it is channel runtime behavior and must remain testable behind a mocked boundary.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves alias matching, persistent link token consumption, identity revocation, Bot API client boundaries, delivery attempts, idempotency receipts, and deterministic QA. See [research.md](./research.md).

Key decisions:

- Use tenant-scoped exact alias matching after whitespace normalization and case folding.
- Reuse existing token audit and identity summary concepts, while adding runtime-safe repository methods and persistent update receipts.
- Add one additive migration for aliases and webhook update receipts.
- Use the existing notification delivery attempt table for Telegram Bot API evidence.
- Inject a mock Bot API client in tests through app container state; production code remains behind a boundary that consumes secret references.

## Phase 1 Design And Contracts

Design artifacts:

- [data-model.md](./data-model.md) defines aliases, persistent identities, update receipts, and delivery attempts.
- [contracts/telegram-alias-delivery.md](./contracts/telegram-alias-delivery.md) defines admin API, webhook routing, Bot API boundary, and delivery evidence contracts.
- [quickstart.md](./quickstart.md) defines deterministic local setup, alias creation, webhook trigger, delivery evidence checks, and browser validation.

## API And UI Surface

- Extend `/admin/telegram` with "Telegram Command Aliases" list and create/update controls.
- Add `/admin/telegram/api/aliases` and `/admin/telegram/api/aliases/{alias_id}` API endpoints.
- Extend `/channels/telegram/webhook/{secret}` to route natural-language aliases after link and readiness validation.
- Keep existing `/run`, `/status`, `/link`, `/result`, `/subscribe`, and approval command behavior compatible.

## Migration Strategy

- Add `telegram_command_aliases` for tenant alias configuration.
- Add `telegram_update_receipts` for persistent webhook update replay.
- Reuse `telegram_link_token_audits`, `telegram_linked_identity_summaries`, `telegram_identity_links`, and `notification_delivery_attempts`.
- The migration is additive and does not delete or rewrite existing data.

## Observability And Audit

- Diagnostics are recorded for alias creation, alias routing, wrong secret, duplicate update replay, access denial, runtime readiness failure, and delivery status.
- Delivery attempts store status, attempt number, payload fingerprint, destination fingerprint, provider message ID, safe failure category, and trace ID.
- Admin views show masked identifiers, fingerprints, status labels, and safe summaries only.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with QA022 entry points.
- Add QA022 guide, QA022 UI walkthrough, non-developer QA user guide, PR review notes, and testing instructions.
