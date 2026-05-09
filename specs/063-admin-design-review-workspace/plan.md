# Implementation Plan: Admin Design Review Workspace

**Branch**: `codex/063-admin-design-review-workspace` | **Date**: 2026-05-08 | **Spec**: `specs/063-admin-design-review-workspace/spec.md`

## Summary

Add a live-data React admin workspace for design-review sessions. The backend
will expose a tenant-scoped `/admin/app/design-reviews/bootstrap.json` envelope
over existing design-review and workflow-registry records. The React workspace
will render session history, selected-session detail, revision and round
history, reviewer verdict summaries, quorum decisions, manual-resolution
actions, workflow options, and development handoff state. The feature is
additive and uses existing design-review/coordinator APIs for mutations.

## Technical Context

**Language/Version**: Python 3.12; TypeScript strict mode on Node.js `>=20.19.0 <26`  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 async ORM, React 19, Vite, Vitest, Testing Library, Playwright  
**Storage**: Existing PostgreSQL design-review, workflow-registry, runtime, audit, and artifact tables  
**Testing**: pytest, ruff, mypy, Vitest, TypeScript typecheck, Playwright, Spec Kit QA runner, multi-agent curl test  
**Constraints**: No raw secrets, prompts, completions, provider payloads, private messages, memory contents, unauthorized payloads, or external tool payloads in UI/API/QA artifacts  
**Scope**: Additive admin workspace; no database migration expected

## Constitution Check

- Tenant isolation fails closed through existing principal and active-scope handling.
- The backend envelope is live-data only and must not create sample records.
- UI visible copy avoids implementation-framework labels.
- Mutations reuse existing domain/coordinator services and idempotency.
- QA is deterministic with local-principal auth and mocked provider boundaries.

## Project Structure

```text
src/multi_agent_platform/admin/design_review/
  react_workspace.py
src/multi_agent_platform/api/schemas/
  admin_design_review_workspace.py
src/multi_agent_platform/api/routers/
  admin_react.py
frontend/admin/src/components/designReviews/
frontend/admin/src/test/designReviewWorkspaceTestData.ts
tests/integration/api/test_admin_design_review_workspace_api.py
scripts/qa/seed_design_review_workspace_qa063.py
scripts/qa/verify_design_review_workspace_qa063.py
```

## Phase 0 Research

See `research.md`.

## Phase 1 Design

See `data-model.md` and `contracts/`.

## Phase 2 Tasks

See `tasks.md`.

## Complexity Tracking

No constitutional violations or planned complexity exceptions.
