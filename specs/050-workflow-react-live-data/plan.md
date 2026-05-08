# Implementation Plan: Workflow React Live Data

**Branch**: `codex/050-workflow-react-live-data` | **Date**: 2026-05-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/050-workflow-react-live-data/spec.md`

## Summary

Replace the workflow React admin deterministic builder payloads with live, authorized projections from existing workflow registry, validation, publish-gate, sharing, artifact, and test-bench evidence services. The implementation will retire fixed `qa030` workflow constants from production route responses, wire React workflow JSON endpoints to service-backed projection functions, preserve existing durable create/save/validate/restore/copy/publish behavior, add truthful empty states and backend-owned provenance, seed QA050 workflow records through durable paths, and validate empty/seeded behavior with backend tests, frontend tests, Playwright, post-UI API/database checks, and curl regression.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv  
**Storage**: Existing workflow registry, validation, version bundle, sharing, artifact, audit, and test-bench tables in PostgreSQL; no new migration planned unless implementation discovers a missing durable field  
**Testing**: pytest route/repository/contract/scanner tests, generated TypeScript contract check, Vitest/Testing Library, frontend typecheck/build, Spec QA, Playwright UI workflow flow, post-UI API/database verification, multi-agent curl regression  
**Target Platform**: FastAPI admin React JSON APIs and React admin browser UI served by built Vite assets  
**Project Type**: Multi-service web platform with backend-owned contracts and React presentation  
**Performance Goals**: Bounded workflow list queries and detail projections avoid N+1 query patterns; empty-state routes complete with only scope and shell authorization work; graph preview generation remains bounded to the selected workflow document  
**Constraints**: No production fixed `qa030` workflow IDs, fake graph nodes, fake publish evidence, fake audit references, or fake mutation success payloads; no frontend authorization or tenant-scoping decisions; no raw secrets, prompts, completions, run payloads, local paths, stack traces, or unauthorized tenant labels in route responses, screenshots, logs, exports, or docs  
**Scale/Scope**: Workflow React registry and builder domain only. Governance, skill lifecycle, test bench, membership, channel, usage, operations, and final terminology cleanup remain in Specs 051 through 059.

## Constitution Check

- **I. Durable By Default**: PASS. Workflow actions use existing durable services, revision tokens, audit records, idempotency, and publish gates; UI responses are projections over persisted state.
- **II. Immutable State And Memory**: PASS. Draft revisions and published bundles remain immutable/versioned; no memory state changes are introduced.
- **III. Contract-First Agent Coordination**: PASS. Pydantic workflow builder contracts remain authoritative and generated TypeScript contracts are updated and checked.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped backend tests and local-principal Playwright validation are required; authorization remains backend-owned.
- **V. Operability Is A Product Requirement**: PASS. Plan includes safe provenance, validation findings, publish-gate evidence, scanner evidence, QA docs, and post-UI database/API proof.
- **VI. Spec-Driven Delivery**: PASS. Spec, clarifications, plan, tasks, implementation, QA docs, and validation must complete before queue advancement.
- **VII. Test And Documentation Discipline**: PASS. Focused backend/frontend tests, generated contracts, QA docs, Playwright, and curl regression are mandatory.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Scope is limited to workflow React projection, workflow route wiring, workflow frontend live-state handling, workflow scanner mappings, QA seed helpers, docs, and validation.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Existing workflow scope guards and route tests cover tenant/platform isolation; no new queue/fairness behavior is introduced.
- **X. Version-Pinned Execution**: PASS. Published workflow bundle pinning is read and rendered; runtime execution pinning behavior is unchanged.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Safe text validators, redacted summaries, and no raw prompt/completion/secret payloads remain required.
- **XII. Tiered Storage For Large Payloads**: PASS. Artifact references remain metadata-backed and object-storage paths are never exposed as local filesystem paths.
- **XIII. Human Approval Is Durable State**: PASS. Publish/approval semantics are not weakened; no transient approval state is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/050-workflow-react-live-data/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-react-live-data-contract.md
│   └── workflow-react-live-data.openapi.yaml
├── tasks.md
├── qa050.md
├── qa050_ui.md
├── qa050_user_guide.md
└── pr_notes.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/workflow_builder.py
├── admin/workflow_registry/
│   ├── graph_preview.py
│   ├── publish_gate.py
│   ├── reference_validation.py
│   ├── service.py
│   ├── sharing.py
│   └── validation.py
├── api/routers/admin_react.py
├── api/schemas/admin_workflow_builder.py
├── admin/migration_hardening/live_data_inventory.py
├── db/repositories/workflow_registry.py
└── web_admin/static/react/

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/workflows/
├── hooks/
└── test/

tests/
├── contract/
├── integration/
├── performance/
└── unit/
```

**Structure Decision**: Keep workflow projection ownership in `src/multi_agent_platform/admin/workflow_builder.py` but convert it from deterministic builders into service-backed projection functions. Route orchestration stays in `api/routers/admin_react.py`; durable workflow logic remains in `admin/workflow_registry/service.py` and `db/repositories/workflow_registry.py`; React components remain presentational and consume generated contracts.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Research

Research decisions are recorded in [research.md](./research.md). Key outcomes:

- Use existing workflow registry services and repositories as the source of truth.
- Add a projection layer that adapts durable records to React admin contracts.
- Preserve existing React workflow route family while making each route live and scope-safe.
- Seed QA050 through durable repositories/services, not production fixture builders.
- Expand scanner mappings to make old workflow deterministic markers blocking in production surfaces.

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](./data-model.md) defines workflow live-data projection entities, state transitions, validation rules, and redaction boundaries.
- [contracts/workflow-react-live-data-contract.md](./contracts/workflow-react-live-data-contract.md) defines route behavior, empty/seeded expectations, mutation semantics, and validation evidence.
- [contracts/workflow-react-live-data.openapi.yaml](./contracts/workflow-react-live-data.openapi.yaml) documents the React workflow JSON/API surfaces touched by the spec.
- [quickstart.md](./quickstart.md) defines QA050 setup, empty/seeded checks, Playwright expectations, post-UI API/database checks, and curl regression.

## Post-Design Constitution Check

- **Durability and immutability**: PASS. The design reads existing durable workflow records and writes through existing revision/version services.
- **Contracts**: PASS. Route contracts are explicit and generated TypeScript must stay synchronized.
- **Security and tenant isolation**: PASS. Backend route tests must cover Auth0-shaped principals, local-principal QA, tenant denial, and redaction.
- **Operability and QA**: PASS. QA docs, scanner output, screenshots, post-UI evidence, and curl artifacts are required before completion.
- **Storage and secret hygiene**: PASS. No blob storage, raw secrets, raw prompt/completion content, or local paths are exposed.

## Implementation Strategy

1. Add failing route, contract, scanner, repository/projection, and frontend tests for empty workflow state, seeded live workflow state, stale conflicts, publish-gate evidence, and redaction.
2. Replace deterministic workflow builder functions with projection functions that accept workflow services/repositories and return live envelopes.
3. Wire React workflow endpoints to workflow registry, artifact, sharing, validation, and test-bench services through existing request dependencies.
4. Update React workflow pages for backend pagination/filter metadata, empty states, explicit draft/version route parameters, stale conflicts, action metadata, and live publish readiness.
5. Add QA seed helpers and docs for an empty state and an Acme seeded workflow with revisions, validation evidence, publish-gate evidence, and a published bundle.
6. Regenerate TypeScript contracts and built assets, update scanner mappings, then run focused tests, Spec QA, Playwright, post-UI API/database verification, and curl regression.
