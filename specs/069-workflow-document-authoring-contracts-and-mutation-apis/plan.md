# Implementation Plan: Workflow Document Authoring Contracts And Mutation APIs

**Branch**: `codex/069-workflow-document-authoring-contracts-and-mutation-apis` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/069-workflow-document-authoring-contracts-and-mutation-apis/spec.md`

## Summary

Extend the existing React Admin workflow builder JSON contract so browser saves can submit and reload the complete `WorkflowDraftDocument`, not only name and description. The implementation will add backend-owned editor state, section summaries, full document save request/result contracts, stale conflict recovery, validation finding mapping, redaction-safe audit summaries, generated TypeScript types, API client helpers, focused backend/frontend tests, curl coverage, and QA docs. Full document save is required for Spec 069; section patches remain optional only if they reuse the same validation, revision, idempotency, authorization, and audit path.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, Alembic, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, Playwright, existing Admin React shell/workflow builder/generated type pipeline  
**Storage**: Existing workflow registry lineages, drafts, revisions, validation, artifact, audit, sharing, and test-bench tables remain authoritative; add revision-level idempotency fingerprint fields only if required to make React document saves durable across process restarts  
**Testing**: pytest unit/contract/integration tests for schemas, routes, repository/service behavior, tenant isolation, stale conflicts, idempotency, validation, redaction, generated contract checks, Vitest/client type coverage, QA docs, Playwright smoke, and multi-agent curl regression  
**Target Platform**: FastAPI-served React Admin UI with deterministic `AUTH_MODE=local_principal` QA and Auth0-shaped route tests  
**Project Type**: Full-stack Admin web application with durable workflow registry persistence  
**Performance Goals**: Full document editor load/save for bounded QA documents returns within one second locally; payload guard rejects documents above the documented request limit without partial persistence  
**Constraints**: Backend-owned authorization, tenant scope, validation, publish readiness, redaction, and audit; no production fake records; no external provider, Telegram, connector, model, or credential calls; no raw prompt bodies in workflow diagnostics; existing lower-level workflow APIs remain supported  
**Scale/Scope**: Spec 069 covers contracts, mutation endpoints, generated types, API client helpers, validation/audit/idempotency behavior, focused tests, curl coverage, and docs. Graph controls, prompt/profile creation, evidence setup, and the finished wizard are Specs 070 through 073.

## Constitution Check

- Durable By Default: Pass. Full saves use revision tokens and durable idempotency fingerprints so repeated or interrupted browser saves do not create duplicate revisions.
- Immutable State And Memory: Pass. Workflow draft revisions remain append-only immutable records; the browser never becomes the source of truth.
- Contract-First Agent Coordination: Pass. Pydantic contracts and generated TypeScript types define the workflow editor boundary before React controls depend on it.
- Security With Practical Development Ergonomics: Pass. Auth0-shaped tests and local-principal QA exercise the same tenant/platform authorization behavior.
- Operability Is A Product Requirement: Pass. Save results, validation findings, stale conflicts, and audit summaries are safe and actionable for operators.
- Spec-Driven Delivery: Pass. Spec, clarifications, plan, tasks, analysis, implementation, docs, and validation are tracked under Spec 069.
- Test And Documentation Discipline: Pass. Plan includes backend, contract, frontend, docs, Playwright, curl, and generated type validation.
- Clear Ownership And Small Safe Changes: Pass. Changes are scoped to workflow builder contracts/routes/service adapters/generated types and focused tests.
- Tenant Isolation And Fair Scheduling: Pass. Tenant/platform scope is explicit on every draft mutation and reference check; cross-tenant saves fail closed.
- Version-Pinned Execution: Pass. Authoring revisions remain the input to later immutable published bundles and runtime pins.
- Secret Hygiene And Controlled Tool Access: Pass. Workflow save diagnostics store references and safe summaries only; raw secrets, credentials, provider payloads, completions, memory, and raw tool data are blocked.
- Tiered Storage For Large Payloads: Pass. Oversized documents are rejected; large artifacts remain references through existing artifact storage.
- Human Approval Is Durable State: Pass. Approval gates can be edited as document definitions, while runtime approval/resume state remains separate durable runtime state.

## Project Structure

### Documentation

```text
specs/069-workflow-document-authoring-contracts-and-mutation-apis/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workflow-document-authoring.md
├── qa069.md
├── qa069_ui.md
├── qa069_user_guide.md
├── .env.qa069
└── tasks.md
```

### Source Code

```text
alembic/versions/
└── 0023_workflow_document_authoring_idempotency.py

src/multi_agent_platform/
├── api/schemas/
│   ├── admin_workflow_builder.py
│   └── workflow_registry.py
├── api/routers/
│   ├── admin_react.py
│   └── admin_workflows.py
├── admin/
│   ├── workflow_builder.py
│   └── workflow_registry/
│       ├── service.py
│       ├── validation.py
│       └── observability.py
├── db/models/
│   └── workflow_registry.py
└── db/repositories/
    └── workflow_registry.py

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/workflows/
│   ├── WorkflowBuilderPage.tsx
│   ├── WorkflowSectionForm.tsx
│   └── WorkflowSectionForm.test.tsx
└── test/workflowBuilderTestData.ts

scripts/
├── frontend/generate_admin_react_types.py
└── qa/seed_workflow_document_authoring_qa069.py

tests/
├── contract/
│   ├── test_admin_react_contract.py
│   └── test_workflow_builder_contract.py
├── integration/
│   └── test_admin_react_routes.py
└── unit/admin/
    ├── test_workflow_builder_service.py
    └── test_workflow_registry_service.py
```

**Structure Decision**: Keep the canonical authoring document in `api/schemas/workflow_registry.py` and expose React editor projections in `api/schemas/admin_workflow_builder.py`. The React route stays under the existing `/admin/app/workflows/...` family and delegates persistence to the workflow registry service so lower-level `/admin/workflows/...` APIs continue to use the same durable registry path.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Additive revision idempotency fields | Durable full-document save idempotency must survive API process restarts and reject key reuse with different scope or payload | In-memory idempotency or stale-revision heuristics cannot prove same-key/different-payload misuse after restart |

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design

See [data-model.md](data-model.md), [contracts/workflow-document-authoring.md](contracts/workflow-document-authoring.md), and [quickstart.md](quickstart.md).

## Phase 2: Task Planning

See [tasks.md](tasks.md).

## Risk And Mitigation

- **Schema name collision**: Existing simplified React `WorkflowDraftDocument` conflicts with canonical registry `WorkflowDraftDocument`. Mitigate by renaming the React projection to `WorkflowDraftEditorSummary` or introducing explicit `WorkflowDocumentEditorState` names while preserving generated compatibility where tests require it.
- **Duplicate saves**: Persist idempotency scope hash and payload hash on saved revisions; replay exact duplicates and reject mismatches.
- **Overly broad route change**: Keep lower-level `/admin/workflows/drafts/{id}` save behavior intact and extend only the React-facing save wrapper plus shared service helpers.
- **Sensitive data exposure**: Reuse safe text validators, redaction markers, safe problem details, audit redaction, and tests that scan responses/docs/screenshots for protected markers.
- **Invalid document persistence**: Run Pydantic validation and workflow registry validation before saving a new revision; convert validation errors into section/field findings.
- **Payload size abuse**: Preserve bounded payload checks and add focused oversized document tests.
