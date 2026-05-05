# Implementation Plan: Model, Prompt, Profile, And Provider Governance

**Branch**: `codex/031-model-prompt-profile-and-provider-governance` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/031-model-prompt-profile-and-provider-governance/spec.md`

## Summary

Build an additive React governance experience at `/admin/app/governance` for model providers, credential references, prompt versions, prompt previews, runtime profiles, read-only routing previews, policy history, direct-call guardrail evidence, live credential resolution diagnostics, and run provenance. The backend remains authoritative for provider mutation boundaries, prompt/profile/routing policy, credential resolution safety, redaction, tenant scoping, audit evidence, and provenance. React consumes generated TypeScript contracts and presents guided Setup, Prompts, Profiles, Routing, Providers, and Provenance sections while preserving existing Jinja/admin API fallbacks.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing model provider services, prompt services, runtime profile/config services, ModelGateway provenance, ProviderSecretResolver, audit/redaction helpers, React admin shell, generated TypeScript contracts  
**Storage**: PostgreSQL 16+ through existing provider, prompt, profile, routing, audit, gateway, provenance, and usage tables; filesystem/object storage for QA artifacts and screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and local-principal validation  
**Project Type**: Full-stack web application inside existing monorepo  
**Performance Goals**: Keep deterministic governance bootstrap, provider, prompt/profile, routing, history, and provenance fixtures bounded; render governance sections without unbounded tables or background polling  
**Constraints**: Fail closed for auth/tenant/audit/credential/routing/direct-call uncertainty; provider mutation is platform-admin only; no raw secrets, resolved credentials, provider payloads, prompts, completions, memory, connector payloads, or unauthorized tenant labels; no live provider, Telegram, credential-store, connector, or direct SDK calls in local/CI validation  
**Scale/Scope**: One additive React domain route plus backend contracts/services, focused fixtures, docs, and validation evidence

## Constitution Check

- **Tenant isolation**: PASS. All governance contracts include active scope and deny cross-tenant catalog, prompt, profile, routing, history, and provenance access.
- **Authorization**: PASS. Provider mutation/probe/credential-reference actions are platform-admin only; read paths are tenant-authorized and tested in local-principal and Auth0-shaped modes.
- **Audit safety**: PASS. Probe, preview, resolve, routing preview, and mutation results include safe audit references and fail closed when audit persistence cannot be proven.
- **Credential safety**: PASS. Credential references are labels/fingerprints/status only; resolved values, provider tokens, and authorization headers never leave backend safety boundaries.
- **Prompt safety**: PASS. Prompt previews are fixture-backed and blocked/summarized before rendering when unsafe text appears.
- **ModelGateway-only execution**: PASS. Routing previews are read-only policy evaluations and expose direct SDK guardrail summaries without enabling browser/provider execution.
- **Operability**: PASS. The feature surfaces provider health, credential diagnostics, probe results, policy history, run provenance, and audit references; it does not introduce a new runtime execution path.
- **Deterministic QA**: PASS. Local QA uses deterministic mocked probes, previews, resolvers, routing, policy history, and provenance fixtures.

## Project Structure

### Documentation (this feature)

```text
specs/031-model-prompt-profile-and-provider-governance/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── governance.openapi.yaml
│   └── governance-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_governance.py
├── admin/
│   └── governance.py
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/governance/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/governance/test_governance_queries.py
├── unit/admin/test_governance_service.py
└── unit/api/test_admin_governance_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from Specs 026-030. Backend schemas and deterministic service builders live under `api/schemas` and `admin`; FastAPI wiring remains in `api/routers/admin_react.py`; React components live in `frontend/admin/src/components/governance`; tests extend the existing React admin contract/integration suite with focused governance unit and performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Use backend-owned governance contracts over existing model provider, prompt, profile, routing, secret resolver, gateway provenance, and audit/redaction services.
- Keep provider mutation and credential reference actions platform-admin only.
- Use explicit provider probes, fixture-safe prompt previews, profile/routing read-only previews, and bounded history/provenance filters.
- Expose direct-call guardrail evidence and local no-auth allowlist status as backend-produced safe summaries only.
- Avoid live provider, Telegram, connector, credential, and direct SDK calls in local/CI validation.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/governance.openapi.yaml](./contracts/governance.openapi.yaml)
- [contracts/governance-ui.md](./contracts/governance-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Tenant isolation**: PASS. Contracts include active scope and cross-tenant denial tests.
- **Authorization**: PASS. Plan includes dual-auth tests plus platform-admin-only mutation coverage.
- **Audit safety**: PASS. Mutations and previews include safe audit references and dependency-unavailable states.
- **Redaction**: PASS. Data model marks all rendered content as safe summaries, fingerprints, or artifact/reference IDs.
- **Provider safety**: PASS. Probes are explicit mocked actions in QA and never expose raw attempts.
- **Prompt/profile safety**: PASS. Unsafe previews are blocked/summarized before React.
- **Provenance safety**: PASS. Run provenance uses safe identifiers and authorized links, not raw runtime payloads.
- **Operability**: PASS. QA tasks cover safe diagnostics, audit references, direct-call guardrail evidence, history, and provenance rather than raw logs or payloads.

## Complexity Tracking

No constitution violations are introduced.
