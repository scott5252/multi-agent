# Implementation Plan: Design Reviewer Template, Test Bench, And Publish Gates

**Branch**: `codex/064-design-reviewer-template-test-bench-and-publish-gates` | **Date**: 2026-05-08 | **Spec**: `specs/064-design-reviewer-template-test-bench-and-publish-gates/spec.md`
**Input**: Feature specification from `specs/064-design-reviewer-template-test-bench-and-publish-gates/spec.md`

## Summary

Add an explicit tenant-scoped Design Reviewer Council template installation
surface that creates or reuses a workflow draft, attaches required Agent Test
Bench evidence, records safe deterministic and model-backed safe-mode evidence,
and evaluates existing workflow publish gates for the current draft revision.
The Admin design-review workspace will expose the live template setup state and
installation action without inventing sample review sessions or handoffs.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, React 19, Vite, Vitest, Testing Library, Playwright, pytest, Ruff, mypy, uv  
**Storage**: Existing PostgreSQL workflow registry, Agent Test Bench, audit, tenant, and design-review tables  
**Testing**: pytest, httpx/TestClient, Vitest, TypeScript typecheck, Playwright, Spec Kit QA runner, multi-agent curl test  
**Target Platform**: FastAPI control plane with React admin UI and local-principal QA  
**Project Type**: Backend admin API plus React admin workspace  
**Performance Goals**: Template state bootstrap remains bounded to one tenant-scoped lookup set; install action completes within the local QA request timeout  
**Constraints**: No raw secrets, prompts, completions, provider payloads, private messages, memory contents, unauthorized payloads, or external tool payloads in UI/API/QA artifacts  
**Scale/Scope**: One canonical council template per tenant for this feature; no cross-tenant shared template catalog

## Constitution Check

- **Durable By Default**: Installation persists workflow draft, test suite, required evidence, run evidence, audit events, and publish-gate state through existing durable services.
- **Immutable State And Memory**: Workflow draft revisions and Test Bench runs remain immutable; install replays reuse records instead of mutating evidence history.
- **Contract-First Agent Coordination**: Template graph, role outputs, evidence responses, and Admin envelope contracts are documented before implementation.
- **Security With Practical Development Ergonomics**: Local-principal QA still exercises authorization, tenant scope, audit, and denial paths.
- **Operability Is A Product Requirement**: Audit events, evidence summaries, publish-gate status, and QA diagnostics are explicit outputs.
- **Spec-Driven Delivery**: Spec, plan, data model, contracts, tasks, QA docs, and validation manifest are required before completion.
- **Test And Documentation Discipline**: Focused backend/frontend tests, QA docs, quickstart, Playwright, and curl regression are required.
- **Clear Ownership And Small Safe Changes**: Work is scoped to design-review template services, admin routes, workspace state, tests, QA, and curl coverage.
- **Tenant Isolation And Fair Scheduling**: Every route and service call receives tenant context and fails closed for mismatches.
- **Version-Pinned Execution**: Required evidence targets a specific workflow draft revision and cannot satisfy newer revisions.
- **Secret Hygiene And Controlled Tool Access**: Safe-mode model-backed evidence uses governed boundaries without persisting raw provider data.
- **Tiered Storage For Large Payloads**: Evidence and UI expose safe summaries and artifact references only.
- **Human Approval Is Durable State**: Manual-resolution and blocking outcomes are represented in evidence and existing coordinator state.

## Project Structure

### Documentation (this feature)

```text
specs/064-design-reviewer-template-test-bench-and-publish-gates/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── template-api.md
│   └── template-ui.md
├── qa064.md
├── qa064_ui.md
├── qa064_user_guide.md
├── pr_notes.md
└── tasks.md
```

### Source Code (repository root)

```text
src/multi_agent_platform/admin/design_review/
  template.py
  react_workspace.py
src/multi_agent_platform/api/routers/
  admin_design_review.py
src/multi_agent_platform/api/schemas/
  design_review.py
  admin_design_review_workspace.py
frontend/admin/src/components/designReviews/
tests/unit/admin/design_review/
tests/integration/api/
scripts/qa/
```

**Structure Decision**: Extend the existing design-review domain and Admin
workspace created by Specs 060-063. No new database migration is planned unless
implementation discovers a missing durable field in workflow registry or Agent
Test Bench state.

## Phase 0 Research

See `research.md`.

## Phase 1 Design

See `data-model.md`, `contracts/template-api.md`, `contracts/template-ui.md`,
and `quickstart.md`.

## Phase 2 Tasks

See `tasks.md`.

## Complexity Tracking

No constitutional violations or planned complexity exceptions.
