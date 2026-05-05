# Implementation Plan: React Skill Registry And Tool Execution Lifecycle

**Branch**: `codex/032-react-skill-registry-and-tool-execution-lifecycle` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/032-react-skill-registry-and-tool-execution-lifecycle/spec.md`

## Summary

Build an additive React skill lifecycle workspace for platform package publication and tenant skill discovery, installation, credential configuration, smoke-test/readiness review, connector diagnostics, binding eligibility preview, quarantine/withdrawal state, and audit timeline evidence. Existing Specs 014, 014-v2, and 021 remain authoritative for package lifecycle behavior, validation, smoke tests, tenant grants, installations, credential readiness, binding eligibility, SkillExecutionGateway diagnostics, connector adapters, policy decisions, audit, object storage, redaction, and tenant isolation. React consumes generated TypeScript contracts and presents guided browser-first workflows while preserving existing Jinja/admin API fallbacks.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing `admin.skill_registry` services, existing `skill_execution` gateway/adapters/policies/redaction, React admin shell, generated TypeScript contracts, audit/redaction helpers  
**Storage**: PostgreSQL 16+ through existing skill registry, installation, audit, credential readiness, smoke-test, eligibility, and tool execution records; filesystem/object storage for QA artifacts, uploaded fixture references, and screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and local-principal validation  
**Project Type**: Full-stack web application inside existing monorepo  
**Performance Goals**: Keep React lifecycle bootstrap, package lists, installation lists, diagnostics, eligibility previews, and audit timeline bounded; avoid unbounded polling; make explicit queued refresh actions visible with safe last-known state  
**Constraints**: Fail closed for auth, tenant scope, package grants, credential policy, side-effect policy, staging-probe approval, and audit uncertainty; platform-only package publication/grants/quarantine/withdrawal; no raw manifests, credentials, connector payloads, tool outputs, stack traces, local paths, or unauthorized tenant labels; browser-first QA must avoid curl/API as the primary feature path  
**Scale/Scope**: One additive React domain route plus backend contracts/services, focused fixtures, docs, and validation evidence

## Constitution Check

- **Tenant isolation**: PASS. All lifecycle contracts carry active scope, tenant grant boundaries, and cross-tenant denial behavior.
- **Authorization**: PASS. Platform package publication/grants/quarantine/withdrawal and staging-probe approval are platform-admin only; tenant discovery/install/configuration is tenant-authorized and tested in local-principal and Auth0-shaped modes.
- **Audit safety**: PASS. Package, manifest, validation, publish, grant, install, credential, smoke-test, diagnostic, eligibility, quarantine, withdrawal, and stale-conflict actions return safe audit references.
- **Credential safety**: PASS. Credential configuration uses authorized reference options only; resolved values and authorization headers never enter React contracts.
- **Controlled tool access**: PASS. Smoke tests, connector diagnostics, and SkillExecutionGateway evidence use deterministic mocks or approved staging evidence; local/CI validation has no live connector side effects.
- **Immutable state**: PASS. Published package versions and tenant installations remain immutable; mutations use revision tokens and produce new safe state.
- **Operability**: PASS. The feature surfaces validation findings, smoke-test readiness, connector readiness, gateway diagnostics, binding eligibility, lifecycle audit timeline, and recovery guidance.
- **Deterministic QA**: PASS. QA uses deterministic package, tenant, credential, smoke-test, connector diagnostic, eligibility, quarantine, and audit fixtures with screenshot evidence.

## Project Structure

### Documentation (this feature)

```text
specs/032-react-skill-registry-and-tool-execution-lifecycle/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── skill-lifecycle.openapi.yaml
│   └── skill-lifecycle-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_skill_lifecycle.py
├── admin/
│   ├── skill_lifecycle.py
│   └── skill_registry/
├── skill_execution/
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/skills/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/skills/test_skill_lifecycle_queries.py
├── unit/admin/test_skill_lifecycle_service.py
└── unit/api/test_admin_skill_lifecycle_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from Specs 026-031. Backend schemas and deterministic aggregation live under `api/schemas` and `admin`; FastAPI wiring remains in `api/routers/admin_react.py`; React components live in `frontend/admin/src/components/skills`; tests extend the existing React admin contract/integration suite with focused skill lifecycle unit and performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Compose React contracts from existing Spec 014/014-v2 skill registry services and Spec 021 SkillExecutionGateway diagnostics.
- Use backend-owned guided wizard sections for platform publication and tenant installation.
- Keep platform-only lifecycle actions behind backend authorization.
- Use upload precedence, no raw manifest echo, explicit queued smoke-test/diagnostic refresh, and revision-token stale conflict recovery.
- Make browser-first Playwright validation the primary QA path while still retaining API/curl checks for protected contracts and setup.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/skill-lifecycle.openapi.yaml](./contracts/skill-lifecycle.openapi.yaml)
- [contracts/skill-lifecycle-ui.md](./contracts/skill-lifecycle-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Data model and contracts include active scope, tenant grants, installation ownership, and cross-tenant denial tests.
- **Authorization**: PASS. Platform-only and tenant-authorized action metadata is backend-owned and dual-auth tested.
- **Audit safety**: PASS. Mutations, previews, smoke tests, diagnostics, and lifecycle history include safe audit references.
- **Redaction**: PASS. Data model restricts rendered content to safe summaries, digests, fingerprints, references, statuses, and authorized links.
- **Tool/secret safety**: PASS. Local/CI smoke tests and diagnostics use deterministic fixtures and never expose raw credentials or connector payloads.
- **Browser-first QA**: PASS. Quickstart and tasks require Playwright workflows for package publication, tenant installation, credential configuration, smoke/readiness, eligibility, diagnostics, audit, quarantine, and redaction evidence.
- **Operability**: PASS. Plan covers readiness evidence, queued job state, connector diagnostics, gateway policy decisions, audit timeline, and recovery guidance.

## Complexity Tracking

No constitution violations are introduced.
