# Implementation Plan: React Workflow Graph And Agent Role Builder

**Branch**: `codex/070-react-workflow-graph-and-agent-role-builder` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/070-react-workflow-graph-and-agent-role-builder/spec.md`

## Summary

Spec 070 turns the workflow builder from metadata-only editing into a browser-first workflow structure editor. The implementation will build on Spec 069's full-document save route and existing workflow graph components to add guided collection editors for roles, contracts, graph nodes, graph edges, joins, approvals, subworkflows, and layout annotations. Durable persistence remains backend-owned through the existing React workflow save action; browser controls assemble safe document changes, render equivalent graph lists, and surface backend validation/stale/idempotency results.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, PostgreSQL, React 19, Vite, `@xyflow/react`, `lucide-react`, generated TypeScript contracts  
**Storage**: Existing PostgreSQL workflow registry draft/revision tables; no new durable table planned  
**Testing**: pytest, pytest-asyncio, httpx/TestClient, Ruff, mypy, Vitest, Testing Library, Playwright, Spec QA runner, multi-agent curl regression  
**Target Platform**: FastAPI control plane plus React Admin browser UI served by the existing app  
**Project Type**: Full-stack web application inside the existing multi-agent platform repository  
**Performance Goals**: Graph editor remains responsive for common custom workflows with at least 25 nodes and 40 edges; no additional unbounded database queries on builder load/save  
**Constraints**: Backend-owned authorization, tenant scope, validation, publish readiness, redaction, and audit; no production fake records; no raw JSON setup path; no real provider, connector, Telegram, credential, or external tool calls  
**Scale/Scope**: Spec 070 covers workflow roles, contracts, topology, joins, approvals, subworkflows, and layout annotations. Prompt/profile create/publish flows remain Spec 071, and required test evidence setup remains Spec 072.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Durable By Default**: PASS. All edits persist through workflow draft revisions with Spec 069 revision and idempotency behavior.
- **II. Immutable State And Memory**: PASS. Browser state is transient; workflow draft revisions remain the source of truth.
- **III. Contract-First Agent Coordination**: PASS. Roles, contracts, nodes, edges, joins, approvals, and subworkflows remain explicit workflow document entries.
- **IV. Security With Practical Development Ergonomics**: PASS. Auth0-shaped route tests and local-principal QA remain required; no browser-only authorization.
- **V. Operability Is A Product Requirement**: PASS. Validation findings, mutation summaries, stale conflicts, screenshots, and QA evidence are planned.
- **VI. Spec-Driven Delivery**: PASS. This plan follows spec and generated roadmap artifacts.
- **VII. Test And Documentation Discipline**: PASS. Tasks will include backend, frontend, docs, Playwright, Spec QA, and curl validation.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Implementation is scoped to workflow builder modules and focused tests.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. All workflow loads/saves use existing scoped service checks.
- **X. Version-Pinned Execution**: PASS. Draft topology remains tied to workflow revisions and future publish bundles.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. UI controls store safe references and reject protected text through backend validation.
- **XII. Tiered Storage For Large Payloads**: PASS. No large artifacts are introduced; document size guardrails remain.
- **XIII. Human Approval Is Durable State**: PASS. Approval gates are authored as durable workflow document entries, not transient browser state.

## Project Structure

### Documentation (this feature)

```text
specs/070-react-workflow-graph-and-agent-role-builder/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workflow-graph-role-builder.md
├── qa070.md
├── qa070_ui.md
├── qa070_user_guide.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/workflow_builder.py
├── admin/workflow_registry/validation.py
├── api/routers/admin_react.py
├── api/schemas/admin_workflow_builder.py
└── db/repositories/workflow_registry.py

frontend/admin/src/
├── api/client.ts
├── api/generated/reactAdminApi.ts
├── components/workflows/
│   ├── WorkflowBuilderPage.tsx
│   ├── WorkflowSectionForm.tsx
│   ├── WorkflowGraphPanel.tsx
│   ├── WorkflowRoleEditor.tsx
│   ├── WorkflowContractEditor.tsx
│   ├── WorkflowTopologyEditor.tsx
│   └── WorkflowJoinApprovalEditor.tsx
└── test/workflowBuilderTestData.ts

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Use the existing React Admin workflow workspace and backend workflow builder contracts. Add focused workflow editor components under `frontend/admin/src/components/workflows/` rather than creating a second app or generic raw document editor. Backend changes should be limited to schema/projection/validation helpers needed to support typed editor controls.

## Phase 0 Research

Research outputs are captured in [research.md](./research.md). Key decisions:

- Use `@xyflow/react` already present in the admin frontend for read-oriented canvas rendering.
- Persist through Spec 069 full-document save rather than introducing patch endpoints in this spec.
- Use collection editors and keyboard-readable lists as the required editing surface; direct canvas dragging is optional.
- Keep prompt/profile authoring out of scope until Spec 071.

## Phase 1 Design

Design outputs:

- [data-model.md](./data-model.md)
- [contracts/workflow-graph-role-builder.md](./contracts/workflow-graph-role-builder.md)
- [quickstart.md](./quickstart.md)

### Post-Design Constitution Check

- **Durability**: PASS. Full-document save, revision tokens, idempotency, and stale conflict behavior remain the persistence boundary.
- **Tenant Isolation**: PASS. No client-side reference authorization; route/service checks remain required.
- **Redaction And Secret Hygiene**: PASS. Editors accept safe labels and references only; unsafe text is rejected or summarized by backend validation.
- **Accessibility And Operability**: PASS. Keyboard-readable lists and validation findings are first-class deliverables with Playwright evidence.
- **Scope Control**: PASS. Prompt/profile authoring and test evidence setup are explicitly deferred to Specs 071 and 072.

## Complexity Tracking

No constitution violations are introduced. No new project, storage system, runtime engine, or external side-effect path is required.
