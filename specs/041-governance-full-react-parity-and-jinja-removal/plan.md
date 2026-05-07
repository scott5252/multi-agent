# Implementation Plan: Governance Full React Parity And Jinja Removal

**Branch**: `codex/041-governance-full-react-parity-and-jinja-removal` | **Date**: 2026-05-06 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/041-governance-full-react-parity-and-jinja-removal/spec.md`

## Summary

Complete React parity for governance browser surfaces introduced in Spec 031, then remove governance-owned Jinja rendering. The implementation will extend backend-owned schemas and deterministic builders for provider, prompt, profile, routing, history, model-skill config, provenance, credential diagnostic, direct-call guardrail, legacy route mapping, and safe mutation result coverage; add React panels/routes for missing create/edit/detail/history/preview/resolve states; convert old model provider, prompt, agent profile, and model-skill config browser URLs to redirects or non-Jinja safe compatibility responses; and delete only governance-owned templates after route, scanner, redaction, Auth0-shaped, local-principal, QA, and Playwright evidence passes.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode; React 19; Vite; Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing model provider services, prompt services, runtime profile/config services, ModelGateway provenance, ProviderSecretResolver, audit/redaction helpers, React admin shell/design system, generated TypeScript contracts, Testing Library, Vitest, Playwright QA runner  
**Storage**: PostgreSQL 16+ through existing provider, prompt, profile, routing, audit, gateway, provenance, and usage tables; filesystem/object storage for QA artifacts and screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, generated TypeScript drift checks, Vitest, Testing Library, Vite build, Playwright UI runner, Spec QA runner with 90 percent coverage gate  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0-shaped authorization and `AUTH_MODE=local_principal` browser QA  
**Project Type**: Full-stack admin web application inside the existing monorepo  
**Performance Goals**: Keep governance bootstrap, provider, prompt, profile, routing, history, provenance, and legacy mapping fixtures bounded; avoid unbounded tables, unbounded route scans, or background probe polling  
**Constraints**: Fail closed for auth, tenant, audit, credential, routing, redaction, direct-call guardrail, and legacy redirect uncertainty; provider/probe/credential/direct-call mutations remain platform-admin only; no raw secrets, resolved credentials, provider payloads, prompts, completions, memory, connector payloads, stack traces, local paths, or unauthorized tenant labels; no live provider, Auth0, Telegram, credential-store, connector, external tool, or direct SDK calls in local/CI validation  
**Scale/Scope**: Governance browser surfaces only: `model_providers`, `prompts`, `agent_profiles`, `model_skill_config`, and `/admin/app/governance` React parity. Later specs own skill registry, test bench, operations, channels/memberships, run UI, and global Jinja infrastructure.

## Constitution Check

- **Durable by default**: PASS. This spec changes browser/admin governance surfaces only; it does not introduce a new runtime side-effect path. Existing mutation services keep idempotency, audit, and persisted revision behavior.
- **Immutable state and memory**: PASS. Prompt/profile/provider histories remain versioned or append-only through existing services. React renders safe summaries and mutation results.
- **Contract-first coordination**: PASS. React consumes backend-owned Pydantic contracts and generated TypeScript definitions.
- **Security with development ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows are required. Local validation uses deterministic fake principals and no real external calls.
- **Operability**: PASS. Provider health, credential diagnostics, policy history, direct-call guardrail evidence, and run provenance remain visible as safe summaries.
- **Spec-driven delivery**: PASS. This plan follows the active Spec 041 artifacts and queue bookkeeping.
- **Test and documentation discipline**: PASS. Tasks will include QA docs, focused tests, generated contract checks, frontend build/tests, full Spec QA, and Playwright.
- **Clear ownership and small safe changes**: PASS. Implementation is scoped to governance backend contracts/routes, React governance components, legacy governance route handlers, templates/static deletion, docs, and tests.
- **Tenant isolation and fair scheduling**: PASS. All governance read/mutation routes remain tenant scoped and fail closed for cross-tenant access.
- **Version-pinned execution**: PASS. No workflow runtime execution changes are introduced; run provenance remains read-only evidence.
- **Secret hygiene and controlled tool access**: PASS. Credential references are labels/fingerprints/status only; probes and previews are mocked-safe in validation.
- **Tiered storage for large payloads**: PASS. Large or unsafe evidence stays as artifact references, not rendered payloads.
- **Human approval durable state**: PASS. No approval/resume behavior is changed.

## Project Structure

### Documentation (this feature)

```text
specs/041-governance-full-react-parity-and-jinja-removal/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── governance-react-parity-ui.md
│   └── governance-react-parity.openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── governance.py
├── api/
│   ├── routers/
│   │   ├── admin_react.py
│   │   ├── admin_model_providers.py
│   │   ├── admin_prompts.py
│   │   ├── admin_agent_profiles.py
│   │   └── admin_model_skill_config.py
│   ├── schemas/
│   │   └── admin_governance.py
│   └── ui/
│       ├── admin_console.py
│       ├── model_providers.py
│       └── agent_profiles.py
└── web_admin/
    ├── templates/
    │   ├── model_providers/
    │   ├── prompts/
    │   ├── agent_profiles/
    │   └── model_skill_config/
    └── static/

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/governance/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Extend the existing React admin governance domain from Spec 031 rather than adding a second governance workspace. Keep source changes in established backend schema/service/router modules and established frontend governance components. Convert legacy Jinja browser handlers in their current routers so API routes used by React remain intact.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Extend Spec 031 backend-owned governance contracts instead of inventing browser-only models.
- Use stable React governance child paths and JSON endpoints for direct-link recovery.
- Convert old browser GET routes to redirects or non-Jinja safe compatibility responses; keep backend JSON/API mutation routes used by React.
- Keep platform-admin-only provider/probe/credential/guardrail mutations enforced by backend authorization.
- Delete only governance-owned templates after route tests prove no governance browser path renders TemplateResponse.
- Retain shared Jinja infrastructure and non-governance templates until later specs.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/governance-react-parity.openapi.yaml](./contracts/governance-react-parity.openapi.yaml)
- [contracts/governance-react-parity-ui.md](./contracts/governance-react-parity-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts include active scope, authorized links, safe denied states, and cross-tenant tests.
- **Authorization**: PASS. Platform-only mutation and tenant read-only behavior are explicit in requirements and tasks.
- **Credential and prompt safety**: PASS. The plan keeps safe summaries and blocked/summarized preview outputs only.
- **No live side effects in validation**: PASS. Probes, previews, routing, resolution, and provenance are deterministic fixtures in local/CI.
- **Deletion safety**: PASS. Template/static deletion is blocked until redirects, tests, scanner evidence, docs, and Playwright pass.
- **Coverage and docs**: PASS. Validation requires QA docs, focused tests, coverage, frontend tests/build, Spec QA, and Playwright.

## Complexity Tracking

No constitution violations are introduced.
