# Implementation Plan: Agent And Workflow Test Bench

**Branch**: `codex/015-agent-workflow-test-bench` | **Date**: 2026-05-02 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/015-agent-workflow-test-bench/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a governed agent and workflow test bench for platform and tenant admins.
The implementation introduces tenant-scoped suites, cases, assertions, durable
test runs, run-step diagnostics, artifact metadata, and publication gate
evidence. It reuses the existing FastAPI admin application, server-rendered
admin shell, Auth0/local-principal authorization, SQLAlchemy async storage,
model gateway test-bench metadata, runtime side-effect safety patterns,
workflow registry publish gate summary fields, redaction helpers, filesystem
artifact storage, and audit/debugging services.

The first implementation focuses on deterministic and safe local QA paths:
mock model, mock tools, mocked real-gateway execution, blocked tool side
effects, evaluator assertions with mocked provider output, redacted evidence,
usage summaries marked as test mode, browser result pages, and publish-gate
checks. Approved real dependency probes are represented by policy and audit
metadata, but validation must not require real credentials or production
hosts.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test
mode, existing workflow registry services/schemas/templates, prompt library,
agent runtime profile services, model provider gateway, model_skill_config
resolver and policy models, skill registry policy/readiness models, audit and
redaction helpers, filesystem/object storage providers, prometheus-client,
pytest, pytest-asyncio, httpx, Ruff, mypy, uv  
**Storage**: New additive PostgreSQL tables for `agent_test_suites`,
`agent_test_cases`, `agent_test_assertions`, `agent_test_runs`,
`agent_test_run_steps`, `agent_test_artifacts`, and
`agent_test_publication_requirements`. Large fixtures, transcripts, and
result artifacts use object/filesystem storage with PostgreSQL metadata and
checksums.  
**Testing**: pytest unit tests for schemas, models, repository behavior,
sandbox execution, assertion evaluation, redaction, publish-gate summaries,
and UI view models; pytest-asyncio/httpx integration tests for API and admin
UI flows, authorization, tenant isolation, publish gate behavior, and mocked
provider execution; docs tests for QA guides and README updates; Playwright
validation through the configured QA runner.  
**Target Platform**: Linux web service containers plus local macOS/Linux
development, served through the existing FastAPI control-plane application,
admin shell, local-principal test login, PostgreSQL, and worker process.  
**Project Type**: Multi-tenant Python web service with JSON admin APIs,
server-rendered admin UI, durable runtime support, and background workers.  
**Performance Goals**: Suite/case list pages p95 <= 250 ms for 100 suites and
1,000 cases in a tenant; run creation p95 <= 500 ms; mock-mode suite with two
cases completes under 30 seconds in QA; run detail page p95 <= 500 ms for 100
steps excluding artifact downloads; publish-gate check p95 <= 200 ms for up to
10 required suites.  
**Constraints**: Cross-tenant access fails closed; raw fixtures, raw prompt
bodies, raw provider messages, raw credential values, raw tool payloads, and
large artifacts never render inline. Safe modes must block unapproved side
effects. Real external calls are forbidden in QA and require explicit approved
probe metadata outside QA. Test usage is marked as test mode and not mixed
with production workflow usage. PostgreSQL stores metadata only for large
payloads. Publication evidence must be tied to the candidate target version and
must reject stale runs.  
**Scale/Scope**: One full vertical feature slice: database models and
migration, repository, service/sandbox execution, schemas, API router,
server-rendered UI pages, publish-gate integration helper, tests, QA docs,
manual QA user guide, PR notes, testing instructions, and README updates.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Runs, run steps, side-effect decisions, usage summaries, gate evidence, and artifact metadata are persisted. Mock and gateway execution use idempotency keys. Interrupted runs resume from persisted status. |
| Immutable State And Memory | PASS | Published workflow/prompt/profile/skill references remain immutable; runs and steps are append-mostly result records; suite changes use revision tokens and audit records. |
| Contract-First Agent Coordination | PASS | API schemas, UI contracts, assertion contracts, target reference contracts, and publish-gate semantics are documented before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal paths reuse existing policy checks with deterministic QA principals. Security shortcuts are local-only and explicit. |
| Operability Is A Product Requirement | PASS | Run traces, side-effect blocks, usage, latency, redaction outcomes, artifact references, and audit events are first-class result fields. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, tasks, QA docs, and implementation remain traceable. |
| Test And Documentation Discipline | PASS | Test-first tasks cover CRUD, execution modes, assertions, redaction, tenant isolation, publish gating, docs, and coverage >= 90 percent. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to `testing/agent_bench`, `agents`, `api`, `db`, `admin/workflow_registry`, templates, migration, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Every suite, case, run, artifact, and gate requirement carries tenant scope; run admission is prepared for quota/fairness hooks. |
| Version-Pinned Execution | PASS | Runs store target type/id/version plus prompt, profile, provider, model, skill, and workflow bundle references used during execution. |
| Secret Hygiene And Controlled Tool Access | PASS | Test runs use mock/mocked-provider modes by default; real probes require approved metadata; no raw secret value is accepted or rendered. |
| Tiered Storage For Large Payloads | PASS | Fixtures/transcripts/artifacts over inline-safe limits are stored through artifact storage with metadata in PostgreSQL. |
| Human Approval Is Durable State | PASS | Approved real dependency probe mode and publication gate requirements are persisted admin decisions with audit evidence. |

Post-Phase-1 re-check: research, data model, contracts, and quickstart keep all
constitution gates in `PASS` status. No exceptions are required.

