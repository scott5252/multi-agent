# Implementation Plan: Design Review Coordinator And Iteration Loop

**Branch**: `codex/062-design-review-coordinator-and-iteration-loop` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/062-design-review-coordinator-and-iteration-loop/spec.md`

## Summary

Add a coordinator service on top of the Spec 060 design-review domain and the
existing DB-backed runtime orchestration tables. The coordinator will launch
one acyclic runtime workflow run per review round, record assignments and safe
reviewer verdicts, evaluate four-of-five or three-of-four zero-blocker quorum,
create development handoffs for approved revisions, create immutable next
revisions when changes are required, and pause for durable manual resolution
when evidence is incomplete, policy conflicts occur, or max rounds are reached.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM,
PostgreSQL 16+, existing design review service/repository/models,
`RuntimeOrchestrationRepository`, `WorkflowVersionBundle`,
`GraphExecutionService`, worker polling, audit service, pytest, Ruff, mypy  
**Storage**: Existing design-review tables and runtime orchestration tables.
No migration is planned; repository methods will update existing status fields
and create revisions using existing columns.  
**Testing**: pytest unit/contract/integration coverage, QA document validation,
`run_spec_qa.py`, Playwright smoke validation, full multi-agent curl runner  
**Target Platform**: FastAPI control plane with DB-backed runtime worker  
**Project Type**: Backend domain/runtime coordinator feature  
**Performance Goals**: Round launch and state projection use bounded queries.
Coordinator iteration never scans unbounded run history.  
**Constraints**: Workflow graphs remain acyclic. Local QA uses local-principal
auth, deterministic workflow documents, and mocked provider/model paths only.
No raw prompts, completions, provider payloads, credentials, private messages,
memory contents, unauthorized payloads, or raw tool payloads in records,
responses, logs, screenshots, or QA artifacts.  
**Scale/Scope**: One coordinator service module, small repository/service
extensions, coordinator JSON API routes, schemas, QA scripts/docs, and curl
coverage.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Durable By Default: PASS. Rounds, verdicts, quorum decisions, revisions,
  manual decisions, handoffs, runtime runs, and timeline events are durable.
- Immutable State And Memory: PASS. New revisions are append-only; prior
  revisions are not mutated.
- Contract-First Agent Coordination: PASS. Coordinator request/response schemas
  and quorum contracts gate side effects.
- Security With Practical Development Ergonomics: PASS. Local QA remains
  deterministic and no external credentials are needed.
- Operability Is A Product Requirement: PASS. State projections, audit-safe
  rationale, QA docs, and curl evidence are required.
- Spec-Driven Delivery: PASS. Work follows specify, clarify, plan, tasks,
  analyze, implement, and validation phases.
- Test And Documentation Discipline: PASS. Unit, contract, integration, QA,
  Playwright, and curl evidence are planned.
- Clear Ownership And Small Safe Changes: PASS. Changes are scoped to design
  review coordinator behavior and route contracts.
- Tenant Isolation And Fair Scheduling: PASS. Every operation requires tenant
  scope and runtime runs inherit tenant id.
- Version-Pinned Execution: PASS. Runtime launches use selected published
  workflow version bundles.
- Secret Hygiene And Controlled Tool Access: PASS. Coordinator stores only safe
  summaries, ids, digests, and artifact references.
- Tiered Storage For Large Payloads: PASS. Existing artifact references remain
  the path for large design/reviewer outputs.
- Human Approval Is Durable State: PASS. Manual decisions are durable and
  idempotent.

## Project Structure

### Documentation (this feature)

```text
specs/062-design-review-coordinator-and-iteration-loop/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── coordinator-api.md
│   └── coordinator-ui.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── admin/design_review/
│   ├── coordinator.py
│   ├── models.py
│   └── service.py
├── api/
│   ├── routers/admin_design_review.py
│   └── schemas/design_review.py
└── db/repositories/design_review.py

tests/
├── contract/test_design_review_coordinator_contracts.py
├── integration/api/test_admin_design_review_coordinator_api.py
├── integration/runtime/test_design_review_coordinator_runtime.py
└── unit/admin/design_review/test_design_review_coordinator.py

scripts/qa/
├── seed_design_review_coordinator_qa062.py
└── verify_design_review_coordinator_qa062.py
```

**Structure Decision**: Keep coordinator behavior under
`admin/design_review` because it owns design review domain state while delegating
runtime run creation to `RuntimeOrchestrationRepository`.

## Complexity Tracking

No constitution violations are expected.

## Phase 0: Research

Research covers coordinator launch idempotency, runtime run creation, quorum
policy, revision loop semantics, manual-resolution actions, redaction,
state projection, API/curl impact, and deterministic QA. Findings are recorded
in [research.md](research.md).

## Phase 1: Design And Contracts

Design outputs:

- [data-model.md](data-model.md)
- [contracts/coordinator-api.md](contracts/coordinator-api.md)
- [contracts/coordinator-ui.md](contracts/coordinator-ui.md)
- [quickstart.md](quickstart.md)

## Migration Notes

- No Alembic migration is planned for Spec 062.
- Existing design-review status fields, revision links, round workflow_run_id,
  verdicts, quorum decisions, manual decisions, and handoff tables are enough
  for coordinator state.
- If implementation discovers a missing durable field, stop and revise this
  plan before adding schema.

## Post-Design Constitution Check

The design keeps graph execution acyclic, creates one runtime run per round,
uses append-only revision records, preserves tenant scope, stores only safe
metadata and digests, and requires deterministic local QA. No new constitution
violation was introduced by Phase 1 design.
