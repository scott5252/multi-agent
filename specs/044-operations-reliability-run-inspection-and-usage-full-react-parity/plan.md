# Implementation Plan: Operations, Reliability, Run Inspection, And Usage Full React Parity

**Branch**: `codex/044-operations-reliability-run-inspection-and-usage-full-react-parity` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/spec.md`

## Summary

Complete React parity for operations, reliability controls, admin run inspection,
user-facing run links, and usage analytics before deleting the bounded Jinja
templates for those domains.
Keep JSON/API routes that React uses, convert old browser-rendering routes to
authenticated React redirects or safe non-Jinja problems, preserve filters and
object ids where authorized, add deletion-grade route/scanner tests, refresh
docs/QA assets, and validate with Spec QA and Playwright.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode with Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy async ORM, operations workbench services, reliability services, run inspection services, usage analytics services, React 19, Vite, Testing Library, Vitest, generated TypeScript contracts, audit/redaction helpers  
**Storage**: Existing PostgreSQL operations/reliability/runtime/usage tables and object/filesystem artifact references; no new tables planned  
**Testing**: pytest, httpx/TestClient, Ruff, mypy, generated contract drift check, Vitest, Vite build, performance tests, QA docs validator, Spec QA, Playwright  
**Target Platform**: FastAPI admin app with Auth0 production auth and local-principal QA, served React admin UI, deterministic `multi_agent_platform_qa044` database  
**Project Type**: Full-stack web application inside the existing monorepo  
**Performance Goals**: Bounded operations summaries, run search, timeline events, dead-letter lists, usage events, and exports; no unbounded client polling or raw payload rendering  
**Constraints**: No real Auth0, Telegram, provider, credential, connector, model, or external tool calls in local/CI; no raw prompts, completions, memory, private messages, tool payloads, raw logs, stack traces, raw CSV rows, local paths, storage paths, secrets, headers, or unauthorized tenant labels in UI/docs/logs/screenshots  
**Scale/Scope**: `/admin/app/operations`, `/admin/app/channels/runs/{run_id}`, `/admin/app/usage`, React run-debug/usage export child routes, old `/admin/operations`, `/admin/reliability/ui...`, `/admin/runs...`, user-facing `/runs...`, and `/admin/usage...` browser routes, plus templates under `operations`, `reliability`, `runs`, and `usage`

## Constitution Check

- **I Durable By Default**: PASS. Reliability actions remain backend-owned, idempotent where required, and audit-recorded.
- **II Immutable State And Memory**: PASS. Run inspection and replay expose persisted references, not browser-owned state.
- **III Contract-First Agent Coordination**: PASS. React consumes Pydantic/TypeScript contracts and safe redirect records.
- **IV Security With Practical Development Ergonomics**: PASS. Auth0-shaped tests and local-principal Playwright are required.
- **V Operability Is A Product Requirement**: PASS. The whole feature is an operator-facing triage and recovery hardening step.
- **VI Spec-Driven Delivery**: PASS. Work proceeds through Spec Kit artifacts, tasks, analysis, implementation, docs, and validation.
- **VII Test And Documentation Discipline**: PASS. Requires route tests, scanners, frontend tests, QA docs, performance tests, and Spec QA.
- **VIII Clear Ownership And Small Safe Changes**: PASS. Deletes only operations/reliability/run/usage templates.
- **IX Tenant Isolation And Fair Scheduling**: PASS. Tenant-scoped summaries and denied direct links are explicit requirements.
- **X Version-Pinned Execution**: PASS. Run replay, lineage, bundle snapshots, and usage evidence remain version/reference-bound.
- **XI Secret Hygiene And Controlled Tool Access**: PASS. Reliability and replay actions expose safe summaries only.
- **XII Tiered Storage For Large Payloads**: PASS. Exports and artifacts render as references/metadata only.
- **XIII Human Approval Is Durable State**: PASS. Recovery/replay decisions remain backend policy and audit evidence.

## Project Structure

### Documentation

```text
specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── operations-react-parity-ui.md
│   └── operations-react-parity.openapi.yaml
├── checklists/
│   └── requirements.md
├── qa044.md
├── qa044_ui.md
├── qa044_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code

```text
src/multi_agent_platform/
├── api/routers/
│   ├── admin_operations.py
│   ├── reliability_controls.py
│   ├── admin_run_inspection.py
│   ├── admin_usage.py
│   ├── web_run_ui.py
│   └── admin_react.py
├── operations/
│   ├── service.py
│   └── workbench.py
├── reliability/
├── usage/
└── web_admin/templates/
    ├── operations/      # delete after redirect parity
    ├── reliability/     # delete after redirect parity
    ├── runs/            # delete after redirect parity
    └── usage/           # delete after redirect parity

frontend/admin/src/
├── components/workbench/
├── components/usage/
├── App.tsx
└── routes.tsx

tests/
├── integration/api/test_admin_operations_ui.py
├── integration/api/test_reliability_controls_ui.py
├── integration/api/test_admin_run_inspection_ui.py
├── integration/api/test_admin_usage_ui.py
├── integration/test_admin_react_routes.py
├── contract/test_admin_react_contract.py
├── performance/operations/test_workbench_queries.py
├── performance/usage/test_react_usage_queries.py
└── unit/admin/test_operations_jinja_retirement.py
```

## Phase 0: Research

Research decisions are recorded in [research.md](research.md). Main decisions:

- Redirect old operations console routes to `/admin/app/operations`.
- Redirect reliability index/breaker/dead-letter browser routes to React
  operations with active panel and safe object/filter context.
- Redirect admin run search/detail/replay/lineage browser routes to React
  operations run-debug panels, and user-facing `/runs` detail links to React
  channel run status pages.
- Redirect usage dashboard/export detail browser routes to React usage routes.
- Keep retained JSON/API routes and shared Jinja infrastructure until later
  specs.

## Phase 1: Design And Contracts

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/operations-react-parity-ui.md](contracts/operations-react-parity-ui.md)
- [contracts/operations-react-parity.openapi.yaml](contracts/operations-react-parity.openapi.yaml)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

All pre-design gates remain PASS. Redirects are not state authority, reliability
mutations remain backend-owned, run and export evidence remains reference-bound,
and deletion scope is limited to templates proven obsolete by React routes and
tests.

## Complexity Tracking

No constitution violations require complexity exceptions.
