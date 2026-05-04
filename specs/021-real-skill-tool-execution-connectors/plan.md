# Implementation Plan: Real Skill Tool Execution Connectors

**Branch**: `codex/021-real-skill-tool-execution-connectors` | **Date**: 2026-05-04 | **Spec**: `specs/021-real-skill-tool-execution-connectors/spec.md`
**Input**: Feature specification from `/specs/021-real-skill-tool-execution-connectors/spec.md`

## Summary

Introduce a governed `SkillExecutionGateway` that executes approved, read-only Daily Intelligence Briefing skill tools through first-party adapters. The gateway evaluates installed skill/version eligibility, tool policy, outbound policy, tenant/credential metadata, side-effect defaults, execution mode, redaction, and contract shaping before returning normalized outputs to graph role nodes and admin diagnostics.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 templates, Pydantic v2, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+, psycopg 3, Auth0 JWT validation, local-principal admin test mode, existing skill registry services, model-skill config policy models, secret/delegated credential metadata, audit/redaction helpers, reliability controls, prometheus-client, pytest, pytest-asyncio, httpx, Ruff, mypy, uv
**Storage**: PostgreSQL for execution metadata and safe summaries; artifact storage for oversized evidence references only
**Testing**: pytest, pytest-asyncio, httpx, Playwright validation through project QA scripts
**Target Platform**: Linux service runtime with browser admin console
**Project Type**: FastAPI web service plus worker/runtime services
**Performance Goals**: Mock connector execution under 250 ms p95 per adapter in local tests; policy denial under 50 ms p95 in unit tests; diagnostics page renders under existing admin UI latency targets
**Constraints**: No raw external payloads inline; no raw secret values; no live external calls in local QA; fail-closed tenant, tool, outbound, and side-effect policy; preserve 90 percent coverage target
**Scale/Scope**: Five first-party read-only adapters for Daily Briefing; gateway contract reusable by later specs

## Constitution Check

- **I. Durable By Default**: PASS. Execution evidence includes status, policy decisions, adapter identity, and safe summaries for resume/debugging.
- **II. Immutable State And Memory**: PASS. Gateway summaries are append-only records and do not mutate memory directly.
- **III. Contract-First Agent Coordination**: PASS. Request/result schemas and adapter output schemas are defined before implementation.
- **IV. Security With Practical Development Ergonomics**: PASS. Mock fixtures are deterministic while local auth, tenant context, and policy checks remain exercised.
- **V. Operability Is A Product Requirement**: PASS. Admin diagnostics, safe audit summaries, metrics hooks, and denial reasons are in scope.
- **VI. Spec-Driven Delivery**: PASS. Spec, plan, contracts, tasks, quickstart, and validation evidence are produced before implementation.
- **VII. Test And Documentation Discipline**: PASS. TDD tasks cover contracts, policy, redaction, adapters, runtime integration, docs, and QA guide.
- **VIII. Clear Ownership And Small Safe Changes**: PASS. Work is scoped to skill execution runtime, admin diagnostics, runtime integration, docs, and tests.
- **IX. Tenant Isolation And Fair Scheduling**: PASS. Tenant context is mandatory and credential summaries are tenant checked.
- **X. Version-Pinned Execution**: PASS. Requests include installed skill package/version and policy references.
- **XI. Secret Hygiene And Controlled Tool Access**: PASS. Gateway persists only references and redacted summaries; outbound/tool policy is enforced before adapter invocation.
- **XII. Tiered Storage For Large Payloads**: PASS. Raw provider payloads are not stored inline; oversized evidence uses artifact references.
- **XIII. Human Approval Is Durable State**: PASS. No approval/resume semantics are changed by this feature.

## Project Structure

### Documentation (this feature)

```text
specs/021-real-skill-tool-execution-connectors/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── skill-execution-gateway.openapi.yaml
├── tasks.md
├── qa021.md
├── qa021_ui.md
├── qa021_user_guide.md
└── .env.qa021
```

### Source Code (repository root)

```text
src/multi_agent_platform/
├── skill_execution/
│   ├── __init__.py
│   ├── adapters.py
│   ├── fixtures.py
│   ├── gateway.py
│   ├── policies.py
│   ├── redaction.py
│   └── schemas.py
├── api/routers/
│   └── admin_skill_execution.py
├── runtime/
│   └── skill_tools.py
└── web_admin/templates/skill_execution/
    └── diagnostics.html

tests/
├── contract/
│   └── test_skill_execution_gateway_contract.py
├── integration/api/
│   └── test_admin_skill_execution_ui.py
├── unit/skill_execution/
│   ├── test_adapters.py
│   ├── test_gateway.py
│   ├── test_policies.py
│   └── test_redaction.py
└── unit/runtime/
    └── test_runtime_skill_tools.py
```

**Structure Decision**: Add a focused `skill_execution` package for the gateway boundary and adapters, a small admin router/template for diagnostics, and a runtime bridge for graph role nodes. Keep database migrations optional unless existing persistence primitives require a new table; if new persistence is needed, add an additive Alembic migration only.

## Phase 0: Research

Research conclusions are captured in `research.md` and cover gateway boundary naming, policy ordering, credential metadata handling, mock/live mode boundaries, adapter contract shapes, redaction, diagnostics, and runtime integration.

## Phase 1: Design

Design artifacts:

- `data-model.md` defines request/result, adapter, credential summary, policy decision, and diagnostic record entities.
- `contracts/skill-execution-gateway.openapi.yaml` defines admin/runtime API contracts for diagnostics and execution preview.
- `quickstart.md` defines local QA setup, mock fixture validation, API checks, and Playwright UI checks.

## Risk And Mitigation

- **Credential leakage**: Use reference-only summaries and redaction tests for token-like strings, email bodies, and query parameters.
- **Policy bypass**: Keep adapter lookup private to the gateway and test denied cases assert adapter invocation count remains zero.
- **Live call ambiguity**: Default to mock mode; live-probe requires non-local environment, policy allow, credential metadata, and outbound allow.
- **Contract drift**: Pydantic schemas and contract tests validate output shape for every adapter.
- **Admin overreach**: Diagnostics route remains protected by existing admin authorization.

## Post-Design Constitution Recheck

PASS. The design keeps tool execution contract-first, tenant-scoped, version-pinned, observable, and secret-safe. No destructive data changes or approval/resume semantics are introduced.
