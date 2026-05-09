# Implementation Plan: React Agent Graph Viewer For Workflow Drafts And Versions

**Branch**: `codex/066-react-agent-graph-viewer-for-workflow-drafts-and-versions` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/spec.md`

## Summary

Add a read-only Agent Graph Viewer to the existing React Admin workflow draft and published version detail experience. The implementation will reuse the Spec 065 backend Agent Communication Graph routes, extend generated React Admin API contracts to include the graph schema, add client fetch helpers, build a reusable graph panel with React Flow plus keyboard-readable node and edge lists, and validate the UI through Vitest, Testing Library, QA docs, Playwright desktop/mobile screenshots, and curl regression review.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, React 19, Vite, Vitest, Testing Library, `@xyflow/react`, existing Admin Shell components and generated Admin API types  
**Storage**: No new storage; graph data is fetched from existing workflow draft and published-version projections  
**Testing**: pytest for generator/contract checks; Vitest and Testing Library for component behavior; Playwright for desktop/mobile browser validation; QA document validator and Spec QA runner  
**Target Platform**: FastAPI-served React Admin application and local-principal deterministic QA  
**Project Type**: Full-stack Admin web application with existing backend JSON APIs and React UI  
**Performance Goals**: Seeded QA graph renders and selection detail updates within one second; graph panel remains responsive at desktop and mobile widths  
**Constraints**: Read-only viewer, no fake production graph records, no raw prompt/completion/secret/provider/private/memory/tool payload rendering, no new migration, no new top-level navigation  
**Scale/Scope**: Workflow draft and published-version graph viewing only; runtime overlays remain for Spec 067

## Constitution Check

- Durable By Default: Pass. This spec reads durable draft and published-version graph projections and adds no transient authority.
- Immutable State And Memory: Pass. Published version graphs remain immutable backend projections; the UI does not mutate graph data.
- Contract-First Agent Coordination: Pass. Viewer consumes the explicit Spec 065 Agent Communication Graph contract and refreshes generated TypeScript types.
- Security With Practical Development Ergonomics: Pass. Backend authorization remains authoritative; local-principal QA exercises allowed, denied, and cross-tenant states.
- Operability Is A Product Requirement: Pass. QA and Playwright evidence document visible states and redaction behavior.
- Spec-Driven Delivery: Pass. Spec, plan, tasks, and analysis exist before implementation.
- Test And Documentation Discipline: Pass. Tasks include component tests, typecheck, build, QA docs, user guide, Playwright, and curl regression.
- Clear Ownership And Small Safe Changes: Pass. Changes are scoped to workflow UI components, client helpers, generated types, test data, CSS, docs, and validation.
- Tenant Isolation And Fair Scheduling: Pass. UI does not override backend tenant checks and must show safe denied state.
- Version-Pinned Execution: Not runtime-affecting; no workflow execution behavior changes.
- Secret Hygiene And Controlled Tool Access: Pass. UI renders only schema-validated safe graph text and redaction scans are required.
- Tiered Storage For Large Payloads: Not applicable; no large payload storage is added.
- Human Approval Is Durable State: Not approval-state changing; approval nodes are displayed from graph data only.

## Project Structure

### Documentation

```text
specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── agent-graph-viewer.md
├── qa066.md
├── qa066_ui.md
├── qa066_user_guide.md
├── .env.qa066
└── tasks.md
```

### Source Code

```text
frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/workflows/
│   ├── AgentGraphPanel.tsx
│   ├── AgentGraphPanel.test.tsx
│   ├── WorkflowBuilderPage.tsx
│   └── WorkflowBuilderPage.test.tsx
├── styles/admin.css
└── test/workflowBuilderTestData.ts

scripts/frontend/
└── generate_admin_react_types.py

tests/contract/
└── test_workflow_registry_contract.py
```

**Structure Decision**: Extend the existing workflow builder/detail feature under `frontend/admin/src/components/workflows` because workflow draft and version detail pages already live there and already use React Flow for graph preview.

## Complexity Tracking

No constitution violations require complexity exceptions.
