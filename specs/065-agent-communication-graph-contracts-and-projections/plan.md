# Implementation Plan: Agent Communication Graph Contracts And Projections

**Branch**: `codex/065-agent-communication-graph-contracts-and-projections` | **Date**: 2026-05-09 | **Spec**: `specs/065-agent-communication-graph-contracts-and-projections/spec.md`
**Input**: Feature specification from `specs/065-agent-communication-graph-contracts-and-projections/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add backend-owned Agent Communication Graph JSON contracts and projection
services for workflow drafts and published workflow bundles. The implementation
will extend existing workflow registry schemas, graph preview helpers,
authorization checks, published bundle metadata, and generated React Admin API
contracts without adding a React canvas or new durable graph tables.

## Technical Context

**Language/Version**: Python 3.12; generated TypeScript contracts for React Admin  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, existing workflow registry services, pytest, httpx/TestClient, Ruff, mypy, uv  
**Storage**: Existing PostgreSQL workflow registry draft, revision, validation, published bundle, artifact, and sharing tables; no new migration planned  
**Testing**: pytest unit and integration tests, generated TypeScript freshness, Ruff, mypy, Spec Kit QA, Playwright smoke, multi-agent curl regression  
**Target Platform**: FastAPI control plane with local-principal Admin API validation
**Project Type**: Backend Admin JSON API and generated React Admin contract surface  
**Performance Goals**: Graph projection remains bounded to the loaded draft/version record and completes within existing Admin API request budgets for typical workflow documents  
**Constraints**: No raw prompts, completions, provider payloads, private channel messages, memory contents, credentials, authorization headers, stack traces, local file paths, or raw tool payloads in graph JSON, logs, docs, tests, or QA artifacts  
**Scale/Scope**: Design-time and published workflow graph projection only; runtime graph overlays and durable interaction evidence are deferred to Specs 067 and 068

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Durable By Default**: Graphs derive from existing durable draft revisions, validation records, and published bundle metadata; no transient in-memory graph is authoritative.
- **Immutable State And Memory**: Published graphs reflect immutable published bundle documents or safe metadata; draft graphs reflect the current durable draft revision.
- **Contract-First Agent Coordination**: Pydantic response schemas define node, edge, badge, reference, provenance, layout, and accessibility contracts before UI use.
- **Security With Practical Development Ergonomics**: Local-principal QA exercises the same workflow authorization and tenant-scope checks used by existing Admin workflow routes.
- **Operability Is A Product Requirement**: Responses include provenance, partial/empty state, validation badges, and safe summaries for later debugging surfaces.
- **Spec-Driven Delivery**: This plan, data model, contracts, tasks, QA docs, and validation manifests gate implementation.
- **Test And Documentation Discipline**: Unit, route, generated-contract, docs, Playwright, and curl regression coverage are required before Spec 066.
- **Clear Ownership And Small Safe Changes**: Changes are scoped to schemas, workflow registry projection service, workflow router methods, tests, docs, generated contracts, and curl coverage.
- **Tenant Isolation And Fair Scheduling**: Existing workflow draft/version visibility checks are reused; cross-tenant access fails closed.
- **Version-Pinned Execution**: Published graph provenance records the published workflow version and source revision metadata.
- **Secret Hygiene And Controlled Tool Access**: Graph references are safe summaries and IDs only, never secret values or raw external/tool payloads.
- **Tiered Storage For Large Payloads**: No graph payload stores or emits large blobs; artifact references remain references.
- **Human Approval Is Durable State**: Approval nodes summarize existing approval-gate metadata and do not invent manual-resolution state.

## Project Structure

### Documentation (this feature)

```text
specs/065-agent-communication-graph-contracts-and-projections/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── agent-graph-api.md
├── qa065.md
├── qa065_ui.md
├── qa065_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)
```text
src/multi_agent_platform/api/schemas/
  admin_agent_graph.py
src/multi_agent_platform/admin/workflow_registry/
  agent_graph.py
  service.py
src/multi_agent_platform/api/routers/
  admin_workflows.py
tests/unit/admin/
  test_agent_graph.py
tests/unit/api/
  test_admin_agent_graph_schemas.py
tests/integration/api/
  test_admin_agent_graph_api.py
frontend/admin/src/api/generated/
  reactAdminApi.ts
```

**Structure Decision**: Add a focused `admin_agent_graph.py` schema module and
`workflow_registry/agent_graph.py` projection service rather than expanding the
existing generic graph preview contract. Route wiring stays under
`admin_workflows.py` so draft/version authorization remains consistent with the
workflow registry API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations or planned complexity exceptions.
