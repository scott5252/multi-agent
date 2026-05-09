# Implementation Plan: Runtime Agent Communication Graph For Runs

**Branch**: `codex/067-runtime-agent-communication-graph-for-runs` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/067-runtime-agent-communication-graph-for-runs/spec.md`

## Summary

Add a backend-owned runtime Agent Communication Graph for workflow runs and surface it in existing Admin run inspection and operations workbench run-debug flows. The implementation will reuse Spec 065 graph contracts and projection helpers, overlay statuses and safe evidence from runtime run records, run steps, timeline events, handoffs, gateway/tool/delivery summaries, lineage, and artifacts, refresh generated TypeScript contracts, and reuse the Spec 066 `AgentGraphPanel` for read-only runtime visualization.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, React 19, Vite, Vitest, Testing Library, `@xyflow/react`, existing Admin Shell and operations workbench components  
**Storage**: Existing workflow registry, runtime execution bundle, workflow run, run step, runtime timeline, audit/debugging, artifact, gateway, tool, delivery, handoff, and operations records; no new migration planned  
**Testing**: pytest for projection/route/authorization tests; Vitest and Testing Library for runtime graph UI behavior; Playwright for desktop/mobile run graph validation; QA document validator, Spec QA runner, and multi-agent curl regression  
**Target Platform**: FastAPI-served React Admin application and local-principal deterministic QA  
**Project Type**: Full-stack Admin web application with existing backend JSON APIs and React UI  
**Performance Goals**: Runtime graph projection for seeded QA runs returns within one second and renders without text overlap at desktop and mobile widths  
**Constraints**: Read-only runtime graph, no message-level persistence, no raw prompt/completion/secret/provider/private/memory/tool/stack trace rendering, cross-tenant fail-closed behavior, no fake production run records  
**Scale/Scope**: Admin runtime graph route and operations workbench UI integration for completed, failed/retrying, paused/manual-resolution, partial, and denied run evidence

## Constitution Check

- Durable By Default: Pass. The graph is derived from existing durable runtime records and adds no transient authority.
- Immutable State And Memory: Pass. Runtime graph projection is read-only and does not mutate run, memory, or evidence records.
- Contract-First Agent Coordination: Pass. Additive runtime fields extend explicit Agent Communication Graph contracts and generated TypeScript types.
- Security With Practical Development Ergonomics: Pass. Local-principal QA exercises authorization, tenant scoping, and denial without external providers.
- Operability Is A Product Requirement: Pass. This feature directly improves run inspection and documents QA evidence, screenshots, and curl coverage.
- Spec-Driven Delivery: Pass. Specify, clarify, plan, tasks, analysis, and implementation stay traceable under Spec 067.
- Test And Documentation Discipline: Pass. Plan requires backend tests, frontend tests, QA docs, Playwright, and curl regression.
- Clear Ownership And Small Safe Changes: Pass. Changes are scoped to runtime graph projection, Admin route, generated contracts, operations workbench UI, test data, docs, and QA seed.
- Tenant Isolation And Fair Scheduling: Pass. Runtime graph requests use existing tenant scope and fail closed for unauthorized or cross-tenant runs.
- Version-Pinned Execution: Pass. Graph uses the persisted execution bundle and published workflow version evidence already pinned for a run.
- Secret Hygiene And Controlled Tool Access: Pass. Selected details render only safe summaries and references, never raw tool or provider payloads.
- Tiered Storage For Large Payloads: Pass. Artifacts are referenced through existing metadata and storage links; no blob data is embedded in the graph.
- Human Approval Is Durable State: Pass. Approval, paused, waiting, and manual-resolution states are represented from existing durable evidence only.

## Project Structure

### Documentation

```text
specs/067-runtime-agent-communication-graph-for-runs/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── runtime-agent-graph.md
├── qa067.md
├── qa067_ui.md
├── qa067_user_guide.md
├── .env.qa067
└── tasks.md
```

### Source Code

```text
src/multi_agent_platform/
├── admin/workflow_registry/
│   └── agent_graph.py
├── operations/
│   └── runtime_agent_graph.py
├── api/routers/
│   ├── admin_run_inspection.py
│   └── admin_react.py
└── api/schemas/
    └── admin_agent_graph.py

frontend/admin/src/
├── api/
│   ├── client.ts
│   └── generated/reactAdminApi.ts
├── components/workbench/
│   ├── WorkbenchPage.tsx
│   ├── WorkbenchTimeline.tsx
│   └── RuntimeAgentGraphPanel.test.tsx
├── components/workflows/
│   └── AgentGraphPanel.tsx
├── styles/admin.css
└── test/workbenchTestData.ts

scripts/frontend/
└── generate_admin_react_types.py

scripts/qa/
└── seed_runtime_agent_graph_qa067.py
```

**Structure Decision**: Put runtime projection logic under `operations/runtime_agent_graph.py` because it combines runtime, audit/debugging, gateway/tool/delivery, and workbench evidence. Keep reusable topology mapping in `admin/workflow_registry/agent_graph.py` when shared with design-time graphs.

## Complexity Tracking

No constitution violations require complexity exceptions.
