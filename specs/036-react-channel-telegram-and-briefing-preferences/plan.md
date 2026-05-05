# Implementation Plan: React Channel, Telegram, And Briefing Preferences

**Branch**: `codex/036-react-channel-telegram-and-briefing-preferences` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/036-react-channel-telegram-and-briefing-preferences/spec.md`

## Summary

Build an additive React workspace for channel readiness, Telegram tenant configuration, natural-language aliases, identity linking, delivery diagnostics, safe run status links, and Daily Intelligence Briefing preference profiles. The implementation will preserve existing Jinja fallbacks and domain services, expose backend-owned JSON contracts through `admin_react.py`, generate TypeScript contracts, and render React components that never derive authorization, tenant scoping, secret readiness, alias protection, link-token visibility, delivery diagnostics, or preference redaction rules in the browser.

## Technical Context

**Language/Version**: Python 3.12; TypeScript/React/Vite admin frontend already introduced by Specs 026-035  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async repositories, existing Telegram/channel/briefing admin services, React, generated React admin API contracts, lucide-react icons  
**Storage**: PostgreSQL for tenant configuration, aliases, linked identities, delivery attempts, briefing preference heads/revisions, audit metadata; filesystem/object storage for safe import/export artifact metadata  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, performance query tests, Vitest, TypeScript check, Vite build, Spec QA runner, Playwright UI runner  
**Target Platform**: FastAPI control plane and React admin SPA served from `/admin/app`  
**Project Type**: Web admin application with backend JSON contracts and frontend React components  
**Performance Goals**: Bootstrap payloads under 500ms in deterministic QA; bounded alias, identity, delivery, webhook, and preference rows; no unbounded diagnostic rendering  
**Constraints**: No real Telegram, Auth0, provider, credential, or connector calls in local QA; fail closed on tenant, authorization, audit, revision, idempotency, link-token, or secret-readiness uncertainty; preserve `/admin/telegram`, `/admin/briefing-preferences`, channel run UI, and related Jinja fallbacks until Spec 037  
**Scale/Scope**: One React channel workspace plus safe run status and briefing preference profile/detail panels, deterministic QA036 fixtures, docs, and validation evidence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. Alias mutations, link-token creation, webhook validation, delivery diagnostics, and preference saves use persisted service projections, revisions, idempotency, and audit evidence.
- **II. Immutable State And Memory**: PASS. Preference profiles retain immutable revisions; audit and diagnostic evidence are append-only summaries.
- **III. Contract-First Agent Coordination**: PASS. React consumes explicit Pydantic/OpenAPI contracts and generated TypeScript types.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped route tests and local-principal Playwright flows are required.
- **V. Operability Is A Product Requirement**: PASS. Readiness, validation, delivery attempts, webhook receipts, safe run links, and audit references are first-class views.
- **VI. Spec-Driven Delivery**: PASS. Specify, clarify, plan, tasks, analyze, implement, docs, and QA are required before moving to Spec 037.
- **VII. Test And Documentation Discipline**: PASS. Focused backend/frontend tests, full Spec QA, Playwright, QA docs, README, and quickstart updates are required.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Work is scoped to additive schema/service/router/frontend/docs/test files.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Tenant scope is explicit; cross-tenant channel, alias, identity, diagnostics, and preference access fails closed.
- **X. Version-Pinned Execution**: PASS. Safe run status links do not mutate execution bundles; runtime links remain read-only summaries.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Bot tokens, webhook secrets, link-token follow-up display, provider credentials, and raw external payloads remain hidden.
- **XII. Tiered Storage For Large Payloads**: PASS. Preference import/export uses artifact metadata and never browser-renders raw private values.
- **XIII. Human Approval Is Durable State**: PASS. No new approval flow is introduced; run status links remain safe read-only evidence.

## Project Structure

### Documentation (this feature)

```text
specs/036-react-channel-telegram-and-briefing-preferences/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── channel-telegram-briefing-react.openapi.yaml
│   └── channel-telegram-briefing-react-ui.md
├── qa036.md
├── qa036_ui.md
├── qa036_user_guide.md
├── .env.qa036
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/channel_telegram_briefing/       # React-safe deterministic adapter/projection service
├── api/schemas/admin_channel_telegram_briefing_react.py
├── api/routers/admin_react.py             # React route/API endpoints
├── auth/policy.py                         # Protected route surfaces
└── web_admin/static/react/                # Built React assets

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── App.tsx
├── routes.tsx
├── components/channelTelegramBriefing/
├── styles/admin.css
└── test/channelTelegramBriefingTestData.ts

tests/
├── unit/api/test_admin_channel_telegram_briefing_react_schema.py
├── unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py
├── performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py
├── contract/test_admin_react_contract.py
└── integration/test_admin_react_routes.py
```

**Structure Decision**: Reuse the additive React admin pattern from Specs 029-035: a backend schema module, deterministic admin projection service, protected routes in the React admin router, generated frontend types, route-specific components, focused tests, and QA docs.

## Phase 0 Research

Research output is recorded in [research.md](research.md). All planning unknowns are resolved using established Specs 006, 017, 022, and 023 patterns.

## Phase 1 Design

Design outputs:

- [data-model.md](data-model.md)
- [contracts/channel-telegram-briefing-react.openapi.yaml](contracts/channel-telegram-briefing-react.openapi.yaml)
- [contracts/channel-telegram-briefing-react-ui.md](contracts/channel-telegram-briefing-react-ui.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

PASS. The design remains additive, contract-first, tenant-scoped, redaction-first, mock-safe for local validation, and reversible before Spec 037 retirement work. No constitution violations or waivers are required.

## Complexity Tracking

No constitution violations require justification.
