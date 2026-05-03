# Implementation Plan: Workflow Graph Execution And Parallel Sub-Agent Runtime

**Branch**: `codex/020-workflow-graph-execution-parallel-sub-agent-runtime` | **Date**: 2026-05-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/spec.md`

## Summary

Add a durable graph execution service for published workflow bundles. The
implementation introduces a focused `runtime.orchestration.graph_execution`
module, a deterministic role executor for QA, a graph planner/scheduler, join
policy evaluation, safe output/redaction helpers, database repository methods
for run steps and bundle loading, worker integration, tests, docs, QA artifacts,
and README updates. The worker will execute claimed runs from the pinned bundle
graph, schedule independent branches in parallel waves, persist step and
timeline evidence, pause for manual resolution when required, and complete runs
with final safe structured outputs.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy
2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation,
existing workflow registry bundle summaries, runtime orchestration models,
ModelGateway boundary, model-skill config provenance, immutable memory service
contracts, audit/redaction helpers, reliability worker leases, pytest,
pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: Reuse existing runtime execution bundles, workflow runs, run steps,
checkpoint refs, handoff envelopes, side-effect intents, approval gates,
timeline events, workflow version bundles, and artifact metadata. No new table
is required for v1.
**Testing**: Unit tests for graph contracts, planner, scheduler, role executor,
join policies, redaction, and resume behavior; integration tests for database
repository methods, worker execution, Daily Intelligence Briefing, tenant
isolation, and crash-resume; docs and QA validation tests; Playwright smoke via
the generated validation plan even though no new browser UI is added.
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane app and worker
process.
**Project Type**: Multi-tenant Python web service with background workers,
server-rendered admin shell, and durable runtime orchestration.
**Performance Goals**: Schedule 50 graph nodes within 250 ms excluding model
calls; execute the Daily Intelligence Briefing mock graph under 5 seconds in
local QA; resume a partially completed 20-node graph within 500 ms; keep run
step lookup bounded by workflow_run_id and step_key.
**Constraints**: Cross-tenant bundle access fails closed. QA must not call real
external providers or tools. Inline payloads contain safe summaries only.
Resume reuses pinned bundles and existing succeeded steps. Manual resolution
enters durable paused state. No raw secrets, credential values, prompts, model
responses, tool payloads, or channel messages render inline.
**Scale/Scope**: One runtime feature slice: graph planner, join policy
evaluator, safe mock role executor, repository persistence, worker integration,
runtime/channel-safe output update, tests, QA docs, PR notes, testing
instructions, README updates, and quickstart updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Runs, steps, checkpoints, handoffs, joins, approvals, timeline events, and final output references persist before lifecycle changes complete. |
| Immutable State And Memory | PASS | Execution uses pinned published bundle data and append-mostly run evidence; resume does not mutate published definitions. |
| Contract-First Agent Coordination | PASS | Graph execution contracts, role inputs/outputs, join decisions, and handoff summaries are documented before implementation. |
| Security With Practical Development Ergonomics | PASS | Local QA uses deterministic mock execution while preserving tenant checks and safe authorization boundaries. |
| Operability Is A Product Requirement | PASS | Timeline events, step evidence, partial failures, checkpoints, and final output summaries support operations and audit inspection. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation remain traceable. |
| Test And Documentation Discipline | PASS | Tasks include tests, docs, QA docs, README updates, and coverage gate. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to runtime orchestration, worker integration, repository methods, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant id is explicit in run, bundle, step, handoff, approval, and timeline checks. |
| Version-Pinned Execution | PASS | Execution reads the run bundle and published workflow version already pinned for the run. |
| Secret Hygiene And Controlled Tool Access | PASS | QA avoids real calls; role outputs are redacted and future live gateway calls remain behind controlled boundaries. |
| Tiered Storage For Large Payloads | PASS | Inline records store summaries and references; oversized outputs use artifact references. |
| Human Approval Is Durable State | PASS | Manual resolution joins pause through durable approval/timeline evidence. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/020-workflow-graph-execution-parallel-sub-agent-runtime/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workflow-graph-execution.md
├── tasks.md
├── qa020.md
├── qa020_ui.md
├── qa020_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── runtime/
│   └── orchestration/
│       ├── graph_execution.py
│       ├── graph_redaction.py
│       └── graph_roles.py
├── db/
│   └── repositories/
│       └── runtime_orchestration.py
└── workers/
    └── orchestration.py

tests/
├── contract/
│   └── test_workflow_graph_execution_contract.py
├── integration/
│   ├── runtime/
│   │   └── test_workflow_graph_execution.py
│   └── workers/
│       └── test_orchestration_worker.py
├── performance/
│   └── runtime/
│       └── test_workflow_graph_execution_performance.py
├── unit/
│   └── runtime/
│       └── orchestration/
│           ├── test_graph_execution.py
│           ├── test_graph_redaction.py
│           └── test_graph_roles.py
└── docs/
    └── test_workflow_graph_execution_docs.py
```

