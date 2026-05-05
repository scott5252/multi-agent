# Implementation Plan: React Agent And Workflow Test Bench

**Branch**: `codex/033-react-agent-and-workflow-test-bench` | **Date**: 2026-05-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/033-react-agent-and-workflow-test-bench/spec.md`

## Summary

Build an additive React test bench workspace for suite and case authoring, safe run launch, progress/status review, pass/fail diagnostics, redacted trace and artifact evidence, and workflow publish-gate evidence. Existing Spec 015 test bench services remain authoritative for suites, cases, runs, artifacts, audit, and gate decisions; Spec 020 graph/runtime evidence, Spec 024 publish-gate evidence, and Spec 025 ModelGateway credential behavior provide the safe runtime and gate context. React consumes generated TypeScript contracts and presents guided browser-first workflows while preserving existing Jinja/admin API fallbacks.

## Technical Context

**Language/Version**: Python 3.12, TypeScript, React 19, Vite  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, existing `testing.agent_bench` services/repositories, workflow registry publish-gate helpers, ModelGateway metadata, SkillExecutionGateway summaries, React admin shell, generated TypeScript contracts, audit/redaction helpers  
**Storage**: PostgreSQL 16+ through existing test suite, case, assertion, run, run step, artifact metadata, publish-gate, and audit records; filesystem/object storage for oversized fixtures, transcripts, artifacts, exports, and QA screenshots  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Vite build, Playwright QA runner, Spec QA runner  
**Target Platform**: Local and CI FastAPI admin web app with production Auth0 and local-principal validation  
**Project Type**: Full-stack web application inside existing monorepo  
**Performance Goals**: Keep dashboard, suite list, run list, run detail, gate evidence, and audit lists bounded; avoid client-side polling loops without backend cadence; render large artifact evidence as references only  
**Constraints**: Fail closed for auth, tenant scope, target access, suite revision, target revision, safe mode, external dependency policy, artifact access, redaction, and audit uncertainty; no raw prompts, completions, transcripts, secrets, connector payloads, storage paths, stack traces, local paths, or unauthorized tenant labels; browser-first QA must validate both passing and failing run evidence  
**Scale/Scope**: One additive React domain route plus backend contracts/adapters, focused deterministic fixtures, docs, and validation evidence

## Constitution Check

- **Durable by default**: PASS. Run launch and progress are backend-owned, idempotent, revision-bound, and resume-safe.
- **Immutable state and memory**: PASS. Suites, cases, runs, run steps, artifact metadata, and gate evidence use revision tokens, immutable run evidence, and append-only audit records.
- **Contract-first coordination**: PASS. React consumes generated contracts for dashboard, suites, cases, assertions, targets, runs, artifacts, gates, mutations, and safe problem states.
- **Security ergonomics**: PASS. Local-principal and Auth0-shaped tests are mandatory; local QA uses deterministic mock execution.
- **Operability**: PASS. The route surfaces progress, diagnostics, gateway evidence, redaction summaries, artifact retention, audit references, and publish-gate state.
- **Spec-driven delivery**: PASS. Specify, clarify, plan, tasks, analyze, implementation, docs, and validation are required before advancing.
- **Test and documentation discipline**: PASS. Plan requires focused backend/frontend tests, full coverage, QA docs, Playwright, quickstart, README, and PR notes.
- **Small safe changes**: PASS. Backend adapters, generated contracts, React components, and tests are scoped to the test bench route.
- **Tenant isolation and fair scheduling**: PASS. Active scope, target access, suite/run/artifact ownership, and cross-tenant denials are explicit.
- **Version-pinned execution**: PASS. Runs and gates bind to target revisions and reject stale evidence.
- **Secret hygiene and controlled tool access**: PASS. Default execution is mock model/mock tools; real probes require approval; raw payloads stay outside React contracts.
- **Tiered storage**: PASS. Large fixtures, transcripts, and artifacts render as metadata references with object storage backing.
- **Human approval durable state**: PASS. Probe approval and publish-gate readiness are represented as durable policy/gate evidence, not browser state.

## Project Structure

### Documentation (this feature)

```text
specs/033-react-agent-and-workflow-test-bench/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── test-bench.openapi.yaml
│   └── test-bench-ui.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/admin_react.py
│   └── schemas/admin_test_bench.py
├── testing/
│   └── agent_bench/
├── admin/
│   └── workflow_registry/
├── auth/policy.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/testBench/
├── App.tsx
├── routes.tsx
└── styles/admin.css

tests/
├── contract/test_admin_react_contract.py
├── integration/test_admin_react_routes.py
├── performance/test_bench/test_react_test_bench_queries.py
├── unit/admin/test_test_bench_react_service.py
└── unit/api/test_admin_test_bench_schema.py
```

**Structure Decision**: Use the existing React admin domain-route pattern from Specs 026-032. Backend schema/adapters live under `api/schemas` and `testing`/admin services; FastAPI wiring remains in `api/routers/admin_react.py`; React components live in `frontend/admin/src/components/testBench`; tests extend the existing React admin contract/integration suite with focused schema/service/performance coverage.

## Phase 0: Research

Research conclusions are recorded in [research.md](./research.md). Main decisions:

- Compose React contracts from existing Spec 015 test bench services, Spec 020 runtime trace evidence, Spec 024 publish-gate evidence, and Spec 025 gateway metadata.
- Use backend-owned guided suite/case forms and assertion descriptors.
- Keep default local execution in mock model/mock tools mode.
- Represent run progress through backend-owned status snapshots and optional existing SSE-compatible links.
- Store trace/artifact evidence by reference with safe summaries only.
- Bind publish-gate evidence to current target revisions and fail closed on stale evidence.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/test-bench.openapi.yaml](./contracts/test-bench.openapi.yaml)
- [contracts/test-bench-ui.md](./contracts/test-bench-ui.md)
- [quickstart.md](./quickstart.md)

## Rechecked Constitution

- **Durability**: PASS. Run and gate evidence are revision-bound and backend-owned.
- **Tenant isolation**: PASS. Data model and contracts include active scope, target access checks, suite/run/artifact ownership, and cross-tenant denial tests.
- **Authorization**: PASS. Suite/case mutation, run launch, gate mutation, and artifact access are action-scoped and dual-auth tested.
- **Audit safety**: PASS. Mutations, run launches, side-effect blocks, artifact access, redaction, and gate decisions include safe audit references.
- **Redaction**: PASS. Data model restricts rendered content to safe summaries, target labels, assertion summaries, diagnostics, references, statuses, and authorized links.
- **Tool/secret safety**: PASS. Local/CI execution uses deterministic fixtures and no live provider, connector, Telegram, or credential calls.
- **Browser-first QA**: PASS. Quickstart and tasks require Playwright workflows for suite authoring, run launch, diagnostics, artifacts, gate evidence, and cross-tenant denial.
- **Operability**: PASS. Plan covers progress, diagnostics, gateway decisions, artifact retention, audit timeline, and recovery guidance.

## Complexity Tracking

No constitution violations are introduced.
