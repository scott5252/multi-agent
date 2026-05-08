# Implementation Plan: Channels, Telegram, Briefing React Live Data

**Branch**: `codex/055-channels-telegram-briefing-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/055-channels-telegram-briefing-react-live-data/spec.md`

## Summary

Replace deterministic channel, Telegram, and briefing React payloads with live backend projections over existing Telegram configuration, command alias, link-token audit, linked identity, delivery/notification, webhook receipt, channel run, briefing preference, artifact, and audit services. The React admin workspace must render live authorized rows, truthful empty states, redaction-safe details, and at least one persisted browser action that is verified through qa055 API/database evidence.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript strict mode with React 19 and Node.js `>=20.19.0 <26` for `frontend/admin`.  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, PostgreSQL, existing Telegram/channel/briefing/admin services, React Router, Vite, Vitest, Testing Library, generated TypeScript contracts.  
**Storage**: PostgreSQL remains source of truth for config, aliases, identities, delivery attempts, notifications, webhook receipts, briefing preferences, audit records, and artifact metadata; filesystem/object storage only for QA/import/export artifacts.  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, contract tests, performance tests, Ruff, mypy, Vitest, TypeScript typecheck, Vite build, QA document validation, Spec QA, Playwright, post-UI verifier, multi-agent curl test.  
**Target Platform**: FastAPI web service serving React admin assets and JSON contracts.  
**Project Type**: Full-stack web application in the existing monorepo.  
**Performance Goals**: Bounded channel/briefing projections should use limited queries and avoid unbounded delivery/run/audit scans.  
**Constraints**: No real Telegram/provider/external calls in local QA; no raw tokens, link tokens after creation, full Telegram identifiers, private messages, raw webhook payloads, raw run payloads, local paths, stack traces, or unauthorized tenant labels in UI/API/docs/artifacts.  
**Scale/Scope**: Spec 055 owns `channel_telegram_briefing` React production surfaces and directly related route/schema/frontend tests; later specs own other domains.

## Constitution Check

*GATE: Passed before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Safe mutations must use existing persisted services and idempotency/audit evidence.
- Immutable State And Memory: PASS. Briefing revisions, link-token audit, webhook receipts, deliveries, and audit rows remain append-only/versioned where the domain already models them.
- Contract-First Agent Coordination: PASS. React consumes generated Pydantic/TypeScript contracts.
- Security With Practical Development Ergonomics: PASS. Auth0-shaped tests and local-principal QA both exercise authorization and tenant scoping.
- Operability Is A Product Requirement: PASS. Readiness, delivery diagnostics, webhook evidence, run links, and audit references are explicit.
- Spec-Driven Delivery: PASS. Specification, plan, research, data model, contracts, tasks, and validation are required before completion.
- Test And Documentation Discipline: PASS. QA docs, focused tests, full Spec QA, Playwright, verifier, and curl are required.
- Clear Ownership And Small Safe Changes: PASS. Scope is bounded to channel/Telegram/briefing React live-data surfaces.
- Tenant Isolation And Fair Scheduling: PASS. Cross-tenant IDs fail closed and delivery diagnostics are bounded.
- Version-Pinned Execution: PASS. Channel run links are references to persisted run state; this spec does not alter runtime bundle semantics.
- Secret Hygiene And Controlled Tool Access: PASS. Telegram token, webhook secret, and link-token visibility are explicitly redacted/one-time.
- Tiered Storage For Large Payloads: PASS. Import/export evidence uses artifact references, not raw payload rendering.
- Human Approval Is Durable State: PASS. No new approval semantics; any existing admin action audit remains durable.

## Project Structure

### Documentation (this feature)

```text
specs/055-channels-telegram-briefing-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── channels-briefing-live-data.openapi.yaml
│   └── channels-briefing-live-data-ui.md
├── qa055.md
├── qa055_ui.md
├── qa055_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/channel_telegram_briefing/react_channel_telegram_briefing.py
├── api/routers/admin_react.py
├── api/schemas/admin_channel_telegram_briefing_react.py
├── channels/
├── admin/briefing_preferences.py
├── db/models/
├── db/repositories/
└── web_admin/static/react/

frontend/admin/src/
├── api/generated/reactAdminApi.ts
├── components/channelTelegramBriefing/
├── test/
└── routes.tsx

scripts/qa/
├── seed_channels_briefing_qa055.py
└── verify_channels_briefing_qa055.py

tests/
├── fixtures/
├── integration/
├── performance/
└── unit/
```

**Structure Decision**: Use the existing FastAPI admin route, backend projection, repository/service, generated contract, React component, and pytest/Vitest layout. No new package or application boundary is needed.

## Complexity Tracking

No constitution violations require justification.

## Phase 0: Research

Research decisions are captured in [research.md](research.md). The key outcome is to use existing Telegram configuration, alias/link-token, delivery/notification, channel run, briefing preference, artifact, and audit services as source of truth, with QA scripts creating real local database rows and no live external calls.

## Phase 1: Design And Contracts

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/channels-briefing-live-data.openapi.yaml](contracts/channels-briefing-live-data.openapi.yaml)
- [contracts/channels-briefing-live-data-ui.md](contracts/channels-briefing-live-data-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

*GATE: Passed after Phase 1 design.*

Design keeps the feature within established services and generated contracts, preserves tenant isolation, redacts Telegram and briefing-sensitive content, avoids external calls in QA, uses artifact references for import/export evidence, and requires mandatory docs, Spec QA, Playwright, post-UI verification, and curl validation before queue advancement.
