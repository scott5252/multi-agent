# Implementation Plan: React Admin UI Foundation

**Branch**: `codex/026-react-admin-ui-foundation` | **Date**: 2026-05-04 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/026-react-admin-ui-foundation/spec.md`

## Summary

Add an additive React admin foundation without migrating domain pages: a Vite
SPA mounted at `/admin/app`, built assets served by FastAPI under
`/admin/static/react`, backend-owned bootstrap/navigation/config/version JSON
contracts, generated TypeScript contract checks, and deterministic dual-auth
validation. Existing Jinja admin routes remain direct and authorized fallbacks
until later specs prove parity.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode; Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Starlette StaticFiles, Pydantic v2, React, React Router, Vite, Vitest, Testing Library, Playwright  
**Storage**: PostgreSQL remains authoritative for tenant/principal state; no new durable tables for Spec 026; built React assets are repository/build artifacts served from the admin static tree  
**Testing**: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, npm frontend lint/typecheck/test/build scripts, Playwright smoke via QA manifest  
**Target Platform**: FastAPI admin service plus browser SPA for platform and tenant administrators  
**Project Type**: Web application with existing Python backend and new `frontend/admin` React frontend  
**Performance Goals**: React shell bootstrap returns in under 500 ms locally; built app initial JS/CSS payload stays below 300 KB gzip for the minimal foundation; existing `/admin` Jinja landing latency does not regress measurably in route tests  
**Constraints**: No production auth shortcuts; no domain page migration; no raw secrets, raw claims, prompts, completions, memory, provider payloads, tool payloads, or stack traces in browser contracts; browser state cannot become an authorization source of truth  
**Scale/Scope**: One minimal shell route, one bootstrap contract family, one generated type workflow, and smoke validation for Auth0-backed and local-principal principals

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. No workflow state or external side effects are introduced; route behavior is idempotent read-only except future server-issued action token scaffolding.
- **II. Immutable State And Memory**: PASS. No mutable memory source of truth is added; contracts are versioned files and generated outputs.
- **III. Contract-First Agent Coordination**: PASS. Browser/backend boundary is defined through Pydantic/OpenAPI-style contracts and generated TypeScript validation.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0 remains production authority; local-principal mode remains explicit and still exercises admin authorization and tenant scope checks.
- **V. Operability Is A Product Requirement**: PASS. Bootstrap failures use safe problem responses, audit/visibility behavior stays in existing admin shell helpers, audit persistence failures fail closed, and QA captures browser evidence.
- **VI. Spec-Driven Delivery**: PASS. Spec, clarifications, plan, tasks, QA docs, and validation manifest govern the work.
- **VII. Test And Documentation Discipline**: PASS. Backend route tests, frontend unit tests, generated contract checks, Playwright smoke, QA docs, and quickstart updates are required.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is limited to a foundation route, contracts, frontend shell skeleton, tests, docs, and static serving.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Tenant scope is resolved server-side through existing principal and admin shell policy helpers; no queue or scheduling behavior changes.
- **X. Version-Pinned Execution**: PASS. Runtime workflow execution is out of scope; app/version metadata is surfaced read-only for operators.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Browser contracts explicitly exclude secrets, credential values, raw provider headers, raw tool payloads, and external calls.
- **XII. Tiered Storage For Large Payloads**: PASS. No large payload storage changes; Playwright screenshots remain QA artifacts.
- **XIII. Human Approval Is Durable State**: PASS. Approval/resume flows are not modified.

Post-design re-check: PASS. Phase 0 and Phase 1 artifacts keep the same additive, read-only, fail-closed boundary with no unresolved constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/026-react-admin-ui-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── react-admin-bootstrap.openapi.yaml
├── qa026.md
├── qa026_ui.md
├── qa026_user_guide.md
├── .env.qa026
└── tasks.md
```

### Source Code (repository root)

```text
frontend/admin/
├── package.json
├── package-lock.json
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── vitest.config.ts
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── routes.tsx
│   ├── api/
│   │   ├── client.ts
│   │   └── generated/
│   │       └── reactAdminApi.ts
│   ├── components/
│   │   ├── AdminShell.tsx
│   │   ├── ScopeSummary.tsx
│   │   └── StatePanel.tsx
│   ├── styles/
│   │   └── admin.css
│   └── test/
│       └── setup.ts
├── src/App.test.tsx
└── src/bootstrapContract.test.ts

src/multi_agent_platform/
├── api/
│   ├── routers/
│   │   └── admin_react.py
│   └── schemas/
│       └── admin_react.py
├── config/
│   └── settings.py
└── web_admin/
    ├── static/
    │   └── react/
    └── templates/
        └── admin_react/
            └── app.html

tests/
├── contract/
│   └── test_admin_react_contract.py
├── integration/
│   └── test_admin_react_routes.py
└── unit/
    └── api/test_admin_react_schema.py

scripts/
└── frontend/
    └── generate_admin_react_types.py
```

**Structure Decision**: Use `frontend/admin` for the React app so the Python
package remains focused on the FastAPI platform and future React specs can
grow inside one frontend workspace. Add a thin `admin_react.py` router and
Pydantic schema module for the bridge; reuse existing admin shell helpers
instead of creating new authorization services.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