**Structure Decision**: Keep graph execution inside `runtime.orchestration`
because it is runtime behavior over existing run, step, checkpoint, handoff,
approval, and timeline primitives. Keep the worker thin: claim a run, delegate
to the executor, and report the outcome.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves bundle loading, graph planning, parallel scheduling, role
execution boundaries, join policy semantics, checkpoint/resume, tenant
isolation, output redaction, and worker integration. See [research.md](./research.md).

Key decisions:

- Build a deterministic graph planner from the published bundle document and
  summary, with defensive validation before execution.
- Execute ready nodes in waves with `asyncio.gather` for independent role nodes
  while persisting one durable run step per node key.
- Use a `RoleNodeExecutor` interface and a `DeterministicRoleNodeExecutor` for
  QA; future live execution can bind ModelGateway and tool policies behind the
  same interface.
- Treat join nodes as scheduler decisions rather than model calls.
- Persist safe summaries inline and reserve artifact references for oversized
  or sensitive content.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines graph execution plans, node states,
  waves, branch results, join decisions, partial failures, and final output
  references.
- [contracts/workflow-graph-execution.md](./contracts/workflow-graph-execution.md)
  defines the internal executor contract, role-executor boundary, join policy
  contract, and timeline evidence contract.
- [quickstart.md](./quickstart.md) gives local setup, deterministic Daily
  Intelligence Briefing validation, worker execution, and QA commands.

## API And UI Surface

- No new browser-admin route is introduced.
- Existing `/runs/{run_id}/status`, `/runs/{run_id}/timeline`,
  `/runs/{run_id}/result`, `/admin/runs`, `/admin/operations`, and workflow
  bundle views should show the new runtime evidence where they already read
  runtime state.
- Worker validation is API and database driven, with a minimal browser smoke
  check in QA020 UI documentation to confirm the admin shell still opens.

## Migration Strategy

- No migration is required.
- Reuse existing `runtime_run_steps`, `runtime_checkpoint_refs`,
  `runtime_handoff_envelopes`, `runtime_side_effect_intents`,
  `runtime_approval_gates`, `runtime_timeline_events`, `runtime_workflow_runs`,
  `runtime_execution_bundles`, and `workflow_version_bundles`.
- Repository changes are additive methods over existing tables.

## Observability And Audit

- Emit timeline events for graph load, node scheduled, node started, node
  succeeded, node failed, join evaluated, manual resolution required, checkpoint
  recorded, final output persisted, run succeeded, and run failed.
- Persist safe step metadata with role key, role kind, node key, attempt,
  upstream keys, contract keys, branch summary counts, and redaction markers.
- Failures use safe reason codes and payload digests, not raw payload text.

## Documentation And Review

- Update `README.md` and `docs/quickstart.md` with the worker graph execution
  summary and QA020 validation entry.
- Add QA020 guide, QA020 UI smoke guide, non-developer QA user guide, PR review
  notes, and testing instructions.
