# Implementation Plan: Durable Agent Interaction Evidence And Replay Graph

**Branch**: `codex/068-durable-agent-interaction-evidence-and-replay-graph` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/068-durable-agent-interaction-evidence-and-replay-graph/spec.md`

## Summary

Add a minimal durable runtime interaction evidence table and use it to enrich the Spec 067 runtime agent graph with replay references. The implementation records safe, idempotent source/target interaction summaries during graph execution, exposes them through the existing Admin run graph route, refreshes generated React contracts, and reuses `AgentGraphPanel` in the operations workbench for replay detail without storing raw prompts, completions, provider responses, credentials, memory, private payloads, raw tool outputs, or stack traces.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, Alembic, PostgreSQL 16+, React 19, Vite, Vitest, Testing Library, `@xyflow/react`, existing Admin Shell and operations workbench graph components  
**Storage**: Additive Alembic migration for `runtime_interaction_evidence`; existing workflow run, run step, timeline, handoff, approval, side-effect, artifact, and execution bundle records remain authoritative  
**Testing**: pytest repository/service/runtime/projection/API tests; Vitest graph/workbench tests; Playwright desktop/mobile replay validation; QA document validation, Spec QA, and multi-agent curl regression  
**Target Platform**: FastAPI-served React Admin UI with deterministic local-principal QA  
**Project Type**: Full-stack Admin web application with runtime orchestration persistence  
**Performance Goals**: Replay-enriched graph for seeded QA runs returns within one second; replay evidence lists remain readable on desktop and mobile  
**Constraints**: Additive only, tenant-scoped, idempotent, read-only UI, no external calls, no raw protected content, fail-closed authorization, no production fake data  
**Scale/Scope**: One durable interaction table, repository/service helpers, graph execution instrumentation, runtime graph projection updates, generated contracts, workbench UI reuse, QA/curl coverage

## Constitution Check

- Durable By Default: Pass. Interaction evidence is durable, tenant-scoped, and replayable.
- Immutable State And Memory: Pass. Records are append-oriented and idempotent; no memory contents are stored.
- Contract-First Agent Coordination: Pass. Runtime graph contract gains explicit replay references and generated TypeScript types.
- Security With Practical Development Ergonomics: Pass. Local-principal QA exercises authz and redaction deterministically.
- Operability Is A Product Requirement: Pass. Replay evidence improves run inspection and incident review.
- Spec-Driven Delivery: Pass. Specification, clarifications, plan, tasks, analysis, implementation, docs, and validation are tracked under Spec 068.
- Test And Documentation Discipline: Pass. Plan includes backend, frontend, docs, Playwright, and curl regression.
- Clear Ownership And Small Safe Changes: Pass. Persistence, repository, execution instrumentation, projection, and UI details are scoped to runtime interaction evidence.
- Tenant Isolation And Fair Scheduling: Pass. Repository and route queries require tenant scope; cross-tenant requests fail closed.
- Version-Pinned Execution: Pass. Evidence provenance links to workflow run and execution bundle context.
- Secret Hygiene And Controlled Tool Access: Pass. Structured metadata is redacted and digested before persistence.
- Tiered Storage For Large Payloads: Pass. Artifact references are IDs/metadata only; blobs stay in existing storage.
- Human Approval Is Durable State: Pass. Approval pause/resume and manual-resolution interactions are recorded as safe evidence.

## Project Structure

### Documentation

```text
specs/068-durable-agent-interaction-evidence-and-replay-graph/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interaction-replay-graph.md
├── qa068.md
├── qa068_ui.md
├── qa068_user_guide.md
├── .env.qa068
└── tasks.md
```

### Source Code

```text
alembic/versions/
└── 0022_runtime_interaction_evidence.py

src/multi_agent_platform/
├── db/models/
│   ├── runtime_orchestration.py
│   └── __init__.py
├── db/repositories/
│   └── runtime_orchestration.py
├── runtime/orchestration/
│   ├── graph_execution.py
│   └── interaction_evidence.py
├── operations/
│   └── runtime_agent_graph.py
└── api/schemas/
    └── admin_agent_graph.py

frontend/admin/src/
├── api/generated/reactAdminApi.ts
├── components/workflows/AgentGraphPanel.tsx
├── components/workbench/RuntimeAgentGraphPanel.test.tsx
└── test/workbenchTestData.ts

scripts/
├── frontend/generate_admin_react_types.py
└── qa/seed_runtime_interaction_evidence_qa068.py
```

**Structure Decision**: Keep persistence in the existing runtime orchestration model/repository because evidence belongs to workflow runs and worker retry/resume behavior. Keep graph replay projection in `operations/runtime_agent_graph.py` so the Admin route remains a single backend-owned graph source.

## Complexity Tracking

No constitution violations require complexity exceptions.

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design

See [data-model.md](data-model.md), [contracts/interaction-replay-graph.md](contracts/interaction-replay-graph.md), and [quickstart.md](quickstart.md).

## Phase 2: Task Planning

See [tasks.md](tasks.md).

## Risk And Mitigation

- **Duplicate evidence on retry/resume**: deterministic idempotency keys and repository replay behavior.
- **Sensitive payload persistence**: use `redact_graph_value`, safe text truncation, classification labels, and digest metadata before persistence.
- **Graph overclaiming**: mapped interactions attach to existing topology edges only; unmapped evidence appears in partial provenance.
- **Migration risk**: additive table only, no destructive migration, downgrade drops only the new table.