## Project Structure

### Documentation (this feature)

```text
specs/015-agent-workflow-test-bench/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── agent-test-bench.openapi.yaml
│   └── admin-agent-test-bench-ui.md
├── tasks.md
├── qa015.md
├── qa015_ui.md
├── qa015_user_guide.md
├── pr-review-notes.md
└── testing-instructions.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── testing/
│   └── agent_bench/
│       ├── __init__.py
│       ├── assertions.py
│       ├── models.py
│       ├── redaction.py
│       ├── sandbox.py
│       └── service.py
├── agents/
│   └── test_bench.py
├── admin/
│   └── workflow_registry/
│       └── publish_gate.py
├── api/
│   ├── routers/
│   │   └── admin_agent_tests.py
│   ├── schemas/
│   │   └── agent_tests.py
│   └── ui/
│       └── agent_tests.py
├── db/
│   ├── models/
│   │   └── agent_tests.py
│   └── repositories/
│       └── agent_tests.py
└── web_admin/
    └── templates/
        └── agent_tests/
            ├── index.html
            ├── suite_detail.html
            ├── suite_form.html
            ├── case_form.html
            ├── run_detail.html
            └── components/
                ├── assertions.html
                ├── gate_status.html
                ├── result_summary.html
                └── trace_steps.html

alembic/
└── versions/
    └── <revision>_add_agent_workflow_test_bench.py

tests/
├── contract/
│   └── test_agent_test_bench_contract.py
├── integration/
│   ├── api/
│   │   ├── test_admin_agent_tests_api.py
│   │   └── test_admin_agent_tests_ui.py
│   └── db/
│       └── test_agent_tests_migration.py
├── unit/
│   ├── api/
│   │   ├── test_agent_test_schemas.py
│   │   └── test_agent_test_ui_models.py
│   ├── db/
│   │   └── test_agent_tests_models.py
│   └── testing/
│       └── agent_bench/
│           ├── test_assertions.py
│           ├── test_redaction.py
│           ├── test_sandbox.py
│           └── test_service.py
└── docs/
    └── test_agent_test_bench_docs.py
```

**Structure Decision**: Add a focused `testing.agent_bench` domain package for
bench semantics and keep API/UI/database adapters thin. Reuse the existing
admin shell and publish gate helper rather than creating a separate frontend or
workflow compiler path.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations or complexity exceptions are required.

## Phase 0 Research Summary

Research resolves safe execution, artifact storage, assertions, evaluator
strategy, publication gates, and tenant isolation. See [research.md](./research.md).

Key decisions:

- Model test bench execution as a safe sandbox service with explicit safe modes
  and side-effect decisions recorded per run step.
- Use deterministic mock outputs for default QA and a mocked provider adapter
  for real-gateway tests; real dependency probes require persisted approval
  metadata and are not used by validation.
- Store only safe summaries inline; large fixtures, transcripts, and artifacts
  go through existing storage providers with checksums and retention metadata.
- Represent deterministic assertions as typed path/comparator checks and
  evaluator assertions as governed gateway invocations with redacted input and
  mocked-provider test behavior.
- Integrate publication gating through required suite summaries tied to current
  target version evidence.

## Phase 1 Design And Contracts

Design artifacts produced by this plan:

- [data-model.md](./data-model.md) defines suites, cases, assertions, runs,
  run steps, artifacts, publication requirements, states, validation rules, and
  tenant boundaries.
- [contracts/agent-test-bench.openapi.yaml](./contracts/agent-test-bench.openapi.yaml)
  defines the JSON admin API for suite/case CRUD, run creation/detail/listing,
  and publish-gate evaluation.
- [contracts/admin-agent-test-bench-ui.md](./contracts/admin-agent-test-bench-ui.md)
  defines the server-rendered admin routes, forms, result pages, and redaction
  behavior.
- [quickstart.md](./quickstart.md) gives local setup and QA validation flows.

## API And UI Surface

- API routes live under `/admin/agent-tests`.
- UI routes live under `/admin/agent-tests/ui`.
- All API and UI routes require an authenticated local-principal/Auth0
  principal with platform-admin or tenant-admin role, except auditor-safe result
  views where policy allows read-only access.
- Navigation adds an Admin Console entry for "Agent Tests" with tenant scope.
- The validation plan uses `/admin/agent-tests/ui` for browser screenshots.

## Migration Strategy

- Add only new tables and indexes; do not mutate existing feature tables.
- Use JSONB for assertion definitions, fixture summaries, expected contract
  shapes, run metadata, usage summaries, and safe diagnostics where the shape is
  intentionally extensible.
- Add tenant, target, status, and current-evidence indexes to keep list and gate
  checks fast.
- Migration downgrade drops only the new tables.

## Observability And Audit

- Audit records are emitted for suite/case creation and update, run creation,
  safe mode selection, side-effect blocking, run finalization, redaction
  outcomes, artifact creation, and publication gate decisions.
- Metrics include run counts by mode/status, assertion pass/fail counts,
  blocked side effects, gate blocked/ready counts, and execution latency.
- Result pages expose trace IDs and run IDs suitable for log correlation.

## Documentation And QA

- Generate `qa015.md`, `qa015_ui.md`, `.env.qa015`, and
  `qa015_user_guide.md` with copy/paste local QA steps.
- Add `pr-review-notes.md`, `testing-instructions.md`, README updates, and
  docs tests.
- Validation uses the repo quality gates plus generated QA scripts from
  `validation.yml`.
