# Implementation Plan: Custom Workflow Test Evidence And Publish Setup

**Branch**: `codex/072-custom-workflow-test-evidence-and-publish-setup` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/072-custom-workflow-test-evidence-and-publish-setup/spec.md`

**Note**: This plan is filled for the autonomous workflow setup roadmap and uses the generated Spec 072 prompt bundle.

## Summary

Spec 072 connects the React Workflow Registry builder to the existing Agent Tests/Test Bench domain so custom workflows can define required evidence, create deterministic suites and cases for the current draft revision, launch safe evidence runs, refresh diagnostics, and block publish until backend-owned validation and current evidence both pass. The implementation will reuse existing Test Bench repositories, service methods, React components, generated schemas, and publish-gate summaries, adding workflow-context contracts and UI glue only where the current Test Bench surface cannot create or bind evidence from the workflow setup flow without copied ids.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv  
**Storage**: Existing workflow registry draft documents, workflow validation/publish gate state, Agent Test Bench suite/case/run/artifact/publication requirement tables, audit records, and object-storage artifact metadata; no new migration planned unless implementation discovers the current publication requirement records cannot bind workflow draft revision evidence durably  
**Testing**: pytest/httpx contract and integration tests, service/unit tests, generated TypeScript freshness check, Vitest/Testing Library, Playwright UI runner, QA docs validation, multi-agent curl regression  
**Target Platform**: FastAPI control-plane app with React Admin UI served by backend static assets  
**Project Type**: Web application with backend domain services and React Admin frontend  
**Performance Goals**: Workflow evidence bootstrap must use bounded tenant-scoped queries and avoid N+1 lookups for suites, cases, and recent runs in QA-sized tenants; evidence refresh should return a compact summary suitable for desktop and mobile workflow setup panels  
**Constraints**: Publish readiness, evidence freshness, tenant scope, run status, suite/case eligibility, and safe execution-mode acceptance remain backend-owned. Raw transcripts, raw prompts, completions, provider/tool payloads, credentials, local paths, stack traces, memory contents, private payloads, and unauthorized tenant labels must not render in UI, screenshots, exports, docs, logs, or audit summaries. Local QA must not call real providers, credentials, connectors, models, or external services.  
**Scale/Scope**: Spec 072 covers test evidence setup and publish gating inside workflow setup. It does not need to complete the full end-to-end setup wizard or runtime launch path, which remain Spec 073.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. Suites, cases, runs, requirements, evidence summaries, and workflow draft edits remain durable backend state with idempotency and stale conflict handling.
- **II. Immutable State And Memory**: PASS. Evidence targets immutable workflow draft revision identifiers and becomes stale when the draft changes.
- **III. Contract-First Agent Coordination**: PASS. Test cases, assertions, expected contracts, and workflow requirements are explicit backend contracts.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped route tests and local-principal Playwright QA are required.
- **V. Operability Is A Product Requirement**: PASS. Run status, diagnostics, artifact references, stale blockers, and publish readiness are visible operator surfaces.
- **VI. Spec-Driven Delivery**: PASS. Specification, plan, design artifacts, tasks, docs, and validation are required before Spec 073.
- **VII. Test And Documentation Discipline**: PASS. Plan requires backend, frontend, QA docs, Playwright, generated contract, and curl regression coverage.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Work is scoped to workflow-context evidence contracts, Test Bench adapters, React workflow setup panels, tests, docs, and QA seed data.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Suite/case/run/evidence access stays tenant-scoped and backend-authorized.
- **X. Version-Pinned Execution**: PASS. Required evidence must match the draft revision that publish will pin.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Only deterministic safe execution modes are allowed in QA and unsafe payloads are redacted.
- **XII. Tiered Storage For Large Payloads**: PASS. Large run artifacts remain referenced through artifact metadata; PostgreSQL does not store raw transcripts or blobs in this spec.
- **XIII. Human Approval Is Durable State**: PASS. No new approval/resume semantics are introduced.

## Project Structure

### Documentation (this feature)

```text
specs/072-custom-workflow-test-evidence-and-publish-setup/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workflow-test-evidence-publish-setup.md
├── tasks.md
├── qa072.md
├── qa072_ui.md
├── qa072_user_guide.md
└── .env.qa072
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── api/
│   ├── routers/
│   │   ├── admin_react.py
│   │   └── admin_agent_tests.py
│   └── schemas/
│       ├── admin_workflow_builder.py
│       ├── admin_test_bench.py
│       └── agent_tests.py
├── admin/
│   ├── workflow_builder.py
│   └── workflow_registry/
│       ├── publish_gate.py
│       ├── validation.py
│       └── reference_validation.py
├── testing/agent_bench/
│   ├── react_test_bench.py
│   ├── service.py
│   └── redaction.py
└── db/repositories/
    ├── agent_tests.py
    └── workflow_registry.py

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/
│   ├── testBench/
│   └── workflows/
│       ├── WorkflowTestEvidencePanel.tsx
│       ├── workflowTestEvidence.ts
│       ├── WorkflowBuilderPage.tsx
│       ├── WorkflowPublishPanel.tsx
│       └── WorkflowValidationPanel.tsx
└── test/

tests/
├── contract/
├── integration/
└── unit/

scripts/
├── frontend/generate_admin_react_types.py
└── qa/seed_workflow_test_evidence_qa072.py
```

**Structure Decision**: Extend existing Test Bench and workflow builder modules. Do not create a second evidence service, alternate publish gate, or browser-only publish readiness path.

## Phase 0 Research

Research output is captured in [research.md](./research.md).

## Phase 1 Design

Design output is captured in [data-model.md](./data-model.md), [contracts/workflow-test-evidence-publish-setup.md](./contracts/workflow-test-evidence-publish-setup.md), and [quickstart.md](./quickstart.md).

## Post-Design Constitution Check

- **Durability and versioning**: PASS. Evidence requirements are persisted in workflow draft documents and Test Bench publication requirement records; freshness compares target revisions.
- **Tenant isolation**: PASS. All suite/case/run lookups and contextual actions require active tenant authorization and fail closed for cross-tenant records.
- **Secret and transcript hygiene**: PASS. UI contracts expose only safe summaries, counts, statuses, and opaque artifact references.
- **Testing and documentation**: PASS. Design requires QA docs, Playwright desktop/mobile journeys, focused backend/frontend tests, generated contracts, and curl review.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
