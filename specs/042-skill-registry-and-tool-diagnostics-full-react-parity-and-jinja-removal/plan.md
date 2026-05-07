# Implementation Plan: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

**Branch**: `codex/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal` | **Date**: 2026-05-06 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/spec.md`

## Summary

Complete deletion-grade React parity for the skill registry and SkillExecutionGateway diagnostics surfaces from Spec 032, then remove skill-owned Jinja rendering. The implementation will extend existing backend-owned skill lifecycle schemas/builders, generated TypeScript contracts, React skill components, route coverage, legacy route mapping, safe mutation result handling, upload precedence, revision/stale conflict behavior, explicit smoke/diagnostic refresh actions, and redaction checks. Old `/admin/skill-registry/ui/*` and `/admin/skill-execution/ui/diagnostics` browser URLs become authenticated redirects or non-Jinja safe problems only after parity evidence exists, while JSON/API routes used by React remain intact.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode; React 19; Vite; Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, existing `SkillRegistryService`, `SkillExecutionGateway`, skill lifecycle builders, credential/readiness helpers, audit/redaction helpers, React admin shell/design system, generated TypeScript contracts, Testing Library, Vitest, Playwright QA runner  
**Storage**: PostgreSQL 16+ for durable tenant, package, installation, credential, smoke-test, audit, and policy state where existing services persist it; deterministic in-memory service fixtures for current local skill lifecycle coverage; filesystem/object storage for QA artifacts and screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, generated TypeScript drift checks, Vitest, Testing Library, Vite build, Playwright UI runner, Spec QA runner with 90 percent coverage gate  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0-shaped authorization and `AUTH_MODE=local_principal` browser QA  
**Project Type**: Full-stack admin web application inside the existing monorepo  
**Performance Goals**: Keep skill dashboard/bootstrap, route mapping, audit timeline, smoke history, validation findings, and diagnostics bounded; avoid hidden background refresh loops, unbounded manifest echoes, or unbounded route scans  
**Constraints**: Fail closed for auth, tenant, manifest, credential, side-effect, connector, audit, revision, and legacy redirect uncertainty; platform-only package publication/grant/quarantine/withdrawal controls remain backend-enforced; no raw secrets, resolved credentials, provider headers, raw manifests after submit, raw tool payloads, raw smoke transcripts, stack traces, local paths, or unauthorized tenant labels; no real provider, Auth0, Telegram, credential-store, connector, external tool, or direct SDK calls in local/CI validation  
**Scale/Scope**: Skill registry and SkillExecutionGateway diagnostics browser surfaces only: `/admin/app/skills`, old `/admin/skill-registry/ui/*`, old `/admin/skill-execution/ui/diagnostics`, skill registry templates/components/static links, related navigation/docs/tests. Later specs own test bench, operations, channels/memberships, user-facing run UI, and global Jinja infrastructure.

## Constitution Check

- **Durable by default**: PASS. Browser mutations use existing service revision/idempotency semantics and safe mutation result contracts. No new runtime side effect is introduced.
- **Immutable state and memory**: PASS. Published package versions and audit events remain immutable/versioned. React renders safe snapshots, revisions, and audit references.
- **Contract-first coordination**: PASS. React consumes backend-owned Pydantic schemas and generated TypeScript definitions.
- **Security with development ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright flows are required. Local validation uses deterministic principals and mocked diagnostics.
- **Operability**: PASS. Skill readiness, smoke-test history, connector diagnostics, policy decisions, stale conflicts, and audit timeline remain visible as safe summaries.
- **Spec-driven delivery**: PASS. This plan follows the active Spec 042 artifacts and queue bookkeeping.
- **Test and documentation discipline**: PASS. Tasks will include QA docs, focused tests, generated contract checks, frontend tests/build, full Spec QA, and Playwright.
- **Clear ownership and small safe changes**: PASS. Implementation is scoped to skill lifecycle schemas/builders/routes, React skill components, legacy skill route handlers, skill templates/static deletion, docs, and tests.
- **Tenant isolation and fair scheduling**: PASS. Tenant package availability, installations, credential references, diagnostics, and audit summaries remain tenant-scoped and fail closed.
- **Version-pinned execution**: PASS. Workflow runtime execution is unchanged; binding eligibility remains a read-only preview of versioned skill availability.
- **Secret hygiene and controlled tool access**: PASS. Credential references are labels/fingerprints/status only; diagnostics and smoke tests are explicit mocked-safe actions in validation.
- **Tiered storage for large payloads**: PASS. Raw manifests, transcripts, and connector payloads are replaced by safe summaries or artifact references.
- **Human approval durable state**: PASS. No approval/resume behavior is changed.

## Project Structure

### Documentation (this feature)

```text
specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── skill-registry-react-parity-ui.md
│   └── skill-registry-react-parity.openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/
│   └── skill_lifecycle.py
├── api/
│   ├── routers/
│   │   ├── admin_react.py
│   │   ├── admin_skill_registry.py
│   │   └── admin_skill_execution.py
│   └── schemas/
│       ├── admin_skill_lifecycle.py
│       ├── admin_react.py
│       └── skill_registry.py
└── web_admin/
    └── templates/
        ├── skill_registry/
        └── skill_execution/

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/skills/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Extend the existing React skill lifecycle workspace from Spec 032 rather than creating a second skill admin page. Keep source changes in established backend skill lifecycle schema/builder/router modules and established frontend skill components. Convert legacy skill Jinja browser handlers in their current routers so API routes used by React remain available.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Extend the existing Spec 032 skill lifecycle dashboard and mutation result contracts.
- Add stable React skill child routes and backend legacy route mappings for package, version, grant, installation, configure, smoke, eligibility, audit, and diagnostics direct links.
- Convert old browser GET routes to redirects or non-Jinja safe problems; keep backend JSON/API routes consumed by React.
- Preserve upload-over-paste manifest precedence and never re-render raw manifests after submit.
- Keep all refresh actions explicit and mocked-safe in local/CI.
- Delete only skill-owned templates after route tests, scanner evidence, redaction sweeps, QA docs, and Playwright pass.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/skill-registry-react-parity.openapi.yaml](./contracts/skill-registry-react-parity.openapi.yaml)
- [contracts/skill-registry-react-parity-ui.md](./contracts/skill-registry-react-parity-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts include active scope, authorized links, safe denied states, and cross-tenant tests.
- **Authorization**: PASS. Platform-only package mutation and tenant-scoped installation behavior are explicit.
- **Credential, manifest, and connector safety**: PASS. The design renders safe summaries, fingerprints, findings, references, and blocked states only.
- **No live side effects in validation**: PASS. Diagnostics, smoke tests, and binding previews use deterministic mocked-safe behavior in local/CI.
- **Deletion safety**: PASS. Template/static deletion is blocked until redirects, tests, scanner evidence, docs, and Playwright pass.
- **Coverage and docs**: PASS. Validation requires QA docs, focused tests, coverage, frontend tests/build, Spec QA, and Playwright.

## Complexity Tracking

No constitution violations are introduced.
